"""
Тесты для VoiceJarvisService — edge-tts fallback и STT.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.mark.asyncio
async def test_synthesize_uses_edge_tts_when_no_elevenlabs_key():
    """При отсутствии ELEVENLABS_API_KEY должен использоваться edge-tts и возвращать непустые байты."""
    from app.services.voice_jarvis_service import VoiceJarvisService

    service = VoiceJarvisService()

    # Мокаем settings — ключа нет
    mock_settings = MagicMock()
    mock_settings.ELEVENLABS_API_KEY = ""

    # Мокаем edge-tts — возвращает тестовые байты
    fake_audio = b"\xff\xfb\x90\x00" * 100  # минимальный MP3-заголовок

    async def fake_stream():
        yield {"type": "audio", "data": fake_audio}

    mock_communicate = MagicMock()
    mock_communicate.stream = fake_stream

    with patch("app.services.voice_jarvis_service.VoiceJarvisService._tts_edge",
               new_callable=AsyncMock, return_value=fake_audio):
        with patch("app.config.settings", mock_settings):
            result = await service.synthesize("Привет, сэр.")

    assert isinstance(result, bytes)
    assert len(result) > 0


@pytest.mark.asyncio
async def test_synthesize_uses_elevenlabs_when_key_present():
    """При наличии ELEVENLABS_API_KEY должен вызываться ElevenLabs, не edge-tts."""
    from app.services.voice_jarvis_service import VoiceJarvisService

    service = VoiceJarvisService()

    mock_settings = MagicMock()
    mock_settings.ELEVENLABS_API_KEY = "test-key-123"
    mock_settings.ELEVENLABS_VOICE_ID = "pNInz6obpgDQGcFmaJgB"
    mock_settings.ELEVENLABS_STABILITY = 0.75
    mock_settings.ELEVENLABS_SIMILARITY_BOOST = 0.85
    mock_settings.ELEVENLABS_STYLE = 0.2

    fake_audio = b"elevenlabs-audio-data"

    with patch("app.services.voice_jarvis_service.VoiceJarvisService._tts_elevenlabs_v2",
               new_callable=AsyncMock, return_value=fake_audio) as mock_el:
        with patch("app.config.settings", mock_settings):
            result = await service.synthesize("Тест.")

    mock_el.assert_called_once()
    assert result == fake_audio


@pytest.mark.asyncio
async def test_transcribe_returns_empty_string_when_no_providers():
    """При отсутствии всех STT-ключей должна возвращаться пустая строка."""
    from app.services.voice_jarvis_service import VoiceJarvisService

    service = VoiceJarvisService()

    mock_settings = MagicMock()
    mock_settings.OPENAI_API_KEY = ""
    mock_settings.YANDEX_IAM_TOKEN = ""

    with patch("app.config.settings", mock_settings):
        result = await service.transcribe(b"fake-audio")

    assert result == ""


@pytest.mark.asyncio
async def test_transcribe_uses_whisper_when_openai_key_present():
    """При наличии OPENAI_API_KEY должен использоваться Whisper."""
    from app.services.voice_jarvis_service import VoiceJarvisService

    service = VoiceJarvisService()

    mock_settings = MagicMock()
    mock_settings.OPENAI_API_KEY = "sk-test"
    mock_settings.YANDEX_IAM_TOKEN = ""

    with patch("app.services.voice_jarvis_service.VoiceJarvisService._stt_whisper",
               new_callable=AsyncMock, return_value="Привет JARVIS") as mock_whisper:
        with patch("app.config.settings", mock_settings):
            result = await service.transcribe(b"audio")

    mock_whisper.assert_called_once()
    assert result == "Привет JARVIS"
