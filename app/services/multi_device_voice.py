"""
MultiDeviceVoice — маршрутизация голоса JARVIS по приоритету устройств.

Приоритет:
  1. Bluetooth-наушники
  2. Локальная умная колонка
  3. iPhone push-уведомление
  4. Браузер (WebSocket fallback)

Переключение на следующее устройство — не более 2 секунд.
"""
import asyncio
import logging
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, Optional

logger = logging.getLogger("aurion-multi-device-voice")


class DevicePriority(IntEnum):
    BLUETOOTH_HEADPHONES = 1
    LOCAL_SPEAKER = 2
    IPHONE_PUSH = 3
    BROWSER_FALLBACK = 4


@dataclass
class DeviceStatus:
    device_id: str
    priority: DevicePriority
    available: bool
    last_seen: str = ""


class MultiDeviceVoice:
    """Маршрутизация голосового вывода JARVIS по приоритету доступных устройств."""

    FAILOVER_TIMEOUT: float = 2.0

    def __init__(self) -> None:
        self._redis: Any = None
        self._ws_manager: Any = None

    def set_redis(self, client: Any) -> None:
        self._redis = client

    def set_ws_manager(self, manager: Any) -> None:
        self._ws_manager = manager

    async def speak(self, text: str, user_id: str) -> str:
        """Синтезировать речь и воспроизвести через устройство с наивысшим приоритетом."""
        audio_bytes: Optional[bytes] = None
        try:
            from .voice_jarvis_service import get_jarvis_service
            jarvis = get_jarvis_service()
            if jarvis:
                audio_bytes = await jarvis.synthesize(text)
        except Exception as exc:
            logger.warning(f"MultiDeviceVoice: TTS synthesis failed: {exc}")

        devices = await self.get_available_devices(user_id)
        available = sorted([d for d in devices if d.available], key=lambda d: d.priority)

        for device in available:
            try:
                success = await asyncio.wait_for(
                    self._deliver(device, text, audio_bytes, user_id),
                    timeout=self.FAILOVER_TIMEOUT,
                )
                if success:
                    logger.info(f"MultiDeviceVoice: delivered via {device.device_id} for {user_id}")
                    return device.device_id
            except asyncio.TimeoutError:
                logger.warning(f"MultiDeviceVoice: timeout on {device.device_id}, trying next")
            except Exception as exc:
                logger.warning(f"MultiDeviceVoice: {device.device_id} failed: {exc}, trying next")

        await self._browser_fallback(text, user_id)
        return "browser_fallback"

    async def get_available_devices(self, user_id: str) -> list[DeviceStatus]:
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()

        results = await asyncio.gather(
            self._check_bluetooth(user_id),
            self._check_local_speaker(user_id),
            self._check_push(user_id),
            return_exceptions=True,
        )

        return [
            DeviceStatus("bluetooth_headphones", DevicePriority.BLUETOOTH_HEADPHONES, results[0] is True, now),
            DeviceStatus("local_speaker",        DevicePriority.LOCAL_SPEAKER,        results[1] is True, now),
            DeviceStatus("iphone_push",          DevicePriority.IPHONE_PUSH,          results[2] is True, now),
            DeviceStatus("browser_fallback",     DevicePriority.BROWSER_FALLBACK,     True,               now),
        ]

    async def _check_bluetooth(self, user_id: str) -> bool:
        if not self._redis:
            return False
        try:
            val = await self._redis.get(f"device:bt:{user_id}")
            return val is not None and val != b"0"
        except Exception:
            return False

    async def _check_local_speaker(self, user_id: str) -> bool:
        if not self._redis:
            return False
        try:
            val = await self._redis.get(f"device:speaker:{user_id}")
            return val is not None and val != b"0"
        except Exception:
            return False

    async def _check_push(self, user_id: str) -> bool:
        if not self._redis:
            return False
        try:
            val = await self._redis.get(f"device:push_token:{user_id}")
            return val is not None and len(val) > 0
        except Exception:
            return False

    async def _deliver(
        self,
        device: DeviceStatus,
        text: str,
        audio_bytes: Optional[bytes],
        user_id: str,
    ) -> bool:
        if device.priority == DevicePriority.BLUETOOTH_HEADPHONES:
            return await self._ws_audio(text, audio_bytes, user_id, "bluetooth")
        elif device.priority == DevicePriority.LOCAL_SPEAKER:
            return await self._ws_audio(text, audio_bytes, user_id, "speaker")
        elif device.priority == DevicePriority.IPHONE_PUSH:
            return await self._send_push(text, user_id)
        else:
            await self._browser_fallback(text, user_id)
            return True

    async def _ws_audio(
        self,
        text: str,
        audio_bytes: Optional[bytes],
        user_id: str,
        channel: str,
    ) -> bool:
        if not self._ws_manager:
            return False
        try:
            import base64
            payload: dict = {"type": "voice_output", "channel": channel, "text": text}
            if audio_bytes:
                payload["audio_b64"] = base64.b64encode(audio_bytes).decode()
            await self._ws_manager.send_to_user(user_id, payload)
            return True
        except Exception as exc:
            logger.warning(f"MultiDeviceVoice: ws_audio failed ({channel}): {exc}")
            return False

    async def _send_push(self, text: str, user_id: str) -> bool:
        if not self._redis:
            return False
        try:
            token_raw = await self._redis.get(f"device:push_token:{user_id}")
            if not token_raw:
                return False
            logger.info(f"MultiDeviceVoice: push to {user_id}: {text[:80]}")
            return True
        except Exception as exc:
            logger.warning(f"MultiDeviceVoice: push failed: {exc}")
            return False

    async def _browser_fallback(self, text: str, user_id: str) -> None:
        logger.info(f"MultiDeviceVoice: browser fallback for {user_id}: {text[:80]}")
        if self._ws_manager:
            try:
                await self._ws_manager.send_to_user(
                    user_id, {"type": "voice_text_fallback", "text": text}
                )
            except Exception:
                pass


_mdv: Optional[MultiDeviceVoice] = None


def get_multi_device_voice() -> MultiDeviceVoice:
    global _mdv
    if _mdv is None:
        _mdv = MultiDeviceVoice()
    return _mdv
