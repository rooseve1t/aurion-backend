import logging
import asyncio
from typing import Dict, Any, List

logger = logging.getLogger("jarvis-self-repair")

class SelfRepairModule:
    """Модуль автоматического восстановления систем (Stage 21)"""

    def __init__(self, services: Dict[str, Any]):
        self.services = services
        self._is_monitoring = False
        self._repair_history: List[Dict[str, Any]] = []
        self._failure_counts: Dict[str, int] = {}

    async def start_monitoring(self):
        """Запустить мониторинг здоровья сервисов"""
        if self._is_monitoring:
            return
            
        self._is_monitoring = True
        logger.info("🛠️ Self-Repair Module: Monitoring initiated.")
        
        while self._is_monitoring:
            try:
                await self._check_all_services()
                await asyncio.sleep(60)  # Проверка каждую минуту
            except Exception as e:
                logger.error(f"Error in self-repair loop: {e}")
                await asyncio.sleep(10)

    async def _check_all_services(self):
        """Проверить все зарегистрированные сервисы"""
        for name, service in self.services.items():
            try:
                # Имитация проверки (в реальности - вызов health_check())
                is_alive = True
                if hasattr(service, "is_active"):
                    is_alive = service.is_active
                
                if not is_alive:
                    await self._repair_service(name, service)
            except Exception as e:
                logger.error(f"Failed to check service {name}: {e}")
                await self._repair_service(name, service)

    async def _repair_service(self, name: str, service: Any):
        """Попытка восстановить сервис"""
        logger.warning(f"⚠️ Self-Repair: Service '{name}' is down. Attempting recovery...")

        # Track consecutive failures
        self._failure_counts[name] = self._failure_counts.get(name, 0) + 1
        failure_count = self._failure_counts[name]

        # Trigger emergency protocol if threshold exceeded
        try:
            from .emergency_protocol import get_emergency_protocol
            ep = get_emergency_protocol()
            await ep.evaluate_and_trigger(
                failed_service=name,
                failure_count=failure_count,
                system_metrics={},
                user_id="system",
                redis_client=None,
            )
        except Exception as _ep_exc:
            logger.warning(f"Emergency protocol evaluation error: {_ep_exc}")

        try:
            if hasattr(service, "initialize"):
                await service.initialize()
                logger.info(f"✅ Self-Repair: Service '{name}' successfully recovered.")
                self._failure_counts[name] = 0
                self._repair_history.append({
                    "service": name,
                    "status": "recovered",
                    "timestamp": asyncio.get_event_loop().time()
                })
            else:
                logger.error(f"❌ Self-Repair: Service '{name}' has no initialization method.")
        except Exception as e:
            logger.error(f"❌ Self-Repair: Recovery failed for '{name}': {e}")
