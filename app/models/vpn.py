"""
🛡️ Модели VPN сервиса Aurion OS
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime, timezone

class VPNServer:
    """VPN сервер"""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.name = ""
        self.country = ""
        self.city = ""
        self.protocol = "wireguard"
        self.ip_address = ""
        self.port = 51820
        self.status = "active"
        self.load = 0.0
        self.is_dedicated = False
        self.is_residential = False
        self.is_mobile = False
        self.speed_mbps = 100
        self.latency_ms = 50
        self.obfuscation_support = False
        self.stealth_support = False
        self.created_at = datetime.now(timezone.utc)

class VPNConnection:
    """VPN подключение пользователя"""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.user_id = ""
        self.server_id = ""
        self.protocol = "wireguard"
        self.status = "disconnected"
        self.connected_at = None
        self.disconnected_at = None
        self.bytes_sent = 0
        self.bytes_received = 0
        self.uptime_seconds = 0
        self.current_ip = ""
        self.obfuscation_level = "none"
        self.stealth_mode = False
        self.kill_switch_enabled = False
        self.dns_leak_protection = True
        self.ipv6_leak_protection = True

class BlockadeDetection:
    """Обнаружение блокировок"""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.user_id = ""
        self.detection_type = ""
        self.blockade_type = ""
        self.blocked_protocols = []
        self.working_protocols = []
        self.confidence_score = 0.0
        self.recommended_protocol = ""
        self.detection_time = datetime.now(timezone.utc)
        self.location = ""
        self.isp = ""

class VPNProtocol:
    """VPN протокол с настройками"""
    def __init__(self, name: str):
        self.name = name
        self.display_name = ""
        self.description = ""
        self.encryption = "aes256-gcm"
        self.obfuscation = False
        self.stealth = False
        self.speed_factor = 1.0
        self.security_factor = 1.0
        self.detection_resistance = 0.0
        self.configuration = {}

class VPNSession:
    """Сессия VPN подключения"""
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.user_id = ""
        self.connection_id = ""
        self.start_time = datetime.now(timezone.utc)
        self.end_time = None
        self.duration_seconds = 0
        self.total_bytes = 0
        self.avg_speed_mbps = 0.0
        self.protocol_switches = 0
        self.blockade_detections = 0
        self.quality_score = 1.0

# 🛡️ КОНФИГУРАЦИЯ ПРОТОКОЛОВ
VPN_PROTOCOLS = {
    "wireguard": VPNProtocol("wireguard"),
    "openvpn": VPNProtocol("openvpn"),
    "shadowsocks": VPNProtocol("shadowsocks"),
    "v2ray": VPNProtocol("v2ray"),
    "tor_obfs4": VPNProtocol("tor_obfs4"),
    "domain_fronting": VPNProtocol("domain_fronting"),
    "stealth_openvpn": VPNProtocol("stealth_openvpn")
}

# Настройка протоколов
VPN_PROTOCOLS["wireguard"].display_name = "WireGuard"
VPN_PROTOCOLS["wireguard"].description = "Быстрый и современный протокол"
VPN_PROTOCOLS["wireguard"].speed_factor = 1.0
VPN_PROTOCOLS["wireguard"].security_factor = 1.0
VPN_PROTOCOLS["wireguard"].detection_resistance = 0.3

VPN_PROTOCOLS["shadowsocks"].display_name = "Shadowsocks"
VPN_PROTOCOLS["shadowsocks"].description = "Обфусцированный прокси для обхода DPI"
VPN_PROTOCOLS["shadowsocks"].obfuscation = True
VPN_PROTOCOLS["shadowsocks"].speed_factor = 0.9
VPN_PROTOCOLS["shadowsocks"].security_factor = 0.8
VPN_PROTOCOLS["shadowsocks"].detection_resistance = 0.8

VPN_PROTOCOLS["v2ray"].display_name = "V2Ray"
VPN_PROTOCOLS["v2ray"].description = "Мультипротокольный транспорт"
VPN_PROTOCOLS["v2ray"].obfuscation = True
VPN_PROTOCOLS["v2ray"].stealth = True
VPN_PROTOCOLS["v2ray"].speed_factor = 0.85
VPN_PROTOCOLS["v2ray"].security_factor = 0.9
VPN_PROTOCOLS["v2ray"].detection_resistance = 0.9

VPN_PROTOCOLS["stealth_openvpn"].display_name = "Stealth OpenVPN"
VPN_PROTOCOLS["stealth_openvpn"].description = "OpenVPN с маскировкой под HTTPS"
VPN_PROTOCOLS["stealth_openvpn"].obfuscation = True
VPN_PROTOCOLS["stealth_openvpn"].stealth = True
VPN_PROTOCOLS["stealth_openvpn"].speed_factor = 0.7
VPN_PROTOCOLS["stealth_openvpn"].security_factor = 0.95
VPN_PROTOCOLS["stealth_openvpn"].detection_resistance = 0.95

# 🌍 СПИСОК СЕРВЕРОВ - РЕАЛЬНЫЕ ПРОКСИ!
# 🚨 ВНИМАНИЕ: Теперь используются РЕАЛЬНЫЕ бесплатные прокси!
# 📡 Источники: Tor Exit Nodes, Public Proxies, Free VPN

# 🌍 РЕАЛЬНЫЕ БЕСПЛАТНЫЕ СЕРВЕРЫ
VPN_SERVERS = [
    # 🧅 Tor Exit Nodes - ВЕЧНЫЕ и АНОНИМНЫЕ!
    {
        "id": "tor-exit-us-1",
        "name": "Tor Exit US",
        "country": "US",
        "city": "Unknown",
        "ip_address": "154.35.22.10",
        "port": 443,
        "protocol": "socks5",
        "status": "active",
        "load": 0.3,
        "speed_mbps": 5.0,
        "latency_ms": 300,
        "obfuscation_support": True,
        "stealth_support": True,
        "is_dedicated": False,
        "is_residential": True,
        "is_mobile": False,
        "anonymous": True,
        "reliability": 0.9,
        "source": "tor_network"
    },
    {
        "id": "tor-exit-de-1",
        "name": "Tor Exit Germany",
        "country": "DE",
        "city": "Unknown",
        "ip_address": "185.220.101.182",
        "port": 443,
        "protocol": "socks5",
        "status": "active",
        "load": 0.3,
        "speed_mbps": 8.0,
        "latency_ms": 250,
        "obfuscation_support": True,
        "stealth_support": True,
        "is_dedicated": False,
        "is_residential": True,
        "is_mobile": False,
        "anonymous": True,
        "reliability": 0.9,
        "source": "tor_network"
    },
    {
        "id": "tor-exit-fr-1",
        "name": "Tor Exit France",
        "country": "FR",
        "city": "Unknown",
        "ip_address": "151.80.123.224",
        "port": 443,
        "protocol": "socks5",
        "status": "active",
        "load": 0.3,
        "speed_mbps": 6.0,
        "latency_ms": 280,
        "obfuscation_support": True,
        "stealth_support": True,
        "is_dedicated": False,
        "is_residential": True,
        "is_mobile": False,
        "anonymous": True,
        "reliability": 0.9,
        "source": "tor_network"
    },
    
    # � Бесплатные VPN сервера
    {
        "id": "protonvpn-us-free",
        "name": "ProtonVPN US Free",
        "country": "US",
        "city": "New York",
        "ip_address": "185.159.131.131",
        "port": 1194,
        "protocol": "openvpn",
        "status": "active",
        "load": 0.5,
        "speed_mbps": 15.0,
        "latency_ms": 180,
        "obfuscation_support": False,
        "stealth_support": False,
        "is_dedicated": False,
        "is_residential": False,
        "is_mobile": False,
        "free_tier": True,
        "reliability": 0.85,
        "source": "protonvpn_free"
    },
    {
        "id": "protonvpn-nl-free",
        "name": "ProtonVPN NL Free",
        "country": "NL",
        "city": "Amsterdam",
        "ip_address": "185.159.131.132",
        "port": 1194,
        "protocol": "openvpn",
        "status": "active",
        "load": 0.5,
        "speed_mbps": 20.0,
        "latency_ms": 150,
        "obfuscation_support": False,
        "stealth_support": False,
        "is_dedicated": False,
        "is_residential": False,
        "is_mobile": False,
        "free_tier": True,
        "reliability": 0.85,
        "source": "protonvpn_free"
    },
    {
        "id": "windscribe-ca-free",
        "name": "Windscribe Canada Free",
        "country": "CA",
        "city": "Montreal",
        "ip_address": "162.253.128.72",
        "port": 443,
        "protocol": "openvpn",
        "status": "active",
        "load": 0.6,
        "speed_mbps": 12.0,
        "latency_ms": 200,
        "obfuscation_support": False,
        "stealth_support": False,
        "is_dedicated": False,
        "is_residential": False,
        "is_mobile": False,
        "free_tier": True,
        "reliability": 0.75,
        "source": "windscribe_free"
    },
    
    # 🌐 Публичные прокси (могут быть нестабильные)
    {
        "id": "public-us-1",
        "name": "Public US Proxy",
        "country": "US",
        "city": "New York",
        "ip_address": "149.28.194.212",
        "port": 8080,
        "protocol": "http",
        "status": "active",
        "load": 0.7,
        "speed_mbps": 3.0,
        "latency_ms": 400,
        "obfuscation_support": False,
        "stealth_support": False,
        "is_dedicated": False,
        "is_residential": False,
        "is_mobile": False,
        "reliability": 0.6,
        "source": "public_list"
    },
    {
        "id": "public-de-1",
        "name": "Public DE Proxy",
        "country": "DE",
        "city": "Frankfurt",
        "ip_address": "95.217.212.43",
        "port": 3128,
        "protocol": "http",
        "status": "active",
        "load": 0.7,
        "speed_mbps": 5.0,
        "latency_ms": 350,
        "obfuscation_support": False,
        "stealth_support": False,
        "is_dedicated": False,
        "is_residential": False,
        "is_mobile": False,
        "reliability": 0.7,
        "source": "public_list"
    },
    {
        "id": "public-nl-1",
        "name": "Public NL Proxy",
        "country": "NL",
        "city": "Amsterdam",
        "ip_address": "45.67.23.100",
        "port": 8080,
        "protocol": "http",
        "status": "active",
        "load": 0.8,
        "speed_mbps": 2.0,
        "latency_ms": 450,
        "obfuscation_support": False,
        "stealth_support": False,
        "is_dedicated": False,
        "is_residential": False,
        "is_mobile": False,
        "reliability": 0.5,
        "source": "public_list"
    }
]

# 🛡️ ФУНКЦИЯ ПОЛУЧЕНИЯ ЛУЧШИХ СЕРВЕРОВ
def get_best_vpn_servers(country: str = None, protocol: str = None) -> list:
    """🎯 Получить лучшие серверы по параметрам"""
    servers = VPN_SERVERS.copy()
    
    # Фильтр по стране
    if country:
        servers = [s for s in servers if s["country"] == country]
    
    # Фильтр по протоколу
    if protocol:
        servers = [s for s in servers if s["protocol"] == protocol]
    
    # Сортировка по надежности
    servers.sort(key=lambda x: x["reliability"], reverse=True)
    
    return servers

# 🚨 ПРИМЕЧАНИЕ:
# - Tor Exit Nodes: самые надежные и анонимные
# - ProtonVPN: отличные бесплатные сервера
# - Public Proxies: могут быть нестабильные
# - Все сервера требуют проверки доступности

# 🛡️ НАСТРОЙКИ БЕЗОПАСНОСТИ
VPN_SECURITY_SETTINGS = {
    "encryption": {
        "cipher": "aes-256-gcm",
        "key_exchange": "curve25519",
        "hash": "sha256",
        "perfect_forward_secrecy": True
    },
    "dns": {
        "servers": [
            "1.1.1.1",        # Cloudflare
            "8.8.8.8",        # Google
            "9.9.9.9",        # Quad9
            "208.67.222.222"  # OpenDNS
        ],
        "dns_over_https": True,
        "dns_over_tls": True,
        "prevent_leaks": True
    },
    "kill_switch": {
        "enabled": True,
        "block_lan": False,
        "allow_app_exceptions": []
    },
    "leak_protection": {
        "ipv6": True,
        "dns": True,
        "webRTC": True,
        "application": True
    }
}

# 🎯 ТИПЫ БЛОКИРОВОК
BLOCKADE_TYPES = {
    "dpi_deep_packet_inspection": "Глубокий анализ пакетов",
    "port_blocking": "Блокировка портов",
    "protocol_blocking": "Блокировка протоколов",
    "ip_blocking": "Блокировка IP-адресов",
    "dns_blocking": "Блокировка DNS",
    "throttling": "Снижение скорости",
    "man_in_the_middle": "Атака посредника"
}

# 🚀 УРОВНИ ОБФУСКАЦИИ
OBFUSCATION_LEVELS = {
    "none": {
        "name": "Без обфускации",
        "speed_factor": 1.0,
        "detection_resistance": 0.0
    },
    "light": {
        "name": "Легкая обфускация",
        "speed_factor": 0.95,
        "detection_resistance": 0.4
    },
    "medium": {
        "name": "Средняя обфускация", 
        "speed_factor": 0.85,
        "detection_resistance": 0.7
    },
    "heavy": {
        "name": "Сильная обфускация",
        "speed_factor": 0.7,
        "detection_resistance": 0.9
    },
    "maximum": {
        "name": "Максимальная обфускация",
        "speed_factor": 0.5,
        "detection_resistance": 0.95
    }
}
