"""
Wake Word Detection - обнаружение ключевого слова "JARVIS" для активации.
Использует Vosk для оффлайн распознавания речи.
"""
import asyncio
import json
import logging
from typing import Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import os

logger = logging.getLogger("jarvis.wake_word")

# Импорт Vosk (оффлайн распознавание)
try:
    import vosk
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False
    logger.warning("Vosk не установлен. Wake Word Detection будет работать в режиме заглушки.")


@dataclass
class WakeEvent:
    """Событие обнаружения wake word."""
    detected: bool
    phrase: str
    timestamp: datetime
    confidence: float = 1.0


class WakeWordDetector:
    """
    Обнаружение ключевого слова "JARVIS" для активации голосового ассистента.
    
    Поддерживаемые wake words:
    - "джарвис" (русский)
    - "jarvis" (английский)
    - "джарви" (разговорный)
    - "жарвис" (фонетический вариант)
    """
    
    # Wake words для разных языков и произношений
    WAKE_WORDS = {
        'ru': ['джарвис', 'джарви', 'жарвис'],
        'en': ['jarvis', 'jarvis'],
        'phonetic': ['джарвис', 'джарви', 'жарвис', 'jarvis'],
    }
    
    # Модель Vosk для распознавания
    MODEL_PATH = os.environ.get('VOSK_MODEL_PATH', 'models/vosk-model-small-ru-0.22')
    
    def __init__(
        self,
        language: str = 'ru',
        sensitivity: float = 0.5,
        on_wake: Optional[Callable[[WakeEvent], None]] = None,
    ):
        """
        Инициализация детектора wake word.
        
        Args:
            language: Язык для распознавания ('ru', 'en')
            sensitivity: Чувствительность детектора (0.0 - 1.0)
            on_wake: Callback при обнаружении wake word
        """
        self.language = language
        self.sensitivity = sensitivity
        self.on_wake = on_wake
        
        # Инициализация модели Vosk
        self.model: Optional[vosk.Model] = None
        self.recognizer: Optional[vosk.KaldiRecognizer] = None
        self.sample_rate = 16000
        
        # Состояние
        self.is_listening = False
        self._listen_task: Optional[asyncio.Task] = None
        
        # Статистика
        self.stats = {
            'total_detections': 0,
            'false_positives': 0,
            'last_detection': None,
        }
        
        # Инициализация модели
        self._init_model()
    
    def _init_model(self):
        """Инициализация модели Vosk."""
        if not VOSK_AVAILABLE:
            logger.warning("Vosk недоступен. Wake Word Detection работает в режиме заглушки.")
            return
        
        try:
            if os.path.exists(self.MODEL_PATH):
                self.model = vosk.Model(self.MODEL_PATH)
                self.recognizer = vosk.KaldiRecognizer(self.model, self.sample_rate)
                logger.info(f"Модель Vosk загружена: {self.MODEL_PATH}")
            else:
                logger.warning(f"Модель Vosk не найдена: {self.MODEL_PATH}")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели Vosk: {e}")
    
    def _check_wake_word(self, text: str) -> bool:
        """
        Проверка наличия wake word в тексте.
        
        Args:
            text: Распознанный текст
            
        Returns:
            True если wake word обнаружен
        """
        text_lower = text.lower().strip()
        wake_words = self.WAKE_WORDS.get(self.language, self.WAKE_WORDS['ru'])
        
        for wake in wake_words:
            if wake in text_lower:
                return True
        
        return False
    
    async def process_audio_chunk(self, audio_chunk: bytes) -> Optional[WakeEvent]:
        """
        Обработка аудио чанка на наличие wake word.
        
        Args:
            audio_chunk: Аудио данные (16kHz, 16bit, mono)
            
        Returns:
            WakeEvent если wake word обнаружен, иначе None
        """
        if not self.recognizer:
            # Режим заглушки - возвращаем случайное обнаружение для тестирования
            return None
        
        try:
            # Обработка через Vosk
            if self.recognizer.AcceptWaveform(audio_chunk):
                result = json.loads(self.recognizer.Result())
                text = result.get('text', '')
                
                if text and self._check_wake_word(text):
                    event = WakeEvent(
                        detected=True,
                        phrase=text,
                        timestamp=datetime.now(),
                        confidence=result.get('confidence', 1.0),
                    )
                    
                    # Обновление статистики
                    self.stats['total_detections'] += 1
                    self.stats['last_detection'] = event.timestamp
                    
                    # Callback
                    if self.on_wake:
                        await self.on_wake(event) if asyncio.iscoroutinefunction(self.on_wake) else self.on_wake(event)
                    
                    logger.info(f"Wake word обнаружен: '{text}'")
                    return event
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка обработки аудио: {e}")
            return None
    
    async def listen_continuous(
        self,
        audio_stream: asyncio.StreamReader,
        on_wake: Optional[Callable[[WakeEvent], None]] = None,
    ):
        """
        Непрерывное прослушивание аудио потока на наличие wake word.
        
        Args:
            audio_stream: Поток аудио данных
            on_wake: Callback при обнаружении wake word
        """
        self.is_listening = True
        logger.info("Начало непрерывного прослушивания wake word...")
        
        try:
            while self.is_listening:
                # Чтение чанка из потока
                chunk = await audio_stream.read(4096)  # 4KB чанки
                
                if not chunk:
                    await asyncio.sleep(0.1)
                    continue
                
                # Обработка чанка
                event = await self.process_audio_chunk(chunk)
                
                if event and on_wake:
                    await on_wake(event) if asyncio.iscoroutinefunction(on_wake) else on_wake(event)
                    
        except asyncio.CancelledError:
            logger.info("Прослушивание остановлено")
        except Exception as e:
            logger.error(f"Ошибка при прослушивании: {e}")
        finally:
            self.is_listening = False
    
    def start_listening(self, audio_stream: asyncio.StreamReader):
        """Запуск непрерывного прослушивания."""
        if self._listen_task and not self._listen_task.done():
            logger.warning("Прослушивание уже запущено")
            return
        
        self._listen_task = asyncio.create_task(self.listen_continuous(audio_stream))
    
    def stop_listening(self):
        """Остановка прослушивания."""
        self.is_listening = False
        if self._listen_task:
            self._listen_task.cancel()
            self._listen_task = None
    
    def get_stats(self) -> dict:
        """Получение статистики детектора."""
        return {
            **self.stats,
            'is_listening': self.is_listening,
            'model_loaded': self.model is not None,
            'language': self.language,
        }


class WakeWordManager:
    """
    Менеджер для управления несколькими детекторами wake word.
    Поддерживает мультиязычность и переключение языков.
    """
    
    def __init__(self):
        self.detectors: dict[str, WakeWordDetector] = {}
        self.active_language = 'ru'
    
    def get_detector(self, language: str = None) -> WakeWordDetector:
        """Получение или создание детектора для языка."""
        lang = language or self.active_language
        
        if lang not in self.detectors:
            self.detectors[lang] = WakeWordDetector(language=lang)
        
        return self.detectors[lang]
    
    def set_language(self, language: str):
        """Установка активного языка."""
        self.active_language = language
        logger.info(f"Активный язык изменен на: {language}")
    
    def stop_all(self):
        """Остановка всех детекторов."""
        for detector in self.detectors.values():
            detector.stop_listening()


# Глобальный экземпляр менеджера
wake_word_manager = WakeWordManager()
