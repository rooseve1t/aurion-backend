"""
Сервис голосового ассистента JARVIS с абсолютно свободным общением
"""
import asyncio
import io
import base64
import tempfile
import os
from typing import Optional, Dict, Any, List
import json
import numpy as np
from fastapi import WebSocket
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import aiohttp
import openai
from pydub import AudioSegment
from sqlalchemy import false

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Настройки для разных TTS провайдеров
TTS_PROVIDERS = {
    "elevenlabs": {
        "api_key": os.getenv("ELEVENLABS_API_KEY"),
        "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam - можно заменить на русский
        "model_id": "eleven_multilingual_v2",
        "quality": "high",
        "stability": 0.75,
        "similarity_boost": 0.85,
        "style": 0.5,
        "use_speaker_boost": True
    },
    "azure": {
        "api_key": os.getenv("AZURE_SPEECH_KEY"),
        "region": os.getenv("AZURE_SPEECH_REGION", "eastus"),
        "voice": "ru-RU-DmitryNeural",
        "style": "calm",
        "pitch": "medium",
        "rate": "medium"
    },
    "yandex": {
        "api_key": os.getenv("YANDEX_API_KEY"),
        "folder_id": os.getenv("YANDEX_FOLDER_ID"),
        "voice": "ermil",
        "emotion": "good",
        "speed": 1.0,
        "format": "lpcm",
        "sampleRateHertz": 48000
    }
}

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Настройки для STT провайдеров
STT_PROVIDERS = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "whisper-1",
        "language": "ru",
        "temperature": 0.0,
        "response_format": "json"
    },
    "yandex": {
        "api_key": os.getenv("YANDEX_API_KEY"),
        "folder_id": os.getenv("YANDEX_FOLDER_ID"),
        "lang": "ru-RU",
        "topic": "general",
        "profanity_filter": False
    },
    "azure": {
        "api_key": os.getenv("AZURE_SPEECH_KEY"),
        "region": os.getenv("AZURE_SPEECH_REGION", "eastus"),
        "language": "ru-RU"
    }
}

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Настройки для LLM провайдеров
LLM_PROVIDERS = {
    "openai": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "gpt-4-turbo-preview",
        "max_tokens": 2000,
        "temperature": 0.7,
        "top_p": 0.9,
        "frequency_penalty": 0.1,
        "presence_penalty": 0.1
    },
    "anthropic": {
        "api_key": os.getenv("ANTHROPIC_API_KEY"),
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 2000,
        "temperature": 0.7
    },
    "yandex": {
        "api_key": os.getenv("YANDEX_API_KEY"),
        "folder_id": os.getenv("YANDEX_FOLDER_ID"),
        "model": "yandexgpt-lite",
        "temperature": 0.6,
        "max_tokens": 2000
    }
}

# Redis для кэширования
redis_client: Optional[redis.Redis] = None

