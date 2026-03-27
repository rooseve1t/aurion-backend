"""
🧪 Тесты для эмоционального JARVIS
Проверка всех компонентов Phase 1
"""
import asyncio
import pytest
import os
from unittest.mock import Mock, patch, AsyncMock
import json

# Импортируем наши модули
from app.services.jarvis.emotional_tts import EmotionalTTS, JARVISEmotion
from app.services.jarvis.personality_engine import JARVISPersonalityEngine, PersonalityTrait
from app.services.jarvis.enhanced_voice_service import EnhancedVoiceJarvisService

class TestEmotionalTTS:
    """Тесты эмоционального TTS"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.tts = EmotionalTTS()
        
    def test_emotion_enum(self):
        """Тест enum эмоций"""
        assert len(JARVISEmotion) == 8
        assert JARVISEmotion.SARCASTIC.value == "sarcastic"
        assert JARVISEmotion.CARING.value == "caring"
        
    def test_emotion_presets(self):
        """Тест пресетов эмоций"""
        assert len(self.tts.emotion_presets) == 8
        assert "stability" in self.tts.emotion_presets[JARVISEmotion.NEUTRAL]
        assert "similarity_boost" in self.tts.emotion_presets[JARVISEmotion.SARCASTIC]
        
    def test_sarcasm_levels(self):
        """Тест уровней сарказма"""
        self.tts.set_sarcasm_level(0.5)
        assert self.tts.personality.sarcasm_level == 0.5
        
        self.tts.set_sarcasm_level(1.5)  # Должен ограничиться
        assert self.tts.personality.sarcasm_level == 1.0
        
        self.tts.set_sarcasm_level(-0.5)  # Должен ограничиться
        assert self.tts.personality.sarcasm_level == 0.0
        
    @patch('aiohttp.ClientSession.post')
    async def test_synthesize_with_emotion(self, mock_post):
        """Тест синтеза с эмоцией"""
        # Мок ответа от ElevenLabs
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=b"fake_audio_data")
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Тест синтеза
        audio = await self.tts.synthesize_with_emotion(
            "Hello sir", 
            JARVISEmotion.SARCASTIC
        )
        
        assert audio == b"fake_audio_data"
        
        # Проверить что был вызван API
        mock_post.assert_called_once()
        
    def test_get_available_emotions(self):
        """Тест получения доступных эмоций"""
        emotions = self.tts.get_available_emotions()
        assert len(emotions) == 8
        assert "sarcastic" in emotions
        assert "caring" in emotions

class TestPersonalityEngine:
    """Тесты движка личности"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.engine = JARVISPersonalityEngine()
        
    def test_initial_traits(self):
        """Тест начальных черт личности"""
        assert len(self.engine.traits) == 8
        assert self.engine.traits[PersonalityTrait.SARCASTIC] == 0.7
        assert self.engine.traits[PersonalityTrait.CARING] == 0.8
        assert self.engine.traits[PersonalityTrait.LOYAL] == 1.0
        
    def test_extract_intent(self):
        """Тест извлечения намерений"""
        assert self.engine._extract_intent("привет джарвис") == "greeting"
        assert self.engine._extract_intent("как дела джарвис") == "status_report"
        assert self.engine._extract_intent("включи впн") == "vpn_command"
        assert self.engine._extract_intent("помоги мне") == "help_request"
        assert self.engine._extract_intent("спасибо") == "gratitude"
        
    def test_detect_emotion(self):
        """Тест определения эмоций"""
        assert self.engine._detect_emotion("спасибо большое") == "grateful"
        assert self.engine._detect_emotion("у меня проблема") == "frustrated"
        assert self.engine._detect_emotion("срочно помоги") == "urgent"
        assert self.engine._detect_emotion("отлично работает") == "happy"
        assert self.engine._detect_emotion("обычный текст") == "neutral"
        
    def test_assess_complexity(self):
        """Тест оценки сложности"""
        assert self.engine._assess_complexity("привет") == "simple"
        assert self.engine._assess_complexity("как дела сегодня") == "medium"
        assert self.engine._assess_complexity("это очень длинное предложение с множеством слов и подробным описанием") == "complex"
        
    def test_choose_response_style(self):
        """Тест выбора стиля ответа"""
        # Стрессовый пользователь
        analysis = {"user_state": "stressed", "urgency": 0.2}
        style = self.engine._choose_response_style(analysis)
        assert style == "caring"
        
        # Срочный запрос
        analysis = {"urgency": 0.8, "user_state": "normal"}
        style = self.engine._choose_response_style(analysis)
        assert style == "professional"
        
        # Благодарный пользователь
        analysis = {"emotion": "grateful", "urgency": 0.1}
        style = self.engine._choose_response_style(analysis)
        assert style == "friendly"
        
    def test_generate_response(self):
        """Тест генерации ответа"""
        response = self.engine.generate_response("привет джарвис")
        
        assert "text" in response
        assert "emotion" in response
        assert "style" in response
        assert "traits_used" in response
        assert "confidence" in response
        
        assert isinstance(response["text"], str)
        assert len(response["text"]) > 0
        
    def test_set_trait_level(self):
        """Тест установки уровня черт"""
        self.engine.set_trait_level(PersonalityTrait.SARCASTIC, 0.9)
        assert self.engine.traits[PersonalityTrait.SARCASTIC] == 0.9
        
        # Тест ограничений
        self.engine.set_trait_level(PersonalityTrait.SARCASTIC, 2.0)
        assert self.engine.traits[PersonalityTrait.SARCASTIC] == 1.0
        
    def test_add_inside_joke(self):
        """Тест добавления внутренних шуток"""
        joke = "Почему программисты считают Halloween и Christmas одинаковыми?"
        self.engine.add_inside_joke(joke)
        
        assert joke in self.engine.user_profile["inside_jokes"]
        assert len(self.engine.user_profile["inside_jokes"]) == 1
        
    def test_personality_summary(self):
        """Тест сводки личности"""
        summary = self.engine.get_personality_summary()
        
        assert "traits" in summary
        assert "user_profile" in summary
        assert "current_mood" in summary
        assert "response_count" in summary
        
        assert len(summary["traits"]) == 8

