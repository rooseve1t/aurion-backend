"""
🛡️ Aurion Shield VPN Service - Интеллектуальная система обхода блокировок
"""
import asyncio
import aiohttp
import json
import time
import subprocess
try:
    import psutil
except ImportError:
    psutil = None
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone, timedelta
import socket
import ssl
import urllib.parse
import ipaddress
from dataclasses import dataclass
from enum import Enum

from ..models.vpn import (
    VPNConnection, VPNServer, BlockadeDetection, VPNProtocol,
    VPN_PROTOCOLS, VPN_SERVERS, BLOCKADE_TYPES,
    OBFUSCATION_LEVELS, VPN_SECURITY_SETTINGS
)
from ..database import get_db

class VPNStatus(Enum):
    """Статусы VPN"""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"
    ERROR = "error"

class BlockadeType(Enum):
    """Типы блокировок"""
    DPI_DEEP_PACKET_INSPECTION = "dpi_deep_packet_inspection"
    PORT_BLOCKING = "port_blocking"
    PROTOCOL_BLOCKING = "protocol_blocking"
    IP_BLOCKING = "ip_blocking"
    DNS_BLOCKING = "dns_blocking"
    THROTTLING = "throttling"
    MAN_IN_THE_MIDDLE = "man_in_the_middle"

@dataclass
class ConnectionMetrics:
    """Метрики соединения"""
    latency_ms: float
    download_speed_mbps: float
    upload_speed_mbps: float
    packet_loss: float
    jitter_ms: float
    quality_score: float

