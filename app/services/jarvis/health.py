"""
Health Monitor и Wellness Jarvis - мониторинг здоровья и wellness-напоминания.
Отслеживает показатели здоровья, напоминает о перерывах, воде, упражнениях.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger("jarvis.health")


class HealthMetric(Enum):
    """Метрики здоровья."""
    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    TEMPERATURE = "temperature"
    SLEEP_QUALITY = "sleep_quality"
    STEPS = "steps"
    CALORIES = "calories"
    WATER_INTAKE = "water_intake"
    STRESS_LEVEL = "stress_level"
    SPO2 = "spo2"  # Кислород в крови


class HealthStatus(Enum):
    """Статус здоровья."""
    EXCELLENT = "excellent"
    GOOD = "good"
    NORMAL = "normal"
    ATTENTION = "attention"
    WARNING = "warning"
    CRITICAL = "critical"


class WellnessAction(Enum):
    """Действия wellness."""
    BREAK_REMINDER = "break_reminder"
    WATER_REMINDER = "water_reminder"
    EXERCISE_REMINDER = "exercise_reminder"
    SLEEP_REMINDER = "sleep_reminder"
    MEDICINE_REMINDER = "medicine_reminder"
    MEDITATION_SUGGESTION = "meditation_suggestion"
    POSTURE_CHECK = "posture_check"
    EYE_REST = "eye_rest"


@dataclass
class HealthData:
    """Данные о здоровье."""
    user_id: int
    timestamp: datetime
    
    # Показатели
    heart_rate: Optional[int] = None
    blood_pressure_systolic: Optional[int] = None
    blood_pressure_diastolic: Optional[int] = None
    temperature: Optional[float] = None
    spo2: Optional[int] = None
    steps: Optional[int] = None
    calories: Optional[int] = None
    water_glasses: Optional[int] = None
    sleep_hours: Optional[float] = None
    stress_level: Optional[int] = None  # 1-10
    
    # Дополнительные данные
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class HealthAlert:
    """Предупреждение о здоровье."""
    metric: HealthMetric
    status: HealthStatus
    message: str
    value: Any
    threshold: Any
    recommendations: List[str]
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WellnessReminder:
    """Напоминание wellness."""
    action: WellnessAction
    message: str
    scheduled_time: datetime
    repeat_interval: Optional[timedelta] = None
    last_triggered: Optional[datetime] = None
    enabled: bool = True


class HealthMonitor:
    """
    Мониторинг здоровья пользователя.
    
    Функции:
    - Сбор данных от носимых устройств (Apple Health, Google Fit, Fitbit)
    - Анализ показателей здоровья
    - Обнаружение аномалий
    - Предупреждения о проблемах
    - Рекомендации по улучшению
    """
    
    # Нормальные диапазоны показателей
    NORMAL_RANGES = {
        HealthMetric.HEART_RATE: {'min': 60, 'max': 100},
        HealthMetric.BLOOD_PRESSURE: {'systolic_min': 90, 'systolic_max': 140, 'diastolic_min': 60, 'diastolic_max': 90},
        HealthMetric.TEMPERATURE: {'min': 36.0, 'max': 37.5},
        HealthMetric.SPO2: {'min': 95, 'max': 100},
        HealthMetric.STEPS: {'min_daily': 5000, 'optimal': 10000},
        HealthMetric.WATER_INTAKE: {'min_daily': 6, 'optimal': 8},  # стаканов
        HealthMetric.SLEEP_QUALITY: {'min_hours': 6, 'optimal': 8},
        HealthMetric.STRESS_LEVEL: {'min': 1, 'max': 5},
    }
    
    def __init__(self, db=None):
        """Инициализация монитора."""
        self.db = db
        
        # Кэш данных
        self._health_cache: Dict[int, HealthData] = {}
        
        # История показателей
        self._metrics_history: Dict[int, List[HealthData]] = {}
        
        # Подключенные провайдеры
        self._connected_providers: Dict[int, List[str]] = {}
    
    async def connect_provider(
        self,
        user_id: int,
        provider: str,
        credentials: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Подключение провайдера здоровья.
        
        Args:
            user_id: ID пользователя
            provider: Провайдер (google_fit, apple_health, fitbit, garmin)
            credentials: Учетные данные
            
        Returns:
            True если успешно
        """
        try:
            if user_id not in self._connected_providers:
                self._connected_providers[user_id] = []
            
            self._connected_providers[user_id].append(provider)
            
            logger.info(f"Подключен провайдер {provider} для пользователя {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка подключения провайдера {provider}: {e}")
            return False
    
    async def fetch_health_data(
        self,
        user_id: int,
        provider: Optional[str] = None,
    ) -> HealthData:
        """
        Получение данных о здоровье.
        
        Args:
            user_id: ID пользователя
            provider: Конкретный провайдер
            
        Returns:
            Данные о здоровье
        """
        # Проверка кэша
        if user_id in self._health_cache:
            cached = self._health_cache[user_id]
            if datetime.now() - cached.timestamp < timedelta(minutes=5):
                return cached
        
        # Получение данных от провайдеров
        data = HealthData(user_id=user_id, timestamp=datetime.now())
        
        providers = self._connected_providers.get(user_id, [])
        
        if 'google_fit' in providers:
            google_data = await self._fetch_google_fit(user_id)
            data = self._merge_health_data(data, google_data)
        
        if 'apple_health' in providers:
            apple_data = await self._fetch_apple_health(user_id)
            data = self._merge_health_data(data, apple_data)
        
        if 'fitbit' in providers:
            fitbit_data = await self._fetch_fitbit(user_id)
            data = self._merge_health_data(data, fitbit_data)
        
        # Кэширование
        self._health_cache[user_id] = data
        
        # Добавление в историю
        if user_id not in self._metrics_history:
            self._metrics_history[user_id] = []
        self._metrics_history[user_id].append(data)
        
        # Ограничение истории
        if len(self._metrics_history[user_id]) > 100:
            self._metrics_history[user_id] = self._metrics_history[user_id][-100:]
        
        return data
    
    async def _fetch_google_fit(self, user_id: int) -> Optional[HealthData]:
        """Получение данных из Google Fit."""
        # TODO: Реальная интеграция с Google Fit API
        return None
    
    async def _fetch_apple_health(self, user_id: int) -> Optional[HealthData]:
        """Получение данных из Apple Health."""
        # TODO: Реальная интеграция с Apple HealthKit
        return None
    
    async def _fetch_fitbit(self, user_id: int) -> Optional[HealthData]:
        """Получение данных из Fitbit."""
        # TODO: Реальная интеграция с Fitbit API
        return None
    
    def _merge_health_data(
        self,
        base: HealthData,
        new: Optional[HealthData],
    ) -> HealthData:
        """Объединение данных здоровья."""
        if not new:
            return base
        
        # Обновление только если есть данные
        if new.heart_rate:
            base.heart_rate = new.heart_rate
        if new.blood_pressure_systolic:
            base.blood_pressure_systolic = new.blood_pressure_systolic
        if new.blood_pressure_diastolic:
            base.blood_pressure_diastolic = new.blood_pressure_diastolic
        if new.temperature:
            base.temperature = new.temperature
        if new.steps:
            base.steps = new.steps
        if new.water_glasses:
            base.water_glasses = new.water_glasses
        
        return base
    
    async def analyze_health(
        self,
        user_id: int,
    ) -> List[HealthAlert]:
        """
        Анализ показателей здоровья.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список предупреждений
        """
        data = await self.fetch_health_data(user_id)
        alerts = []
        
        # Проверка пульса
        if data.heart_rate:
            alert = self._check_heart_rate(data.heart_rate)
            if alert:
                alerts.append(alert)
        
        # Проверка давления
        if data.blood_pressure_systolic and data.blood_pressure_diastolic:
            alert = self._check_blood_pressure(
                data.blood_pressure_systolic,
                data.blood_pressure_diastolic,
            )
            if alert:
                alerts.append(alert)
        
        # Проверка температуры
        if data.temperature:
            alert = self._check_temperature(data.temperature)
            if alert:
                alerts.append(alert)
        
        # Проверка SpO2
        if data.spo2:
            alert = self._check_spo2(data.spo2)
            if alert:
                alerts.append(alert)
        
        # Проверка шагов
        if data.steps is not None:
            alert = self._check_steps(data.steps)
            if alert:
                alerts.append(alert)
        
        # Проверка воды
        if data.water_glasses is not None:
            alert = self._check_water(data.water_glasses)
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def _check_heart_rate(self, heart_rate: int) -> Optional[HealthAlert]:
        """Проверка пульса."""
        range_config = self.NORMAL_RANGES[HealthMetric.HEART_RATE]
        
        if heart_rate < range_config['min']:
            return HealthAlert(
                metric=HealthMetric.HEART_RATE,
                status=HealthStatus.WARNING,
                message=f"Пульс ниже нормы: {heart_rate} уд/мин",
                value=heart_rate,
                threshold=range_config['min'],
                recommendations=[
                    "Проверьте самочувствие",
                    "Измерьте давление",
                    "При ухудшении обратитесь к врачу",
                ],
            )
        elif heart_rate > range_config['max']:
            return HealthAlert(
                metric=HealthMetric.HEART_RATE,
                status=HealthStatus.WARNING,
                message=f"Пульс выше нормы: {heart_rate} уд/мин",
                value=heart_rate,
                threshold=range_config['max'],
                recommendations=[
                    "Сядьте и отдохните",
                    "Глубоко дышите",
                    "Избегайте физической нагрузки",
                ],
            )
        
        return None
    
    def _check_blood_pressure(
        self,
        systolic: int,
        diastolic: int,
    ) -> Optional[HealthAlert]:
        """Проверка давления."""
        range_config = self.NORMAL_RANGES[HealthMetric.BLOOD_PRESSURE]
        
        if systolic > range_config['systolic_max'] or diastolic > range_config['diastolic_max']:
            status = HealthStatus.WARNING if systolic < 160 else HealthStatus.CRITICAL
            
            return HealthAlert(
                metric=HealthMetric.BLOOD_PRESSURE,
                status=status,
                message=f"Давление повышено: {systolic}/{diastolic} мм рт.ст.",
                value=(systolic, diastolic),
                threshold=(range_config['systolic_max'], range_config['diastolic_max']),
                recommendations=[
                    "Примите назначенные лекарства",
                    "Избегайте стресса",
                    "Отдохните 15-20 минут",
                    "При высоких значениях вызовите врача",
                ],
            )
        elif systolic < range_config['systolic_min']:
            return HealthAlert(
                metric=HealthMetric.BLOOD_PRESSURE,
                status=HealthStatus.ATTENTION,
                message=f"Давление понижено: {systolic}/{diastolic} мм рт.ст.",
                value=(systolic, diastolic),
                threshold=(range_config['systolic_min'], range_config['diastolic_min']),
                recommendations=[
                    "Выпейте воды",
                    "Примите горизонтальное положение",
                    "Избегайте резких движений",
                ],
            )
        
        return None
    
    def _check_temperature(self, temperature: float) -> Optional[HealthAlert]:
        """Проверка температуры."""
        range_config = self.NORMAL_RANGES[HealthMetric.TEMPERATURE]
        
        if temperature > range_config['max']:
            status = HealthStatus.WARNING if temperature < 38 else HealthStatus.CRITICAL
            
            return HealthAlert(
                metric=HealthMetric.TEMPERATURE,
                status=status,
                message=f"Температура повышена: {temperature}°C",
                value=temperature,
                threshold=range_config['max'],
                recommendations=[
                    "Измерьте температуру повторно",
                    "Пейте больше жидкости",
                    "Примите жаропонижающее",
                    "При температуре выше 38.5 обратитесь к врачу",
                ],
            )
        
        return None
    
    def _check_spo2(self, spo2: int) -> Optional[HealthAlert]:
        """Проверка уровня кислорода."""
        range_config = self.NORMAL_RANGES[HealthMetric.SPO2]
        
        if spo2 < range_config['min']:
            status = HealthStatus.WARNING if spo2 >= 90 else HealthStatus.CRITICAL
            
            return HealthAlert(
                metric=HealthMetric.SPO2,
                status=status,
                message=f"Уровень кислорода ниже нормы: {spo2}%",
                value=spo2,
                threshold=range_config['min'],
                recommendations=[
                    "Откройте окно для свежего воздуха",
                    "Сделайте глубокие вдохи",
                    "При низких значениях обратитесь к врачу",
                ],
            )
        
        return None
    
    def _check_steps(self, steps: int) -> Optional[HealthAlert]:
        """Проверка активности (шаги)."""
        range_config = self.NORMAL_RANGES[HealthMetric.STEPS]
        
        if steps < range_config['min_daily']:
            return HealthAlert(
                metric=HealthMetric.STEPS,
                status=HealthStatus.ATTENTION,
                message=f"Низкая активность сегодня: {steps} шагов",
                value=steps,
                threshold=range_config['min_daily'],
                recommendations=[
                    "Прогуляйтесь 15-20 минут",
                    "Сделайте разминку",
                    "Паркуйтесь дальше от входа",
                ],
            )
        
        return None
    
    def _check_water(self, glasses: int) -> Optional[HealthAlert]:
        """Проверка потребления воды."""
        range_config = self.NORMAL_RANGES[HealthMetric.WATER_INTAKE]
        
        current_hour = datetime.now().hour
        expected_glasses = min(glasses, current_hour // 2 + 1)  # Примерно стакан каждые 2 часа
        
        if glasses < expected_glasses:
            return HealthAlert(
                metric=HealthMetric.WATER_INTAKE,
                status=HealthStatus.ATTENTION,
                message=f"Выпито мало воды сегодня: {glasses} стаканов",
                value=glasses,
                threshold=expected_glasses,
                recommendations=[
                    "Выпейте стакан воды",
                    "Держите воду рядом",
                    "Установите напоминания",
                ],
            )
        
        return None
    
    async def get_health_summary(self, user_id: int) -> Dict[str, Any]:
        """Получение сводки здоровья."""
        data = await self.fetch_health_data(user_id)
        alerts = await self.analyze_health(user_id)
        
        # Определение общего статуса
        if any(a.status == HealthStatus.CRITICAL for a in alerts):
            overall_status = HealthStatus.CRITICAL
        elif any(a.status == HealthStatus.WARNING for a in alerts):
            overall_status = HealthStatus.WARNING
        elif any(a.status == HealthStatus.ATTENTION for a in alerts):
            overall_status = HealthStatus.ATTENTION
        else:
            overall_status = HealthStatus.GOOD
        
        return {
            'status': overall_status.value,
            'timestamp': data.timestamp.isoformat(),
            'metrics': {
                'heart_rate': data.heart_rate,
                'blood_pressure': f"{data.blood_pressure_systolic}/{data.blood_pressure_diastolic}" if data.blood_pressure_systolic else None,
                'temperature': data.temperature,
                'spo2': data.spo2,
                'steps': data.steps,
                'water_glasses': data.water_glasses,
            },
            'alerts': [
                {
                    'metric': a.metric.value,
                    'status': a.status.value,
                    'message': a.message,
                    'recommendations': a.recommendations,
                }
                for a in alerts
            ],
        }


class WellnessJarvis:
    """
    Wellness-напоминания от JARVIS.
    
    Функции:
    - Напоминания о перерывах
    - Напоминания о воде
    - Напоминания о разминке
    - Напоминания о лекарствах
    - Предложения медитации
    - Проверка осанки
    """
    
    # Интервалы напоминаний по умолчанию
    DEFAULT_INTERVALS = {
        WellnessAction.BREAK_REMINDER: timedelta(minutes=45),
        WellnessAction.WATER_REMINDER: timedelta(hours=2),
        WellnessAction.EXERCISE_REMINDER: timedelta(hours=3),
        WellnessAction.POSTURE_CHECK: timedelta(minutes=30),
        WellnessAction.EYE_REST: timedelta(minutes=20),
    }
    
    # Сообщения напоминаний
    REMINDER_MESSAGES = {
        WellnessAction.BREAK_REMINDER: [
            "Сэр, вы работаете уже {duration}. Рекомендую сделать короткий перерыв.",
            "Сэр, время для перерыва. 5-10 минут отдыха повысят продуктивность.",
            "Сэр, сделайте паузу. Разомните шею и спину.",
        ],
        WellnessAction.WATER_REMINDER: [
            "Сэр, напоминаю выпить воды. Гидратация важна для концентрации.",
            "Сэр, время для стакана воды. Это улучшит работу мозга.",
            "Сэр, не забудьте попить. Обезвоживание снижает продуктивность.",
        ],
        WellnessAction.EXERCISE_REMINDER: [
            "Сэр, время для небольшой разминки. Несколько упражнений взбодрят.",
            "Сэр, рекомендую встать и размяться. Долгое сидение вредно.",
            "Сэр, сделайте несколько приседаний или растяжку.",
        ],
        WellnessAction.MEDICINE_REMINDER: [
            "Сэр, пора принять лекарство.",
            "Сэр, напоминание о приеме препаратов.",
        ],
        WellnessAction.POSTURE_CHECK: [
            "Сэр, проверьте осанку. Выпрямите спину.",
            "Сэр, следите за положением тела. Спина должна быть прямой.",
        ],
        WellnessAction.EYE_REST: [
            "Сэр, дайте глазам отдых. Посмотрите вдаль на 20 секунд.",
            "Сэр, правило 20-20-20: каждые 20 минут смотрите на 20 футов вдаль 20 секунд.",
        ],
        WellnessAction.SLEEP_REMINDER: [
            "Сэр, уже поздно. Рекомендую подготовиться ко сну.",
            "Сэр, время отдыха. Хороший сон важен для продуктивности.",
        ],
        WellnessAction.MEDITATION_SUGGESTION: [
            "Сэр, предлагаю 5 минут медитации для снятия стресса.",
            "Сэр, короткая медитация поможет восстановить концентрацию.",
        ],
    }
    
    def __init__(self, health_monitor: Optional[HealthMonitor] = None):
        """Инициализация wellness-системы."""
        self.health_monitor = health_monitor
        
        # Активные напоминания
        self._reminders: Dict[int, List[WellnessReminder]] = {}
        
        # История срабатываний
        self._trigger_history: Dict[int, Dict[WellnessAction, datetime]] = {}
        
        # Задача мониторинга
        self._monitor_task: Optional[asyncio.Task] = None
        self.is_monitoring = False
        
        # Время начала работы
        self._work_start_time: Dict[int, datetime] = {}
    
    def set_reminder(
        self,
        user_id: int,
        action: WellnessAction,
        interval: Optional[timedelta] = None,
        enabled: bool = True,
    ):
        """
        Настройка напоминания.
        
        Args:
            user_id: ID пользователя
            action: Тип напоминания
            interval: Интервал (по умолчанию стандартный)
            enabled: Включено ли
        """
        if user_id not in self._reminders:
            self._reminders[user_id] = []
        
        interval = interval or self.DEFAULT_INTERVALS.get(action, timedelta(hours=1))
        
        reminder = WellnessReminder(
            action=action,
            message="",  # Будет сгенерировано
            scheduled_time=datetime.now() + interval,
            repeat_interval=interval,
            enabled=enabled,
        )
        
        # Удаление старого напоминания того же типа
        self._reminders[user_id] = [
            r for r in self._reminders[user_id] if r.action != action
        ]
        
        self._reminders[user_id].append(reminder)
        
        logger.info(f"Установлено напоминание {action.value} для пользователя {user_id}")
    
    async def check_reminders(self, user_id: int) -> List[WellnessReminder]:
        """
        Проверка напоминаний для пользователя.
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Список сработавших напоминаний
        """
        now = datetime.now()
        triggered = []
        
        reminders = self._reminders.get(user_id, [])
        
        for reminder in reminders:
            if not reminder.enabled:
                continue
            
            # Проверка времени
            if now >= reminder.scheduled_time:
                # Проверка кулдауна
                if self._is_on_cooldown(user_id, reminder.action):
                    continue
                
                # Генерация сообщения
                reminder.message = self._generate_message(reminder, user_id)
                
                triggered.append(reminder)
                
                # Обновление времени следующего срабатывания
                if reminder.repeat_interval:
                    reminder.scheduled_time = now + reminder.repeat_interval
                    reminder.last_triggered = now
                
                # Запись в историю
                if user_id not in self._trigger_history:
                    self._trigger_history[user_id] = {}
                self._trigger_history[user_id][reminder.action] = now
        
        return triggered
    
    def _is_on_cooldown(self, user_id: int, action: WellnessAction) -> bool:
        """Проверка кулдауна."""
        if user_id not in self._trigger_history:
            return False
        
        last_trigger = self._trigger_history[user_id].get(action)
        if not last_trigger:
            return False
        
        cooldown = self.DEFAULT_INTERVALS.get(action, timedelta(hours=1)) * 0.5
        return datetime.now() - last_trigger < cooldown
    
    def _generate_message(
        self,
        reminder: WellnessReminder,
        user_id: int,
    ) -> str:
        """Генерация сообщения напоминания."""
        import random
        
        messages = self.REMINDER_MESSAGES.get(reminder.action, ["Сэр, напоминание."])
        message = random.choice(messages)
        
        # Подстановка длительности работы
        if '{duration}' in message:
            work_start = self._work_start_time.get(user_id)
            if work_start:
                duration = datetime.now() - work_start
                hours = duration.seconds // 3600
                minutes = (duration.seconds % 3600) // 60
                
                if hours > 0:
                    duration_str = f"{hours} час {minutes} минут"
                else:
                    duration_str = f"{minutes} минут"
                
                message = message.format(duration=duration_str)
        
        return message
    
    def start_work_session(self, user_id: int):
        """Начало рабочей сессии."""
        self._work_start_time[user_id] = datetime.now()
        
        # Установка стандартных напоминаний
        self.set_reminder(user_id, WellnessAction.BREAK_REMINDER)
        self.set_reminder(user_id, WellnessAction.WATER_REMINDER)
        self.set_reminder(user_id, WellnessAction.POSTURE_CHECK)
        
        logger.info(f"Начата рабочая сессия для пользователя {user_id}")
    
    def end_work_session(self, user_id: int):
        """Конец рабочей сессии."""
        self._work_start_time.pop(user_id, None)
        
        # Отключение напоминаний
        if user_id in self._reminders:
            for reminder in self._reminders[user_id]:
                reminder.enabled = False
        
        logger.info(f"Завершена рабочая сессия для пользователя {user_id}")
    
    async def start_monitoring(self, user_ids: List[int] = None):
        """Запуск мониторинга."""
        if self.is_monitoring:
            logger.warning("Мониторинг уже запущен")
            return
        
        self.is_monitoring = True
        self._monitor_task = asyncio.create_task(
            self._monitor_loop(user_ids or [])
        )
        
        logger.info("Запущен wellness-мониторинг")
    
    async def stop_monitoring(self):
        """Остановка мониторинга."""
        self.is_monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            self._monitor_task = None
        
        logger.info("Wellness-мониторинг остановлен")
    
    async def _monitor_loop(self, user_ids: List[int]):
        """Цикл мониторинга."""
        while self.is_monitoring:
            try:
                for user_id in user_ids:
                    triggered = await self.check_reminders(user_id)
                    
                    for reminder in triggered:
                        # TODO: Отправка уведомления через JarvisNotifications
                        logger.info(f"Напоминание для {user_id}: {reminder.message}")
                
                await asyncio.sleep(60)  # Проверка каждую минуту
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Ошибка в wellness-мониторинге: {e}")
                await asyncio.sleep(60)


# Глобальные экземпляры
_health_monitor: Optional[HealthMonitor] = None
_wellness_jarvis: Optional[WellnessJarvis] = None


def get_health_monitor() -> HealthMonitor:
    """Получение монитора здоровья."""
    global _health_monitor
    
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    
    return _health_monitor


def get_wellness_jarvis() -> WellnessJarvis:
    """Получение wellness-системы."""
    global _wellness_jarvis
    
    if _wellness_jarvis is None:
        _wellness_jarvis = WellnessJarvis(get_health_monitor())
    
    return _wellness_jarvis
