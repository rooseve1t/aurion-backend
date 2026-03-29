"""
🏆 ЗОЛОТОЙ СТАНДАРТ: Автономный голосовой ассистент JARVIS
"""
import asyncio
import io
import base64
import tempfile
import os
from typing import Optional, Dict, Any, List
import json
import numpy as np
from datetime import datetime, timezone, time as dt_time
import aiohttp
from fastapi import Depends

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Импортируем openai с graceful fallback
try:
    import openai
except ImportError:
    openai = None  # type: ignore

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Конфигурация провайдеров
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
    "elevenlabs_whisper": {
        "api_key": os.getenv("ELEVENLABS_API_KEY"),
        "voice_id": "pNInz6obpgDQGcFmaJgB",  # Adam - мягкий голос для шепота
        "model_id": "eleven_multilingual_v2",
        "quality": "high",
        "stability": 0.95,      # Очень стабильно для шепота
        "similarity_boost": 0.85,
        "style": 0.1,           # Минимальная эмоциональность
        "use_speaker_boost": False  # Без усиления для шепота
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

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Конфигурация STT
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
    }
}

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Конфигурация LLM
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

class VoiceJarvisStandalone:
    """
    🏆 ЗОЛОТОЙ СТАНДАРТ: Автономный голосовой ассистент JARVIS
    """
    
    def __init__(self):
        self.tts_provider = os.getenv("TTS_PROVIDER", "elevenlabs")
        self.stt_provider = os.getenv("STT_PROVIDER", "openai")
        self.llm_provider = os.getenv("LLM_PROVIDER", "openai")
        
        # 🤫 WHISPER MODE - новая революционная функция
        self.voice_mode = "normal"  # normal, whisper, soft, energetic
        self.whisper_triggers = [
            "спать", "ночь", "отдых", "тихо", "шепот",
            "секрет", "конфиденциально", "поздно", "не буди",
            "устал", "сони", "дрмота", "починяю"
        ]
        self.night_hours_start = 22  # 22:00
        self.night_hours_end = 6     # 06:00
        
        # 🏆 ЗОЛОТОЙ СТАНДАРТ: Настройка OpenAI
        if openai and LLM_PROVIDERS["openai"]["api_key"]:
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
        
        # Контекст разговора
        self.conversation_context = []
    
    def _get_jarvis_system_prompt(self) -> str:
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Получение системного промпта для JARVIS"""
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

Эмоциональный диапазон: {', '.join(self.jarvis_personality['emotional_range'])}
Области знаний: {', '.join(self.jarvis_personality['knowledge_domains'])}

Примеры стиля:
- "Сэр, я обнаружил нечто любопытное..."
- "Позвольте мне проанализировать эту ситуацию..."
- "Интересная задача! Давайте разберемся..."
- "Как я понимаю, вы ищете решение для..."

Отвечай естественно, как живой ассистент, а не робот.
"""
    
    # 🤫 WHISPER MODE - революционные функции
    def detect_whisper_context(self, text: str, user_context: Optional[Dict] = None) -> bool:
        """Определяет, нужно ли говорить шепотом"""
        current_hour = datetime.now().hour
        
        # Автоопределение по времени
        if current_hour >= self.night_hours_start or current_hour <= self.night_hours_end:
            return True
            
        # Проверка триггеров в тексте
        text_lower = text.lower()
        for trigger in self.whisper_triggers:
            if trigger in text_lower:
                return True
                
        # Контекст пользователя
        if user_context:
            if user_context.get("tired", False):
                return True
            if user_context.get("sleep_mode", False):
                return True
                
        return False
    
    def set_voice_mode(self, mode: str) -> None:
        """Устанавливает режим голоса"""
        valid_modes = ["normal", "whisper", "soft", "energetic"]
        if mode in valid_modes:
            self.voice_mode = mode
            print(f"🎤 Voice mode changed to: {mode}")
        else:
            print(f"❌ Invalid voice mode: {mode}")
    
    def get_current_provider_config(self) -> Dict[str, Any]:
        """Получает текущую конфигурацию TTS провайдера"""
        if self.voice_mode == "whisper":
            return TTS_PROVIDERS.get("elevenlabs_whisper", TTS_PROVIDERS["elevenlabs"])
        elif self.voice_mode == "soft":
            soft_config = TTS_PROVIDERS["elevenlabs"].copy()
            soft_config.update({
                "stability": 0.85,
                "similarity_boost": 0.75,
                "style": 0.3,
                "use_speaker_boost": False
            })
            return soft_config
        else:
            return TTS_PROVIDERS[self.tts_provider]
    
    async def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Преобразование речи в текст"""
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
        """🏆 ЗОЛОТОЙ СТАНДАРТ: OpenAI Whisper распознавание"""
        if not openai:
            print("OpenAI not available")
            return None
        try:
            # Сохраняем аудио во временный файл
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                # Конвертируем аудио в нужный формат
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_file(io.BytesIO(audio_data))
                    audio.export(tmp_file.name, format="wav")
                except ImportError:
                    # Если pydub не установлен, сохраняем как есть
                    with open(tmp_file.name, "wb") as f:
                        f.write(audio_data)
                
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
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Yandex SpeechKit распознавание"""
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
    
    async def generate_response(self, user_input: str, context: Optional[List[Dict]] = None, user_context: Optional[Dict] = None) -> str:
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Генерация ответа с помощью LLM и автоопределением шепота"""
        try:
            # 🤫 Автоопределение режима шепота
            if self.detect_whisper_context(user_input, user_context):
                if self.voice_mode != "whisper":
                    self.set_voice_mode("whisper")
                    print("🤫 Auto-switched to whisper mode")
            elif self.voice_mode == "whisper" and not self.detect_whisper_context(user_input, user_context):
                # Возвращаем в нормальный режим если контекст изменился
                self.set_voice_mode("normal")
                print("🎤 Auto-switched back to normal mode")
            
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
        """🏆 ЗОЛОТОЙ СТАНДАРТ: OpenAI GPT-4 генерация ответа"""
        if not openai:
            return "Извините, OpenAI недоступен."
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
                temperature=LLM_PROVIDERS["openai"]["temperature"],
                top_p=LLM_PROVIDERS["openai"]["top_p"],
                frequency_penalty=LLM_PROVIDERS["openai"]["frequency_penalty"],
                presence_penalty=LLM_PROVIDERS["openai"]["presence_penalty"]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenAI LLM Error: {e}")
            return "Извините, я временно недоступен. Попробуйте позже."
    
    async def _llm_anthropic(self, user_input: str, context: Optional[List[Dict]] = None) -> str:
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Anthropic Claude генерация ответа"""
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
                temperature=LLM_PROVIDERS["anthropic"]["temperature"],
                system=system_prompt,
                messages=messages
            )
            
            return response.content[0].text
        except Exception as e:
            print(f"Anthropic LLM Error: {e}")
            return "Извините, я временно недоступен. Попробуйте позже."
    
    async def _llm_yandex(self, user_input: str, context: Optional[List[Dict]] = None) -> str:
        """🏆 ЗОЛОТОЙ СТАНДАРТ: YandexGPT генерация ответа"""
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
                    "temperature": LLM_PROVIDERS["yandex"]["temperature"],
                    "maxTokens": LLM_PROVIDERS["yandex"]["max_tokens"]
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
    
    async def text_to_speech(self, text: str) -> Optional[bytes]:
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Преобразование текста в речь с поддержкой шепота"""
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
        """🏆 ЗОЛОТОЙ СТАНДАРТ: ElevenLabs TTS с поддержкой шепота"""
        try:
            # 🤫 Получаем конфигурацию в зависимости от режима голоса
            provider_config = self.get_current_provider_config()
            voice_id = provider_config["voice_id"]
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "xi-api-key": provider_config["api_key"],
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "model_id": provider_config["model_id"],
                "voice_settings": {
                    "stability": provider_config["stability"],
                    "similarity_boost": provider_config["similarity_boost"],
                    "style": provider_config["style"],
                    "use_speaker_boost": provider_config["use_speaker_boost"]
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
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Azure TTS"""
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
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Yandex TTS с поддержкой шепота"""
        try:
            url = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"
            
            headers = {
                "Authorization": f"Api-Key {TTS_PROVIDERS['yandex']['api_key']}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            # 🤫 Адаптируем параметры для шепота
            emotion = "good"
            speed = 1.0
            
            if self.voice_mode == "whisper":
                emotion = "neutral"
                speed = 0.8  # Медленнее для шепота
            elif self.voice_mode == "soft":
                emotion = "gentle"
                speed = 0.9
            
            data = {
                "text": text,
                "voice": TTS_PROVIDERS["yandex"]["voice"],
                "folderId": TTS_PROVIDERS["yandex"]["folder_id"],
                "format": TTS_PROVIDERS["yandex"]["format"],
                "sampleRateHertz": TTS_PROVIDERS["yandex"]["sampleRateHertz"],
                "emotion": emotion,
                "speed": speed
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
    
    async def process_voice_message(self, audio_data: bytes, context: Optional[List[Dict]] = None, user_context: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Полная обработка голосового сообщения с поддержкой шепота"""
        try:
            # 1. Распознавание речи
            user_text = await self.speech_to_text(audio_data)
            if not user_text:
                return {"error": "Не удалось распознать речь"}
            
            # 2. Генерация ответа с автоопределением шепота
            jarvis_response = await self.generate_response(user_text, context, user_context)
            
            # 3. Синтез речи с учетом режима
            audio_response = await self.text_to_speech(jarvis_response)
            
            return {
                "user_text": user_text,
                "jarvis_text": jarvis_response,
                "audio_response": audio_response,
                "voice_mode": self.voice_mode,  # 🤫 Добавляем информацию о режиме
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            print(f"Voice processing error: {e}")
            return {"error": f"Ошибка обработки голоса: {str(e)}"}
    
    # 🤫 DOPOЛНИТЕЛЬНЫЕ WHISPER ФУНКЦИИ
    async def speak_whisper(self, text: str) -> Optional[bytes]:
        """Принудительно говорит шепотом"""
        original_mode = self.voice_mode
        self.set_voice_mode("whisper")
        try:
            result = await self.text_to_speech(text)
            return result
        finally:
            self.set_voice_mode(original_mode)
    
    async def speak_soft(self, text: str) -> Optional[bytes]:
        """Принудительно говорит мягко"""
        original_mode = self.voice_mode
        self.set_voice_mode("soft")
        try:
            result = await self.text_to_speech(text)
            return result
        finally:
            self.set_voice_mode(original_mode)
    
    def get_voice_status(self) -> Dict[str, Any]:
        """Получает текущий статус голосовой системы"""
        current_hour = datetime.now().hour
        is_night_time = current_hour >= self.night_hours_start or current_hour <= self.night_hours_end
        
        return {
            "current_mode": self.voice_mode,
            "is_night_time": is_night_time,
            "night_hours": f"{self.night_hours_start}:00 - {self.night_hours_end}:00",
            "available_modes": ["normal", "whisper", "soft", "energetic"],
            "auto_whisper_enabled": True,
            "current_hour": current_hour
        }
    
    def get_conversation_context(self, limit: int = 10) -> List[Dict]:
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Получение контекста разговора"""
        return self.conversation_context[-limit:] if self.conversation_context else []
    
    def save_conversation_message(self, role: str, content: str):
        """🏆 ЗОЛОТОЙ СТАНДАРТ: Сохранение сообщения в контекст"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        self.conversation_context.append(message)
        
        # Ограничиваем историю до 50 сообщений
        if len(self.conversation_context) > 50:
            self.conversation_context = self.conversation_context[-50:]

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Глобальный экземпляр
voice_jarvis_standalone = VoiceJarvisStandalone()

# 🏆 ЗОЛОТОЙ СТАНДАРТ: Функции инициализации
async def init_voice_jarvis_standalone():
    """🏆 ЗОЛОТОЙ СТАНДАРТ: Инициализация голосового сервиса JARVIS"""
    print("🎤 JARVIS standalone service initialized")
    print(f"🎯 TTS Provider: {voice_jarvis_standalone.tts_provider}")
    print(f"🎯 STT Provider: {voice_jarvis_standalone.stt_provider}")
    print(f"🎯 LLM Provider: {voice_jarvis_standalone.llm_provider}")
    print("🏆 JARVIS готов к общению!")

async def get_voice_jarvis_standalone() -> VoiceJarvisStandalone:
    """🏆 ЗОЛОТОЙ СТАНДАРТ: Получение экземпляра голосового сервиса"""
    return voice_jarvis_standalone
