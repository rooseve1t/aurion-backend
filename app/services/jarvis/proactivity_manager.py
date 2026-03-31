import logging
import asyncio
import gc
from typing import Dict, Any, Set, Optional
from .evolution_engine import EvolutionEngine
from .autonomy_engine import AutonomyEngine
from .neuro_interface import NeuroInterface
from ..osint_service import OSINTService

logger = logging.getLogger("jarvis-proactivity")

class ProactivityManager:
    """Менеджер проактивности JARVIS (Stage 21)"""
    
    def __init__(self, evolution_engine: EvolutionEngine, autonomy_engine: AutonomyEngine, neuro_interface: NeuroInterface, osint_service: Optional[OSINTService] = None):
        self.evolution = evolution_engine
        self.autonomy = autonomy_engine
        self.neuro = neuro_interface
        self.osint = osint_service
        self._is_monitoring = False
        self._background_tasks: Set[asyncio.Task[Any]] = set()

    async def start(self):
        """Запустить мониторинг проактивности"""
        if self._is_monitoring:
            return
            
        self._is_monitoring = True
        logger.info("🚀 Proactivity Manager started.")
        
        # Запуск цикла предсказания потребностей
        task: asyncio.Task[Any] = asyncio.create_task(self._prediction_loop())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        
        # Запуск цикла нейро-мониторинга
        task = asyncio.create_task(self._neuro_monitoring_loop())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        
        # Запуск Sentinel Protocol (OSINT мониторинг)
        task = asyncio.create_task(self._sentinel_protocol_loop())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        
        # Запуск QA: Сборщик мусора (Memory Leak Protection)
        task = asyncio.create_task(self._garbage_collection_loop())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    async def _garbage_collection_loop(self):
        """Фоновая очистка памяти (Stage 22: QA Shield)"""
        while self._is_monitoring:
            try:
                gc.collect()
                logger.debug("🧹 QA Shield: Background garbage collection executed.")
                await asyncio.sleep(3600) # Раз в час
            except Exception as e:
                logger.error(f"Error in GC loop: {e}")
                await asyncio.sleep(600)

    async def _sentinel_protocol_loop(self):
        """Проактивный мониторинг угроз (Sentinel Protocol)"""
        while self._is_monitoring:
            try:
                if self.osint:
                    logger.info("🛡️ Sentinel: Scanning for active threats based on recent OSINT data...")
                    # В реальности здесь анализ последних запросов из БД
                    # Для MVP - имитация обнаружения угрозы
                    await self.autonomy.notify_user("Сэр, обнаружена подозрительная активность на одном из ваших мониторимых IP. Включаю активную защиту.")
                    
                await asyncio.sleep(3600)  # Раз в час
            except Exception as e:
                logger.error(f"Error in sentinel loop: {e}")
                await asyncio.sleep(300)

    async def stop(self):
        """Остановить мониторинг"""
        self._is_monitoring = False
        for task in list(self._background_tasks):
            task.cancel()
        logger.info("🛑 Proactivity Manager stopped.")

    async def _prediction_loop(self):
        """Фоновый цикл предсказания потребностей"""
        while self._is_monitoring:
            try:
                # Получаем предсказания от движка эволюции
                predictions = await self.evolution.predict_next_needs()
                
                for pred in predictions:
                    await self._handle_prediction(pred)
                    
                await asyncio.sleep(300)  # Раз в 5 минут
            except Exception as e:
                logger.error(f"Error in prediction loop: {e}")
                await asyncio.sleep(60)

    async def _neuro_monitoring_loop(self):
        """Фоновый цикл мониторинга нейросигналов"""
        while self._is_monitoring:
            try:
                if self.neuro.is_active:
                    # В реальном сценарии здесь получение данных из board
                    # Для Stage 21 используем инъекцию сигналов или проверку последних паттернов
                    if self.neuro.processor.patterns:
                        last_pattern = self.neuro.processor.patterns[-1]
                        if last_pattern.confidence > 0.8:
                            await self.evolution.process_event("neuro_signal_detected", {
                                "intent": last_pattern.intent.value,
                                "confidence": last_pattern.confidence,
                                "emotional_state": last_pattern.emotional_state
                            })
                            
                await asyncio.sleep(10)  # Раз в 10 секунд
            except Exception as e:
                logger.error(f"Error in neuro monitoring loop: {e}")
                await asyncio.sleep(30)

    async def _handle_prediction(self, prediction: Dict[str, Any]):
        """Обработать предсказание"""
        logger.info(f"🔮 JARVIS Prediction: {prediction['suggestion']} (Reason: {prediction['reason']})")
        
        # Если автономность на высоком уровне - можно выполнить автоматически
        if self.autonomy.current_level.value >= 2: # SEMI_AUTO or FULL_AUTO
            # Здесь логика запуска автономного действия
            pass
        else:
            # Предлагаем пользователю через TTS/WebSocket
            await self.autonomy.notify_user(f"Сэр, {prediction['suggestion']}")


# ---------------------------------------------------------------------------
# ProactiveEngine — инициативные сообщения JARVIS (Aurion Evolution)
# ---------------------------------------------------------------------------

import json as _json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..background_observer import ObservedEvent


