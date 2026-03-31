"""
DeviceDiscovery — гибридное обнаружение IoT-устройств в локальной сети.

Сканирует через mDNS (zeroconf) и UPnP SSDP.
При обнаружении устройства создаёт FeedCard для подтверждения пользователем.
"""
import asyncio
import logging
import socket
import re
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("aurion-device-discovery")


@dataclass
class DiscoveredDevice:
    name: str
    ip: str
    mac: str = ""
    device_type: str = "unknown"
    protocol: str = "unknown"
    properties: dict = field(default_factory=dict)


class DeviceDiscovery:

    def __init__(self) -> None:
        self._redis: Any = None

    def set_redis(self, client: Any) -> None:
        self._redis = client

    async def scan(self, user_id: str) -> list[DiscoveredDevice]:
        """Сканировать сеть. Найденные устройства публикуются в Activity Feed."""
        mdns = await self._scan_mdns()
        upnp = await self._scan_upnp()

        seen: set[str] = set()
        unique: list[DiscoveredDevice] = []
        for d in mdns + upnp:
            if d.ip not in seen:
                seen.add(d.ip)
                unique.append(d)

        logger.info(f"DeviceDiscovery: found {len(unique)} devices for user {user_id}")
        for device in unique:
            await self._notify_user(user_id, device)
        return unique

    async def register_device(self, user_id: str, device_data: dict) -> bool:
        """Зарегистрировать устройство после подтверждения пользователем."""
        try:
            from ..database_final import AsyncSessionLocal
            from ..models.device import Device
            import uuid

            async with AsyncSessionLocal() as db:
                device = Device(
                    user_id=uuid.UUID(user_id),
                    name=device_data.get("name", "Новое устройство"),
                    device_type=device_data.get("device_type", "unknown"),
                    ip_address=device_data.get("ip", ""),
                    mac_address=device_data.get("mac", ""),
                    is_active=True,
                    properties=device_data.get("properties", {}),
                )
                db.add(device)
                await db.commit()
            return True
        except Exception as exc:
            logger.error(f"DeviceDiscovery: register_device failed: {exc}")
            return False

    async def _scan_mdns(self) -> list[DiscoveredDevice]:
        devices: list[DiscoveredDevice] = []
        try:
            from zeroconf.asyncio import AsyncZeroconf
            from zeroconf import ServiceBrowser

            service_types = [
                "_http._tcp.local.",
                "_googlecast._tcp.local.",
                "_hap._tcp.local.",
                "_matter._tcp.local.",
            ]
            azc = AsyncZeroconf()
            found: list[dict] = []

            class Listener:
                def add_service(self, zc: Any, type_: str, name: str) -> None:
                    info = zc.get_service_info(type_, name)
                    if info:
                        addrs = info.parsed_addresses()
                        found.append({
                            "name": name.split(".")[0],
                            "ip": addrs[0] if addrs else "",
                            "device_type": _guess_type_mdns(type_),
                            "protocol": "mdns",
                        })
                def remove_service(self, *_: Any) -> None: pass
                def update_service(self, *_: Any) -> None: pass

            browsers = [ServiceBrowser(azc.zeroconf, st, Listener()) for st in service_types]
            await asyncio.sleep(3)
            for b in browsers:
                b.cancel()
            await azc.async_close()
            devices = [DiscoveredDevice(**d) for d in found if d.get("ip")]
        except ImportError:
            logger.debug("zeroconf не установлен — mDNS недоступен")
        except Exception as exc:
            logger.warning(f"mDNS scan failed: {exc}")
        return devices

    async def _scan_upnp(self) -> list[DiscoveredDevice]:
        devices: list[DiscoveredDevice] = []
        try:
            SSDP_ADDR = "239.255.255.250"
            SSDP_PORT = 1900
            msg = (
                "M-SEARCH * HTTP/1.1\r\n"
                f"HOST: {SSDP_ADDR}:{SSDP_PORT}\r\n"
                "MAN: \"ssdp:discover\"\r\n"
                "MX: 2\r\n"
                "ST: upnp:rootdevice\r\n\r\n"
            ).encode()

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
            sock.settimeout(3)
            sock.sendto(msg, (SSDP_ADDR, SSDP_PORT))

            seen: set[str] = set()
            try:
                while True:
                    data, addr = sock.recvfrom(1024)
                    ip = addr[0]
                    if ip not in seen:
                        seen.add(ip)
                        response = data.decode(errors="ignore")
                        m = re.search(r"SERVER:\s*(.+)", response, re.IGNORECASE)
                        server = m.group(1).strip() if m else ""
                        devices.append(DiscoveredDevice(
                            name=server or f"UPnP ({ip})",
                            ip=ip,
                            device_type=_guess_type_upnp(server),
                            protocol="upnp",
                        ))
            except socket.timeout:
                pass
            finally:
                sock.close()
        except Exception as exc:
            logger.warning(f"UPnP scan failed: {exc}")
        return devices

    async def _notify_user(self, user_id: str, device: DiscoveredDevice) -> None:
        try:
            from ..database_final import AsyncSessionLocal
            from ..models.feed_card import FeedCard
            import uuid

            async with AsyncSessionLocal() as db:
                card = FeedCard(
                    user_id=uuid.UUID(user_id),
                    type="suggestion",
                    domain="security",
                    title=f"Обнаружено устройство: {device.name}",
                    body=f"IP: {device.ip}, тип: {device.device_type}. Добавить в умный дом?",
                    priority="medium",
                    requires_confirmation=True,
                )
                db.add(card)
                await db.commit()
        except Exception as exc:
            logger.warning(f"DeviceDiscovery: notify_user failed: {exc}")


def _guess_type_mdns(service_type: str) -> str:
    if "googlecast" in service_type:
        return "tv"
    if "hap" in service_type or "matter" in service_type:
        return "smart_home"
    return "unknown"


def _guess_type_upnp(server: str) -> str:
    s = server.lower()
    if any(x in s for x in ("yeelight", "hue", "philips")):
        return "light"
    if any(x in s for x in ("chromecast", "roku")):
        return "tv"
    return "unknown"


_discovery: Optional[DeviceDiscovery] = None


def get_device_discovery() -> DeviceDiscovery:
    global _discovery
    if _discovery is None:
        _discovery = DeviceDiscovery()
    return _discovery
