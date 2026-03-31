"""
Jarvis Notifications - система умных уведомлений от JARVIS.
Классифицирует важность, выбирает канал доставки и генерирует персонализированные сообщения.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger("jarvis.notifications")


class NotificationPriority(Enum):
    """Приоритет уведомления."""
    LOW = "low"           # Информационное
    MEDIUM = "medium"     # Важное
    HIGH = "high"         # Срочное
    CRITICAL = "critical" # Критическое


class NotificationChannel(Enum):
    """Каналы доставки уведомлений."""
    PUSH = "push"         # Push-уведомление (браузер/мобильное)
    WEBSOCKET = "websocket"  # WebSocket (реальное время)
    EMAIL = "email"       # Email
    TELEGRAM = "telegram" # Telegram бот
    VOICE = "voice"       # Голосовое уведомление
    SMS = "sms"           # SMS


class NotificationType(Enum):
    """Типы уведомлений."""
    SYSTEM = "system"           # Системное
    SECURITY = "security"       # Безопасность
    REMINDER = "reminder"       # Напоминание
    ALERT = "alert"             # Предупреждение
    INFO = "info"               # Информация
    SOCIAL = "social"           # Социальное
    FINANCE = "finance"         # Финансовое
    HEALTH = "health"           # Здоровье
    SCHEDULE = "schedule"       # Расписание
    SMART_HOME = "smart_home"   # Умный дом


@dataclass
class Notification:
    """Уведомление от JARVIS."""
    id: str
    user_id: int
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority
    channels: List[NotificationChannel]
    
    # Метаданные
    data: Dict[str, Any] = field(default_factory=dict)
    actions: List[Dict[str, str]] = field(default_factory=list)
    
    # Время
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    
    # Статус
    read: bool = False
    delivered: bool = False
    delivered_at: Optional[datetime] = None
    
    # Персонализация
    voice_message: Optional[str] = None
    require_confirmation: bool = False


@dataclass
class NotificationPreferences:
    """Предпочтения уведомлений пользователя."""
    user_id: int
    
    # Разрешенные каналы
    enabled_channels: List[NotificationChannel] = field(default_factory=lambda: [
        NotificationChannel.WEBSOCKET,
        NotificationChannel.PUSH,
    ])
    
    # Тихий режим
    quiet_hours_start: Optional[int] = 23  # 23:00
    quiet_hours_end: Optional[int] = 7     # 07:00
    
    # Приоритеты для голосовых уведомлений
    voice_for_priority: List[NotificationPriority] = field(default_factory=lambda: [
        NotificationPriority.HIGH,
        NotificationPriority.CRITICAL,
    ])
    
    # Группировка
    group_similar: bool = True
    group_interval_minutes: int = 5
    
    # Telegram
    telegram_enabled: bool = False
    telegram_chat_id: Optional[str] = None
    
    # Email
    email_enabled: bool = False
    email_address: Optional[str] = None


class NotificationClassifier:
    """
    Классификатор уведомлений.
    Определяет приоритет и тип на основе содержимого.
    """
    
    # Ключевые слова для определения приоритета
    PRIORITY_KEYWORDS = {
        NotificationPriority.CRITICAL: [
            'угроза', 'взлом', 'атака', 'критическая ошибка', 'авария',
            'экстренная ситуация', 'немедленно', 'срочно',
        ],
        NotificationPriority.HIGH: [
            'важно', 'срочно', 'внимание', 'предупреждение', 'ошибка',
            'проблема', 'требует внимания', 'низкий заряд',
        ],
        NotificationPriority.MEDIUM: [
            'напоминание', 'встреча', 'событие', 'изменение', 'обновление',
            'уведомление', 'сообщение',
        ],
        NotificationPriority.LOW: [
            'информация', 'статистика', 'отчет', 'совет', 'предложение',
        ],
    }
    
    # Ключевые слова для определения типа
    TYPE_KEYWORDS = {
        NotificationType.SECURITY: [
            'безопасность', 'угроза', 'взлом', 'атака', 'пароль', 'доступ',
            'подозрительн', 'несанкционирован',
        ],
        NotificationType.REMINDER: [
            'напомин', 'не забудь', 'пора', 'время', 'срок',
        ],
        NotificationType.ALERT: [
            'предупреждение', 'внимание', 'ошибка', 'проблема', 'сбой',
        ],
        NotificationType.FINANCE: [
            'баланс', 'платеж', 'перевод', 'счет', 'деньги', 'рубл',
            'доллар', 'евро', 'крипто',
        ],
        NotificationType.HEALTH: [
            'здоровье', 'пульс', 'давление', 'температура', 'лекарств',
            'вода', 'отдых', 'перерыв',
        ],
        NotificationType.SCHEDULE: [
            'встреча', 'событие', 'календарь', 'расписание', 'план',
        ],
        NotificationType.SMART_HOME: [
            'свет', 'температура', 'устройство', 'датчик', 'камера',
            'замок', 'шторы',
        ],
    }
    
    def classify(self, content: str) -> tuple[NotificationPriority, NotificationType]:
        """
        Классификация уведомления по содержимому.
        
        Args:
            content: Содержимое уведомления
            
        Returns:
            Кортеж (приоритет, тип)
        """
        content_lower = content.lower()
        
        # Определение приоритета
        priority = NotificationPriority.MEDIUM
        for p, keywords in self.PRIORITY_KEYWORDS.items():
            if any(kw in content_lower for kw in keywords):
                priority = p
                break
        
        # Определение типа
        notification_type = NotificationType.INFO
        for t, keywords in self.TYPE_KEYWORDS.items():
            if any(kw in content_lower for kw in keywords):
                notification_type = t
                break
        
        return priority, notification_type


class ChannelSelector:
    """
    Селектор каналов доставки.
    Выбирает оптимальный канал на основе приоритета и предпочтений.
    """
    
    # Маппинг приоритета на каналы по умолчанию
    DEFAULT_CHANNELS = {
        NotificationPriority.LOW: [NotificationChannel.WEBSOCKET],
        NotificationPriority.MEDIUM: [NotificationChannel.WEBSOCKET, NotificationChannel.PUSH],
        NotificationPriority.HIGH: [NotificationChannel.WEBSOCKET, NotificationChannel.PUSH, NotificationChannel.TELEGRAM],
        NotificationPriority.CRITICAL: [NotificationChannel.WEBSOCKET, NotificationChannel.PUSH, NotificationChannel.TELEGRAM, NotificationChannel.VOICE],
    }
    
    def select(
        self,
        priority: NotificationPriority,
        preferences: NotificationPreferences,
        notification_type: NotificationType,
    ) -> List[NotificationChannel]:
        """
        Выбор каналов доставки.
        
        Args:
            priority: Приоритет уведомления
            preferences: Предпочтения пользователя
            notification_type: Тип уведомления
            
        Returns:
            Список каналов доставки
        """
        # Базовые каналы по приоритету
        channels = self.DEFAULT_CHANNELS.get(priority, [NotificationChannel.WEBSOCKET]).copy()
        
        # Фильтрация по разрешенным каналам
        channels = [ch for ch in channels if ch in preferences.enabled_channels]
        
        # Проверка тихого режима
        if self._is_quiet_hours(preferences):
            # В тихий режим только критические через голос
            if priority not in [NotificationPriority.CRITICAL]:
                channels = [ch for ch in channels if ch != NotificationChannel.VOICE]
        
        # Проверка Telegram
        if NotificationChannel.TELEGRAM in channels:
            if not preferences.telegram_enabled or not preferences.telegram_chat_id:
                channels.remove(NotificationChannel.TELEGRAM)
        
        # Проверка Email
        if NotificationChannel.EMAIL in channels:
            if not preferences.email_enabled or not preferences.email_address:
                channels.remove(NotificationChannel.EMAIL)
        
        return channels
    
    def _is_quiet_hours(self, preferences: NotificationPreferences) -> bool:
        """Проверка тихого режима."""
        if preferences.quiet_hours_start is None:
            return False
        
        now = datetime.now().hour
        start = preferences.quiet_hours_start
        end = preferences.quiet_hours_end
        
        if start > end:  # Переход через полночь
            return now >= start or now < end
        else:
            return start <= now < end


class NotificationGenerator:
    """
    Генератор персонализированных уведомлений.
    Создает сообщения в стиле JARVIS.
    """
    
    # Шаблоны сообщений
    TEMPLATES = {
        NotificationType.SECURITY: {
            NotificationPriority.CRITICAL: "⚠️ КРИТИЧЕСКАЯ УГРОЗА: {message}",
            NotificationPriority.HIGH: "🔒 Внимание: {message}",
            NotificationPriority.MEDIUM: "🛡️ Уведомление безопасности: {message}",
            NotificationPriority.LOW: "ℹ️ {message}",
        },
        NotificationType.REMINDER: {
            NotificationPriority.HIGH: "⏰ Срочно: {message}",
            NotificationPriority.MEDIUM: "📅 Напоминание: {message}",
            NotificationPriority.LOW: "💡 {message}",
        },
        NotificationType.ALERT: {
            NotificationPriority.CRITICAL: "🚨 КРИТИЧЕСКОЕ ПРЕДУПРЕЖДЕНИЕ: {message}",
            NotificationPriority.HIGH: "⚠️ Внимание! {message}",
            NotificationPriority.MEDIUM: "⚡ {message}",
            NotificationPriority.LOW: "ℹ️ {message}",
        },
        NotificationType.FINANCE: {
            NotificationPriority.HIGH: "💰 Важно: {message}",
            NotificationPriority.MEDIUM: "💳 {message}",
            NotificationPriority.LOW: "📊 {message}",
        },
        NotificationType.HEALTH: {
            NotificationPriority.HIGH: "❤️ Важно для здоровья: {message}",
            NotificationPriority.MEDIUM: "🏥 {message}",
            NotificationPriority.LOW: "💪 Совет: {message}",
        },
        NotificationType.SCHEDULE: {
            NotificationPriority.HIGH: "📅 Скоро: {message}",
            NotificationPriority.MEDIUM: "📆 {message}",
            NotificationPriority.LOW: "📋 {message}",
        },
        NotificationType.SMART_HOME: {
            NotificationPriority.HIGH: "🏠 Внимание: {message}",
            NotificationPriority.MEDIUM: "🏡 {message}",
            NotificationPriority.LOW: "💡 {message}",
        },
        NotificationType.SYSTEM: {
            NotificationPriority.CRITICAL: "🔧 КРИТИЧЕСКАЯ ОШИБКА: {message}",
            NotificationPriority.HIGH: "⚙️ {message}",
            NotificationPriority.MEDIUM: "🔧 {message}",
            NotificationPriority.LOW: "ℹ️ {message}",
        },
        NotificationType.INFO: {
            NotificationPriority.HIGH: "📌 {message}",
            NotificationPriority.MEDIUM: "ℹ️ {message}",
            NotificationPriority.LOW: "💡 {message}",
        },
    }
    
    def generate(
        self,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority,
        user_name: str = "Сэр",
    ) -> str:
        """
        Генерация персонализированного сообщения.
        
        Args:
            message: Базовое сообщение
            notification_type: Тип уведомления
            priority: Приоритет
            user_name: Имя пользователя
            
        Returns:
            Персонализированное сообщение
        """
        # Получение шаблона
        type_templates = self.TEMPLATES.get(notification_type, self.TEMPLATES[NotificationType.INFO])
        template = type_templates.get(priority, "{message}")
        
        # Форматирование
        formatted = template.format(message=message)
        
        # Добавление обращения для высоких приоритетов
        if priority in [NotificationPriority.HIGH, NotificationPriority.CRITICAL]:
            formatted = f"{user_name}, {formatted}"
        
        return formatted
    
    def generate_voice(
        self,
        message: str,
        notification_type: NotificationType,
        priority: NotificationPriority,
        user_name: str = "Сэр",
    ) -> str:
        """
        Генерация голосового сообщения.
        Более естественная формулировка для TTS.
        """
        # Для голоса используем более естественные фразы
        if priority == NotificationPriority.CRITICAL:
            return f"{user_name}, срочно! {message}"
        elif priority == NotificationPriority.HIGH:
            return f"{user_name}, {message}"
        else:
            return message


class JarvisNotifications:
    """
    Система уведомлений JARVIS.
    
    Функции:
    - Классификация важности событий
    - Выбор оптимального канала доставки
    - Генерация персонализированных сообщений
    - Управление предпочтениями пользователя
    - Группировка похожих уведомлений
    """
    
    def __init__(self, db=None):
        """
        Инициализация системы уведомлений.
        
        Args:
            db: Сессия базы данных (опционально)
        """
        self.db = db
        
        # Компоненты
        self.classifier = NotificationClassifier()
        self.channel_selector = ChannelSelector()
        self.generator = NotificationGenerator()
        
        # Кэш предпочтений
        self._preferences_cache: Dict[int, NotificationPreferences] = {}
        
        # Очередь уведомлений
        self._notification_queue: asyncio.Queue = asyncio.Queue()
        
        # Обработчики каналов
        self._channel_handlers: Dict[NotificationChannel, Callable] = {}
        
        # Группировка
        self._pending_groups: Dict[str, List[Notification]] = {}
        
        # Задача обработки
        self._process_task: Optional[asyncio.Task] = None
    
    def register_channel_handler(
        self,
        channel: NotificationChannel,
        handler: Callable,
    ):
        """Регистрация обработчика канала."""
        self._channel_handlers[channel] = handler
        logger.info(f"Зарегистрирован обработчик для канала {channel.value}")
    
    async def notify(
        self,
        user_id: int,
        content: str,
        title: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        actions: Optional[List[Dict[str, str]]] = None,
        force_priority: Optional[NotificationPriority] = None,
        force_type: Optional[NotificationType] = None,
    ) -> Notification:
        """
        Создание и отправка уведомления.
        
        Args:
            user_id: ID пользователя
            content: Содержимое уведомления
            title: Заголовок (опционально)
            data: Дополнительные данные
            actions: Доступные действия
            force_priority: Принудительный приоритет
            force_type: Принудительный тип
            
        Returns:
            Созданное уведомление
        """
        # Классификация
        if force_priority and force_type:
            priority = force_priority
            notification_type = force_type
        else:
            priority, notification_type = self.classifier.classify(content)
            if force_priority:
                priority = force_priority
            if force_type:
                notification_type = force_type
        
        # Получение предпочтений
        preferences = await self._get_preferences(user_id)
        
        # Выбор каналов
        channels = self.channel_selector.select(
            priority,
            preferences,
            notification_type,
        )
        
        # Генерация сообщений
        user_name = preferences.telegram_chat_id or "Сэр"  # TODO: Реальное имя
        
        message = self.generator.generate(
            content,
            notification_type,
            priority,
            user_name,
        )
        
        voice_message = self.generator.generate_voice(
            content,
            notification_type,
            priority,
            user_name,
        )
        
        # Создание уведомления
        notification = Notification(
            id=self._generate_id(),
            user_id=user_id,
            title=title or self._get_default_title(notification_type),
            message=message,
            notification_type=notification_type,
            priority=priority,
            channels=channels,
            data=data or {},
            actions=actions or [],
            voice_message=voice_message,
            expires_at=self._calculate_expiry(priority),
        )
        
        # Добавление в очередь
        await self._notification_queue.put(notification)
        
        logger.info(f"Создано уведомление для пользователя {user_id}: {message[:50]}...")
        
        return notification
    
    async def _get_preferences(self, user_id: int) -> NotificationPreferences:
        """Получение предпочтений пользователя."""
        if user_id in self._preferences_cache:
            return self._preferences_cache[user_id]
        
        # TODO: Загрузка из БД
        preferences = NotificationPreferences(user_id=user_id)
        self._preferences_cache[user_id] = preferences
        
        return preferences
    
    def _generate_id(self) -> str:
        """Генерация ID уведомления."""
        import uuid
        return f"notif_{uuid.uuid4().hex[:12]}"
    
    def _get_default_title(self, notification_type: NotificationType) -> str:
        """Заголовок по умолчанию для типа."""
        titles = {
            NotificationType.SECURITY: "Безопасность",
            NotificationType.REMINDER: "Напоминание",
            NotificationType.ALERT: "Предупреждение",
            NotificationType.FINANCE: "Финансы",
            NotificationType.HEALTH: "Здоровье",
            NotificationType.SCHEDULE: "Расписание",
            NotificationType.SMART_HOME: "Умный дом",
            NotificationType.SYSTEM: "Система",
            NotificationType.INFO: "Информация",
            NotificationType.SOCIAL: "Социальное",
        }
        return titles.get(notification_type, "JARVIS")
    
    def _calculate_expiry(self, priority: NotificationPriority) -> datetime:
        """Расчет времени истечения."""
        expiry_hours = {
            NotificationPriority.CRITICAL: 1,
            NotificationPriority.HIGH: 4,
            NotificationPriority.MEDIUM: 24,
            NotificationPriority.LOW: 72,
        }
        
        hours = expiry_hours.get(priority, 24)
        return datetime.now() + timedelta(hours=hours)
    
    async def start_processing(self):
        """Запуск обработки очереди уведомлений."""
        if self._process_task and not self._process_task.done():
            logger.warning("Обработка уже запущена")
            return
        
        self._process_task = asyncio.create_task(self._process_queue())
        logger.info("Запущена обработка очереди уведомлений")
    
    async def stop_processing(self):
        """Остановка обработки."""
        if self._process_task:
            self._process_task.cancel()
            self._process_task = None
            logger.info("Обработка очереди остановлена")
    
    async def _process_queue(self):
        """Обработка очереди уведомлений."""
        while True:
            try:
                notification = await self._notification_queue.get()
                
                # Доставка по каналам
                for channel in notification.channels:
                    await self._deliver(notification, channel)
                
                notification.delivered = True
                notification.delivered_at = datetime.now()
                
                # Сохранение в БД
                await self._save_notification(notification)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка обработки уведомления: {e}")
    
    async def _deliver(
        self,
        notification: Notification,
        channel: NotificationChannel,
    ):
        """Доставка уведомления через канал."""
        handler = self._channel_handlers.get(channel)
        
        if handler:
            try:
                await handler(notification)
                logger.info(f"Уведомление {notification.id} доставлено через {channel.value}")
            except Exception as e:
                logger.error(f"Ошибка доставки через {channel.value}: {e}")
        else:
            logger.warning(f"Обработчик для канала {channel.value} не зарегистрирован")
    
    async def _save_notification(self, notification: Notification):
        """Сохранение уведомления в БД."""
        # TODO: Реальное сохранение
        logger.debug(f"Уведомление {notification.id} сохранено")
    
    async def mark_read(self, notification_id: str, user_id: int):
        """Пометить уведомление как прочитанное."""
        # TODO: Обновление в БД
        logger.info(f"Уведомление {notification_id} прочитано")
    
    async def get_unread(self, user_id: int, limit: int = 50) -> List[Notification]:
        """Получение непрочитанных уведомлений."""
        # TODO: Загрузка из БД
        return []
    
    async def get_history(
        self,
        user_id: int,
        days: int = 7,
        limit: int = 100,
    ) -> List[Notification]:
        """Получение истории уведомлений."""
        # TODO: Загрузка из БД
        return []


# Глобальный экземпляр
_notification_system: Optional[JarvisNotifications] = None


def get_notification_system(db=None) -> JarvisNotifications:
    """Получение или создание системы уведомлений."""
    global _notification_system
    
    if _notification_system is None:
        _notification_system = JarvisNotifications(db)
    
    return _notification_system