class TestEnhancedVoiceService:
    """Тесты улучшенного голосового сервиса"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.mock_websocket = Mock()
        self.service = EnhancedVoiceJarvisService(self.mock_websocket, "test_user")
        
    @pytest.mark.asyncio
    async def test_initialize(self):
        """Тест инициализации"""
        await self.service.initialize()
        
        assert self.service.emotional_tts is not None
        assert self.service.personality_engine is not None
        assert self.service.interaction_count == 0
        
    @pytest.mark.asyncio
    async def test_get_emotional_status(self):
        """Тест получения эмоционального статуса"""
        await self.service.initialize()
        
        status = await self.service.get_emotional_status()
        
        assert "current_mood" in status
        assert "traits" in status
        assert "interaction_count" in status
        assert "emotion_distribution" in status
        assert "user_relationship" in status
        
    @pytest.mark.asyncio
    async def test_adjust_personality(self):
        """Тест настройки личности"""
        await self.service.initialize()
        
        adjustments = {"sarcastic": 0.9, "caring": 0.5}
        result = await self.service.adjust_personality(adjustments)
        
        assert "success" in result
        assert result["success"] is True
        assert "updated_traits" in result
        assert "current_traits" in result
        
    @pytest.mark.asyncio
    async def test_add_inside_joke(self):
        """Тест добавления внутренней шутки"""
        await self.service.initialize()
        
        joke = "Тестовая шутка"
        result = await self.service.add_inside_joke(joke)
        
        assert result["success"] is True
        assert result["joke_added"] == joke
        assert result["total_jokes"] == 1
        
    @pytest.mark.asyncio
    async def test_get_available_emotions(self):
        """Тест получения доступных эмоций"""
        await self.service.initialize()
        
        emotions = await self.service.get_available_emotions()
        
        assert len(emotions) == 8
        assert "sarcastic" in emotions
        
    @pytest.mark.asyncio
    async def test_set_sarcasm_level(self):
        """Тест установки уровня сарказма"""
        await self.service.initialize()
        
        result = await self.service.set_sarcasm_level(0.8)
        
        assert result["success"] is True
        assert result["sarcasm_level"] == 0.8
        
    @patch('aiohttp.ClientSession.post')
    @pytest.mark.asyncio
    async def test_emotion_test(self, mock_post):
        """Тест эмоции"""
        await self.service.initialize()
        
        # Мок ответа от ElevenLabs
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.read = AsyncMock(return_value=b"test_audio")
        mock_post.return_value.__aenter__.return_value = mock_response
        
        result = await self.service.test_emotion("sarcastic", "Test message")
        
        assert result["success"] is True
        assert result["emotion"] == "sarcastic"
        assert result["text"] == "Test message"
        assert "audio" in result
        assert "audio_size" in result

# Интеграционные тесты
class TestIntegration:
    """Интеграционные тесты"""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Тест полного pipeline"""
        mock_websocket = Mock()
        service = EnhancedVoiceJarvisService(mock_websocket, "test_user")
        await service.initialize()
        
        # Тест генерации ответа
        response = service.personality_engine.generate_response(
            "джарвис как дела",
            {"urgency": 0.2, "user_state": "normal"}
        )
        
        assert response["text"] is not None
        assert len(response["text"]) > 0
        
        # Тест определения эмоции
        emotion = service.personality_engine._determine_response_emotion(
            {"urgency": 0.2, "user_state": "normal"}
        )
        assert emotion in ["neutral", "sarcastic", "caring", "serious"]

# Performance тесты
class TestPerformance:
    """Тесты производительности"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.engine = JARVISPersonalityEngine()
        
    def test_response_generation_speed(self):
        """Тест скорости генерации ответа"""
        import time
        
        start_time = time.time()
        
        for _ in range(100):
            self.engine.generate_response("тестовое сообщение")
            
        end_time = time.time()
        avg_time = (end_time - start_time) / 100
        
        # Должно быть быстрее 10ms на ответ
        assert avg_time < 0.01, f"Too slow: {avg_time:.4f}s per response"
        
    def test_emotion_detection_speed(self):
        """Тест скорости определения эмоций"""
        import time
        
        test_texts = [
            "спасибо большое",
            "у меня проблема",
            "срочно помоги",
            "отлично работает",
            "обычный текст"
        ] * 20
        
        start_time = time.time()
        
        for text in test_texts:
            self.engine._detect_emotion(text)
            
        end_time = time.time()
        avg_time = (end_time - start_time) / len(test_texts)
        
        # Должно быть быстрее 1ms на определение
        assert avg_time < 0.001, f"Too slow: {avg_time:.4f}s per detection"

# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
