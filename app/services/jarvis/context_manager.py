"""
Context Manager - управление контекстом пользователя для JARVIS.
Собирает и анализирует историю, предпочтения, состояние и окружение.
"""
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

logger = logging.getLogger("jarvis.context")


class EmotionalState(Enum):
    """Эмоциональное состояние пользователя."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    STRESSED = "stressed"
    TIRED = "tired"
    FOCUSED = "focused"
    RELAXED = "relaxed"


class TimeContext(Enum):
    """Временной контекст."""
    MORNING = "morning"      # 6:00 - 12:00
    AFTERNOON = "afternoon"  # 12:00 - 18:00
    EVENING = "evening"      # 18:00 - 22:00
    NIGHT = "night"          # 22:00 - 6:00


@dataclass
class UserPreferences:
    """Предпочтения пользователя."""
    voice_persona: str = "calm"
    language: str = "ru"
    temperature_unit: str = "celsius"
    currency: str = "RUB"
    timezone: str = "Europe/Moscow"
    notification_level: str = "normal"  # silent, normal, verbose
    proactive_mode: bool = True
    preferred_name: str = "Сэр"


@dataclass
class DeviceContext:
    """Контекст устройства."""
    device_id: str
    device_type: str  # desktop, mobile, tablet, watch, car
    is_online: bool
    last_active: datetime
    battery_level: Optional[int] = None
    location: Optional[Dict[str, float]] = None


@dataclass
class UserContext:
    """
    Полный контекст пользователя для генерации ответов JARVIS.
    """
    user_id: int
    username: str
    
    # Временной контекст
    time_of_day: TimeContext
    day_of_week: int
    is_workday: bool
    
    # Эмоциональное состояние
    emotional_state: EmotionalState
    
    # Предпочтения
    preferences: UserPreferences
    
    # История
    recent_messages: List[Dict[str, Any]] = field(default_factory=list)
    recent_actions: List[Dict[str, Any]] = field(default_factory=list)
    
    # Устройства
    active_devices: List[DeviceContext] = field(default_factory=list)
    primary_device: Optional[DeviceContext] = None
    
    # Местоположение
    location: Optional[Dict[str, float]] = None
    location_name: Optional[str] = None
    
    # Активность
    is_active: bool = True
    last_interaction: Optional[datetime] = None
    session_duration: Optional[timedelta] = None
    
    # Метаданные
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """
    Менеджер контекста пользователя.
    Собирает и агрегирует информацию для персонализированных ответов JARVIS.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Инициализация менеджера контекста.
        
        Args:
            db: Сессия базы данных
        """
        self.db = db
        
        # Кэш контекстов
        self._context_cache: Dict[int, UserContext] = {}
        self._cache_ttl = timedelta(minutes=5)
        self._cache_timestamps: Dict[int, datetime] = {}
    
    def _get_time_context(self) -> TimeContext:
        """Определение временного контекста."""
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            return TimeContext.MORNING
        elif 12 <= hour < 18:
            return TimeContext.AFTERNOON
        elif 18 <= hour < 22:
            return TimeContext.EVENING
        else:
            return TimeContext.NIGHT
    
    def _is_workday(self) -> bool:
        """Проверка рабочего дня."""
        day_of_week = datetime.now().weekday()
        return 0 <= day_of_week <= 4  # Пн-Пт
    
    async def _get_user_preferences(self, user_id: int) -> UserPreferences:
        """Получение предпочтений пользователя из БД."""
        from app.models.user import User
        
        try:
            result = await self.db.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user and hasattr(user, 'preferences'):
                prefs = user.preferences or {}
                return UserPreferences(
                    voice_persona=prefs.get('voice_persona', 'calm'),
                    language=prefs.get('language', 'ru'),
                    temperature_unit=prefs.get('temperature_unit', 'celsius'),
                    currency=prefs.get('currency', 'RUB'),
                    timezone=prefs.get('timezone', 'Europe/Moscow'),
                    notification_level=prefs.get('notification_level', 'normal'),
                    proactive_mode=prefs.get('proactive_mode', True),
                    preferred_name=prefs.get('preferred_name', 'Сэр'),
                )
        except Exception as e:
            logger.error(f"Ошибка получения предпочтений: {e}")
        
        return UserPreferences()
    
    async def _get_recent_messages(
        self, 
        user_id: int, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Получение недавних сообщений пользователя."""
        from app.models.memory import MemoryEntry
        
        try:
            result = await self.db.execute(
                select(MemoryEntry)
                .where(MemoryEntry.user_id == user_id)
                .order_by(MemoryEntry.created_at.desc())
                .limit(limit)
            )
            entries = result.scalars().all()
            
            return [
                {
                    'content': entry.content,
                    'role': entry.metadata.get('role', 'user'),
                    'timestamp': entry.created_at,
                }
                for entry in entries
            ]
        except Exception as e:
            logger.error(f"Ошибка получения сообщений: {e}")
            return []
    
    async def _get_active_devices(self, user_id: int) -> List[DeviceContext]:
        """Получение активных устройств пользователя."""
        from app.models.smarthome import Device
        
        try:
            result = await self.db.execute(
                select(Device).where(Device.user_id == user_id)
            )
            devices = result.scalars().all()
            
            return [
                DeviceContext(
                    device_id=str(device.id),
                    device_type=device.device_type,
                    is_online=device.is_online,
                    last_active=datetime.now(),
                )
                for device in devices
            ]
        except Exception as e:
            logger.error(f"Ошибка получения устройств: {e}")
            return []
    
    def _detect_emotional_state(
        self, 
        recent_messages: List[Dict[str, Any]]
    ) -> EmotionalState:
        """
        Определение эмоционального состояния по истории сообщений.
        Использует простой эвристический анализ.
        """
        if not recent_messages:
            return EmotionalState.NEUTRAL
        
        # Анализ последних сообщений
        recent_text = " ".join(
            msg.get('content', '') 
            for msg in recent_messages[:3]
        ).lower()
        
        # Ключевые слова для определения состояния
        stress_keywords = ['срочно', 'быстро', 'проблема', 'ошибка', 'не работает', 'помогите']
        tired_keywords = ['устал', 'спать', 'отдых', 'перерыв', 'выключи']
        happy_keywords = ['отлично', 'супер', 'спасибо', 'работает', 'получилось']
        focus_keywords = ['работаю', 'проект', 'задача', 'сделай', 'нужно']
        
        if any(kw in recent_text for kw in stress_keywords):
            return EmotionalState.STRESSED
        elif any(kw in recent_text for kw in tired_keywords):
            return EmotionalState.TIRED
        elif any(kw in recent_text for kw in happy_keywords):
            return EmotionalState.HAPPY
        elif any(kw in recent_text for kw in focus_keywords):
            return EmotionalState.FOCUSED
        
        # Временной контекст влияет на состояние
        time_context = self._get_time_context()
        if time_context == TimeContext.NIGHT:
            return EmotionalState.TIRED
        elif time_context == TimeContext.MORNING:
            return EmotionalState.FOCUSED
        
        return EmotionalState.NEUTRAL
    
    async def build(self, user_id: int) -> UserContext:
        """
        Построение полного контекста пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            UserContext с полной информацией
        """
        # Проверка кэша
        if user_id in self._context_cache:
            cache_time = self._cache_timestamps.get(user_id)
            if cache_time and datetime.now() - cache_time < self._cache_ttl:
                return self._context_cache[user_id]
        
        # Получение базовой информации пользователя
        from app.models.user import User
        
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"Пользователь {user_id} не найден")
        
        # Сбор компонентов контекста
        preferences = await self._get_user_preferences(user_id)
        recent_messages = await self._get_recent_messages(user_id)
        active_devices = await self._get_active_devices(user_id)
        
        emotional_state = self._detect_emotional_state(recent_messages)
        
        # Построение контекста
        context = UserContext(
            user_id=user_id,
            username=user.username,
            time_of_day=self._get_time_context(),
            day_of_week=datetime.now().weekday(),
            is_workday=self._is_workday(),
            emotional_state=emotional_state,
            preferences=preferences,
            recent_messages=recent_messages,
            active_devices=active_devices,
            primary_device=active_devices[0] if active_devices else None,
            last_interaction=datetime.now(),
        )
        
        # Кэширование
        self._context_cache[user_id] = context
        self._cache_timestamps[user_id] = datetime.now()
        
        return context
    
    def update_context(
        self, 
        user_id: int, 
        updates: Dict[str, Any]
    ) -> Optional[UserContext]:
        """
        Обновление контекста пользователя.
        
        Args:
            user_id: ID пользователя
            updates: Обновляемые поля
            
        Returns:
            Обновленный контекст
        """
        if user_id not in self._context_cache:
            return None
        
        context = self._context_cache[user_id]
        
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        self._cache_timestamps[user_id] = datetime.now()
        
        return context
    
    def clear_cache(self, user_id: Optional[int] = None):
        """Очистка кэша контекста."""
        if user_id:
            self._context_cache.pop(user_id, None)
            self._cache_timestamps.pop(user_id, None)
        else:
            self._context_cache.clear()
            self._cache_timestamps.clear()
    
    def get_greeting(self, context: UserContext) -> str:
        """
        Генерация персонализированного приветствия.
        
        Args:
            context: Контекст пользователя
            
        Returns:
            Строка приветствия
        """
        name = context.preferences.preferred_name
        time_ctx = context.time_of_day
        emotional = context.emotional_state
        
        # Базовое приветствие по времени
        greetings = {
            TimeContext.MORNING: "Доброе утро",
            TimeContext.AFTERNOON: "Добрый день",
            TimeContext.EVENING: "Добрый вечер",
            TimeContext.NIGHT: "Доброй ночи",
        }
        
        greeting = greetings.get(time_ctx, "Здравствуйте")
        
        # Адаптация под эмоциональное состояние
        if emotional == EmotionalState.STRESSED:
            greeting += f", {name}. Вижу, вы заняты. Чем могу помочь?"
        elif emotional == EmotionalState.TIRED:
            greeting += f", {name}. Может, сделаете перерыв?"
        elif emotional == EmotionalState.HAPPY:
            greeting += f", {name}! Отличное настроение!"
        else:
            greeting += f", {name}."
        
        return greeting


# Функция для быстрого создания менеджера
def create_context_manager(db: AsyncSession) -> ContextManager:
    """Создание менеджера контекста с сессией БД."""
    return ContextManager(db)