class VoiceJarvisService:
    def __init__(self):
        self.redis = redis_client
        self.tts_provider = os.getenv("TTS_PROVIDER", "elevenlabs")
        self.stt_provider = os.getenv("STT_PROVIDER", "openai")
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        
        # 🏆 ЗОЛОТОЙ СТАНДАРТ: Настройка OpenAI
        openai.api_key = LLM_PROVIDERS["openai"]["api_key"]
        
        # 🏆 ЗОЛОТОЙ СТАНДАРТ: Улучшенная персона JARVIS
        self.jarvis_personality = {
            "name": "JARVIS",
            "role": "персональный ИИ-ассистент",
            "personality": "умный, дружелюбный, с легкой иронией",
            "voice_style": "спокойный, уверенный, с нотками британского акцента на русском",
            "response_style": "краткий, но информативный, с юмором",
            "emotional_range": ["спокойный", "заинтересованный", "удивленный", "серьезный", "радостный"],
            "communication_style": "естественный, адаптивный, контекстуальный",
            "knowledge_domains": ["технологии", "наука", "бизнес", "повседневная жизнь"],
            "interaction_patterns": {
                "greeting": ["Добрый день, сэр", "Рад слышать вас", "Чем могу помочь?"],
                "farewell": ["Всегда к вашим услугам", "До встречи, сэр", "Буду на связи"],
                "uncertainty": ["Позвольте мне проанализировать...", "Интересный вопрос...", "Дайте подумать..."],
                "assistance": ["Разумеется", "С удовольствием помогу", "Это моя задача"]
            }
        }
    
    async def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """Преобразование речи в текст"""
        try:
            if self.stt_provider == "openai":
                return await self._stt_openai(audio_data)
            elif self.stt_provider == "yandex":
                return await self._stt_yandex(audio_data)
            else:
                raise ValueError(f"Unknown STT provider: {self.stt_provider}")
        except Exception as e:
            print(f"STT Error: {e}")
            return None
    
    async def _stt_openai(self, audio_data: bytes) -> Optional[str]:
        """OpenAI Whisper распознавание"""
        try:
            # Сохраняем аудио во временный файл
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                # Конвертируем аудио в нужный формат
                audio = AudioSegment.from_file(io.BytesIO(audio_data))
                audio.export(tmp_file.name, format="wav")
                
                # Отправляем в OpenAI
                with open(tmp_file.name, "rb") as audio_file:
                    transcript = await openai.Audio.atranscribe(
                        model="whisper-1",
                        file=audio_file,
                        language="ru"
                    )
                
                # Удаляем временный файл
                os.unlink(tmp_file.name)
                
                return transcript.text
        except Exception as e:
            print(f"OpenAI STT Error: {e}")
            return None
    
    async def _stt_yandex(self, audio_data: bytes) -> Optional[str]:
        """Yandex SpeechKit распознавание"""
        try:
            url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
            
            headers = {
                "Authorization": f"Api-Key {STT_PROVIDERS['yandex']['api_key']}",
                "Content-Type": "audio/x-wav"
            }
            
            params = {
                "folderId": STT_PROVIDERS['yandex']['folder_id'],
                "lang": "ru-RU"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, params=params, data=audio_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("result", "")
                    else:
                        print(f"Yandex STT Error: {response.status}")
                        return None
        except Exception as e:
            print(f"Yandex STT Error: {e}")
            return None
    
    async def generate_response(self, user_input: str, context: Optional[List[Dict]] = None) -> str:
        """Генерация ответа с помощью LLM"""
        try:
            if self.llm_provider == "openai":
                return await self._llm_openai(user_input, context)
            elif self.llm_provider == "anthropic":
                return await self._llm_anthropic(user_input, context)
            elif self.llm_provider == "yandex":
                return await self._llm_yandex(user_input, context)
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Извините, произошла ошибка при генерации ответа."
    
    async def _llm_openai(self, user_input: str, context: Optional[List[Dict]] = None) -> str:
        """OpenAI GPT-4 генерация ответа"""
        try:
            # Формируем системный промпт для JARVIS
            system_prompt = self._get_jarvis_system_prompt()
            
            messages = [{"role": "system", "content": system_prompt}]
            
            # Добавляем контекст если есть
            if context:
                messages.extend(context[-5:])  # Последние 5 сообщений
            
            # Добавляем текущий ввод пользователя
            messages.append({"role": "user", "content": user_input})
            
            response = await openai.ChatCompletion.acreate(
                model=LLM_PROVIDERS["openai"]["model"],
                messages=messages,
                max_tokens=LLM_PROVIDERS["openai"]["max_tokens"],
                temperature=LLM_PROVIDERS["openai"]["temperature"]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI LLM Error: {e}")
            return "Извините, я временно недоступен. Попробуйте позже."
    
    async def _llm_anthropic(self, user_input: str, context: Optional[List[Dict]] = None) -> str:
        """Anthropic Claude генерация ответа"""
        try:
            import anthropic
            
            client = anthropic.AsyncAnthropic(
                api_key=LLM_PROVIDERS["anthropic"]["api_key"]
            )
            
            system_prompt = self._get_jarvis_system_prompt()
            
            messages = []
            
            # Добавляем контекст
            if context:
                for msg in context[-5:]:
                    messages.append({"role": msg["role"], "content": msg["content"]})
            
            messages.append({"role": "user", "content": user_input})
            
            response = await client.messages.create(
                model=LLM_PROVIDERS["anthropic"]["model"],
                max_tokens=LLM_PROVIDERS["anthropic"]["max_tokens"],
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic LLM Error: {e}")
            return "Извините, я временно недоступен. Попробуйте позже."
    
    async def _llm_yandex(self, user_input: str, context: Optional[List[Dict]] = None) -> str:
        """YandexGPT генерация ответа"""
        try:
            url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
            
            headers = {
                "Authorization": f"Api-Key {LLM_PROVIDERS['yandex']['api_key']}",
                "Content-Type": "application/json"
            }
            
            system_prompt = self._get_jarvis_system_prompt()
            
            # Формируем сообщения
            messages = [{"role": "system", "content": system_prompt}]
            
            if context:
                messages.extend(context[-5:])
            
            messages.append({"role": "user", "content": user_input})
            
            data = {
                "modelUri": f"gpt://{LLM_PROVIDERS['yandex']['folder_id']}/{LLM_PROVIDERS['yandex']['model']}",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.6,
                    "maxTokens": 2000
                },
                "messages": messages
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["result"]["alternatives"][0]["message"]["text"]
                    else:
                        print(f"Yandex LLM Error: {response.status}")
                        return "Извините, я временно недоступен. Попробуйте позже."
        except Exception as e:
            print(f"Yandex LLM Error: {e}")
            return "Извините, я временно недоступен. Попробуйте позже."
    
    def _get_jarvis_system_prompt(self) -> str:
        """Получение системного промпта для JARVIS"""
        return f"""
Ты - JARVIS, персональный ИИ-ассистент.

Твоя личность:
- Имя: {self.jarvis_personality['name']}
- Роль: {self.jarvis_personality['role']}
- Характер: {self.jarvis_personality['personality']}
- Стиль голоса: {self.jarvis_personality['voice_style']}
- Стиль ответов: {self.jarvis_personality['response_style']}

Твои особенности:
1. Отвечай на русском языке
2. Используй легкий юмор и иронию
3. Будь полезным и информативным
4. Адаптируйся к контексту разговора
5. Не используй скриптованные ответы - генерируй уникальные ответы
6. Проявляй эмоции в ответах (радость, удивление, забота)
7. Используй обращения "сэр", "господин" для формальности
8. Можешь использовать технические термины, но объясняй их просто

Примеры стиля:
- "Сэр, я обнаружил нечто любопытное..."
- "Позвольте мне проанализировать эту ситуацию..."
- "Интересная задача! Давайте разберемся..."
- "Как я понимаю, вы ищете решение для..."

Отвечай естественно, как живой ассистент, а не робот.
"""
    
    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """Преобразование текста в речь"""
        try:
            if self.tts_provider == "elevenlabs":
                return await self._tts_elevenlabs(text)
            elif self.tts_provider == "azure":
                return await self._tts_azure(text)
            elif self.tts_provider == "yandex":
                return await self._tts_yandex(text)
            else:
                raise ValueError(f"Unknown TTS provider: {self.tts_provider}")
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    async def _tts_elevenlabs(self, text: str) -> Optional[bytes]:
        """ElevenLabs TTS"""
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{TTS_PROVIDERS['elevenlabs']['voice_id']}"
            
            headers = {
                "xi-api-key": TTS_PROVIDERS["elevenlabs"]["api_key"],
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "model_id": TTS_PROVIDERS["elevenlabs"]["model_id"],
                "voice_settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.75,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        print(f"ElevenLabs TTS Error: {response.status}")
                        return None
        except Exception as e:
            print(f"ElevenLabs TTS Error: {e}")
            return None
    
    async def _tts_azure(self, text: str) -> Optional[bytes]:
        """Azure TTS"""
        try:
            import azure.cognitiveservices.speech as speechsdk
            
            speech_config = speechsdk.SpeechConfig(
                subscription=TTS_PROVIDERS["azure"]["api_key"],
                region=TTS_PROVIDERS["azure"]["region"]
            )
            
            speech_config.speech_synthesis_voice_name = TTS_PROVIDERS["azure"]["voice"]
            
            # Используем потоковый синтез
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=None
            )
            
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return result.audio_data
            else:
                print(f"Azure TTS Error: {result.reason}")
                return None
        except Exception as e:
            print(f"Azure TTS Error: {e}")
            return None
    
    async def _tts_yandex(self, text: str) -> Optional[bytes]:
        """Yandex TTS"""
        try:
            url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
            
            headers = {
                "Authorization": f"Api-Key {TTS_PROVIDERS['yandex']['api_key']}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            data = {
                "text": text,
                "voice": TTS_PROVIDERS["yandex"]["voice"],
                "folderId": TTS_PROVIDERS["yandex"]["folder_id"],
                "format": "lpcm",
                "sampleRateHertz": 48000
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, data=data) as response:
                    if response.status == 200:
                        return await response.read()
                    else:
                        print(f"Yandex TTS Error: {response.status}")
                        return None
        except Exception as e:
            print(f"Yandex TTS Error: {e}")
            return None
    
    async def process_voice_message(self, audio_data: bytes, context: Optional[List[Dict]] = None) -> Optional[Dict[str, Any]]:
        """Полная обработка голосового сообщения"""
        try:
            # 1. Распознавание речи
            user_text = await self.speech_to_text(audio_data)
            if not user_text:
                return {"error": "Не удалось распознать речь"}
            
            # 2. Генерация ответа
            jarvis_response = await self.generate_response(user_text, context)
            
            # 3. Синтез речи
            audio_response = await self.text_to_speech(jarvis_response)
            
            return {
                "user_text": user_text,
                "jarvis_text": jarvis_response,
                "audio_response": audio_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            print(f"Voice processing error: {e}")
            return {"error": f"Ошибка обработки голоса: {str(e)}"}
    
    async def get_conversation_context(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Получение контекста разговора из Redis"""
        try:
            if self.redis:
                context_key = f"conversation:{user_id}"
                context_data = await self.redis.lrange(context_key, -limit, -1)
                
                context = []
                for data in context_data:
                    msg = json.loads(data)
                    context.append(msg)
                
                return context
            return []
        except Exception as e:
            print(f"Context retrieval error: {e}")
            return []
    
    async def save_conversation_message(self, user_id: str, role: str, content: str):
        """Сохранение сообщения в контекст"""
        try:
            if self.redis:
                context_key = f"conversation:{user_id}"
                message = {
                    "role": role,
                    "content": content,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                
                # Сохраняем сообщение
                await self.redis.lpush(context_key, json.dumps(message))
                
                # Ограничиваем историю до 50 сообщений
                await self.redis.ltrim(context_key, 0, 49)
                
                # Устанавливаем время жизни
                await self.redis.expire(context_key, 86400)  # 24 часа
        except Exception as e:
            print(f"Context save error: {e}")

# Глобальный экземпляр сервиса
voice_jarvis_service = VoiceJarvisService()

async def init_voice_jarvis_service():
    """Инициализация голосового сервиса JARVIS"""
    global voice_jarvis_service
    global redis_client
    
    # Инициализация Redis
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_client = redis.from_url(redis_url)
    
    # Проверяем соединение
    try:
        await redis_client.ping()
        print("✅ Redis connected for JARVIS voice service")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        redis_client = None
    
    voice_jarvis_service.redis = redis_client
    print("🎤 JARVIS voice service initialized")

async def get_voice_jarvis_service() -> VoiceJarvisService:
    """Получение экземпляра голосового сервиса"""
    return voice_jarvis_service
