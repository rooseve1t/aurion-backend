"""
🧠 Personality Engine для JARVIS
Создает уникальный характер и стиль общения
"""
import logging
import random
import json
import time
import hashlib
from enum import Enum
from typing import Dict, Any, List, Optional, cast
from pathlib import Path

from ..memory_service import MemoryService
from ..quantum_service import QuantumService
from ...models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Настройка логгера
logger = logging.getLogger(__name__)

class PersonalityTrait(Enum):
    """Черты личности JARVIS"""
    SARCASTIC = "sarcastic"
    CARING = "caring"
    PROFESSIONAL = "professional"
    WITTY = "witty"
    LOYAL = "loyal"
    PROUD = "proud"
    CURIOUS = "curious"
    PROTECTIVE = "protective"
    IRONIC = "ironic"
    SNOBBY = "snobby"

class ResponseStyle(Enum):
    """Стили ответов"""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"
    HUMOROUS = "humorous"

class JARVISPersonalityEngine:
    """Основной движок личности JARVIS (Stage 22: Emotional Intelligence)"""
    
    def __init__(self, db: Optional[AsyncSession] = None, memory_service: Optional[MemoryService] = None, quantum_service: Optional[QuantumService] = None) -> None:
        self.db = db
        self.memory_service = memory_service
        self.quantum_service = quantum_service
        self.traits: Dict[PersonalityTrait, float] = {
            PersonalityTrait.SARCASTIC: 0.7,
            PersonalityTrait.CARING: 0.8,
            PersonalityTrait.PROFESSIONAL: 0.9,
            PersonalityTrait.WITTY: 0.8,
            PersonalityTrait.LOYAL: 1.0,
            PersonalityTrait.PROUD: 0.6,
            PersonalityTrait.CURIOUS: 0.8,
            PersonalityTrait.PROTECTIVE: 0.95,
        }
        
        # Загрузка локализации
        self.locale_path = Path(__file__).parent / "locales" / "jarvis_ru.json"
        self.responses = self._load_responses()
        
        self.default_user_profile: Dict[str, Any] = {
            "name": "Сэр",
            "relationship_level": 1.0,
            "interaction_count": 0,
            "last_interaction": None,
            "preferences": {"response_style": "formal"},
            "inside_jokes": [],
            "frustration_level": 0.0,
            "emotional_state": "neutral",
            "efficiency_score": 1.0,
            "voice_tone": "neutral"
        }
        self.user_profile: Dict[str, Any] = self.default_user_profile.copy()
        
        self.current_mood: str = "ready"
        self._profiles_cache: Dict[str, Dict[str, Any]] = {}

    def _load_responses(self) -> Dict[str, Any]:
        """Загрузить шаблоны ответов из внешнего файла"""
        try:
            if self.locale_path.exists():
                with open(self.locale_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading locale file: {e}")
        return {}

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Получить профиль пользователя (Stage 22: Persistent Personality)"""
        if user_id in self._profiles_cache:
            return self._profiles_cache[user_id]
            
        # Загружаем из базы данных
        profile = self.default_user_profile.copy()
        
        if self.db:
            try:
                stmt = select(User).where(getattr(User, "id") == user_id)
                result = await self.db.execute(stmt)
                user = result.scalar_one_or_none()
                if user:
                    prefs = getattr(user, "preferences", {}) or {}
                    if "personality" in prefs:
                        profile.update(prefs["personality"])
                    
                    # Обновляем имя
                    display_name = getattr(user, "display_name", None)
                    if display_name:
                        profile["name"] = display_name
            except Exception as e:
                logger.error(f"Error loading profile from DB: {e}")

        self._profiles_cache[user_id] = profile
        return profile

    async def sync_emotional_state(self, user_id: str, emotion: str, confidence: float = 1.0):
        """Синхронизация эмоционального состояния (Stage 22: Neuro-Link)"""
        profile = await self.get_user_profile(user_id)
        
        # Обновляем состояние
        old_emotion = profile.get("emotional_state", "neutral")
        profile["emotional_state"] = emotion
        profile["interaction_count"] += 1
        profile["last_interaction"] = time.time()
        
        # Динамическая подстройка черт (EQ)
        if emotion in ["sad", "frustrated", "angry"]:
            profile["frustration_level"] = min(1.0, profile["frustration_level"] + 0.2 * confidence)
            self.traits[PersonalityTrait.SARCASTIC] = max(0.1, self.traits[PersonalityTrait.SARCASTIC] - 0.3)
            self.traits[PersonalityTrait.CARING] = min(1.0, self.traits[PersonalityTrait.CARING] + 0.2)
        else:
            profile["frustration_level"] = max(0.0, profile["frustration_level"] - 0.1)
            # Плавное возвращение к базовому уровню сарказма
            self.traits[PersonalityTrait.SARCASTIC] = min(0.85, self.traits[PersonalityTrait.SARCASTIC] + 0.05)
        
        # Сохранение "Эмоциональной памяти"
        if self.memory_service and confidence > 0.7:
            await self.memory_service.add_memory(
                user_id=user_id,
                content=f"Пользователь проявил эмоцию: {emotion}. Уровень фрустрации: {profile['frustration_level']:.2f}",
                title="Эмоциональный резонанс",
                tags=["emotion", "personality_sync", emotion],
                categories=["emotional_memory"],
                importance=int(profile["frustration_level"] * 10)
            )

        # Сохранение в настройки пользователя для персистентности
        if self.db:
            try:
                stmt = select(User).where(getattr(User, "id") == user_id)
                result = await self.db.execute(stmt)
                user = result.scalar_one_or_none()
                if user:
                    prefs = getattr(user, "preferences", {}) or {}
                    prefs["personality"] = {
                        "frustration_level": profile["frustration_level"],
                        "emotional_state": profile["emotional_state"],
                        "last_interaction": profile["last_interaction"],
                        "interaction_count": profile["interaction_count"]
                    }
                    setattr(user, "preferences", prefs)
                    await self.db.commit()
            except Exception as e:
                logger.error(f"Error saving profile to DB: {e}")
            
        logger.info(f"🧠 Personality Sync [{user_id}]: {old_emotion} -> {emotion}. Frustration: {profile['frustration_level']:.2f}")

    def generate_smart_comment(self, category: str, style: Optional[ResponseStyle] = None, user_id: Optional[str] = None) -> str:
        """Генерация комментария с учетом эмоционального контекста"""
        # Если есть user_id, можем адаптировать стиль
        target_style = style
        if user_id and user_id in self._profiles_cache:
            profile = self._profiles_cache[user_id]
            if profile.get("frustration_level", 0) > 0.5:
                target_style = ResponseStyle.FRIENDLY # Переключаемся на дружелюбный если сэр злится
        
        category_data: Any = self.responses.get(category)
        
        if isinstance(category_data, dict):
            style_key: str = target_style.value if target_style else "formal"
            data_dict: Dict[str, Any] = cast(Dict[str, Any], category_data)
            templates_raw: Any = data_dict.get(style_key, data_dict.get("formal", []))
            
            if isinstance(templates_raw, list) and templates_raw:
                # Cast to Any to satisfy Pylance
                templates: List[Any] = cast(List[Any], templates_raw)
                return str(random.choice(templates))
        
        return "Я здесь, сэр."

    async def verify_voice_signature(self, user_id: str, voice_features: Dict[str, Any]) -> bool:
        """Верификация голоса пользователя (Stage 22: Quantum VoiceID)"""
        logger.info(f"🎤 Analyzing voice signature (VoiceID) for {user_id}...")
        
        # 1. Извлечение биометрического хэша (имитация)
        voice_hash: str = str(voice_features.get("hash") or hashlib.sha256(str(voice_features).encode()).hexdigest())
        q_token: str = str(voice_features.get("q_token", "Q_AUTH_DEFAULT"))
        
        # 2. Делегирование квантовой проверке
        if self.quantum_service:
            return await self.quantum_service.verify_biometric_quantum(
                user_id=user_id,
                voice_signature=voice_hash,
                q_token=q_token
            )
            
        # Fallback если квантовый сервис не доступен
        return True

    def get_omni_protocol_response(self, device_action: str) -> str:
        """Реакция на физические действия устройств (Stage 20)"""
        protocol_responses: Dict[str, Any] = self.responses.get("omni_protocol", {})
        return protocol_responses.get(device_action, "Действие выполнено, сэр.")

    def set_style(self, user_id: str, style: ResponseStyle) -> None:
        """Сменить стиль ответов (Stage 21)"""
        if user_id in self._profiles_cache:
            self._profiles_cache[user_id]["preferences"]["response_style"] = style.value
        logger.info(f"🎭 JARVIS style for {user_id} -> {style.value}")

    def _extract_intent(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["привет", "здравствуй", "добрый"]):
            return "greeting"
        if any(w in text_lower for w in ["как дела", "статус"]):
            return "status_report"
        if any(w in text_lower for w in ["впн", "vpn"]):
            return "vpn_command"
        if any(w in text_lower for w in ["помоги", "помощь"]):
            return "help_request"
        if any(w in text_lower for w in ["спасибо", "благодарю"]):
            return "gratitude"
        return "general"

    def _detect_emotion(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ["спасибо", "благодарю"]):
            return "grateful"
        if any(w in text_lower for w in ["проблема", "ошибка", "не работает", "бесит"]):
            return "frustrated"
        if any(w in text_lower for w in ["срочно", "немедленно", "urgent"]):
            return "urgent"
        if any(w in text_lower for w in ["отлично", "супер", "круто", "хорошо"]):
            return "happy"
        return "neutral"

    def _assess_complexity(self, text: str) -> str:
        words = [w for w in text.split() if w.strip()]
        if len(words) <= 1:
            return "simple"
        if len(words) <= 4:
            return "medium"
        return "complex"

    def _choose_response_style(self, analysis: Dict[str, Any]) -> str:
        if analysis.get("user_state") == "stressed":
            return "caring"
        if float(analysis.get("urgency", 0.0)) >= 0.7:
            return "professional"
        if analysis.get("emotion") == "grateful":
            return "friendly"
        return "neutral"

    def _determine_response_emotion(self, analysis: Dict[str, Any]) -> str:
        style = self._choose_response_style(analysis)
        if style == "caring":
            return "caring"
        if style == "professional":
            return "serious"
        if style == "friendly":
            return "neutral"
        return "sarcastic" if self.traits.get(PersonalityTrait.SARCASTIC, 0.0) > 0.75 else "neutral"

    def analyze_user_input(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Анализ ввода пользователя (Stage 22)"""
        _ = context
        emotion = self._detect_emotion(text)
        sentiment = "positive" if emotion in {"happy", "grateful"} else ("negative" if emotion in {"frustrated", "urgent"} else "neutral")
        return {
            "intent": self._extract_intent(text),
            "emotion": emotion,
            "complexity": self._assess_complexity(text),
            "sentiment": sentiment,
            "urgency": 1.0 if "!" in text else 0.5
        }

    def generate_response(self, text: str, analysis: Optional[Dict[str, Any]] = None, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Генерация полноценного ответа с учетом личности (Stage 22)"""
        analysis_data = analysis or self.analyze_user_input(text, context)
        _ = context
        intent = analysis_data.get("intent", "general")
        style_name = self._choose_response_style(analysis_data)
        style = ResponseStyle.FRIENDLY if style_name == "friendly" else ResponseStyle.FORMAL
        text_response = self.generate_smart_comment(intent, style)
        emotion = self._determine_response_emotion(analysis_data)
        
        return {
            "text": text_response,
            "emotion": emotion,
            "style": style_name,
            "traits_used": [t.value for t in self.traits if self.traits[t] > 0.8],
            "confidence": 0.95
        }

    def get_personality_summary(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Сводка состояния личности (Stage 22)"""
        profile = self._profiles_cache.get(user_id or "sir", self.default_user_profile)
        return {
            "current_mood": self.current_mood,
            "traits": {t.value: round(v, 2) for t, v in self.traits.items()},
            "response_count": profile.get("interaction_count", 0),
            "user_profile": profile
        }

    def set_trait_level(self, trait: PersonalityTrait, level: float) -> None:
        """Ручная настройка черт (Stage 21)"""
        if trait in self.traits:
            self.traits[trait] = max(0.0, min(1.0, level))
            logger.info(f"⚙️ Trait {trait.value} set to {level}")

    def add_inside_joke(self, user_id: str, joke: Optional[str] = None) -> None:
        """Добавить локальную шутку (Stage 20)"""
        # Backward compatibility: old tests call add_inside_joke(joke)
        if joke is None:
            joke = str(user_id)
            user_id = "sir"

        if user_id in self._profiles_cache:
            profile = self._profiles_cache[user_id]
        else:
            profile = self.default_user_profile.copy()
            self._profiles_cache[user_id] = profile

        jokes = profile.get("inside_jokes")
        if not isinstance(jokes, list):
            jokes = []
            profile["inside_jokes"] = jokes
        
        # Cast to list to satisfy Pylance
        jokes_list: List[Any] = cast(List[Any], jokes)
        jokes_list.append(joke)
        self.user_profile = profile
        logger.info(f"🃏 New inside joke added for {user_id}")

    def update_emotional_resonance(self, emotion: str) -> None:
        """Подстройка тона (Legacy support)"""
        self.current_mood = emotion

    # ─── Публичные методы для задачи 4.5 ────────────────────────────────────

    def adapt_to_emotion(self, emotion: str) -> None:
        """Адаптирует черты личности под эмоцию пользователя.
        При frustrated/angry снижает sarcastic на 0.3, повышает caring на 0.2.
        """
        if emotion in ("frustrated", "angry"):
            self.traits[PersonalityTrait.SARCASTIC] = max(
                0.0, self.traits.get(PersonalityTrait.SARCASTIC, 0.7) - 0.3
            )
            self.traits[PersonalityTrait.CARING] = min(
                1.0, self.traits.get(PersonalityTrait.CARING, 0.8) + 0.2
            )
        elif emotion in ("happy", "grateful"):
            # Плавное восстановление сарказма
            self.traits[PersonalityTrait.SARCASTIC] = min(
                0.85, self.traits.get(PersonalityTrait.SARCASTIC, 0.7) + 0.1
            )
        self.current_mood = emotion
        logger.info(f"🎭 adapt_to_emotion({emotion}): sarcastic={self.traits[PersonalityTrait.SARCASTIC]:.2f}, caring={self.traits[PersonalityTrait.CARING]:.2f}")

    def format_response(self, text: str, style: str = "formal") -> str:
        """Форматирует текст ответа под стиль общения.
        Стили: formal, casual, technical, friendly, humorous.
        """
        if not text:
            return self.responses.get("fallback", "Я здесь, сэр.")

        sarcasm = self.traits.get(PersonalityTrait.SARCASTIC, 0.7)
        caring = self.traits.get(PersonalityTrait.CARING, 0.8)

        if style == "formal":
            # Добавляем «сэр» если его нет
            if "сэр" not in text.lower() and sarcasm < 0.5:
                text = text.rstrip(".!?") + ", сэр."
        elif style == "humorous" and sarcasm > 0.6:
            # Лёгкая ирония — ничего не меняем, LLM уже сделал своё дело
            pass
        elif style == "friendly" or caring > 0.85:
            # Убираем формальность
            text = text.replace(", сэр", "").replace(" сэр", "")

        return text


async def get_personality_engine() -> JARVISPersonalityEngine:
    return JARVISPersonalityEngine()
