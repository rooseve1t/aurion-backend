"""
BackgroundObserver — фоновый наблюдатель JARVIS.

Непрерывно опрашивает источники данных пользователя (финансы, здоровье,
безопасность, календарь) каждые 5 минут и публикует события в Redis pub/sub
канал `jarvis:events:{user_id}` для обработки ProactiveEngine.

При недоступности источника — читает кэш из Redis и логирует предупреждение.
"""
import asyncio
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

logger = logging.getLogger("aurion-background-observer")


class EventDomain(str, Enum):
    HEALTH = "health"
    FINANCE = "finance"
    SECURITY = "security"
    CALENDAR = "calendar"


class EventPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ObservedEvent:
    domain: EventDomain
    priority: EventPriority
    title: str
    body: str
    user_id: str
    source: str
    payload: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class BackgroundObserver:
    """Фоновый наблюдатель — опрашивает источники и публикует события."""

    POLL_INTERVAL_SECONDS: int = 300
    CACHE_TTL_SECONDS: int = 600

    def __init__(self) -> None:
        self._tasks: dict[str, asyncio.Task] = {}
        self._redis: Any = None

    def set_redis(self, client: Any) -> None:
        self._redis = client

    async def start(self, user_id: str) -> None:
        if user_id in self._tasks and not self._tasks[user_id].done():
            return
        task = asyncio.create_task(self._poll_loop(user_id))
        self._tasks[user_id] = task
        logger.info(f"BackgroundObserver started for user {user_id}")

    async def stop(self, user_id: Optional[str] = None) -> None:
        targets = [user_id] if user_id else list(self._tasks.keys())
        for uid in targets:
            task = self._tasks.pop(uid, None)
            if task and not task.done():
                task.cancel()

    async def _poll_loop(self, user_id: str) -> None:
        while True:
            try:
                events = await self.poll_once(user_id)
                for event in events:
                    await self._publish(event)
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error(f"BackgroundObserver poll error for {user_id}: {exc}")
            await asyncio.sleep(self.POLL_INTERVAL_SECONDS)

    async def poll_once(self, user_id: str) -> list[ObservedEvent]:
        """Опросить все источники один раз."""
        events: list[ObservedEvent] = []
        pollers = [
            (EventDomain.FINANCE,  self._poll_finance),
            (EventDomain.HEALTH,   self._poll_health),
            (EventDomain.SECURITY, self._poll_security),
            (EventDomain.CALENDAR, self._poll_calendar),
        ]
        for domain, poller in pollers:
            try:
                result = await poller(user_id)
                if result:
                    await self._cache_set(f"observer_cache:{user_id}:{domain.value}", result)
                    event = self._result_to_event(domain, user_id, result)
                    if event:
                        events.append(event)
            except Exception as exc:
                logger.warning(
                    f"Source '{domain.value}' unavailable for {user_id}: {exc}. Using cache."
                )
                cached = await self._cache_get(f"observer_cache:{user_id}:{domain.value}")
                if cached:
                    event = self._result_to_event(domain, user_id, cached, from_cache=True)
                    if event:
                        events.append(event)
        return events

    # ------------------------------------------------------------------
    # Source pollers (graceful fallback — return None on any error)
    # ------------------------------------------------------------------

    async def _poll_finance(self, user_id: str) -> Optional[dict]:
        try:
            from .finance_service import FinanceService
            svc = FinanceService()
            return await svc.get_portfolio_summary(user_id)
        except Exception:
            return None

    async def _poll_health(self, user_id: str) -> Optional[dict]:
        try:
            from .digital_twin import DigitalTwinService
            svc = DigitalTwinService()
            metrics = await svc.get_live_metrics(user_id)
            if metrics is None:
                return None
            return metrics if isinstance(metrics, dict) else asdict(metrics)
        except Exception:
            return None

    async def _poll_security(self, user_id: str) -> Optional[dict]:
        try:
            from .osint_service import OSINTService
            svc = OSINTService()
            threats = await svc.get_active_threats(user_id)
            return {"threats": threats} if threats else None
        except Exception:
            return None

    async def _poll_calendar(self, user_id: str) -> Optional[dict]:
        try:
            from .calendar_service import CalendarService
            svc = CalendarService()
            upcoming = await svc.get_upcoming_events(user_id, hours=24)
            return {"events": upcoming} if upcoming else None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Event classification
    # ------------------------------------------------------------------

    def _result_to_event(
        self,
        domain: EventDomain,
        user_id: str,
        data: dict,
        from_cache: bool = False,
    ) -> Optional[ObservedEvent]:
        if not data:
            return None

        priority = EventPriority.LOW
        title = ""
        body = ""

        if domain == EventDomain.FINANCE:
            changes = data.get("significant_changes", [])
            if not changes:
                return None
            priority = EventPriority.HIGH
            title = "Изменения в портфеле"
            body = "; ".join(str(c) for c in changes[:3])

        elif domain == EventDomain.HEALTH:
            hr = data.get("heart_rate")
            if not hr or not (hr > 100 or hr < 50):
                return None
            priority = EventPriority.HIGH
            title = "Показатели здоровья"
            body = f"Пульс: {hr} уд/мин — требует внимания."

        elif domain == EventDomain.SECURITY:
            threats = data.get("threats", [])
            if not threats:
                return None
            priority = EventPriority.CRITICAL
            title = "Угрозы безопасности"
            body = f"Обнаружено угроз: {len(threats)}"

        elif domain == EventDomain.CALENDAR:
            events = data.get("events", [])
            if not events:
                return None
            priority = EventPriority.MEDIUM
            title = "Предстоящие события"
            body = f"Ближайших событий: {len(events)}"

        else:
            return None

        source = domain.value + (" (кэш)" if from_cache else "")
        return ObservedEvent(
            domain=domain,
            priority=priority,
            title=title,
            body=body,
            user_id=user_id,
            source=source,
            payload=data,
        )

    # ------------------------------------------------------------------
    # Redis helpers
    # ------------------------------------------------------------------

    async def _publish(self, event: ObservedEvent) -> None:
        channel = f"jarvis:events:{event.user_id}"
        payload = json.dumps(asdict(event))
        if self._redis:
            try:
                await self._redis.publish(channel, payload)
                logger.debug(f"Published event to {channel}: {event.title}")
                return
            except Exception as exc:
                logger.warning(f"Redis publish failed: {exc}")
        logger.info(f"[BackgroundObserver] {channel}: {event.title} — {event.body}")

    async def _cache_set(self, key: str, value: Any) -> None:
        if self._redis:
            try:
                await self._redis.setex(key, self.CACHE_TTL_SECONDS, json.dumps(value))
            except Exception:
                pass

    async def _cache_get(self, key: str) -> Optional[dict]:
        if self._redis:
            try:
                raw = await self._redis.get(key)
                if raw:
                    return json.loads(raw.decode() if isinstance(raw, bytes) else raw)
            except Exception:
                pass
        return None


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_observer: Optional[BackgroundObserver] = None


def get_observer() -> BackgroundObserver:
    global _observer
    if _observer is None:
        _observer = BackgroundObserver()
    return _observer
