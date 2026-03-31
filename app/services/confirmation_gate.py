"""
ConfirmationGate — механизм подтверждения критических действий JARVIS.

Критические действия требуют явного подтверждения через Activity Feed.
Автоотмена через Redis TTL 300 секунд (5 минут).
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger("aurion-confirmation-gate")

CONFIRMATION_TTL = 300  # 5 минут


class ConfirmationGate:

    def __init__(self) -> None:
        self._redis: Any = None
        self._memory: dict[str, str] = {}

    def set_redis(self, client: Any) -> None:
        self._redis = client

    async def create_confirmation(
        self,
        user_id: str,
        action_type: str,
        action_data: dict,
    ) -> str:
        """Создать запрос подтверждения. Возвращает action_id."""
        action_id = str(uuid.uuid4())
        payload = json.dumps({
            "user_id": user_id,
            "action_type": action_type,
            "action_data": action_data,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        await self._store(f"confirmation:{action_id}", payload, CONFIRMATION_TTL)
        await self._create_feed_card(user_id, action_id, action_type, action_data)
        logger.info(f"ConfirmationGate: created {action_type} for user {user_id}, id={action_id}")
        return action_id

    async def confirm(self, action_id: str, user_id: str) -> bool:
        """Подтвердить действие."""
        raw = await self._load(f"confirmation:{action_id}")
        if not raw:
            return False
        data = json.loads(raw)
        if data.get("user_id") != user_id:
            return False
        await self._log_result(action_id, user_id, data["action_type"], "confirmed")
        await self._delete(f"confirmation:{action_id}")
        logger.info(f"ConfirmationGate: confirmed {data['action_type']} for {user_id}")
        return True

    async def cancel(self, action_id: str, user_id: str) -> bool:
        """Отменить действие."""
        raw = await self._load(f"confirmation:{action_id}")
        if not raw:
            return False
        data = json.loads(raw)
        await self._log_result(action_id, user_id, data.get("action_type", "unknown"), "cancelled")
        await self._delete(f"confirmation:{action_id}")
        return True

    async def is_pending(self, action_id: str) -> bool:
        return await self._load(f"confirmation:{action_id}") is not None

    async def _create_feed_card(
        self, user_id: str, action_id: str, action_type: str, action_data: dict
    ) -> None:
        try:
            from ..database_final import AsyncSessionLocal
            from ..models.feed_card import FeedCard

            labels = {
                "order_taxi": "Вызов такси",
                "order_food": "Заказ еды",
                "send_message": "Отправка сообщения",
                "reschedule_meeting": "Перенос встречи",
                "make_purchase": "Покупка",
                "send_email": "Отправка письма",
            }
            label = labels.get(action_type, action_type)
            summary = "; ".join(f"{k}: {v}" for k, v in list(action_data.items())[:3])

            async with AsyncSessionLocal() as db:
                card = FeedCard(
                    user_id=uuid.UUID(user_id),
                    type="suggestion",
                    domain="calendar",
                    title=f"JARVIS: {label}",
                    body=f"Подтвердите действие. {summary}",
                    priority="high",
                    requires_confirmation=True,
                )
                db.add(card)
                await db.commit()
        except Exception as exc:
            logger.warning(f"ConfirmationGate: create_feed_card failed: {exc}")

    async def _log_result(self, action_id: str, user_id: str, action_type: str, result: str) -> None:
        try:
            from ..database_final import AsyncSessionLocal
            from sqlalchemy import text
            async with AsyncSessionLocal() as db:
                await db.execute(
                    text(
                        "INSERT INTO confirmation_log (id, user_id, action_type, result, created_at) "
                        "VALUES (:id, :uid, :atype, :result, NOW()) ON CONFLICT DO NOTHING"
                    ),
                    {"id": action_id, "uid": user_id, "atype": action_type, "result": result},
                )
                await db.commit()
        except Exception as exc:
            logger.debug(f"ConfirmationGate: log_result skipped: {exc}")

    async def _store(self, key: str, value: str, ttl: int) -> None:
        if self._redis:
            try:
                await self._redis.setex(key, ttl, value)
                return
            except Exception as exc:
                logger.warning(f"ConfirmationGate: Redis store failed: {exc}")
        self._memory[key] = value

    async def _load(self, key: str) -> Optional[str]:
        if self._redis:
            try:
                raw = await self._redis.get(key)
                if raw:
                    return raw.decode() if isinstance(raw, bytes) else raw
                return None
            except Exception as exc:
                logger.warning(f"ConfirmationGate: Redis load failed: {exc}")
        return self._memory.get(key)

    async def _delete(self, key: str) -> None:
        if self._redis:
            try:
                await self._redis.delete(key)
                return
            except Exception as exc:
                logger.warning(f"ConfirmationGate: Redis delete failed: {exc}")
        self._memory.pop(key, None)


_gate: Optional[ConfirmationGate] = None


def get_confirmation_gate() -> ConfirmationGate:
    global _gate
    if _gate is None:
        _gate = ConfirmationGate()
    return _gate
