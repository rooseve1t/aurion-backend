"""
🎭 Enhanced Voice JARVIS Service с эмоциональным TTS и личностью
Интеграция эмоционального движка в основной сервис
"""
import base64
import tempfile
import os
from typing import Optional, Dict, Any, List, cast
import json
from fastapi import WebSocket
import redis.asyncio as redis
from datetime import datetime
import aiohttp
try:
    from pydub import AudioSegment # type: ignore
except ImportError:
    AudioSegment = Any

# Импортируем новые компоненты
from .emotional_tts import EmotionalTTS, JARVISEmotion, get_emotional_tts
from .personality_engine import JARVISPersonalityEngine, get_personality_engine

class EnhancedVoiceJarvisService:
    """Улучшенный голосовой сервис JARVIS с личностью"""
    
    def __init__(self, websocket: WebSocket, user_id: str):
        self.websocket = websocket
        self.user_id = user_id
        self.redis_client: Optional[redis.Redis] = None
        
        # Новые компоненты
        self.emotional_tts: Optional[EmotionalTTS] = None
        self.personality_engine: Optional[JARVISPersonalityEngine] = None
        
        # Кэш для быстрого ответа
        self.response_cache = {}
        
        # Метрики
        self.interaction_count = 0
        self.emotion_stats = {emotion.value: 0 for emotion in JARVISEmotion}
        
    async def initialize(self):
        """Инициализация компонентов"""
        self.emotional_tts = await get_emotional_tts()
        self.personality_engine = await get_personality_engine()
        
        # Подключение к Redis
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            # Cast to Any to satisfy Pylance for from_url
            redis_module: Any = redis.Redis
            self.redis_client = cast(redis.Redis, redis_module.from_url(
                redis_url,
                decode_responses=True
            ))
        except Exception as e:
            print(f"Redis connection failed: {e}")
            
    async def process_voice_input(
        self, 
        audio_data: bytes, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Обработать голосовой ввод с эмоциональным ответом"""
        
        start_time = datetime.now()
        
        if not self.personality_engine or not self.emotional_tts:
            return {"error": "Сервисы не инициализированы"}
            
        try:
            # 1. Распознать речь
            text = await self._speech_to_text(audio_data)
            if not text:
                return {"error": "Не удалось распознать речь"}
                
            # 2. Проанализировать с помощью personality engine
            analysis = self.personality_engine.analyze_user_input(text, context)
            
            # 3. Сгенерировать ответ с личностью
            response_data = self.personality_engine.generate_response(text, analysis, context)
            
            # 4. Определить эмоцию для TTS
            emotion = JARVISEmotion(response_data["emotion"])
            
            # 5. Синтезировать речь с эмоцией
            audio_response = await self.emotional_tts.synthesize_with_emotion(
                response_data["text"], 
                emotion, 
                context
            )
            
            # 6. Обновить статистику
            await self._update_metrics(analysis, emotion, start_time)
            
            # 7. Отправить ответ
            result_data: Dict[str, Any] = {
                "text": response_data["text"],
                "audio": base64.b64encode(audio_response).decode(),
                "emotion": emotion.value,
                "style": response_data["style"],
                "traits_used": response_data["traits_used"],
                "confidence": response_data["confidence"],
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "interaction_id": self.interaction_count
            }
            
            return result_data
            
        except Exception as e:
            print(f"Error processing voice input: {e}")
            return {"error": f"Ошибка обработки: {str(e)}"}
    
    async def _speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """Распознать речь в текст"""
        tmp_file_path: Optional[str] = None
        wav_path: Optional[str] = None
        try:
            # Используем OpenAI Whisper
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return None
                
            # Сохранить аудио во временный файл
            with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            # Конвертировать в нужный формат
            audio_cls: Any = AudioSegment
            audio = audio_cls.from_file(tmp_file_path)
            wav_path = tmp_file_path.replace(".webm", ".wav")
            audio.export(wav_path, format="wav", parameters=["-ar", "16000"])
            
            # Отправить в Whisper
            with open(wav_path, "rb") as audio_file:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        "Authorization": f"Bearer {api_key}"
                    }
                    
                    data = aiohttp.FormData()
                    data.add_field('file', audio_file, 
                                    filename='audio.wav', 
                                    content_type='audio/wav')
                    data.add_field('model', 'whisper-1')
                    data.add_field('language', 'ru')
                    
                    async with session.post(
                        "https://api.openai.com/v1/audio/transcriptions",
                        headers=headers, 
                        data=data
                    ) as response:
                        if response.status == 200:
                            result_raw = await response.json()
                            result: Dict[str, Any] = cast(Dict[str, Any], result_raw)
                            return cast(str, result.get('text', ''))
                        else:
                            print(f"Whisper API error: {response.status}")
                            return None
                                
        except Exception as e:
            print(f"Speech to text error: {e}")
            return None
        finally:
            # Очистить временные файлы
            try:
                if tmp_file_path: os.unlink(tmp_file_path)
                if wav_path: os.unlink(wav_path)
            except:
                pass
    
    async def _update_metrics(
        self, 
        analysis: Dict[str, Any], 
        emotion: JARVISEmotion,
        start_time: datetime
    ):
        """Обновить метрики взаимодействия"""
        self.interaction_count += 1
        self.emotion_stats[emotion.value] += 1
        
        # Сохранить в Redis если доступно
        if self.redis_client:
            try:
                metrics: Dict[str, Any] = {
                    "interaction_count": self.interaction_count,
                    "emotion_stats": self.emotion_stats,
                    "last_interaction": datetime.now().isoformat(),
                    "avg_processing_time": (datetime.now() - start_time).total_seconds()
                }
                
                # Use cast and Any to bypass setex type issues
                rc: Any = self.redis_client
                await rc.setex(
                    f"jarvis_metrics:{self.user_id}",
                    3600,  # 1 час
                    json.dumps(metrics)
                )
            except Exception as e:
                print(f"Redis metrics error: {e}")
    
    async def get_emotional_status(self) -> Dict[str, Any]:
        """Получить эмоциональный статус JARVIS"""
        if not self.personality_engine:
            return {"error": "Personality engine not initialized"}
            
        summary = self.personality_engine.get_personality_summary(self.user_id)
        
        return {
            "current_mood": summary["current_mood"],
            "traits": summary["traits"],
            "interaction_count": summary["response_count"],
            "emotion_distribution": self.emotion_stats,
            "user_relationship": {
                "level": summary["user_profile"].get("relationship_level", 1.0),
                "frustration": summary["user_profile"].get("frustration_level", 0.0)
            }
        }
    
    async def adjust_personality(
        self, 
        trait_adjustments: Dict[str, float]
    ) -> Dict[str, Any]:
        """Настроить черты личности"""
        if not self.personality_engine:
            return {"error": "Personality engine not initialized"}
            
        from .personality_engine import PersonalityTrait
        
        try:
            for trait_name, level in trait_adjustments.items():
                trait = PersonalityTrait(trait_name)
                self.personality_engine.set_trait_level(trait, level)
                
            return {
                "success": True,
                "updated_traits": trait_adjustments,
                "current_traits": self.personality_engine.get_personality_summary()["traits"]
            }
        except Exception as e:
            return {"error": f"Failed to adjust personality: {str(e)}"}
    
    async def add_inside_joke(self, joke: str) -> Dict[str, Any]:
        """Добавить внутреннюю шутку"""
        if not self.personality_engine:
            return {"error": "Personality engine not initialized"}
            
        self.personality_engine.add_inside_joke(self.user_id, joke)
        
        summary = self.personality_engine.get_personality_summary(self.user_id)
        return {
            "success": True,
            "joke_added": joke,
            "total_jokes": len(summary["user_profile"].get("inside_jokes", []))
        }
    
    async def test_emotion(self, emotion: str, text: str) -> Dict[str, Any]:
        """Тестировать эмоциональный ответ"""
        if not self.emotional_tts:
            return {"error": "TTS not initialized"}
            
        try:
            jarvis_emotion = JARVISEmotion(emotion)
            
            # Синтезировать речь с эмоцией
            audio_data = await self.emotional_tts.synthesize_with_emotion(
                text, 
                jarvis_emotion
            )
            
            return {
                "success": True,
                "emotion": emotion,
                "text": text,
                "audio": base64.b64encode(audio_data).decode(),
                "audio_size": len(audio_data)
            }
            
        except Exception as e:
            return {"error": f"Emotion test failed: {str(e)}"}
    
    async def get_available_emotions(self) -> List[str]:
        """Получить список доступных эмоций"""
        if not self.emotional_tts:
            return []
            
        return self.emotional_tts.get_available_emotions()
    
    async def set_sarcasm_level(self, level: float) -> Dict[str, Any]:
        """Установить уровень сарказма 0-1"""
        if not self.emotional_tts:
            return {"error": "TTS not initialized"}
            
        self.emotional_tts.set_sarcasm_level(level)
        
        return {
            "success": True,
            "sarcasm_level": level,
            "current_mood": self.emotional_tts.get_current_mood()
        }
    
    async def send_emotional_notification(
        self, 
        message: str, 
        emotion: str = "neutral"
    ) -> Dict[str, Any]:
        """Отправить эмоциональное уведомление"""
        if not self.personality_engine or not self.emotional_tts:
            return {"error": "Services not initialized"}
            
        try:
            jarvis_emotion = JARVISEmotion(emotion)
            
            # Сгенерировать ответ с личностью
            analysis: Dict[str, Any] = {"intent": "notification", "urgency": 0.5}
            response_data = self.personality_engine.generate_response(
                message, 
                analysis
            )
            
            # Синтезировать речь
            audio_data = await self.emotional_tts.synthesize_with_emotion(
                response_data["text"],
                jarvis_emotion
            )
            
            # Отправить через WebSocket
            await self.websocket.send_json({
                "type": "emotional_notification",
                "text": response_data["text"],
                "audio": base64.b64encode(audio_data).decode(),
                "emotion": emotion,
                "style": response_data["style"]
            })
            
            return {
                "success": True,
                "message_sent": response_data["text"]
            }
            
        except Exception as e:
            return {"error": f"Failed to send notification: {str(e)}"}

# Фабрика для создания enhanced сервиса
async def create_enhanced_jarvis_service(
    websocket: WebSocket, 
    user_id: str
) -> EnhancedVoiceJarvisService:
    """Создать улучшенный JARVIS сервис"""
    service = EnhancedVoiceJarvisService(websocket, user_id)
    await service.initialize()
    return service
