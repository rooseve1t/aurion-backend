"""
Calendar Integration - интеграция JARVIS с календарями.
Поддержка Google Calendar, Apple Calendar, Outlook, CalDAV.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import os

logger = logging.getLogger("jarvis.calendar")


class CalendarProvider(Enum):
    """Провайдеры календаря."""
    GOOGLE = "google"
    APPLE = "apple"
    OUTLOOK = "outlook"
    CALDAV = "caldav"
    LOCAL = "local"


class EventStatus(Enum):
    """Статус события."""
    CONFIRMED = "confirmed"
    TENTATIVE = "tentative"
    CANCELLED = "cancelled"


class EventType(Enum):
    """Тип события."""
    MEETING = "meeting"
    TASK = "task"
    REMINDER = "reminder"
    APPOINTMENT = "appointment"
    SOCIAL = "social"
    TRAVEL = "travel"
    PERSONAL = "personal"
    WORK = "work"


@dataclass
class CalendarEvent:
    """Событие календаря."""
    id: str
    title: str
    description: Optional[str] = None
    
    # Время
    start_time: datetime
    end_time: Optional[datetime] = None
    all_day: bool = False
    timezone: str = "Europe/Moscow"
    
    # Статус
    status: EventStatus = EventStatus.CONFIRMED
    event_type: EventType = EventType.MEETING
    
    # Участники
    attendees: List[Dict[str, str]] = field(default_factory=list)
    organizer: Optional[str] = None
    
    # Местоположение
    location: Optional[str] = None
    is_online: bool = False
    meeting_url: Optional[str] = None
    
    # Метаданные
    provider: CalendarProvider = CalendarProvider.LOCAL
    calendar_id: Optional[str] = None
    color_id: Optional[str] = None
    reminders: List[Dict[str, Any]] = field(default_factory=list)
    
    # Дополнительные данные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CalendarInsight:
    """Инсайт из анализа календаря."""
    insight_type: str
    title: str
    description: str
    events: List[CalendarEvent]
    recommendations: List[str]
    priority: str  # low, medium, high


class CalendarIntegration:
    """
    Интеграция JARVIS с календарями.
    
    Функции:
    - Синхронизация с Google Calendar, Apple, Outlook
    - Анализ расписания
    - Обнаружение конфликтов
    - Предложения по оптимизации
    - Напоминания о встречах
    - Управление событиями голосом
    """
    
    def __init__(
        self,
        google_credentials: Optional[Dict[str, Any]] = None,
        outlook_credentials: Optional[Dict[str, Any]] = None,
        caldav_url: Optional[str] = None,
    ):
        """
        Инициализация интеграции.
        
        Args:
            google_credentials: Учетные данные Google
            outlook_credentials: Учетные данные Outlook
            caldav_url: URL CalDAV сервера
        """
        self.google_credentials = google_credentials
        self.outlook_credentials = outlook_credentials
        self.caldav_url = caldav_url
        
        # Кэш событий
        self._events_cache: Dict[int, List[CalendarEvent]] = {}
        self._cache_timestamp: Dict[int, datetime] = {}
        self._cache_ttl = timedelta(minutes=5)
        
        # Клиенты API
        self._google_client = None
        self._outlook_client = None
        
        # Задача синхронизации
        self._sync_task: Optional[asyncio.Task] = None
        self.is_syncing = False
    
    async def connect_google(self, user_id: int) -> bool:
        """
        Подключение к Google Calendar.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            True если успешно
        """
        try:
            # TODO: Реальная OAuth2 авторизация
            logger.info(f"Подключение Google Calendar для пользователя {user_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения Google Calendar: {e}")
            return False
    
    async def connect_outlook(self, user_id: int) -> bool:
        """Подключение к Outlook Calendar."""
        try:
            logger.info(f"Подключение Outlook Calendar для пользователя {user_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка подключения Outlook Calendar: {e}")
            return False
    
    async def fetch_events(
        self,
        user_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        providers: Optional[List[CalendarProvider]] = None,
    ) -> List[CalendarEvent]:
        """
        Получение событий из всех календарей.
        
        Args:
            user_id: ID пользователя
            start_date: Начало периода
            end_date: Конец периода
            providers: Список провайдеров
            
        Returns:
            Список событий
        """
        start_date = start_date or datetime.now()
        end_date = end_date or start_date + timedelta(days=7)
        
        # Проверка кэша
        cache_key = f"{user_id}_{start_date.date()}_{end_date.date()}"
        if user_id in self._events_cache:
            cache_time = self._cache_timestamp.get(user_id)
            if cache_time and datetime.now() - cache_time < self._cache_ttl:
                return self._events_cache[user_id]
        
        events = []
        
        # Получение из Google
        if CalendarProvider.GOOGLE in (providers or [CalendarProvider.GOOGLE]):
            google_events = await self._fetch_google_events(user_id, start_date, end_date)
            events.extend(google_events)
        
        # Получение из Outlook
        if CalendarProvider.OUTLOOK in (providers or []):
            outlook_events = await self._fetch_outlook_events(user_id, start_date, end_date)
            events.extend(outlook_events)
        
        # Получение локальных событий
        local_events = await self._fetch_local_events(user_id, start_date, end_date)
        events.extend(local_events)
        
        # Сортировка по времени
        events.sort(key=lambda e: e.start_time)
        
        # Кэширование
        self._events_cache[user_id] = events
        self._cache_timestamp[user_id] = datetime.now()
        
        return events
    
    async def _fetch_google_events(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> List[CalendarEvent]:
        """Получение событий из Google Calendar."""
        # TODO: Реальная интеграция с Google Calendar API
        return []
    
    async def _fetch_outlook_events(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> List[CalendarEvent]:
        """Получение событий из Outlook Calendar."""
        # TODO: Реальная интеграция с Microsoft Graph API
        return []
    
    async def _fetch_local_events(
        self,
        user_id: int,
        start_date: datetime,
        end_date: datetime,
    ) -> List[CalendarEvent]:
        """Получение локальных событий из БД."""
        # TODO: Загрузка из БД
        return []
    
    async def create_event(
        self,
        user_id: int,
        title: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[List[str]] = None,
        provider: CalendarProvider = CalendarProvider.LOCAL,
    ) -> CalendarEvent:
        """
        Создание события в календаре.
        
        Args:
            user_id: ID пользователя
            title: Название события
            start_time: Время начала
            end_time: Время окончания
            description: Описание
            location: Местоположение
            attendees: Участники
            provider: Провайдер календаря
            
        Returns:
            Созданное событие
        """
        event = CalendarEvent(
            id=self._generate_event_id(),
            title=title,
            description=description,
            start_time=start_time,
            end_time=end_time or start_time + timedelta(hours=1),
            location=location,
            attendees=[{'email': email} for email in (attendees or [])],
            provider=provider,
        )
        
        # Сохранение
        if provider == CalendarProvider.GOOGLE:
            await self._create_google_event(user_id, event)
        elif provider == CalendarProvider.OUTLOOK:
            await self._create_outlook_event(user_id, event)
        else:
            await self._create_local_event(user_id, event)
        
        # Инвалидация кэша
        self._events_cache.pop(user_id, None)
        
        logger.info(f"Создано событие: {title} на {start_time}")
        
        return event
    
    async def _create_google_event(self, user_id: int, event: CalendarEvent) -> bool:
        """Создание события в Google Calendar."""
        # TODO: Реальная реализация
        return True
    
    async def _create_outlook_event(self, user_id: int, event: CalendarEvent) -> bool:
        """Создание события в Outlook."""
        return True
    
    async def _create_local_event(self, user_id: int, event: CalendarEvent) -> bool:
        """Создание локального события."""
        # TODO: Сохранение в БД
        return True
    
    async def update_event(
        self,
        user_id: int,
        event_id: str,
        updates: Dict[str, Any],
    ) -> Optional[CalendarEvent]:
        """Обновление события."""
        # TODO: Реальная реализация
        logger.info(f"Обновлено событие {event_id}")
        return None
    
    async def delete_event(self, user_id: int, event_id: str) -> bool:
        """Удаление события."""
        # TODO: Реальная реализация
        logger.info(f"Удалено событие {event_id}")
        return True
    
    async def analyze_schedule(
        self,
        user_id: int,
        days: int = 7,
    ) -> List[CalendarInsight]:
        """
        Анализ расписания пользователя.
        
        Args:
            user_id: ID пользователя
            days: Период анализа
            
        Returns:
            Список инсайтов
        """
        start_date = datetime.now()
        end_date = start_date + timedelta(days=days)
        
        events = await self.fetch_events(user_id, start_date, end_date)
        
        insights = []
        
        # 1. Обнаружение конфликтов
        conflicts = self._detect_conflicts(events)
        if conflicts:
            insights.append(CalendarInsight(
                insight_type="conflicts",
                title="Обнаружены конфликты в расписании",
                description=f"Найдено {len(conflicts)} пересекающихся событий",
                events=conflicts,
                recommendations=[
                    "Перенести одну из встреч",
                    "Сократить длительность",
                    "Делегировать участие",
                ],
                priority="high",
            ))
        
        # 2. Анализ загрузки
        workload = self._analyze_workload(events, days)
        if workload['overloaded_days']:
            insights.append(CalendarInsight(
                insight_type="workload",
                title="Дни с высокой нагрузкой",
                description=f"Обнаружено {len(workload['overloaded_days'])} дней с перегрузкой",
                events=[],
                recommendations=[
                    "Перераспределить встречи",
                    "Оставить время для перерывов",
                    "Делегировать часть задач",
                ],
                priority="medium",
            ))
        
        # 3. Свободные слоты
        free_slots = self._find_free_slots(events, start_date, end_date)
        if free_slots:
            insights.append(CalendarInsight(
                insight_type="availability",
                title="Свободное время",
                description=f"Найдено {len(free_slots)} слотов для новых встреч",
                events=[],
                recommendations=[
                    "Запланировать важные задачи",
                    "Выделить время на фокус-работу",
                    "Назначить личные встречи",
                ],
                priority="low",
            ))
        
        # 4. Предстоящие важные события
        upcoming_important = self._find_important_events(events, hours=24)
        if upcoming_important:
            insights.append(CalendarInsight(
                insight_type="upcoming",
                title="Важные события",
                description=f"В ближайшие 24 часа: {len(upcoming_important)} важных событий",
                events=upcoming_important,
                recommendations=[
                    "Подготовить материалы",
                    "Проверить подключение",
                    "Установить напоминания",
                ],
                priority="high",
            ))
        
        return insights
    
    def _detect_conflicts(self, events: List[CalendarEvent]) -> List[CalendarEvent]:
        """Обнаружение пересекающихся событий."""
        conflicts = []
        
        for i, event1 in enumerate(events):
            for event2 in events[i+1:]:
                if self._events_overlap(event1, event2):
                    if event1 not in conflicts:
                        conflicts.append(event1)
                    if event2 not in conflicts:
                        conflicts.append(event2)
        
        return conflicts
    
    def _events_overlap(self, event1: CalendarEvent, event2: CalendarEvent) -> bool:
        """Проверка пересечения событий."""
        if event1.all_day or event2.all_day:
            return False
        
        start1, end1 = event1.start_time, event1.end_time or event1.start_time + timedelta(hours=1)
        start2, end2 = event2.start_time, event2.end_time or event2.start_time + timedelta(hours=1)
        
        return start1 < end2 and start2 < end1
    
    def _analyze_workload(
        self,
        events: List[CalendarEvent],
        days: int,
    ) -> Dict[str, Any]:
        """Анализ загрузки."""
        # Группировка по дням
        daily_hours: Dict[str, float] = {}
        
        for event in events:
            if event.all_day:
                continue
            
            date_key = event.start_time.strftime('%Y-%m-%d')
            duration = (event.end_time or event.start_time + timedelta(hours=1)) - event.start_time
            hours = duration.total_seconds() / 3600
            
            daily_hours[date_key] = daily_hours.get(date_key, 0) + hours
        
        # Определение перегруженных дней (> 8 часов)
        overloaded = [date for date, hours in daily_hours.items() if hours > 8]
        
        return {
            'daily_hours': daily_hours,
            'overloaded_days': overloaded,
            'average_hours': sum(daily_hours.values()) / days if days > 0 else 0,
        }
    
    def _find_free_slots(
        self,
        events: List[CalendarEvent],
        start_date: datetime,
        end_date: datetime,
        min_duration_minutes: int = 30,
    ) -> List[Dict[str, Any]]:
        """Поиск свободных слотов."""
        # Рабочие часы
        work_start = 9
        work_end = 18
        
        free_slots = []
        current = start_date.replace(hour=work_start, minute=0, second=0)
        
        while current < end_date:
            # Пропуск выходных
            if current.weekday() >= 5:
                current += timedelta(days=1)
                continue
            
            # Проверка каждого часа
            hour_end = current + timedelta(hours=1)
            
            is_free = True
            for event in events:
                if self._events_overlap(
                    CalendarEvent(id='', title='', start_time=current, end_time=hour_end),
                    event
                ):
                    is_free = False
                    break
            
            if is_free:
                free_slots.append({
                    'start': current,
                    'end': hour_end,
                    'duration_minutes': 60,
                })
            
            current += timedelta(hours=1)
        
        return free_slots
    
    def _find_important_events(
        self,
        events: List[CalendarEvent],
        hours: int = 24,
    ) -> List[CalendarEvent]:
        """Поиск важных событий в ближайшее время."""
        now = datetime.now()
        threshold = now + timedelta(hours=hours)
        
        important = []
        
        for event in events:
            # Проверка времени
            if event.start_time < now or event.start_time > threshold:
                continue
            
            # Проверка важности
            if event.event_type in [EventType.MEETING, EventType.APPOINTMENT]:
                important.append(event)
            elif len(event.attendees) > 2:
                important.append(event)
        
        return important
    
    async def get_upcoming_events(
        self,
        user_id: int,
        hours: int = 24,
    ) -> List[CalendarEvent]:
        """Получение предстоящих событий."""
        start = datetime.now()
        end = start + timedelta(hours=hours)
        
        events = await self.fetch_events(user_id, start, end)
        
        return [e for e in events if e.start_time >= start]
    
    async def get_today_summary(self, user_id: int) -> Dict[str, Any]:
        """Получение сводки на сегодня."""
        now = datetime.now()
        start = now.replace(hour=0, minute=0, second=0)
        end = start + timedelta(days=1)
        
        events = await self.fetch_events(user_id, start, end)
        
        return {
            'date': now.strftime('%Y-%m-%d'),
            'total_events': len(events),
            'meetings': len([e for e in events if e.event_type == EventType.MEETING]),
            'first_event': events[0].start_time.strftime('%H:%M') if events else None,
            'last_event': events[-1].end_time.strftime('%H:%M') if events else None,
            'events': [
                {
                    'time': e.start_time.strftime('%H:%M'),
                    'title': e.title,
                    'location': e.location,
                }
                for e in events
            ],
        }
    
    def _generate_event_id(self) -> str:
        """Генерация ID события."""
        import uuid
        return f"evt_{uuid.uuid4().hex[:12]}"
    
    async def start_sync(self, user_ids: List[int], interval_minutes: int = 15):
        """Запуск периодической синхронизации."""
        if self.is_syncing:
            logger.warning("Синхронизация уже запущена")
            return
        
        self.is_syncing = True
        self._sync_task = asyncio.create_task(
            self._sync_loop(user_ids, interval_minutes)
        )
        
        logger.info("Запущена синхронизация календарей")
    
    async def stop_sync(self):
        """Остановка синхронизации."""
        self.is_syncing = False
        
        if self._sync_task:
            self._sync_task.cancel()
            self._sync_task = None
        
        logger.info("Синхронизация календарей остановлена")
    
    async def _sync_loop(self, user_ids: List[int], interval_minutes: int):
        """Цикл синхронизации."""
        while self.is_syncing:
            try:
                for user_id in user_ids:
                    # Инвалидация кэша
                    self._events_cache.pop(user_id, None)
                    
                    # Загрузка свежих данных
                    await self.fetch_events(user_id)
                
                await asyncio.sleep(interval_minutes * 60)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка синхронизации: {e}")
                await asyncio.sleep(60)


# Глобальный экземпляр
_calendar_integration: Optional[CalendarIntegration] = None


def get_calendar_integration() -> CalendarIntegration:
    """Получение или создание интеграции."""
    global _calendar_integration
    
    if _calendar_integration is None:
        _calendar_integration = CalendarIntegration()
    
    return _calendar_integration