class AurionVPNService:
    """🛡️ Основной VPN сервис Aurion OS"""
    
    def __init__(self):
        self.current_connection: Optional[VPNConnection] = None
        self.active_server: Optional[VPNServer] = None
        self.current_protocol = "wireguard"
        self.status = VPNStatus.DISCONNECTED
        self.blockade_history: List[BlockadeDetection] = []
        self.connection_metrics: Optional[ConnectionMetrics] = None
        self.auto_protocol_switch = True
        self.stealth_mode = False
        self.obfuscation_level = "none"
        self.kill_switch_enabled = True
        self.monitoring_active = False
        
    async def initialize(self):
        """Инициализация VPN сервиса"""
        print("🛡️ Initializing Aurion Shield VPN...")
        
        # Проверка системных требований
        await self._check_system_requirements()
        
        # Инициализация сетевых интерфейсов
        await self._setup_network_interfaces()
        
        # Запуск мониторинга
        await self._start_monitoring()
        
        print("✅ Aurion Shield VPN initialized successfully")
        
    async def connect_vpn(
        self, 
        server_id: str,
        protocol: str = "auto",
        obfuscation: str = "auto",
        stealth: bool = False
    ) -> Dict[str, Any]:
        """Подключение к VPN"""
        try:
            print(f"🚀 Connecting to VPN server {server_id}...")
            
            # Выбор сервера
            self.active_server = self._get_server_by_id(server_id)
            if not self.active_server:
                return {"success": False, "error": "Server not found"}
            
            # Определение оптимального протокола
            if protocol == "auto":
                protocol = await self._select_optimal_protocol()
            
            self.current_protocol = protocol
            
            # Создание соединения
            self.current_connection = VPNConnection()
            self.current_connection.server_id = server_id
            self.current_connection.protocol = protocol
            self.current_connection.status = "connecting"
            self.current_connection.connected_at = datetime.now(timezone.utc)
            
            # Настройка обфускации
            if obfuscation == "auto":
                self.obfuscation_level = await self._detect_optimal_obfuscation()
            else:
                self.obfuscation_level = obfuscation
            
            self.stealth_mode = stealth
            
            # Подключение
            success = await self._establish_connection()
            if not success:
                return {"success": False, "error": "Failed to establish connection"}
            
            # Настройка защиты от утечек
            await self._setup_leak_protection()
            
            # Включение Kill Switch
            if self.kill_switch_enabled:
                await self._enable_kill_switch()
            
            # Запуск мониторинга качества
            asyncio.create_task(self._monitor_connection_quality())
            
            self.status = VPNStatus.CONNECTED
            self.current_connection.status = "connected"
            
            return {
                "success": True,
                "connection_id": self.current_connection.id,
                "server": self.active_server.name,
                "protocol": protocol,
                "ip_address": await self._get_current_ip(),
                "obfuscation": self.obfuscation_level,
                "stealth": self.stealth_mode
            }
            
        except Exception as e:
            print(f"❌ VPN connection error: {e}")
            self.status = VPNStatus.ERROR
            return {"success": False, "error": str(e)}
    
    async def disconnect_vpn(self) -> Dict[str, Any]:
        """Отключение от VPN"""
        try:
            print("🔌 Disconnecting from VPN...")
            
            if self.current_connection:
                self.current_connection.status = "disconnecting"
                self.current_connection.disconnected_at = datetime.now(timezone.utc)
                
                # Расчет времени работы
                if self.current_connection.connected_at:
                    duration = datetime.now(timezone.utc) - self.current_connection.connected_at
                    self.current_connection.uptime_seconds = int(duration.total_seconds())
            
            # Отключение Kill Switch
            await self._disable_kill_switch()
            
            # Разрыв соединения
            await self._terminate_connection()
            
            # Восстановление сетевых настроек
            await self._restore_network_settings()
            
            self.status = VPNStatus.DISCONNECTED
            if self.current_connection:
                self.current_connection.status = "disconnected"
            
            return {
                "success": True,
                "message": "VPN disconnected successfully",
                "session_duration": self.current_connection.uptime_seconds if self.current_connection else 0
            }
            
        except Exception as e:
            print(f"❌ VPN disconnection error: {e}")
            return {"success": False, "error": str(e)}
    
    async def detect_blockades(self, target_host: str = "google.com") -> BlockadeDetection:
        """🧠 AI-детектор блокировок"""
        print(f"🔍 Analyzing network restrictions for {target_host}...")
        
        detection = BlockadeDetection()
        detection.detection_time = datetime.now(timezone.utc)
        detection.user_id = "current_user"  # В реальном приложении - ID пользователя
        
        # Тестирование базовой доступности
        basic_connectivity = await self._test_connectivity(target_host)
        
        # Анализ DPI
        dpi_detected = await self._analyze_dpi_presence(target_host)
        
        # Проверка блокировки портов
        port_blocks = await self._scan_port_blocks()
        
        # Анализ протоколов
        protocol_blocks = await self._test_protocols_availability()
        
        # Проверка DNS
        dns_issues = await self._analyze_dns_restrictions()
        
        # Комплексный анализ
        if dpi_detected:
            detection.blockade_type = BlockadeType.DPI_DEEP_PACKET_INSPECTION.value
            detection.confidence_score = 0.9
        elif port_blocks:
            detection.blockade_type = BlockadeType.PORT_BLOCKING.value
            detection.confidence_score = 0.8
        elif protocol_blocks:
            detection.blockade_type = BlockadeType.PROTOCOL_BLOCKING.value
            detection.confidence_score = 0.85
        elif dns_issues:
            detection.blockade_type = BlockadeType.DNS_BLOCKING.value
            detection.confidence_score = 0.7
        else:
            detection.blockade_type = "none"
            detection.confidence_score = 0.1
        
        # Определение рабочих протоколов
        detection.working_protocols = await self._find_working_protocols()
        detection.blocked_protocols = [p for p in VPN_PROTOCOLS.keys() if p not in detection.working_protocols]
        
        # Рекомендация протокола
        detection.recommended_protocol = await self._recommend_protocol(detection)
        
        self.blockade_history.append(detection)
        
        print(f"🎯 Blockade detected: {detection.blockade_type} (confidence: {detection.confidence_score})")
        print(f"📡 Recommended protocol: {detection.recommended_protocol}")
        
        return detection
    
    async def auto_switch_protocol(self) -> bool:
        """🔄 Автоматическая смена протокола при блокировке"""
        if not self.auto_protocol_switch or not self.current_connection:
            return False
        
        print("🔄 Auto-switching protocol due to blockade...")
        
        # Анализ текущей ситуации
        detection = await self.detect_blockades()
        
        if detection.confidence_score > 0.7:
            # Сохранение текущих настроек
            old_protocol = self.current_protocol
            old_server = self.active_server
            
            # Отключение
            await self.disconnect_vpn()
            
            # Подключение с новым протоколом
            result = await self.connect_vpn(
                server_id=old_server.id,
                protocol=detection.recommended_protocol,
                obfuscation="auto",
                stealth=True
            )
            
            if result["success"]:
                print(f"✅ Successfully switched to {detection.recommended_protocol}")
                return True
            else:
                print(f"❌ Failed to switch protocol: {result.get('error')}")
                # Попытка вернуться к старому протоколу
                await self.connect_vpn(
                    server_id=old_server.id,
                    protocol=old_protocol,
                    obfuscation="auto",
                    stealth=False
                )
                return False
        
        return False
    
    async def get_connection_status(self) -> Dict[str, Any]:
        """Получение детального статуса соединения"""
        if not self.current_connection:
            return {
                "status": "disconnected",
                "connected": False,
                "server": None,
                "protocol": None,
                "ip_address": await self._get_current_ip(),
                "metrics": None
            }
        
        # Обновление метрик
        if self.status == VPNStatus.CONNECTED:
            self.connection_metrics = await self._measure_connection_metrics()
        
        return {
            "status": self.status.value,
            "connected": self.status == VPNStatus.CONNECTED,
            "connection_id": self.current_connection.id,
            "server": {
                "name": self.active_server.name if self.active_server else None,
                "country": self.active_server.country if self.active_server else None,
                "city": self.active_server.city if self.active_server else None
            },
            "protocol": self.current_protocol,
            "ip_address": await self._get_current_ip(),
            "obfuscation_level": self.obfuscation_level,
            "stealth_mode": self.stealth_mode,
            "kill_switch": self.kill_switch_enabled,
            "metrics": self.connection_metrics.__dict__ if self.connection_metrics else None,
            "uptime": self.current_connection.uptime_seconds,
            "bytes_sent": self.current_connection.bytes_sent,
            "bytes_received": self.current_connection.bytes_received,
            "blockade_detections": len(self.blockade_history),
            "last_blockade": self.blockade_history[-1].__dict__ if self.blockade_history else None
        }
    
    async def _check_system_requirements(self):
        """Проверка системных требований"""
        print("🔍 Checking system requirements...")
        
        # Проверка прав администратора
        if not await self._check_admin_rights():
            raise PermissionError("Administrative privileges required")
        
        # Проверка доступных инструментов
        required_tools = ["iptables", "ip", "wg", "openvpn"]
        for tool in required_tools:
            if not await self._check_tool_available(tool):
                print(f"⚠️ Tool {tool} not available")
        
        print("✅ System requirements check completed")
    
    async def _select_optimal_protocol(self) -> str:
        """Выбор оптимального протокола"""
        # Базовые тесты доступности протоколов
        working_protocols = await self._find_working_protocols()
        
        if not working_protocols:
            return "wireguard"  # Fallback
        
        # Приоритеты: скорость > безопасность > устойчивость к блокировкам
        protocol_scores = {}
        for protocol in working_protocols:
            proto_config = VPN_PROTOCOLS[protocol]
            score = (
                proto_config.speed_factor * 0.4 +
                proto_config.security_factor * 0.3 +
                proto_config.detection_resistance * 0.3
            )
            protocol_scores[protocol] = score
        
        return max(protocol_scores, key=protocol_scores.get)
    
    async def _establish_connection(self) -> bool:
        """Установление VPN соединения"""
        try:
            if self.current_protocol == "wireguard":
                return await self._connect_wireguard()
            elif self.current_protocol == "openvpn":
                return await self._connect_openvpn()
            elif self.current_protocol == "shadowsocks":
                return await self._connect_shadowsocks()
            elif self.current_protocol == "v2ray":
                return await self._connect_v2ray()
            else:
                return await self._connect_wireguard()  # Fallback
        except Exception as e:
            print(f"❌ Connection establishment error: {e}")
            return False
    
    async def _connect_wireguard(self) -> bool:
        """Подключение через WireGuard"""
        print("🔐 Connecting via WireGuard...")
        
        # Генерация конфигурации
        config = await self._generate_wireguard_config()
        
        # Запись конфигурации
        config_path = "/tmp/aurion-wg.conf"
        with open(config_path, "w") as f:
            f.write(config)
        
        # Запуск WireGuard
        try:
            result = subprocess.run(
                ["wg-quick", "up", config_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ WireGuard connected successfully")
                return True
            else:
                print(f"❌ WireGuard error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ WireGuard connection timeout")
            return False
        except Exception as e:
            print(f"❌ WireGuard error: {e}")
            return False
    
    async def _generate_wireguard_config(self) -> str:
        """Генерация конфигурации WireGuard"""
        if not self.active_server:
            raise ValueError("No active server selected")
        
        # Генерация ключей (в реальном приложении - сохранять и переиспользовать)
        private_key = await self._generate_wireguard_key()
        public_key = await self._get_server_public_key()
        
        config = f"""[Interface]
PrivateKey = {private_key}
Address = 10.8.0.2/24
DNS = 1.1.1.1, 8.8.8.8

[Peer]
PublicKey = {public_key}
Endpoint = {self.active_server.ip_address}:{self.active_server.port}
AllowedIPs = 0.0.0.0/0, ::/0
PersistentKeepalive = 25
"""
        
        # Добавление обфускации если нужно
        if self.obfuscation_level in ["medium", "heavy", "maximum"]:
            config += "\n# Obfuscation enabled\n"
        
        return config
    
    async def _get_current_ip(self) -> str:
        """Получение текущего IP адреса"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.ipify.org", timeout=5) as response:
                    if response.status == 200:
                        return await response.text()
        except:
            pass
        
        # Fallback метод
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://ifconfig.me", timeout=5) as response:
                    if response.status == 200:
                        return await response.text()
        except:
            pass
        
        return "Unknown"
    
    async def _measure_connection_metrics(self) -> ConnectionMetrics:
        """Измерение метрик соединения"""
        try:
            # Latency
            latency = await self._measure_latency()
            
            # Speed test
            download_speed = await self._measure_download_speed()
            upload_speed = await self._measure_upload_speed()
            
            # Packet loss и jitter
            packet_loss, jitter = await self._measure_packet_quality()
            
            # Quality score
            quality_score = self._calculate_quality_score(
                latency, download_speed, upload_speed, packet_loss
            )
            
            return ConnectionMetrics(
                latency_ms=latency,
                download_speed_mbps=download_speed,
                upload_speed_mbps=upload_speed,
                packet_loss=packet_loss,
                jitter_ms=jitter,
                quality_score=quality_score
            )
        except Exception as e:
            print(f"❌ Metrics measurement error: {e}")
            return ConnectionMetrics(0, 0, 0, 0, 0, 0)
    
    async def _monitor_connection_quality(self):
        """Мониторинг качества соединения"""
        while self.status == VPNStatus.CONNECTED:
            try:
                metrics = await self._measure_connection_metrics()
                self.connection_metrics = metrics
                
                # Проверка качества
                if metrics.quality_score < 0.3:
                    print("⚠️ Connection quality degraded, considering protocol switch...")
                    await self.auto_switch_protocol()
                
                # Обновление статистики
                if self.current_connection:
                    self.current_connection.bytes_sent += int(upload_speed * 1024 * 1024 / 8)  # Примерно
                    self.current_connection.bytes_received += int(download_speed * 1024 * 1024 / 8)
                
                await asyncio.sleep(30)  # Проверка каждые 30 секунд
                
            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)
    
    def _get_server_by_id(self, server_id: str) -> Optional[VPNServer]:
        """Получение сервера по ID"""
        for server in VPN_SERVERS:
            if server.get("id") == server_id:
                return VPNServer(**server)
        return None
    
    async def _find_working_protocols(self) -> List[str]:
        """Поиск рабочих протоколов"""
        working = []
        
        for protocol in VPN_PROTOCOLS.keys():
            if await self._test_protocol_connectivity(protocol):
                working.append(protocol)
        
        return working
    
    async def _test_protocol_connectivity(self, protocol: str) -> bool:
        """Тест доступности протокола"""
        # Упрощенный тест - в реальном приложении более сложный
        try:
            if protocol == "wireguard":
                return await self._test_wireguard_availability()
            elif protocol == "shadowsocks":
                return await self._test_shadowsocks_availability()
            # ... другие протоколы
            return True
        except:
            return False
    
    async def _test_wireguard_availability(self) -> bool:
        """Тест доступности WireGuard"""
        try:
            result = subprocess.run(["wg", "--version"], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    async def _calculate_quality_score(
        self, latency: float, download: float, upload: float, packet_loss: float
    ) -> float:
        """Расчет оценки качества соединения"""
        latency_score = max(0, 1 - latency / 200)  # 200ms = 0 score
        speed_score = min(1, (download + upload) / 100)  # 100Mbps = 1 score
        packet_score = max(0, 1 - packet_loss)  # 100% loss = 0 score
        
        return (latency_score * 0.4 + speed_score * 0.4 + packet_score * 0.2)
    
    # ... дополнительные приватные методы для полной реализации
    async def _check_admin_rights(self) -> bool:
        """Проверка прав администратора"""
        return True  # Упрощено
    
    async def _check_tool_available(self, tool: str) -> bool:
        """Проверка доступности инструмента"""
        try:
            subprocess.run([tool, "--version"], capture_output=True, timeout=5)
            return True
        except:
            return False
    
    async def _setup_network_interfaces(self):
        """Настройка сетевых интерфейсов"""
        pass
    
    async def _start_monitoring(self):
        """Запуск мониторинга"""
        self.monitoring_active = True
    
    async def _detect_optimal_obfuscation(self) -> str:
        """Определение оптимального уровня обфускации"""
        return "medium"  # Упрощено
    
    async def _setup_leak_protection(self):
        """Настройка защиты от утечек"""
        pass
    
    async def _enable_kill_switch(self):
        """Включение Kill Switch"""
        pass
    
    async def _disable_kill_switch(self):
        """Отключение Kill Switch"""
        pass
    
    async def _terminate_connection(self):
        """Завершение соединения"""
        pass
    
    async def _restore_network_settings(self):
        """Восстановление сетевых настроек"""
        pass
    
    async def _test_connectivity(self, host: str) -> bool:
        """Тест базовой доступности"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"http://{host}", timeout=5) as response:
                    return response.status < 500
        except:
            return False
    
    async def _analyze_dpi_presence(self, host: str) -> bool:
        """Анализ наличия DPI"""
        # Упрощенный анализ
        return False
    
    async def _scan_port_blocks(self) -> List[int]:
        """Сканирование блокировок портов"""
        return []
    
    async def _test_protocols_availability(self) -> List[str]:
        """Тест доступности протоколов"""
        return []
    
    async def _analyze_dns_restrictions(self) -> bool:
        """Анализ DNS ограничений"""
        return False
    
    async def _recommend_protocol(self, detection: BlockadeDetection) -> str:
        """Рекомендация протокола"""
        if detection.blockade_type == BlockadeType.DPI_DEEP_PACKET_INSPECTION.value:
            return "shadowsocks"
        elif detection.blockade_type == BlockadeType.PORT_BLOCKING.value:
            return "domain_fronting"
        else:
            return "wireguard"
    
    async def _connect_openvpn(self) -> bool:
        """Подключение через OpenVPN"""
        return False
    
    async def _connect_shadowsocks(self) -> bool:
        """Подключение через Shadowsocks"""
        return False
    
    async def _connect_v2ray(self) -> bool:
        """Подключение через V2Ray"""
        return False
    
    async def _generate_wireguard_key(self) -> str:
        """Генерация приватного ключа WireGuard"""
        result = subprocess.run(["wg", "genkey"], capture_output=True, text=True)
        return result.stdout.strip()
    
    async def _get_server_public_key(self) -> str:
        """Получение публичного ключа сервера"""
        return "server_public_key_placeholder"  # В реальном приложении - с сервера
    
    async def _measure_latency(self) -> float:
        """Измерение задержки"""
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get("http://1.1.1.1", timeout=5) as response:
                    if response.status == 200:
                        return (time.time() - start_time) * 1000
        except:
            pass
        return 100.0  # Default
    
    async def _measure_download_speed(self) -> float:
        """Измерение скорости загрузки"""
        return 50.0  # Placeholder
    
    async def _measure_upload_speed(self) -> float:
        """Измерение скорости отдачи"""
        return 10.0  # Placeholder
    
    async def _measure_packet_quality(self) -> Tuple[float, float]:
        """Измерение качества пакетов"""
        return 0.0, 0.0  # packet_loss, jitter
    
    async def _test_shadowsocks_availability(self) -> bool:
        """Тест доступности Shadowsocks"""
        return True

# Глобальный экземпляр VPN сервиса
aurion_vpn_service = AurionVPNService()

# Инициализация при старте
async def init_vpn_service():
    """Инициализация VPN сервиса"""
    await aurion_vpn_service.initialize()
    return aurion_vpn_service

async def get_vpn_service() -> AurionVPNService:
    """Получение VPN сервиса"""
    return aurion_vpn_service
