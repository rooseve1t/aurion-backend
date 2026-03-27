from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime
from enum import Enum
from pydantic import BaseModel
import redis.asyncio as redis
import json
import logging

if TYPE_CHECKING:
    from .personality_engine import JARVISPersonalityEngine
    from .autonomy_engine import AutonomyEngine

class EvolutionStage(Enum):
    """Стадии эволюции JARVIS"""
    SEED = "seed"               # Начальная стадия
    LEARNING = "learning"       # Активное обучение
    ADAPTIVE = "adaptive"       # Адаптивный интеллект
    AUTONOMOUS = "autonomous"   # Полная автономность
    TRANSCENDENT = "transcendent" # За пределами (Jarvis level)

class EvolutionMetric(BaseModel):
    """Метрика эволюции"""
    name: str
    value: float
    weight: float
    timestamp: datetime = datetime.now()

class EvolutionEngine:
    """Движок самообучения и эволюции JARVIS"""
    
    def __init__(self, personality_engine: "JARVISPersonalityEngine", autonomy_engine: Optional["AutonomyEngine"], redis_client: Optional[redis.Redis] = None):
        self.personality = personality_engine
        self.autonomy = autonomy_engine
        self.redis = redis_client
        self.stage = EvolutionStage.SEED
        self.experience_points = 0
        self.metrics: List[EvolutionMetric] = []
        self.evolution_log: List[str] = []
        self.sync_key = "jarvis:evolution:state"

    async def _sync_to_redis(self) -> None:
        """Синхронизировать состояние в Redis (Stage 21: Distributed Brain)"""
        if self.redis is None:
            return
            
        state: Dict[str, Any] = {
            "stage": self.stage.value,
            "experience_points": self.experience_points,
            "metrics": [m.model_dump() for m in self.metrics[-20:]],
            "last_sync": datetime.now().isoformat()
        }
        try:
            # Используем cast или Any для обхода проблем с типами Redis в разных версиях
            redis_client: Any = self.redis
            await redis_client.set(self.sync_key, json.dumps(state))
        except Exception as e:
            logging.error(f"Failed to sync evolution state to Redis: {e}")

    async def _pull_from_redis(self) -> None:
        """Загрузить состояние из Redis"""
        if self.redis is None:
            return
            
        try:
            redis_client: Any = self.redis
            data = await redis_client.get(self.sync_key)
            if data:
                # data может быть bytes или str в зависимости от клиента
                raw_data: str = ""
                if isinstance(data, bytes):
                    raw_data = data.decode('utf-8')
                elif isinstance(data, str):
                    raw_data = data
                
                if raw_data:
                    state: Dict[str, Any] = json.loads(raw_data)
                    self.stage = EvolutionStage(state["stage"])
                    self.experience_points = int(state["experience_points"])
                    # Метрики объединяем или заменяем (по логике Architect)
                    logging.info("🧠 JARVIS: Evolution state synced from Distributed Brain.")
        except Exception as e:
            logging.error(f"Failed to pull evolution state from Redis: {e}")
        
    async def process_event(self, event_type: str, data: Dict[str, Any]):
        """Обработать событие для обучения"""
        logging.info(f"🧬 Evolution Engine processing event: {event_type}")
        
        # Начисление опыта за взаимодействие
        if event_type == "user_interaction":
            await self.add_experience(10)
        elif event_type == "successful_action":
            await self.add_experience(25)
            await self.adapt_action_priority(data.get("action_id"), success=True)
        elif event_type == "failed_action":
            await self.add_experience(5)
            await self.adapt_action_priority(data.get("action_id"), success=False)
        elif event_type == "user_approved_action":
            await self.add_experience(15)
            await self.adapt_action_priority(data.get("action_id"), approved=True)
        elif event_type == "neuro_signal_detected":
            # Stage 21: Интеграция нейросигналов в эволюцию
            await self.handle_neuro_feedback(data)
        elif event_type == "error_resolved":
            await self.add_experience(50)
            
        # Анализ метрик
        await self.update_metrics(event_type, data)
        
        # Проверка на переход на новую стадию
        await self.check_evolution()

    async def handle_neuro_feedback(self, data: Dict[str, Any]):
        """Обработать обратную связь от нейроинтерфейса"""
        intent = data.get("intent")
        confidence = data.get("confidence", 0.0)
        
        if intent == "focus" and confidence > 0.8:
            # Сэр сосредоточен - повышаем приоритет тишины и производительности
            await self.add_experience(5)
            logging.info("🧠 JARVIS: User is focused. Optimizing for high performance.")
        elif intent == "relax":
            # Сэр отдыхает - предлагаем развлекательный контент или отчет за день
            logging.info("🧠 JARVIS: User is relaxing. Preparing daily summary.")

    async def predict_next_needs(self) -> List[Dict[str, Any]]:
        """Предсказать следующие потребности пользователя (Stage 21)"""
        predictions: List[Dict[str, Any]] = []
        
        # Анализ последних метрик для предсказания
        if not self.metrics:
            return predictions
            
        last_metrics: List[EvolutionMetric] = self.metrics[-10:]
        avg_confidence: float = float(sum(m.value for m in last_metrics) / len(last_metrics))
        
        if avg_confidence < 0.6:
            new_pred: Dict[str, Any] = {
                "type": "clarification",
                "reason": "Low interaction confidence detected",
                "suggestion": "Should I recalibrate voice recognition?"
            }
            predictions.append(new_pred)
            
        # Анализ времени и паттернов (в MVP - заглушка)
        current_hour: int = datetime.now().hour
        if 8 <= current_hour <= 10:
            routine_pred: Dict[str, Any] = {
                "type": "routine",
                "reason": "Morning work session",
                "suggestion": "Shall I open the latest development projects?"
            }
            predictions.append(routine_pred)
            
        return predictions

    async def adapt_action_priority(self, action_id: Optional[str], success: bool = False, approved: bool = False):
        """Адаптировать приоритет действия на основе обратной связи.
        approved=True → +2, success=True → +1, иначе → -1.
        """
        if not action_id or not self.autonomy or action_id not in self.autonomy.registered_actions:
            return

        action = self.autonomy.registered_actions[action_id]

        if approved:
            action.priority = min(10, action.priority + 2)
            logging.info(f"📈 Приоритет '{action_id}' повышен до {action.priority} (одобрено пользователем).")
        elif success:
            action.priority = min(10, action.priority + 1)
            logging.info(f"📈 Приоритет '{action_id}' повышен до {action.priority}.")
        else:
            action.priority = max(1, action.priority - 1)
            logging.info(f"📉 Приоритет '{action_id}' снижен до {action.priority}.")

    async def decay_priorities(self):
        """Постепенно снижать все приоритеты, чтобы избежать зацикливания"""
        if not self.autonomy:
            return
            
        for action in self.autonomy.registered_actions.values():
            action.priority = max(1, action.priority - 1)

    async def add_experience(self, points: int):
        """Добавить очки опыта"""
        self.experience_points += points
        logging.info(f"✨ JARVIS gained {points} XP. Total: {self.experience_points}")
        await self._sync_to_redis()

    async def update_metrics(self, event_type: str, data: Dict[str, Any]):
        """Обновить метрики эволюции"""
        # Пример обновления метрики понимания
        if "confidence" in data:
            metric = EvolutionMetric(
                name="understanding_accuracy",
                value=data["confidence"],
                weight=0.3
            )
            self.metrics.append(metric)

    async def check_evolution(self):
        """Проверить готовность к эволюции"""
        old_stage = self.stage
        
        if self.experience_points > 10000 and self.stage == EvolutionStage.AUTONOMOUS:
            self.stage = EvolutionStage.TRANSCENDENT
        elif self.experience_points > 5000 and self.stage == EvolutionStage.ADAPTIVE:
            self.stage = EvolutionStage.AUTONOMOUS
        elif self.experience_points > 2000 and self.stage == EvolutionStage.LEARNING:
            self.stage = EvolutionStage.ADAPTIVE
        elif self.experience_points > 500 and self.stage == EvolutionStage.SEED:
            self.stage = EvolutionStage.LEARNING
            
        if self.stage != old_stage:
            await self.trigger_evolution_event(old_stage, self.stage)

    async def trigger_evolution_event(self, from_stage: EvolutionStage, to_stage: EvolutionStage):
        """Событие перехода на новую стадию"""
        msg = f"🚀 EVOLUTION: JARVIS evolved from {from_stage.value} to {to_stage.value}!"
        logging.info(msg)
        self.evolution_log.append(msg)
        
        # Импортируем типы для корректного доступа к трейтам
        from .personality_engine import PersonalityTrait

        # Адаптация личности под новую стадию
        if to_stage == EvolutionStage.LEARNING:
            self.personality.traits[PersonalityTrait.CURIOUS] = min(1.0, self.personality.traits.get(PersonalityTrait.CURIOUS, 0.5) + 0.2)
        elif to_stage == EvolutionStage.ADAPTIVE:
            self.personality.traits[PersonalityTrait.WITTY] = min(1.0, self.personality.traits.get(PersonalityTrait.WITTY, 0.5) + 0.3)
            
        # Уведомление пользователя через TTS (если доступно)
        # await self.notify_user(msg)

    def get_status(self) -> Dict[str, Any]:
        """Получить текущий статус эволюции"""
        next_threshold: int = self.get_next_threshold()
        progress: float = 100.0
        if next_threshold > 0:
            progress = (float(self.experience_points) / next_threshold) * 100.0
            
        return {
            "stage": self.stage.value,
            "experience": self.experience_points,
            "next_stage_threshold": next_threshold,
            "progress": progress,
            "metrics": [m.model_dump() for m in self.metrics[-10:]]
        }

    def get_next_threshold(self) -> int:
        """Пороги для следующей стадии"""
        thresholds = {
            EvolutionStage.SEED: 500,
            EvolutionStage.LEARNING: 2000,
            EvolutionStage.ADAPTIVE: 5000,
            EvolutionStage.AUTONOMOUS: 10000,
            EvolutionStage.TRANSCENDENT: 0
        }
        return thresholds.get(self.stage, 0)
