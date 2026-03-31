"""
Enhanced Emotional TTS - улучшенный эмоциональный синтез речи.
Адаптирует голос JARVIS под контекст и эмоциональное состояние.
"""
import asyncio
import logging
from typing import Optional, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import os
import base64

logger = logging.getLogger("jarvis.emotional_tts")


class Emotion(Enum):
    """Эмоции для синтеза речи."""
    NEUTRAL = "neutral"
    CALM = "calm"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    CONCERNED = "concerned"
    PROFESSIONAL = "professional"
    WARM = "warm"
    URGENT = "urgent"


class VoicePersona(Enum):
    """Персоны голоса JARVIS."""
    CLASSIC = "classic"       # Классический JARVIS (как в Iron Man)
    CALM = "calm"             # Спокойный, расслабленный
    PROFESSIONAL = "professional"  # Деловой, официальный
    FRIENDLY = "friendly"     # Дружелюбный, теплый
    ASSERTIVE = "assertive"   # Уверенный, решительный


@dataclass
class VoiceProfile:
    """Профиль голоса с параметрами."""
    persona: VoicePersona
    emotion: Emotion
    
    # Параметры ElevenLabs
    stability: float = 0.5      # 0-1, стабильность голоса
    similarity_boost: float = 0.75  # 0-1, схожесть с оригиналом
    style: float = 0.0          # 0-1, экспрессивность
    use_speaker_boost: bool = True
    
    # Параметры скорости
    speed: float = 1.0          # 0.5-2.0
    
    # Параметры тона
    pitch_shift: int = 0        # -12 до +12 полутонов


@dataclass
class TTSAudio:
    """Результат синтеза речи."""
    audio_data: bytes
    content_type: str
    duration_ms: int
    sample_rate: int
    text: str
    emotion: Emotion
    persona: VoicePersona


