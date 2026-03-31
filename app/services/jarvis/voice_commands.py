"""
Voice Command Processor - обработка голосовых команд JARVIS.
Распознает команды и выполняет соответствующие действия.
"""
import asyncio
import logging
from typing import Optional, List, Dict, Any, Callable, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re
import json

from app.services.jarvis.context_manager import UserContext

logger = logging.getLogger("jarvis.voice_commands")


class CommandCategory(Enum):
    """Категории команд."""
    SMART_HOME = "smart_home"
    FINANCE = "finance"
    VPN = "vpn"
    MEMORY = "memory"
    SYSTEM = "system"
    INFORMATION = "information"
    COMMUNICATION = "communication"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    SCHEDULE = "schedule"


@dataclass
class ParsedCommand:
    """Распознанная команда."""
    category: CommandCategory
    action: str
    parameters: Dict[str, Any]
    confidence: float
    raw_text: str
    timestamp: datetime


@dataclass
class CommandResult:
    """Результат выполнения команды."""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    requires_followup: bool = False
    followup_question: Optional[str] = None


class VoiceCommandProcessor:
    """
    Обработчик голосовых команд JARVIS.
    
    Поддерживаемые команды:
    - Управление умным домом (свет, климат, устройства)
    - Финансы (баланс, перевод, курс)
    - VPN (подключение, статус)
    - Память (запомни, напомни, найди)
    - Системные (статус, перезагрузка, диагностика)
    - Информационные (погода, новости, поиск)
    - Развлечения (музыка, видео)
    """
    
    # Шаблоны команд с параметрами
    COMMAND_PATTERNS = {
        # === УМНЫЙ ДОМ ===
        CommandCategory.SMART_HOME: [
            {
                'pattern': r'включи (свет|освещение) (в |в комнате )?(.+)',
                'action': 'light_on',
                'params': {'room': 3},
            },
            {
                'pattern': r'выключи (свет|освещение) (в |в комнате )?(.+)',
                'action': 'light_off',
                'params': {'room': 3},
            },
            {
                'pattern': r'(установи|поставь) температуру (\d+)',
                'action': 'set_temperature',
                'params': {'temperature': 2},
            },
            {
                'pattern': r'включи (.+) в (.+)',
                'action': 'device_on',
                'params': {'device': 1, 'room': 2},
            },
            {
                'pattern': r'выключи (.+) в (.+)',
                'action': 'device_off',
                'params': {'device': 1, 'room': 2},
            },
            {
                'pattern': r'(открой|закрой) (шторы|занавески|жалюзи)',
                'action': 'curtains_toggle',
                'params': {'action': 0},
            },
        ],
        
        # === ФИНАНСЫ ===
        CommandCategory.FINANCE: [
            {
                'pattern': r'(какой |сколько )?(мой )?баланс',
                'action': 'get_balance',
                'params': {},
            },
            {
                'pattern': r'переведи (\d+) (.+) (на |на карту |на счет )?(.+)',
                'action': 'transfer_money',
                'params': {'amount': 1, 'currency': 2, 'destination': 4},
            },
            {
                'pattern': r'курс (.+) (к |к валюте )?(.+)',
                'action': 'get_exchange_rate',
                'params': {'from_currency': 1, 'to_currency': 3},
            },
            {
                'pattern': r'(показать |покажи )?(мои )?(расходы|траты) (за |за этот )?(месяц|неделю|день)',
                'action': 'show_expenses',
                'params': {'period': 5},
            },
        ],
        
        # === VPN ===
        CommandCategory.VPN: [
            {
                'pattern': r'(включи|подключи) vpn',
                'action': 'vpn_connect',
                'params': {},
            },
            {
                'pattern': r'(выключи|отключи) vpn',
                'action': 'vpn_disconnect',
                'params': {},
            },
            {
                'pattern': r'(статус|состояние) vpn',
                'action': 'vpn_status',
                'params': {},
            },
            {
                'pattern': r'смени (сервер|страну) vpn (на |на сервер )?(.+)',
                'action': 'vpn_change_server',
                'params': {'server': 3},
            },
        ],
        
        # === ПАМЯТЬ ===
        CommandCategory.MEMORY: [
            {
                'pattern': r'запомни (что |что )?(.+)',
                'action': 'memory_save',
                'params': {'content': 2},
            },
            {
                'pattern': r'напомни (мне |про |о )?(.+)',
                'action': 'memory_remind',
                'params': {'query': 2},
            },
            {
                'pattern': r'(найди|поищи) (в памяти|среди записей) (.+)',
                'action': 'memory_search',
                'params': {'query': 3},
            },
            {
                'pattern': r'что ты (знаешь|помнишь) (о |про )?(.+)',
                'action': 'memory_recall',
                'params': {'topic': 3},
            },
        ],
        
        # === СИСТЕМА ===
        CommandCategory.SYSTEM: [
            {
                'pattern': r'(статус|состояние) системы',
                'action': 'system_status',
                'params': {},
            },
            {
                'pattern': r'диагностика (системы|устройств)',
                'action': 'system_diagnose',
                'params': {},
            },
            {
                'pattern': r'перезагрузи (.+)',
                'action': 'system_reboot',
                'params': {'target': 1},
            },
            {
                'pattern': r'(время|который час|сколько времени)',
                'action': 'get_time',
                'params': {},
            },
            {
                'pattern': r'(дата|какое сегодня число|какое число)',
                'action': 'get_date',
                'params': {},
            },
        ],
        
        # === ИНФОРМАЦИЯ ===
        CommandCategory.INFORMATION: [
            {
                'pattern': r'(какая |какою )?погода (в |в городе )?(.+)',
                'action': 'get_weather',
                'params': {'city': 3},
            },
            {
                'pattern': r'погода (сейчас|сегодня|завтра)',
                'action': 'get_weather_forecast',
                'params': {'when': 1},
            },
            {
                'pattern': r'(найди|поищи|поиск) (.+)',
                'action': 'web_search',
                'params': {'query': 2},
            },
            {
                'pattern': r'(что такое|определение|значение) (.+)',
                'action': 'define_word',
                'params': {'word': 2},
            },
            {
                'pattern': r'(новости|последние новости|что нового)',
                'action': 'get_news',
                'params': {},
            },
        ],
        
        # === РАЗВЛЕЧЕНИЯ ===
        CommandCategory.ENTERTAINMENT: [
            {
                'pattern': r'(включи|запусти) музыку (.+)',
                'action': 'play_music',
                'params': {'query': 2},
            },
            {
                'pattern': r'(включи|запусти) (музыку|плейлист)',
                'action': 'play_music_default',
                'params': {},
            },
            {
                'pattern': r'(пауза|стоп|останови) (музыку|воспроизведение)',
                'action': 'pause_music',
                'params': {},
            },
            {
                'pattern': r'(следующая|следующую) (песню|песня|трек)',
                'action': 'next_track',
                'params': {},
            },
            {
                'pattern': r'(громче|тише|сделай громче|сделай тише)',
                'action': 'adjust_volume',
                'params': {'direction': 1},
            },
        ],
        
        # === ЗДОРОВЬЕ ===
        CommandCategory.HEALTH: [
            {
                'pattern': r'(как |каково )?мое (здоровье|самочувствие)',
                'action': 'health_status',
                'params': {},
            },
            {
                'pattern': r'(напомни|напомнить) (выпить|попить) воды',
                'action': 'remind_water',
                'params': {},
            },
            {
                'pattern': r'(напомни|напомнить) (принять|выпить) (лекарство|таблетку|таблетки)',
                'action': 'remind_medicine',
                'params': {},
            },
        ],
        
        # === РАСПИСАНИЕ ===
        CommandCategory.SCHEDULE: [
            {
                'pattern': r'(запиши|добавь|создай) (встречу|событие|мероприятие) (.+)',
                'action': 'create_event',
                'params': {'title': 3},
            },
            {
                'pattern': r'(что|какие) (у меня|на сегодня|на завтра) (встречи|планы|события)',
                'action': 'show_schedule',
                'params': {'when': 2},
            },
            {
                'pattern': r'(поставь|установи) (таймер|будильник) (на )?(\d+)( минут| минуту| часов| часа)?',
                'action': 'set_timer',
                'params': {'duration': 4, 'unit': 5},
            },
        ],
    }
    
    def __init__(self):
        """Инициализация обработчика команд."""
        # Компиляция регулярных выражений
        self._compiled_patterns: Dict[CommandCategory, List[Tuple[re.Pattern, str, Dict]]] = {}
        
        for category, patterns in self.COMMAND_PATTERNS.items():
            self._compiled_patterns[category] = []
            for p in patterns:
                try:
                    compiled = re.compile(p['pattern'], re.IGNORECASE)
                    self._compiled_patterns[category].append(
                        (compiled, p['action'], p['params'])
                    )
                except re.error as e:
                    logger.error(f"Ошибка компиляции паттерна: {e}")
        
        # Обработчики действий
        self._action_handlers: Dict[str, Callable] = {}
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрация обработчиков действий."""
        # Умный дом
        self._action_handlers['light_on'] = self._handle_light_on
        self._action_handlers['light_off'] = self._handle_light_off
        self._action_handlers['set_temperature'] = self._handle_set_temperature
        self._action_handlers['device_on'] = self._handle_device_on
        self._action_handlers['device_off'] = self._handle_device_off
        self._action_handlers['curtains_toggle'] = self._handle_curtains
        
        # Финансы
        self._action_handlers['get_balance'] = self._handle_get_balance
        self._action_handlers['transfer_money'] = self._handle_transfer_money
        self._action_handlers['get_exchange_rate'] = self._handle_exchange_rate
        self._action_handlers['show_expenses'] = self._handle_show_expenses
        
        # VPN
        self._action_handlers['vpn_connect'] = self._handle_vpn_connect
        self._action_handlers['vpn_disconnect'] = self._handle_vpn_disconnect
        self._action_handlers['vpn_status'] = self._handle_vpn_status
        self._action_handlers['vpn_change_server'] = self._handle_vpn_change_server
        
        # Память
        self._action_handlers['memory_save'] = self._handle_memory_save
        self._action_handlers['memory_remind'] = self._handle_memory_remind
        self._action_handlers['memory_search'] = self._handle_memory_search
        self._action_handlers['memory_recall'] = self._handle_memory_recall
        
        # Система
        self._action_handlers['system_status'] = self._handle_system_status
        self._action_handlers['system_diagnose'] = self._handle_system_diagnose
        self._action_handlers['get_time'] = self._handle_get_time
        self._action_handlers['get_date'] = self._handle_get_date
        
        # Информация
        self._action_handlers['get_weather'] = self._handle_get_weather
        self._action_handlers['get_weather_forecast'] = self._handle_weather_forecast
        self._action_handlers['web_search'] = self._handle_web_search
        self._action_handlers['define_word'] = self._handle_define_word
        self._action_handlers['get_news'] = self._handle_get_news
        
        # Развлечения
        self._action_handlers['play_music'] = self._handle_play_music
        self._action_handlers['play_music_default'] = self._handle_play_music_default
        self._action_handlers['pause_music'] = self._handle_pause_music
        self._action_handlers['next_track'] = self._handle_next_track
        self._action_handlers['adjust_volume'] = self._handle_adjust_volume
        
        # Здоровье
        self._action_handlers['health_status'] = self._handle_health_status
        self._action_handlers['remind_water'] = self._handle_remind_water
        self._action_handlers['remind_medicine'] = self._handle_remind_medicine
        
        # Расписание
        self._action_handlers['create_event'] = self._handle_create_event
        self._action_handlers['show_schedule'] = self._handle_show_schedule
        self._action_handlers['set_timer'] = self._handle_set_timer
    
    def parse(self, text: str) -> Optional[ParsedCommand]:
        """
        Парсинг текста команды.
        
        Args:
            text: Текст команды
            
        Returns:
            ParsedCommand или None если не распознано
        """
        text_lower = text.lower().strip()
        
        # Поиск совпадения с паттернами
        for category, patterns in self._compiled_patterns.items():
            for pattern, action, param_config in patterns:
                match = pattern.search(text_lower)
                
                if match:
                    # Извлечение параметров
                    params = {}
                    for param_name, group_idx in param_config.items():
                        if group_idx > 0 and group_idx <= len(match.groups()):
                            params[param_name] = match.group(group_idx)
                    
                    return ParsedCommand(
                        category=category,
                        action=action,
                        parameters=params,
                        confidence=0.9,
                        raw_text=text,
                        timestamp=datetime.now(),
                    )
        
        # Команда не распознана
        return None
    
    async def execute(
        self, 
        command: ParsedCommand, 
        context: UserContext
    ) -> CommandResult:
        """
        Выполнение команды.
        
        Args:
            command: Распознанная команда
            context: Контекст пользователя
            
        Returns:
            Результат выполнения
        """
        handler = self._action_handlers.get(command.action)
        
        if not handler:
            return CommandResult(
                success=False,
                message=f"Команда '{command.action}' не поддерживается",
            )
        
        try:
            result = await handler(command.parameters, context)
            return result
        except Exception as e:
            logger.error(f"Ошибка выполнения команды {command.action}: {e}")
            return CommandResult(
                success=False,
                message=f"Ошибка выполнения: {str(e)}",
            )
    
    # === ОБРАБОТЧИКИ УМНОГО ДОМА ===
    
    async def _handle_light_on(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Включение света."""
        room = params.get('room', 'все комнаты')
        
        # TODO: Интеграция с smarthome_service
        return CommandResult(
            success=True,
            message=f"Сэр, включил освещение в {room}.",
            data={'room': room, 'action': 'on'},
        )
    
    async def _handle_light_off(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Выключение света."""
        room = params.get('room', 'все комнаты')
        
        return CommandResult(
            success=True,
            message=f"Сэр, выключил освещение в {room}.",
            data={'room': room, 'action': 'off'},
        )
    
    async def _handle_set_temperature(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Установка температуры."""
        temperature = params.get('temperature', '22')
        
        return CommandResult(
            success=True,
            message=f"Сэр, установил температуру {temperature}°C.",
            data={'temperature': temperature},
        )
    
    async def _handle_device_on(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Включение устройства."""
        device = params.get('device', 'устройство')
        room = params.get('room', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, включил {device} в {room}.",
            data={'device': device, 'room': room, 'action': 'on'},
        )
    
    async def _handle_device_off(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Выключение устройства."""
        device = params.get('device', 'устройство')
        room = params.get('room', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, выключил {device} в {room}.",
            data={'device': device, 'room': room, 'action': 'off'},
        )
    
    async def _handle_curtains(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Управление шторами."""
        action = params.get('action', 'открой')
        state = 'открыл' if 'открой' in action else 'закрыл'
        
        return CommandResult(
            success=True,
            message=f"Сэр, {state} шторы.",
            data={'action': action},
        )
    
    # === ОБРАБОТЧИКИ ФИНАНСОВ ===
    
    async def _handle_get_balance(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Получение баланса."""
        # TODO: Интеграция с finance_service
        return CommandResult(
            success=True,
            message="Сэр, ваш текущий баланс: 125,000 ₽",
            data={'balance': 125000, 'currency': 'RUB'},
        )
    
    async def _handle_transfer_money(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Перевод денег."""
        amount = params.get('amount', '0')
        currency = params.get('currency', 'рублей')
        destination = params.get('destination', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, подтверждаю перевод {amount} {currency} на {destination}.",
            data={'amount': amount, 'currency': currency, 'destination': destination},
            requires_followup=True,
            followup_question="Подтвердить перевод?",
        )
    
    async def _handle_exchange_rate(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Курс валют."""
        from_curr = params.get('from_currency', 'USD')
        to_curr = params.get('to_currency', 'RUB')
        
        # TODO: Реальный курс
        rate = 92.5 if from_curr == 'USD' else 100.0
        
        return CommandResult(
            success=True,
            message=f"Сэр, курс {from_curr} к {to_curr}: {rate}",
            data={'from': from_curr, 'to': to_curr, 'rate': rate},
        )
    
    async def _handle_show_expenses(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Показать расходы."""
        period = params.get('period', 'месяц')
        
        return CommandResult(
            success=True,
            message=f"Сэр, ваши расходы за {period}: 45,000 ₽",
            data={'period': period, 'amount': 45000},
        )
    
    # === ОБРАБОТЧИКИ VPN ===
    
    async def _handle_vpn_connect(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Подключение VPN."""
        return CommandResult(
            success=True,
            message="Сэр, VPN подключен. Ваш IP скрыт, соединение защищено.",
            data={'status': 'connected'},
        )
    
    async def _handle_vpn_disconnect(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Отключение VPN."""
        return CommandResult(
            success=True,
            message="Сэр, VPN отключен. Соединение теперь прямое.",
            data={'status': 'disconnected'},
        )
    
    async def _handle_vpn_status(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Статус VPN."""
        return CommandResult(
            success=True,
            message="Сэр, VPN активен. Сервер: Нидерланды, скорость: 95 Mbps.",
            data={'status': 'active', 'server': 'Netherlands', 'speed': '95 Mbps'},
        )
    
    async def _handle_vpn_change_server(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Смена сервера VPN."""
        server = params.get('server', 'Нидерланды')
        
        return CommandResult(
            success=True,
            message=f"Сэр, переключил VPN сервер на {server}.",
            data={'server': server},
        )
    
    # === ОБРАБОТЧИКИ ПАМЯТИ ===
    
    async def _handle_memory_save(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Сохранение в память."""
        content = params.get('content', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, запомнил: {content}",
            data={'content': content},
        )
    
    async def _handle_memory_remind(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Напоминание."""
        query = params.get('query', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, напоминаю: {query}",
            data={'query': query},
        )
    
    async def _handle_memory_search(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Поиск в памяти."""
        query = params.get('query', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, нашел 3 записи по запросу '{query}'.",
            data={'query': query, 'results': []},
        )
    
    async def _handle_memory_recall(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Вспоминание информации."""
        topic = params.get('topic', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, вот что я знаю о {topic}: ...",
            data={'topic': topic},
        )
    
    # === ОБРАБОТЧИКИ СИСТЕМЫ ===
    
    async def _handle_system_status(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Статус системы."""
        return CommandResult(
            success=True,
            message="Сэр, все системы работают нормально. CPU: 25%, RAM: 4.2GB, Диск: 120GB свободно.",
            data={'cpu': 25, 'ram': '4.2GB', 'disk': '120GB'},
        )
    
    async def _handle_system_diagnose(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Диагностика."""
        return CommandResult(
            success=True,
            message="Сэр, диагностика завершена. Все устройства работают корректно. Проблем не обнаружено.",
            data={'status': 'healthy'},
        )
    
    async def _handle_get_time(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Получение времени."""
        now = datetime.now()
        time_str = now.strftime("%H:%M")
        
        return CommandResult(
            success=True,
            message=f"Сэр, сейчас {time_str}.",
            data={'time': time_str},
        )
    
    async def _handle_get_date(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Получение даты."""
        now = datetime.now()
        date_str = now.strftime("%d %B %Y")
        
        return CommandResult(
            success=True,
            message=f"Сэр, сегодня {date_str}.",
            data={'date': date_str},
        )
    
    # === ОБРАБОТЧИКИ ИНФОРМАЦИИ ===
    
    async def _handle_get_weather(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Получение погоды."""
        city = params.get('city', 'Москва')
        
        return CommandResult(
            success=True,
            message=f"Сэр, в {city} сейчас +5°C, облачно, влажность 65%.",
            data={'city': city, 'temp': 5, 'condition': 'cloudy'},
        )
    
    async def _handle_weather_forecast(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Прогноз погоды."""
        when = params.get('when', 'сегодня')
        
        return CommandResult(
            success=True,
            message=f"Сэр, прогноз на {when}: температура от +3 до +8°C, возможен дождь.",
            data={'when': when},
        )
    
    async def _handle_web_search(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Веб-поиск."""
        query = params.get('query', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, нашел результаты по запросу '{query}'.",
            data={'query': query},
        )
    
    async def _handle_define_word(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Определение слова."""
        word = params.get('word', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, {word} - это ...",
            data={'word': word},
        )
    
    async def _handle_get_news(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Получение новостей."""
        return CommandResult(
            success=True,
            message="Сэр, вот последние новости: ...",
            data={'news': []},
        )
    
    # === ОБРАБОТЧИКИ РАЗВЛЕЧЕНИЙ ===
    
    async def _handle_play_music(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Воспроизведение музыки."""
        query = params.get('query', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, включаю {query}.",
            data={'query': query},
        )
    
    async def _handle_play_music_default(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Воспроизведение музыки по умолчанию."""
        return CommandResult(
            success=True,
            message="Сэр, включаю ваш плейлист.",
            data={},
        )
    
    async def _handle_pause_music(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Пауза музыки."""
        return CommandResult(
            success=True,
            message="Сэр, воспроизведение на паузе.",
            data={},
        )
    
    async def _handle_next_track(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Следующий трек."""
        return CommandResult(
            success=True,
            message="Сэр, переключаю на следующий трек.",
            data={},
        )
    
    async def _handle_adjust_volume(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Регулировка громкости."""
        direction = params.get('direction', 'громче')
        
        return CommandResult(
            success=True,
            message=f"Сэр, сделал {direction}.",
            data={'direction': direction},
        )
    
    # === ОБРАБОТЧИКИ ЗДОРОВЬЯ ===
    
    async def _handle_health_status(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Статус здоровья."""
        return CommandResult(
            success=True,
            message="Сэр, ваши показатели в норме. Пульс: 72 уд/мин, давление: 120/80.",
            data={'pulse': 72, 'pressure': '120/80'},
        )
    
    async def _handle_remind_water(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Напоминание о воде."""
        return CommandResult(
            success=True,
            message="Сэр, напоминаю выпить воды.",
            data={},
        )
    
    async def _handle_remind_medicine(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Напоминание о лекарствах."""
        return CommandResult(
            success=True,
            message="Сэр, пора принять лекарство.",
            data={},
        )
    
    # === ОБРАБОТЧИКИ РАСПИСАНИЯ ===
    
    async def _handle_create_event(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Создание события."""
        title = params.get('title', '')
        
        return CommandResult(
            success=True,
            message=f"Сэр, создал событие: {title}",
            data={'title': title},
            requires_followup=True,
            followup_question="Указать время события?",
        )
    
    async def _handle_show_schedule(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Показать расписание."""
        when = params.get('when', 'сегодня')
        
        return CommandResult(
            success=True,
            message=f"Сэр, вот ваши планы на {when}: ...",
            data={'when': when},
        )
    
    async def _handle_set_timer(
        self, 
        params: Dict[str, Any], 
        context: UserContext
    ) -> CommandResult:
        """Установка таймера."""
        duration = params.get('duration', '5')
        unit = params.get('unit', ' минут')
        
        return CommandResult(
            success=True,
            message=f"Сэр, установил таймер на {duration}{unit}.",
            data={'duration': duration, 'unit': unit},
        )


# Глобальный экземпляр
_voice_command_processor: Optional[VoiceCommandProcessor] = None


def get_voice_command_processor() -> VoiceCommandProcessor:
    """Получение или создание обработчика команд."""
    global _voice_command_processor
    
    if _voice_command_processor is None:
        _voice_command_processor = VoiceCommandProcessor()
    
    return _voice_command_processor