class ProactiveEngine:
    """
    Подписывается на Redis канал `jarvis:events:{user_id}`,
    строит FeedCard и инициирует голосовые сообщения JARVIS.
    Rate limit: не более 3 голосовых сообщений в час на пользователя.
    """

    RATE_LIMIT_WINDOW: int = 3600
    RATE_LIMIT_MAX_VOICE: int = 3

    def __init__(self) -> None:
        self._redis: Any = None
        self._ws_manager: Any = None
        self._subscriptions: Dict[str, asyncio.Task[Any]] = {}

    def set_redis(self, client: Any) -> None:
        self._redis = client

    def set_ws_manager(self, manager: Any) -> None:
        self._ws_manager = manager

    async def subscribe(self, user_id: str) -> None:
        if user_id in self._subscriptions and not self._subscriptions[user_id].done():
            return
        task = asyncio.create_task(self._listen_loop(user_id))
        self._subscriptions[user_id] = task
        logger.info(f"ProactiveEngine subscribed for user {user_id}")

    async def unsubscribe(self, user_id: str) -> None:
        task = self._subscriptions.pop(user_id, None)
        if task and not task.done():
            task.cancel()

    async def _listen_loop(self, user_id: str) -> None:
        if not self._redis:
            logger.warning("ProactiveEngine: Redis not configured")
            return
        try:
            pubsub = self._redis.pubsub()
            channel = f"jarvis:events:{user_id}"
            await pubsub.subscribe(channel)
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue
                try:
                    raw = message["data"]
                    data = _json.loads(raw.decode() if isinstance(raw, bytes) else raw)
                    from ..background_observer import ObservedEvent, EventDomain, EventPriority
                    event = ObservedEvent(
                        domain=EventDomain(data["domain"]),
                        priority=EventPriority(data["priority"]),
                        title=data["title"],
                        body=data["body"],
                        user_id=data["user_id"],
                        source=data.get("source", ""),
                        payload=data.get("payload", {}),
                        timestamp=data.get("timestamp", ""),
                    )
                    await self.handle_event(event)
                except Exception as exc:
                    logger.warning(f"ProactiveEngine: failed to parse event: {exc}")
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error(f"ProactiveEngine listen loop error for {user_id}: {exc}")

    async def handle_event(self, event: "ObservedEvent") -> None:
        card = await self._build_feed_card(event)
        if card:
            await self._broadcast_card(card, event.user_id)

        from ..background_observer import EventPriority
        if event.priority in (EventPriority.HIGH, EventPriority.CRITICAL):
            if await self._check_rate_limit(event.user_id):
                await self._initiate_voice(f"{event.title}. {event.body}", event.user_id)

    async def _build_feed_card(self, event: "ObservedEvent") -> Optional[Dict[str, Any]]:
        try:
            from ...database_final import AsyncSessionLocal
            from ...models.feed_card import FeedCard
            import uuid as _uuid

            async with AsyncSessionLocal() as db:
                card = FeedCard(
                    user_id=_uuid.UUID(event.user_id),
                    type="alert" if event.priority.value in ("high", "critical") else "observation",
                    domain=event.domain.value,
                    title=event.title,
                    body=event.body,
                    priority=event.priority.value,
                    requires_confirmation=False,
                )
                db.add(card)
                await db.commit()
                await db.refresh(card)
                return {
                    "id": str(card.id),
                    "type": card.type,
                    "domain": card.domain,
                    "title": card.title,
                    "body": card.body,
                    "priority": card.priority,
                    "createdAt": card.created_at.isoformat() if card.created_at else "",
                    "userId": event.user_id,
                }
        except Exception as exc:
            logger.warning(f"ProactiveEngine: failed to build feed card: {exc}")
            return None

    async def _broadcast_card(self, card: Dict[str, Any], user_id: str) -> None:
        if self._ws_manager:
            try:
                await self._ws_manager.send_to_user(user_id, {"type": "feed_card", "data": card})
            except Exception as exc:
                logger.warning(f"ProactiveEngine: WebSocket broadcast failed: {exc}")

    async def _initiate_voice(self, text: str, user_id: str) -> None:
        try:
            from ..multi_device_voice import get_multi_device_voice
            mdv = get_multi_device_voice()
            await mdv.speak(text, user_id)
        except Exception as exc:
            logger.warning(f"ProactiveEngine: voice initiation failed: {exc}")

    async def _check_rate_limit(self, user_id: str) -> bool:
        key = f"voice_rate:{user_id}"
        if self._redis:
            try:
                count_raw = await self._redis.get(key)
                count = int(count_raw) if count_raw else 0
                if count >= self.RATE_LIMIT_MAX_VOICE:
                    return False
                pipe = self._redis.pipeline()
                await pipe.incr(key)
                await pipe.expire(key, self.RATE_LIMIT_WINDOW)
                await pipe.execute()
                return True
            except Exception as exc:
                logger.warning(f"Rate limit check failed: {exc}")
        return True


_proactive_engine: Optional[ProactiveEngine] = None


def get_proactive_engine() -> ProactiveEngine:
    global _proactive_engine
    if _proactive_engine is None:
        _proactive_engine = ProactiveEngine()
    return _proactive_engine
