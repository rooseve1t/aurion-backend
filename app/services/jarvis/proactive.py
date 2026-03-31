"""
Proactive Jarvis - проактивные действия JARVIS без прямой команды.
JARVIS самостоятельно анализирует ситуацию и предлагает помощь.
"""
import asyncio
import logging
from typing import Optional, List, Callable, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json

from app.services.jarvis.context_manager import ContextManager, UserContext, EmotionalState

logger = logging.getLogger("jarvis.proactive")


class ActionType(Enum):
    """Типы проактивных действий."""
    NOTIFICATION = "notification"
    SUGGESTION = "suggestion"
    AUTOMATION = "automation"
    ALERT = "alert"
    REMINDER = "reminder"


class Priority(Enum):
    """Приоритет действия."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ProactiveAction:
    """Проактивное действие JARVIS."""
    action_type: ActionType
    name: str
    description: str
    priority: Priority
    trigger_condition: str
    execute_func: Callable
    notify_user: bool = True
    requires_confirmation: bool = False
    cooldown_minutes: int = 60
    last_executed: Optional[datetime] = None


@dataclass
class ProactiveInsight:
    """Инсайт от JARVIS."""
    title: str
    content: str
    category: str
    relevance_score: float
    suggested_actions: List[str]


class ProactiveJarvis:
    """
    Проактивный JARVIS - действует без прямой команды пользователя.
    
    Функции:
    - Мониторинг состояния устройств
    - Анализ паттернов поведения
    - Предупреждения о проблемах
    - Предложения по оптимизации
    - Автоматизация рутинных задач
    """
    
    def __init__(self, context_manager: ContextManager):
        """
        Инициализация проактивного JARVIS.
        
        Args:
            context_manager: Менеджер контекста
        """
        self.context_manager = context_manager
        
        # Зарегистрированные условия
        self.conditions: List[ProactiveAction] = []
        
        # Мониторинг
        self._monitoring_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        
        # Интервал проверки (секунды)
        self.check_interval = 60
        
        # История действий
        self.action_history: Dict[int, List[datetime]] = {}
        
        # Регистрация стандартных условий
        self._register_default_conditions()
    
    def _register_default_conditions(self):
        """Регистрация стандартных проактивных условий."""
        
        # Низкий заряд батареи
        self.register_condition(ProactiveAction(
            action_type=ActionType.ALERT,
            name="low_battery",
            description="Предупреждение о низком заряде батареи",
            priority=Priority.HIGH,
            trigger_condition="device_battery < 20",
            execute_func=self._alert_low_battery,
            notify_user=True,
            cooldown_minutes=30,
        ))
        
        # Необычная активность безопасности
        self.register_condition(ProactiveAction(
            action_type=ActionType.ALERT,
            name="security_threat",
            description="Обнаружена подозрительная активность",
            priority=Priority.CRITICAL,
            trigger_condition="security_events > 3",
            execute_func=self._alert_security_threat,
            notify_user=True,
            requires_confirmation=False,
            cooldown_minutes=5,
        ))
        
        # Напоминание о встрече
        self.register_condition(ProactiveAction(
            action_type=ActionType.REMINDER,
            name="meeting_reminder",
            description="Напоминание о предстоящей встрече",
            priority=Priority.MEDIUM,
            trigger_condition="upcoming_meeting_in_minutes == 15",
            execute_func=self._remind_meeting,
            notify_user=True,
            cooldown_minutes=60,
        ))
        
        # Предложение перерыва
        self.register_condition(ProactiveAction(
            action_type=ActionType.SUGGESTION,
            name="break_suggestion",
            description="Предложение сделать перерыв",
            priority=Priority.LOW,
            trigger_condition="continuous_work_minutes > 45",
            execute_func=self._suggest_break,
            notify_user=True,
            cooldown_minutes=45,
        ))
        
        # Напоминание о воде
        self.register_condition(ProactiveAction(
            action_type=ActionType.REMINDER,
            name="water_reminder",
            description="Напоминание выпить воды",
            priority=Priority.LOW,
            trigger_condition="hours_since_last_water > 2",
            execute_func=self._remind_water,
            notify_user=True,
            cooldown_minutes=120,
        ))
        
        # Оптимизация энергопотребления
        self.register_condition(ProactiveAction(
            action_type=ActionType.AUTOMATION,
            name="energy_optimization",
            description="Автоматическая оптимизация энергопотребления",
            priority=Priority.MEDIUM,
            trigger_condition="energy_saving_opportunity",
            execute_func=self._optimize_energy,
            notify_user=True,
            requires_confirmation=True,
            cooldown_minutes=180,
        ))
        
        # Предложение режима сна
        self.register_condition(ProactiveAction(
            action_type=ActionType.SUGGESTION,
            name="sleep_mode_suggestion",
            description="Предложение включить режим сна",
            priority=Priority.LOW,
            trigger_condition="time == 'night' and user_inactive > 30",
            execute_func=self._suggest_sleep_mode,
            notify_user=True,
            cooldown_minutes=60,
        ))
        
        # Резервное копирование
        self.register_condition(ProactiveAction(
            action_type=ActionType.AUTOMATION,
            name="backup_reminder",
            description="Напоминание о резервном копировании",
            priority=Priority.MEDIUM,
            trigger_condition="days_since_last_backup > 7",
            execute_func=self._remind_backup,
            notify_user=True,
            cooldown_minutes=1440,  # 24 часа
        ))
    
    def register_condition(self, action: ProactiveAction):
        """Регистрация проактивного условия."""
        self.conditions.append(action)
        logger.info(f"Зарегистрировано условие: {action.name}")
    
    async def _alert_low_battery(self, context: UserContext) -> str:
        """Предупреждение о низком заряде."""
        device = context.primary_device
        if device and device.battery_level:
            return f"Сэр, заряд батареи устройства {device.device_type} всего {device.battery_level}%. Рекомендую подключить к питанию."
        return "Сэр, заряд батареи устройства низкий. Рекомендую подключить к питанию."
    
    async def _alert_security_threat(self, context: UserContext) -> str:
        """Предупреждение об угрозе безопасности."""
        return "⚠️ Внимание! Обнаружена подозрительная активность. Рекомендую проверить последние действия и включить усиленный режим безопасности."
    
    async def _remind_meeting(self, context: UserContext) -> str:
        """Напоминание о встрече."""
        # Получение информации о встрече из контекста
        meeting = context.metadata.get('upcoming_meeting', {})
        if meeting:
            return f"Сэр, через 15 минут у вас встреча: {meeting.get('title', 'без названия')}. Подготовить материалы?"
        return "Сэр, через 15 минут у вас запланирована встреча."
    
    async def _suggest_break(self, context: UserContext) -> str:
        """Предложение перерыва."""
        work_time = context.metadata.get('continuous_work_minutes', 0)
        return f"Сэр, вы работаете уже {work_time} минут без перерыва. Рекомендую сделать короткую паузу 5-10 минут для восстановления концентрации."
    
    async def _remind_water(self, context: UserContext) -> str:
        """Напоминание о воде."""
        return "Сэр, напоминаю выпить воды. Гидратация важна для продуктивности."
    
    async def _optimize_energy(self, context: UserContext) -> str:
        """Оптимизация энергопотребления."""
        return "Сэр, я обнаружил возможность оптимизации энергопотребления. Хотите, чтобы я выключил неиспользуемые устройства и снизил яркость освещения?"
    
    async def _suggest_sleep_mode(self, context: UserContext) -> str:
        """Предложение режима сна."""
        return "Сэр, уже поздно и вы давно не активны. Хотите, чтобы я включил режим сна? Выключу свет, закрою шторы и включу спокойную музыку."
    
    async def _remind_backup(self, context: UserContext) -> str:
        """Напоминание о бэкапе."""
        return "Сэр, прошло более недели с последнего резервного копирования. Рекомендую создать резервную копию важных данных."
    
    async def check_conditions(self, context: UserContext) -> List[ProactiveInsight]:
        """
        Проверка всех условий для пользователя.
        
        Args:
            context: Контекст пользователя
            
        Returns:
            Список инсайтов
        """
        insights = []
        user_id = context.user_id
        
        for condition in self.conditions:
            try:
                # Проверка кулдауна
                if self._is_on_cooldown(user_id, condition):
                    continue
                
                # Проверка условия
                if await self._evaluate_condition(condition.trigger_condition, context):
                    # Выполнение действия
                    result = await condition.execute_func(context)
                    
                    # Создание инсайта
                    insight = ProactiveInsight(
                        title=condition.name,
                        content=result,
                        category=condition.action_type.value,
                        relevance_score=self._calculate_relevance(condition, context),
                        suggested_actions=self._get_suggested_actions(condition),
                    )
                    
                    insights.append(insight)
                    
                    # Обновление истории
                    self._record_execution(user_id, condition)
                    
                    logger.info(f"Выполнено проактивное действие: {condition.name}")
                    
            except Exception as e:
                logger.error(f"Ошибка проверки условия {condition.name}: {e}")
        
        return insights
    
    async def _evaluate_condition(
        self, 
        condition: str, 
        context: UserContext
    ) -> bool:
        """
        Оценка условия.
        
        Args:
            condition: Строка условия
            context: Контекст пользователя
            
        Returns:
            True если условие выполнено
        """
        # Простая оценка условий
        # В реальной реализации можно использовать eval или парсер
        
        metadata = context.metadata
        
        # Проверка батареи
        if "device_battery <" in condition:
            threshold = int(condition.split("<")[1].strip())
            device = context.primary_device
            if device and device.battery_level:
                return device.battery_level < threshold
        
        # Проверка безопасности
        if "security_events >" in condition:
            threshold = int(condition.split(">")[1].strip())
            events = metadata.get('security_events', 0)
            return events > threshold
        
        # Проверка времени работы
        if "continuous_work_minutes >" in condition:
            threshold = int(condition.split(">")[1].strip())
            work_time = metadata.get('continuous_work_minutes', 0)
            return work_time > threshold
        
        # Проверка времени с последнего питья воды
        if "hours_since_last_water >" in condition:
            threshold = int(condition.split(">")[1].strip())
            hours = metadata.get('hours_since_last_water', 0)
            return hours > threshold
        
        # Проверка ночного времени
        if "time == 'night'" in condition:
            from app.services.jarvis.context_manager import TimeContext
            is_night = context.time_of_day == TimeContext.NIGHT
            inactive = metadata.get('user_inactive_minutes', 0) > 30
            return is_night and inactive
        
        # Проверка бэкапа
        if "days_since_last_backup >" in condition:
            threshold = int(condition.split(">")[1].strip())
            days = metadata.get('days_since_last_backup', 999)
            return days > threshold
        
        # Проверка встречи
        if "upcoming_meeting_in_minutes ==" in condition:
            target = int(condition.split("==")[1].strip())
            meeting_in = metadata.get('upcoming_meeting_in_minutes', -1)
            return meeting_in == target
        
        return False
    
    def _is_on_cooldown(self, user_id: int, condition: ProactiveAction) -> bool:
        """Проверка кулдауна действия."""
        if user_id not in self.action_history:
            return False
        
        history = self.action_history[user_id]
        key = f"{user_id}_{condition.name}"
        
        last_executed = None
        for timestamp in reversed(history):
            # Проверка последнего выполнения этого действия
            if condition.last_executed:
                last_executed = condition.last_executed
                break
        
        if last_executed:
            cooldown = timedelta(minutes=condition.cooldown_minutes)
            return datetime.now() - last_executed < cooldown
        
        return False
    
    def _record_execution(self, user_id: int, condition: ProactiveAction):
        """Запись выполнения действия."""
        if user_id not in self.action_history:
            self.action_history[user_id] = []
        
        self.action_history[user_id].append(datetime.now())
        condition.last_executed = datetime.now()
    
    def _calculate_relevance(
        self, 
        condition: ProactiveAction, 
        context: UserContext
    ) -> float:
        """Расчет релевантности действия."""
        # Базовая релевантность на основе приоритета
        priority_scores = {
            Priority.LOW: 0.3,
            Priority.MEDIUM: 0.5,
            Priority.HIGH: 0.7,
            Priority.CRITICAL: 0.9,
        }
        
        base_score = priority_scores.get(condition.priority, 0.5)
        
        # Корректировка на основе эмоционального состояния
        if context.emotional_state == EmotionalState.STRESSED:
            if condition.action_type == ActionType.SUGGESTION:
                base_score *= 0.5  # Меньше предложений при стрессе
            elif condition.action_type == ActionType.ALERT:
                base_score *= 1.2  # Больше внимания к алертам
        
        return min(1.0, base_score)
    
    def _get_suggested_actions(self, condition: ProactiveAction) -> List[str]:
        """Получение предлагаемых действий."""
        suggestions_map = {
            "low_battery": ["Подключить зарядное устройство", "Включить энергосберегающий режим"],
            "security_threat": ["Проверить последние действия", "Включить усиленную защиту", "Сменить пароли"],
            "meeting_reminder": ["Подготовить материалы", "Проверить подключение", "Установить напоминание"],
            "break_suggestion": ["Сделать перерыв 5 минут", "Выпить воды", "Размяться"],
            "water_reminder": ["Выпить стакан воды"],
            "energy_optimization": ["Подтвердить оптимизацию", "Выбрать устройства для выключения"],
            "sleep_mode_suggestion": ["Включить режим сна", "Отложить на 30 минут"],
            "backup_reminder": ["Создать резервную копию", "Настроить автосохранение"],
        }
        
        return suggestions_map.get(condition.name, [])
    
    async def start_monitoring(self, user_ids: List[int] = None):
        """
        Запуск непрерывного мониторинга.
        
        Args:
            user_ids: Список ID пользователей для мониторинга
        """
        if self.is_monitoring:
            logger.warning("Мониторинг уже запущен")
            return
        
        self.is_monitoring = True
        self._monitoring_task = asyncio.create_task(
            self._monitor_loop(user_ids or [])
        )
        
        logger.info("Проактивный мониторинг запущен")
    
    async def stop_monitoring(self):
        """Остановка мониторинга."""
        self.is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
            self._monitoring_task = None
        
        logger.info("Проактивный мониторинг остановлен")
    
    async def _monitor_loop(self, user_ids: List[int]):
        """Цикл мониторинга."""
        while self.is_monitoring:
            try:
                for user_id in user_ids:
                    try:
                        context = await self.context_manager.build(user_id)
                        insights = await self.check_conditions(context)
                        
                        # Отправка инсайтов пользователю
                        for insight in insights:
                            await self._notify_user(user_id, insight)
                            
                    except Exception as e:
                        logger.error(f"Ошибка мониторинга пользователя {user_id}: {e}")
                
                await asyncio.sleep(self.check_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в цикле мониторинга: {e}")
                await asyncio.sleep(self.check_interval)
    
    async def _notify_user(self, user_id: int, insight: ProactiveInsight):
        """Отправка уведомления пользователю."""
        # Интеграция с системой уведомлений
        logger.info(f"Уведомление для {user_id}: {insight.title}")
        
        # TODO: Интеграция с WebSocket для реального уведомления
        # await notification_service.send(user_id, insight)


# Глобальный экземпляр
_proactive_jarvis: Optional[ProactiveJarvis] = None


def get_proactive_jarvis(context_manager: ContextManager = None) -> ProactiveJarvis:
    """Получение или создание экземпляра ProactiveJarvis."""
    global _proactive_jarvis
    
    if _proactive_jarvis is None and context_manager:
        _proactive_jarvis = ProactiveJarvis(context_manager)
    
    return _proactive_jarvis
