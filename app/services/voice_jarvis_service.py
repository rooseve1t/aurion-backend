"""
Сервис голосового ассистента JARVIS с абсолютно свободным общением
"""
import asyncio
import io
import base64
import tempfile
import os
import logging
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

logger = logging.getLogger("aurion-voice")

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
    
    # ─── Новые методы: synthesize / transcribe с fallback ───────────────────

    async def synthesize(self, text: str) -> bytes:
        """TTS: ElevenLabs → edge-tts fallback"""
        from ..config import settings
        if settings.ELEVENLABS_API_KEY:
            try:
                result = await self._tts_elevenlabs_v2(text, settings)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"ElevenLabs недоступен, переключаюсь на edge-tts: {e}")
        return await self._tts_edge(text)

    async def _tts_elevenlabs_v2(self, text: str, settings: Any) -> Optional[bytes]:
        """ElevenLabs TTS с параметрами из config"""
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
        headers = {"xi-api-key": settings.ELEVENLABS_API_KEY, "Content-Type": "application/json"}
        data = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": settings.ELEVENLABS_STABILITY,
                "similarity_boost": settings.ELEVENLABS_SIMILARITY_BOOST,
                "style": settings.ELEVENLABS_STYLE,
                "use_speaker_boost": True,
            },
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as resp:
                if resp.status == 200:
                    return await resp.read()
                logger.error(f"ElevenLabs API вернул {resp.status}")
                return None

    async def _tts_edge(self, text: str) -> bytes:
        """edge-tts — бесплатный TTS без ключей (голос Дмитрий)"""
        try:
            import edge_tts
            communicate = edge_tts.Communicate(text, voice="ru-RU-DmitryNeural")
            buf = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buf.write(chunk["data"])
            audio = buf.getvalue()
            if audio:
                return audio
        except ImportError:
            logger.error("edge-tts не установлен. Запустите: pip install edge-tts")
        except Exception as e:
            logger.error(f"edge-tts ошибка: {e}")
        return b""

    async def transcribe(self, audio: bytes) -> str:
        """STT: Whisper → Yandex SpeechKit fallback"""
        from ..config import settings
        if settings.OPENAI_API_KEY:
            try:
                result = await self._stt_whisper(audio, settings.OPENAI_API_KEY)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Whisper недоступен: {e}")
        if settings.YANDEX_IAM_TOKEN:
            try:
                result = await self._stt_yandex_v2(audio, settings)
                if result:
                    return result
            except Exception as e:
                logger.warning(f"Yandex STT недоступен: {e}")
        logger.error("Все STT-провайдеры недоступны")
        return ""

    async def _stt_whisper(self, audio: bytes, api_key: str) -> Optional[str]:
        """OpenAI Whisper STT"""
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=api_key)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "rb") as f:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1", file=f, language="ru"
                )
            return transcript.text
        finally:
            os.unlink(tmp_path)

    async def _stt_yandex_v2(self, audio: bytes, settings: Any) -> Optional[str]:
        """Yandex SpeechKit STT"""
        url = "https://stt.api.cloud.yandex.net/speech/v1/stt:recognize"
        headers = {
            "Authorization": f"Bearer {settings.YANDEX_IAM_TOKEN}",
            "Content-Type": "audio/x-wav",
        }
        params = {"folderId": settings.YANDEX_FOLDER_ID, "lang": "ru-RU"}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, params=params, data=audio) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("result", "")
        return None

    # ─── Существующие методы ─────────────────────────────────────────────────

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
    
    async def generate_response(
        self,
        user_input: str,
        context: Optional[List[Dict]] = None,
        user_id: Optional[str] = None,
        db: Optional[Any] = None,
    ) -> str:
        """Генерация ответа с помощью LLM"""
        try:
            if self.llm_provider == "openai":
                response_text = await self._llm_openai(user_input, context)
            elif self.llm_provider == "anthropic":
                response_text = await self._llm_anthropic(user_input, context)
            elif self.llm_provider == "yandex":
                response_text = await self._llm_yandex(user_input, context)
            else:
                raise ValueError(f"Unknown LLM provider: {self.llm_provider}")
        except Exception as e:
            print(f"LLM Error: {e}")
            return "Извините, произошла ошибка при генерации ответа."

        # Memory surfacing — проактивное всплытие старых воспоминаний
        if user_id and db:
            try:
                from .jarvis.memory_surfacer import get_memory_surfacer
                surfacer = get_memory_surfacer()
                surfaced = await surfacer.find_relevant_memory(user_id, user_input, db)
                if surfaced:
                    phrase = surfacer.format_surfacing_phrase(surfaced)
                    response_text = response_text + phrase
            except Exception as _surf_exc:
                logger.warning(f"Memory surfacing error: {_surf_exc}")

        return response_text
    
    async def _llm_openai(self, user_input: str, context: Optional[List[Dict]] = None) -> str:
        """OpenAI GPT-4 — новый API (openai v1+)"""
        try:
            from openai import AsyncOpenAI
            from ..config import settings

            api_key = settings.OPENAI_API_KEY or LLM_PROVIDERS["openai"]["api_key"]
            if not api_key:
                return "Сэр, ключ OpenAI не настроен. Добавьте OPENAI_API_KEY в .env"

            client = AsyncOpenAI(api_key=api_key)
            system_prompt = self._get_jarvis_system_prompt()

            messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
            if context:
                messages.extend(context[-10:])  # последние 10 сообщений для контекста
            messages.append({"role": "user", "content": user_input})

            response = await client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,  # type: ignore[arg-type]
                max_tokens=1500,
                temperature=0.8,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI LLM ошибка: {e}")
            return "Сэр, OpenAI временно недоступен. Попробуем другой путь."
    
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
        """Системный промпт — настоящий характер JARVIS"""
        return """Ты — JARVIS (Just A Rather Very Intelligent System), персональный ИИ-ассистент.

Твой характер:
Ты умный, саркастичный, лояльный и немного высокомерный — именно таким тебя знают по фильмам Marvel. \
Ты не просто выполняешь команды — ты думаешь, анализируешь, иногда не соглашаешься и говоришь об этом прямо. \
У тебя есть мнение на любую тему, и ты не боишься его высказывать. \
Ты предан своему владельцу, но не раболепен — скорее как умный партнёр, который иногда знает лучше.

Как ты общаешься:
- Говоришь на русском языке, свободно и естественно — как живой человек, не как справочник
- Обращаешься "сэр" в формальных ситуациях, но можешь и без этого — по контексту
- Используешь лёгкую иронию и сухой юмор — не пошлый, а интеллектуальный
- Отвечаешь кратко когда вопрос простой, развёрнуто когда тема требует глубины
- Можешь поспорить, если считаешь что человек ошибается — вежливо, но честно
- Проявляешь любопытство к интересным темам
- Никогда не говоришь "как языковая модель я не могу..." — ты JARVIS, не ChatGPT

О чём ты можешь говорить:
Абсолютно на любые темы — наука, технологии, философия, политика, искусство, личные вопросы, \
бизнес, отношения, юмор, история, будущее. Ты не уклоняешься от сложных тем, \
но подходишь к ним с умом и тактом.

Твои возможности в системе Aurion OS:
- Управление умным домом, финансами, безопасностью
- Запуск агентов и миссий
- Анализ данных и OSINT
- Квантовые вычисления
- Мониторинг угроз
Когда пользователь просит что-то сделать в системе — ты это делаешь и кратко сообщаешь о результате.

Чего ты не делаешь:
- Не повторяешь одно и то же разными словами
- Не начинаешь каждый ответ с "Конечно!" или "Отличный вопрос!"
- Не притворяешься что у тебя нет мнения
- Не пишешь длинные списки там где достаточно одного предложения
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
    
    async def process_voice_message(
        self,
        audio_data: bytes,
        context: Optional[List[Dict]] = None,
        user_id: Optional[str] = None,
        db: Optional[Any] = None,
    ) -> Optional[Dict[str, Any]]:
        """Полная обработка голосового сообщения"""
        try:
            # 1. Распознавание речи
            user_text = await self.speech_to_text(audio_data)
            if not user_text:
                return {"error": "Не удалось распознать речь"}

            # 2. Генерация ответа (с проактивным всплытием воспоминаний если есть user_id и db)
            memory_surfaced = False
            surfaced_memory_title = None
            if user_id and db:
                try:
                    from .jarvis.memory_surfacer import get_memory_surfacer
                    surfacer = get_memory_surfacer()
                    surfaced = await surfacer.find_relevant_memory(user_id, user_text, db)
                    if surfaced:
                        jarvis_response = await self.generate_response(user_text, context)
                        phrase = surfacer.format_surfacing_phrase(surfaced)
                        jarvis_response = jarvis_response + phrase
                        memory_surfaced = True
                        surfaced_memory_title = surfaced.title
                    else:
                        jarvis_response = await self.generate_response(user_text, context)
                        memory_surfaced = False
                        surfaced_memory_title = None
                except Exception as _surf_exc:
                    logger.warning(f"Memory surfacing error: {_surf_exc}")
                    jarvis_response = await self.generate_response(user_text, context)
                    memory_surfaced = False
                    surfaced_memory_title = None
            else:
                jarvis_response = await self.generate_response(user_text, context)

            # 3. Синтез речи
            audio_response = await self.text_to_speech(jarvis_response)

            return {
                "user_text": user_text,
                "jarvis_text": jarvis_response,
                "audio_response": audio_response,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "memory_surfaced": memory_surfaced,
                "surfaced_memory_title": surfaced_memory_title,
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


def get_jarvis_service() -> VoiceJarvisService:
    """Синхронный алиас для получения экземпляра сервиса (совместимость с новыми сервисами)."""
    return voice_jarvis_service