class EmotionalTTS:
    """
    Улучшенный эмоциональный TTS для JARVIS.
    
    Особенности:
    - Адаптация под контекст разговора
    - Различные эмоциональные профили
    - Оптимизация для русского языка
    - Кэширование частых фраз
    - Поддержка нескольких провайдеров (ElevenLabs, Yandex)
    """
    
    # Профили эмоций
    EMOTION_PROFILES: Dict[Emotion, Dict[str, float]] = {
        Emotion.NEUTRAL: {
            'stability': 0.5,
            'similarity_boost': 0.75,
            'style': 0.0,
            'speed': 1.0,
        },
        Emotion.CALM: {
            'stability': 0.7,
            'similarity_boost': 0.8,
            'style': 0.1,
            'speed': 0.9,
        },
        Emotion.HAPPY: {
            'stability': 0.4,
            'similarity_boost': 0.75,
            'style': 0.3,
            'speed': 1.05,
        },
        Emotion.SAD: {
            'stability': 0.8,
            'similarity_boost': 0.85,
            'style': 0.0,
            'speed': 0.85,
        },
        Emotion.ANGRY: {
            'stability': 0.3,
            'similarity_boost': 0.7,
            'style': 0.5,
            'speed': 1.1,
        },
        Emotion.EXCITED: {
            'stability': 0.3,
            'similarity_boost': 0.7,
            'style': 0.4,
            'speed': 1.15,
        },
        Emotion.CONCERNED: {
            'stability': 0.6,
            'similarity_boost': 0.8,
            'style': 0.2,
            'speed': 0.95,
        },
        Emotion.PROFESSIONAL: {
            'stability': 0.6,
            'similarity_boost': 0.85,
            'style': 0.0,
            'speed': 1.0,
        },
        Emotion.WARM: {
            'stability': 0.5,
            'similarity_boost': 0.8,
            'style': 0.2,
            'speed': 0.95,
        },
        Emotion.URGENT: {
            'stability': 0.3,
            'similarity_boost': 0.7,
            'style': 0.4,
            'speed': 1.2,
        },
    }
    
    # Профили персон
    PERSONA_PROFILES: Dict[VoicePersona, Dict[str, Any]] = {
        VoicePersona.CLASSIC: {
            'default_emotion': Emotion.PROFESSIONAL,
            'voice_id': 'elevenlabs_jarvis_classic',
            'description': 'Классический JARVIS - британский акцент, профессиональный',
        },
        VoicePersona.CALM: {
            'default_emotion': Emotion.CALM,
            'voice_id': 'elevenlabs_jarvis_calm',
            'description': 'Спокойный JARVIS - мягкий, расслабленный',
        },
        VoicePersona.PROFESSIONAL: {
            'default_emotion': Emotion.PROFESSIONAL,
            'voice_id': 'elevenlabs_jarvis_pro',
            'description': 'Профессиональный JARVIS - деловой, четкий',
        },
        VoicePersona.FRIENDLY: {
            'default_emotion': Emotion.WARM,
            'voice_id': 'elevenlabs_jarvis_friendly',
            'description': 'Дружелюбный JARVIS - теплый, приветливый',
        },
        VoicePersona.ASSERTIVE: {
            'default_emotion': Emotion.NEUTRAL,
            'voice_id': 'elevenlabs_jarvis_assertive',
            'description': 'Уверенный JARVIS - решительный, сильный',
        },
    }
    
    # Ключевые фразы для определения эмоции
    EMOTION_KEYWORDS: Dict[Emotion, list[str]] = {
        Emotion.HAPPY: [
            'отлично', 'прекрасно', 'замечательно', 'успешно', 'готово',
            'супер', 'великолепно', 'блестяще', 'поздравляю',
        ],
        Emotion.CONCERNED: [
            'внимание', 'предупреждение', 'осторожно', 'проблема', 'ошибка',
            'сбой', 'не удалось', 'требует внимания',
        ],
        Emotion.URGENT: [
            'срочно', 'немедленно', 'критично', 'экстренно', 'важно',
            'требуется', 'необходимо',
        ],
        Emotion.EXCITED: [
            'потрясающе', 'удивительно', 'новое открытие', 'прорыв',
            'интересное', 'захватывающе',
        ],
        Emotion.SAD: [
            'к сожалению', 'сожалею', 'не удалось', 'потеря', 'проблема',
        ],
    }
    
    def __init__(
        self,
        elevenlabs_api_key: Optional[str] = None,
        yandex_api_key: Optional[str] = None,
        default_persona: VoicePersona = VoicePersona.CLASSIC,
    ):
        """
        Инициализация TTS.
        
        Args:
            elevenlabs_api_key: API ключ ElevenLabs
            yandex_api_key: API ключ Yandex SpeechKit
            default_persona: Персона по умолчанию
        """
        self.elevenlabs_api_key = elevenlabs_api_key or os.environ.get('ELEVENLABS_API_KEY')
        self.yandex_api_key = yandex_api_key or os.environ.get('YANDEX_API_KEY')
        self.default_persona = default_persona
        
        # Кэш аудио
        self._audio_cache: Dict[str, TTSAudio] = {}
        self._cache_max_size = 100
        
        # Статистика
        self.stats = {
            'total_syntheses': 0,
            'cache_hits': 0,
            'provider_calls': {
                'elevenlabs': 0,
                'yandex': 0,
            },
        }
    
    def detect_emotion(self, text: str, context: Optional[Dict[str, Any]] = None) -> Emotion:
        """
        Определение эмоции на основе текста и контекста.
        
        Args:
            text: Текст для анализа
            context: Контекст разговора
            
        Returns:
            Определенная эмоция
        """
        text_lower = text.lower()
        
        # Проверка ключевых слов
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            if any(kw in text_lower for kw in keywords):
                return emotion
        
        # Учет контекста
        if context:
            # Время суток влияет на эмоцию
            hour = context.get('hour', datetime.now().hour)
            if 6 <= hour < 12:
                return Emotion.WARM  # Утро - теплый тон
            elif 22 <= hour or hour < 6:
                return Emotion.CALM  # Ночь - спокойный тон
            
            # Эмоциональное состояние пользователя
            user_emotion = context.get('user_emotion')
            if user_emotion == 'stressed':
                return Emotion.CALM  # Успокоить пользователя
            elif user_emotion == 'happy':
                return Emotion.HAPPY  # Поддержать радость
        
        return Emotion.NEUTRAL
    
    def get_voice_profile(
        self,
        persona: Optional[VoicePersona] = None,
        emotion: Optional[Emotion] = None,
    ) -> VoiceProfile:
        """
        Получение профиля голоса.
        
        Args:
            persona: Персона голоса
            emotion: Эмоция
            
        Returns:
            Профиль голоса с параметрами
        """
        persona = persona or self.default_persona
        emotion = emotion or self.PERSONA_PROFILES[persona]['default_emotion']
        
        # Базовые параметры персоны
        persona_config = self.PERSONA_PROFILES[persona]
        
        # Параметры эмоции
        emotion_config = self.EMOTION_PROFILES[emotion]
        
        # Объединение параметров
        return VoiceProfile(
            persona=persona,
            emotion=emotion,
            stability=emotion_config['stability'],
            similarity_boost=emotion_config['similarity_boost'],
            style=emotion_config['style'],
            speed=emotion_config['speed'],
        )
    
    async def synthesize(
        self,
        text: str,
        persona: Optional[VoicePersona] = None,
        emotion: Optional[Emotion] = None,
        context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> TTSAudio:
        """
        Синтез речи с эмоциями.
        
        Args:
            text: Текст для озвучивания
            persona: Персона голоса
            emotion: Эмоция (автоопределение если None)
            context: Контекст для определения эмоции
            use_cache: Использовать кэш
            
        Returns:
            Аудио данные
        """
        # Автоопределение эмоции
        if emotion is None:
            emotion = self.detect_emotion(text, context)
        
        persona = persona or self.default_persona
        profile = self.get_voice_profile(persona, emotion)
        
        # Проверка кэша
        cache_key = self._get_cache_key(text, profile)
        if use_cache and cache_key in self._audio_cache:
            self.stats['cache_hits'] += 1
            logger.debug(f"Взят из кэша: {text[:30]}...")
            return self._audio_cache[cache_key]
        
        # Синтез через провайдера
        audio = await self._synthesize_with_provider(text, profile)
        
        # Кэширование
        if use_cache:
            self._cache_audio(cache_key, audio)
        
        self.stats['total_syntheses'] += 1
        
        return audio
    
    async def _synthesize_with_provider(
        self,
        text: str,
        profile: VoiceProfile,
    ) -> TTSAudio:
        """Синтез через провайдера TTS."""
        # Приоритет: ElevenLabs > Yandex
        
        if self.elevenlabs_api_key:
            return await self._synthesize_elevenlabs(text, profile)
        elif self.yandex_api_key:
            return await self._synthesize_yandex(text, profile)
        else:
            # Fallback - заглушка
            logger.warning("Нет доступных TTS провайдеров")
            return TTSAudio(
                audio_data=b'',
                content_type='audio/mpeg',
                duration_ms=0,
                sample_rate=22050,
                text=text,
                emotion=profile.emotion,
                persona=profile.persona,
            )
    
    async def _synthesize_elevenlabs(
        self,
        text: str,
        profile: VoiceProfile,
    ) -> TTSAudio:
        """Синтез через ElevenLabs API."""
        import aiohttp
        
        voice_id = self.PERSONA_PROFILES[profile.persona].get('voice_id', 'default')
        
        # Маппинг voice_id на реальные ID ElevenLabs
        # TODO: Использовать реальные voice_id из конфигурации
        elevenlabs_voice_id = os.environ.get(
            'ELEVENLABS_VOICE_ID',
            '21m00Tcm4TlvDq8ikWAM'  # Пример ID
        )
        
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{elevenlabs_voice_id}"
        
        headers = {
            'xi-api-key': self.elevenlabs_api_key,
            'Content-Type': 'application/json',
        }
        
        payload = {
            'text': text,
            'model_id': 'eleven_multilingual_v2',  # Поддержка русского
            'voice_settings': {
                'stability': profile.stability,
                'similarity_boost': profile.similarity_boost,
                'style': profile.style,
                'use_speaker_boost': profile.use_speaker_boost,
            },
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        
                        self.stats['provider_calls']['elevenlabs'] += 1
                        
                        # Оценка длительности
                        duration_ms = len(text) * 80  # Примерная оценка
                        
                        return TTSAudio(
                            audio_data=audio_data,
                            content_type='audio/mpeg',
                            duration_ms=duration_ms,
                            sample_rate=22050,
                            text=text,
                            emotion=profile.emotion,
                            persona=profile.persona,
                        )
                    else:
                        error = await response.text()
                        logger.error(f"Ошибка ElevenLabs: {error}")
                        raise Exception(f"ElevenLabs API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Ошибка синтеза ElevenLabs: {e}")
            raise
    
    async def _synthesize_yandex(
        self,
        text: str,
        profile: VoiceProfile,
    ) -> TTSAudio:
        """Синтез через Yandex SpeechKit."""
        import aiohttp
        
        # Yandex TTS API endpoint
        url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
        
        headers = {
            'Authorization': f'Api-Key {self.yandex_api_key}',
        }
        
        # Маппинг эмоций Yandex
        emotion_map = {
            Emotion.NEUTRAL: 'neutral',
            Emotion.HAPPY: 'good',
            Emotion.SAD: 'neutral',
            Emotion.ANGRY: 'neutral',
            Emotion.CALM: 'neutral',
        }
        
        data = {
            'text': text,
            'lang': 'ru-RU',
            'voice': 'filuant',  # Мужской голос, похожий на JARVIS
            'emotion': emotion_map.get(profile.emotion, 'neutral'),
            'speed': str(profile.speed),
            'format': 'mp3',
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=headers) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        
                        self.stats['provider_calls']['yandex'] += 1
                        
                        duration_ms = len(text) * 80
                        
                        return TTSAudio(
                            audio_data=audio_data,
                            content_type='audio/mpeg',
                            duration_ms=duration_ms,
                            sample_rate=22050,
                            text=text,
                            emotion=profile.emotion,
                            persona=profile.persona,
                        )
                    else:
                        error = await response.text()
                        logger.error(f"Ошибка Yandex: {error}")
                        raise Exception(f"Yandex API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Ошибка синтеза Yandex: {e}")
            raise
    
    def _get_cache_key(self, text: str, profile: VoiceProfile) -> str:
        """Генерация ключа кэша."""
        import hashlib
        key_data = f"{text}_{profile.persona.value}_{profile.emotion.value}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _cache_audio(self, key: str, audio: TTSAudio):
        """Кэширование аудио."""
        # Ограничение размера кэша
        if len(self._audio_cache) >= self._cache_max_size:
            # Удаление старых записей
            oldest_key = next(iter(self._audio_cache))
            del self._audio_cache[oldest_key]
        
        self._audio_cache[key] = audio
    
    def clear_cache(self):
        """Очистка кэша."""
        self._audio_cache.clear()
        logger.info("Кэш TTS очищен")
    
    def get_stats(self) -> Dict[str, Any]:
        """Получение статистики."""
        return {
            **self.stats,
            'cache_size': len(self._audio_cache),
        }


# Глобальный экземпляр
_emotional_tts: Optional[EmotionalTTS] = None


def get_emotional_tts() -> EmotionalTTS:
    """Получение или создание TTS."""
    global _emotional_tts
    
    if _emotional_tts is None:
        _emotional_tts = EmotionalTTS()
    
    return _emotional_tts
