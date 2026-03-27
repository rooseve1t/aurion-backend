import logging
import asyncio
from typing import Dict, Any, List, Set, Optional
from .osint_service import OSINTService

logger = logging.getLogger("jarvis-threat-response")

class ActiveThreatResponse:
    """Модуль активного противодействия угрозам (Stage 22: Sentinel Protocol)"""
    
    def __init__(self, osint: Optional[OSINTService] = None):
        self.blocked_ips: Set[str] = set()
        self.attack_history: List[Dict[str, Any]] = []
        self.osint = osint or OSINTService()
        self.sentinel_active = False

    async def start_sentinel(self):
        """Запуск Sentinel Protocol (мониторинг + реагирование)"""
        self.sentinel_active = True
        logger.info("🛡️ Sentinel: Protocol initiated. Monitoring OSINT feeds...")
        # В реальности здесь был бы фоновый цикл проверки OSINT и блокировки подозрительных IP
        # Пока просто запускаем мониторинг
        asyncio.create_task(self.osint.start_monitoring())

    async def block_ip(self, ip: str, reason: str) -> bool:
        """Добавить IP в черный список и уведомить систему"""
        if ip in self.blocked_ips:
            return True
            
        self.blocked_ips.add(ip)
        logger.warning(f"🚨 Active Response: IP {ip} blocked. Reason: {reason}")
        
        self.attack_history.append({
            "ip": ip,
            "reason": reason,
            "timestamp": "now", # В реальности datetime.now()
            "action": "blocked"
        })
        
        return True

    def is_blocked(self, ip: str) -> bool:
        """Проверить, заблокирован ли IP"""
        return ip in self.blocked_ips

    async def counter_measure(self, threat_data: Dict[str, Any]):
        """Запустить контрмеры (Stage 22: Sentinel Enhanced)"""
        ip = threat_data.get("ip")
        if ip:
            # Сначала проверяем репутацию
            reputation = await self.osint.check_ip_reputation(ip)
            if reputation.get("is_malicious"):
                await self.block_ip(ip, f"Sentinel: Malicious IP detected (Risk Score: {reputation['risk_score']})")
                logger.info(f"⚔️ Sentinel: Counter-measures active against {ip}. Integrity secured.")
            else:
                logger.info(f"🛡️ Sentinel: IP {ip} analyzed. Risk below threshold.")
