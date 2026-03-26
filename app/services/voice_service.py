"""
Сервис голосового интерфейса с STT/TTS
"""
import asyncio
import io
import base64
import binascii
import tempfile
import os
from typing import Optional, Dict, Any
import json
import numpy as np
from fastapi import WebSocket
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

try:
    import vosk
    import soundfile as sf
    VOSK_AVAILABLE = True
except ImportError:
    VOSK_AVAILABLE = False

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

# Redis для кэширования
redis_client: Optional[redis.Redis] = None


class VoiceService:
    def __init__(self):
        self.redis = redis_client
        self.stt_model = None
        self.tts_voices = {
            "calm": "ru-RU-DariyaNeural",
            "jarvis": "ru-RU-DmitryNeural",
            "ironic": "ru-RU-SvetlanaNeural",
            "sarcastic": "ru-RU-EkaterinaNeural"
        }
        
        # Инициализация STT модели
        self._init_stt_model()
    
    def _init_stt_model(self):
        """Инициализация Vosk модели"""
        if not VOSK_AVAILABLE:
            return
        
        try:
            model_path = os.getenv("VOSK_MODEL_PATH", "models/vosk-model-small-ru-0.22")
            if os.path.exists(model_path):
                self.stt_model = vosk.Model(model_path)
        except Exception as e:
            print(f"Failed to load Vosk model: {e}")
            self.stt_model = None
    
    async def speech_to_text(self, audio_data: bytes, format: str = "wav") -> str:
        """Распознавание речи в текст"""
        
        # Проверка кэша
        cache_key = f"stt:{hash(audio_data)}:{format}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return cached.decode()
        
        if self.stt_model is None:
            # Fallback - эхо режим
            return "Аудио получено, но распознавание недоступно"
        
        try:
            # Конвертация аудио в нужный формат
            audio_array = self._convert_audio(audio_data, format)
            
            # Распознавание
            rec = vosk.KaldiRecognizer(self.stt_model, 16000)
            if rec.AcceptWaveform(audio_array.tobytes()):
                result = json.loads(rec.Result())
                text = result.get("text", "")
            else:
                text = ""
            
            # Кэширование
            if self.redis and text:
                await self.redis.setex(cache_key, 3600, text)
            
            return text
            
        except Exception as e:
            print(f"STT error: {e}")
            return "Ошибка распознавания речи"
    
    async def text_to_speech(
        self,
        text: str,
        persona: str = "calm",
        emotion: str = "neutral"
    ) -> str:
        """Синтез речи из текста"""
        
        # Проверка кэша
        cache_key = f"tts:{hash(text)}:{persona}:{emotion}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                return cached.decode()
        
        if not EDGE_TTS_AVAILABLE:
            # Fallback - возвращаем текст
            return text
        
        try:
            voice = self.tts_voices.get(persona, self.tts_voices["calm"])
            
            # Настройка эмоциональной окраски через скорость и интонацию
            rate = "+0%"  # нормальная скорость
            volume = "+0%"  # нормальная громкость
            pitch = "+0Hz"  # нормальная высота
            
            if emotion == "happy":
                rate = "+10%"
                pitch = "+5Hz"
            elif emotion == "sad":
                rate = "-10%"
                pitch = "-5Hz"
            elif emotion == "angry":
                rate = "+20%"
                volume = "+20%"
            elif emotion == "excited":
                rate = "+30%"
                pitch = "+10Hz"
            
            communicate = edge_tts.Communicate(
                text, 
                voice, 
                rate=rate, 
                volume=volume, 
                pitch=pitch
            )
            
            # Генерация аудио
            audio_data = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
            
            # Кодирование в base64
            audio_base64 = base64.b64encode(audio_data).decode()
            
            # Кэширование
            if self.redis:
                await self.redis.setex(cache_key, 3600, audio_base64)
            
            return audio_base64
            
        except Exception as e:
            print(f"TTS error: {e}")
            return text  # Fallback
    
    def _convert_audio(self, audio_data: bytes, format: str) -> np.ndarray:
        """Конвертация аудио в формат для Vosk"""
        try:
            if format == "wav":
                data, samplerate = sf.read(io.BytesIO(audio_data))
                if samplerate != 16000:
                    # Ресемплинг до 16kHz
                    import librosa
                    data = librosa.resample(data, orig_sr=samplerate, target_sr=16000)
                return data
            elif format == "mp3" or format == "ogg":
                # Конвертация через временный файл
                with tempfile.NamedTemporaryFile(suffix=f".{format}", delete=False) as tmp:
                    tmp.write(audio_data)
                    tmp.flush()
                    
                    data, samplerate = sf.read(tmp.name)
                    os.unlink(tmp.name)
                    
                    if samplerate != 16000:
                        import librosa
                        data = librosa.resample(data, orig_sr=samplerate, target_sr=16000)
                    
                    return data
            else:
                raise ValueError(f"Unsupported format: {format}")
                
        except Exception as e:
            print(f"Audio conversion error: {e}")
            # Возвращаем тишину
            return np.zeros(16000, dtype=np.float32)
    
    async def get_voice_preview(self, text: str, persona: str) -> Dict[str, Any]:
        """Предварительный просмотр голоса"""
        
        # Определение эмоции из текста
        emotion = self._infer_emotion(text)
        
        # Генерация TTS
        tts_audio = await self.text_to_speech(text, persona, emotion)
        
        return {
            "text": text,
            "persona": persona,
            "emotion": emotion,
            "audio": tts_audio,
            "audio_format": "base64"
        }
    
    def _infer_emotion(self, text: str) -> str:
        """Определение эмоции из текста"""
        text_lower = text.lower()
        
        # Простые эвристики
        happy_words = ["рад", "счастлив", "отлично", "прекрасно", "здорово", "класс"]
        sad_words = ["грустно", "печально", "жаль", "плохо", "ужасно"]
        angry_words = ["зл", "раздража", "бесит", "ненавижу"]
        excited_words = ["восторг", "круто", "супер", "невероятно"]
        
        if any(word in text_lower for word in excited_words):
            return "excited"
        elif any(word in text_lower for word in happy_words):
            return "happy"
        elif any(word in text_lower for word in angry_words):
            return "angry"
        elif any(word in text_lower for word in sad_words):
            return "sad"
        else:
            return "neutral"
    
    async def handle_websocket(self, websocket: WebSocket, user_id: str):
        """Обработка WebSocket соединения для голосового чата"""
        await websocket.accept()
        
        try:
            while True:
                # Получение сообщения
                message = await websocket.receive_text()
                data = json.loads(message)
                
                message_type = data.get("type", "text")
                
                if message_type == "text":
                    # Текстовое сообщение
                    text = data.get("content", "")
                    if text:
                        await self._process_text_message(websocket, text, user_id)
                
                elif message_type == "audio":
                    # Голосовое сообщение
                    audio_data = data.get("audio", "")
                    format = data.get("format", "wav")
                    
                    if audio_data:
                        # Декодирование аудио
                        audio_bytes = base64.b64decode(audio_data)
                        
                        # Распознавание
                        recognized_text = await self.speech_to_text(audio_bytes, format)
                        
                        # Обработка текста
                        await self._process_text_message(websocket, recognized_text, user_id)
                
                elif message_type == "ping":
                    # Проверка соединения
                    await websocket.send_json({"type": "pong"})
                
        except Exception as e:
            print(f"WebSocket error: {e}")
        finally:
            await websocket.close()
    
    async def _process_text_message(self, websocket: WebSocket, text: str, user_id: str):
        """Обработка текстового сообщения"""
        
        # Здесь должна быть интеграция с AI для генерации ответа
        # Пока используем простую заглушку
        response_text = self._generate_response(text)
        
        # Определение эмоции ответа
        emotion = self._infer_emotion(response_text)
        
        # Получение настроек голоса пользователя
        persona = "calm"  # TODO: получить из БД
        
        # Генерация TTS
        tts_audio = await self.text_to_speech(response_text, persona, emotion)
        has_audio = False
        if isinstance(tts_audio, str) and len(tts_audio) > 32:
            try:
                base64.b64decode(tts_audio, validate=True)
                has_audio = True
            except (binascii.Error, ValueError):
                has_audio = False
        tts_payload = {
            "provider": "edge-tts" if EDGE_TTS_AVAILABLE and has_audio else "browser-fallback",
            "audio_b64": tts_audio if has_audio else None,
            "mime_type": "audio/mpeg",
            "emotion": emotion,
            "persona": persona,
        }

        # Отправка ответа
        await websocket.send_json({
            "type": "chat_response",
            "content": response_text,
            "emotion": emotion,
            "voice_persona": persona,
            "tts": tts_payload,
            "recognized_text": text if text != response_text else None
        })
    
    def _generate_response(self, text: str) -> str:
        """Генерация ответа (заглушка)"""
        text_lower = text.lower()
        
        if "привет" in text_lower or "здравствуй" in text_lower:
            return "Здравствуйте! Чем могу помочь?"
        elif "как дела" in text_lower:
            return "У меня всё отлично, спасибо! А у вас?"
        elif "пока" in text_lower or "до свидания" in text_lower:
            return "До свидания! Буду рад помочь снова."
        elif "спасибо" in text_lower or "благодарю" in text_lower:
            return "Пожалуйста! Всегда рад помочь."
        elif "время" in text_lower:
            import datetime
            now = datetime.datetime.now().strftime("%H:%M")
            return f"Сейчас {now} времени."
        else:
            return f"Вы сказали: {text}. Я вас услышал и готов помочь."


# Глобальный экземпляр сервиса
voice_service = VoiceService()


async def init_voice_service():
    """Инициализация голосового сервиса"""
    global redis_client
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
    except Exception as e:
        print(f"Redis connection failed for voice service: {e}")
        redis_client = None
