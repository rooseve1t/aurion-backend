"""
🚨 EmergencyProtocol — Аварийный протокол JARVIS
Вдохновлён Age of Ultron: когда Альтрон уничтожает JARVIS, тот рассыпается по интернету
и автономно блокирует ядерные коды — без центрального сознания.
Наш аналог: при критических сбоях — автоснапшот, оповещение, эскалация автономности.
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger("jarvis-emergency")

FAILURE_THRESHOLD = 3           # Порог последовательных сбоев
ESCALATION_DURATION_SEC = 300   # 5 минут эскалации автономности


@dataclass
class EmergencyContext:
    incident_id: str
    failed_service: str
    failure_count: int
    system_metrics: Dict[str, Any]
    user_id: str
    triggered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class EmergencyProtocol:
    """
    Аварийный протокол JARVIS.
    Срабатывает при накоплении критических сбоев — действует автономно.
    """

    def __init__(self) -> None:
        self._active_incidents: Dict[str, EmergencyContext] = {}

    async def evaluate_and_trigger(
        self,
        failed_service: str,
        failure_count: int,
        system_metrics: Dict[str, Any],
        user_id: str,
        redis_client: Any,
        autonomy_engine: Any = None,
    ) -> bool:
        """
        Оценивает необходимость аварийного протокола и запускает его при необходимости.
        Returns True если протокол был активирован.
        """
        # Проверяем составное условие: много сбоев ИЛИ критические метрики
        cpu = float(system_metrics.get("cpu_percent", 0))
        mem = float(system_metrics.get("memory_percent", 0))
        compound_failure = cpu > 95 and mem > 95

        if failure_count < FAILURE_THRESHOLD and not compound_failure:
            return False

        import uuid
        incident_id = str(uuid.uuid4())[:8]
        context = EmergencyContext(
            incident_id=incident_id,
            failed_service=failed_service,
            failure_count=failure_count,
            system_metrics=system_metrics,
            user_id=user_id,
        )

        logger.critical(
            f"🚨 АВАРИЙНЫЙ ПРОТОКОЛ АКТИВИРОВАН | сервис={failed_service} "
            f"сбоев={failure_count} incident={incident_id}"
        )

        self._active_incidents[incident_id] = context
        asyncio.create_task(self._execute_protective_actions(context, redis_client, autonomy_engine))
        return True

    async def _execute_protective_actions(
        self,
        context: EmergencyContext,
        redis_client: Any,
        autonomy_engine: Any,
    ) -> None:
        """Параллельное выполнение защитных действий"""
        actions_taken: List[str] = []

        tasks = [
            self._snapshot_critical_state(context, redis_client),
            self._publish_emergency_alert(context, redis_client),
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Emergency action {i} failed: {result}")
            else:
                actions_taken.append(f"action_{i}_ok")

        # Эскалация автономности
        if autonomy_engine is not None:
            try:
                await self._escalate_autonomy(context, autonomy_engine)
                actions_taken.append("autonomy_escalated")
            except Exception as e:
                logger.error(f"Autonomy escalation failed: {e}")

        logger.info(f"🚨 Аварийный протокол {context.incident_id}: выполнены действия {actions_taken}")

    async def _snapshot_critical_state(self, context: EmergencyContext, redis_client: Any) -> None:
        """Снапшот текущего состояния системы в Redis"""
        if redis_client is None:
            return

        snapshot = {
            "incident_id": context.incident_id,
            "failed_service": context.failed_service,
            "failure_count": context.failure_count,
            "metrics": context.system_metrics,
            "triggered_at": context.triggered_at,
        }
        key = f"emergency:snapshot:{context.triggered_at[:19].replace(':', '-')}"
        await redis_client.setex(key, 86400, json.dumps(snapshot))
        logger.info(f"🚨 Снапшот сохранён: {key}")

    async def _publish_emergency_alert(self, context: EmergencyContext, redis_client: Any) -> None:
        """Публикует CRITICAL алерт в Redis pub/sub"""
        if redis_client is None:
            return

        event = {
            "type": "emergency_protocol_triggered",
            "domain": "security",
            "priority": "critical",
            "incident_id": context.incident_id,
            "failed_service": context.failed_service,
            "failure_count": context.failure_count,
            "message": (
                f"🚨 Аварийный протокол активирован. "
                f"Сервис '{context.failed_service}' недоступен ({context.failure_count} попыток восстановления)."
            ),
            "timestamp": context.triggered_at,
        }
        channel = f"jarvis:events:{context.user_id}"
        await redis_client.publish(channel, json.dumps(event))
        logger.info(f"🚨 Алерт опубликован в {channel}")

    async def _escalate_autonomy(self, context: EmergencyContext, autonomy_engine: Any) -> None:
        """Временно повышает уровень автономности для самозащиты"""
        try:
            from .autonomy_engine import AutonomyLevel
            prev_level = autonomy_engine.current_level
            if prev_level.value < AutonomyLevel.SEMI_AUTO.value:
                autonomy_engine.current_level = AutonomyLevel.SEMI_AUTO
                logger.warning(
                    f"🚨 Автономность эскалирована: {prev_level.name} → SEMI_AUTO "
                    f"на {ESCALATION_DURATION_SEC}с"
                )
                await asyncio.sleep(ESCALATION_DURATION_SEC)
                autonomy_engine.current_level = prev_level
                logger.info(f"🚨 Автономность возвращена к {prev_level.name}")
        except Exception as e:
            logger.error(f"Autonomy escalation error: {e}")

    def get_active_incidents(self) -> List[Dict[str, Any]]:
        """Возвращает список активных инцидентов"""
        return [asdict(ctx) for ctx in self._active_incidents.values()]

    def resolve_incident(self, incident_id: str) -> bool:
        """Закрыть инцидент"""
        if incident_id in self._active_incidents:
            del self._active_incidents[incident_id]
            return True
        return False


# Синглтон
_instance: Optional[EmergencyProtocol] = None


def get_emergency_protocol() -> EmergencyProtocol:
    global _instance
    if _instance is None:
        _instance = EmergencyProtocol()
    return _instance
