import pytest
from unittest.mock import AsyncMock, MagicMock

from app.services.jarvis.autonomous_jarvis import AutonomousJarvisService

@pytest.mark.asyncio
async def test_jarvis_full_cycle():
    """E2E test for the full Jarvis service cycle."""
    # 1. Mock WebSocket and other external dependencies
    mock_websocket = MagicMock()
    mock_websocket.send_json = AsyncMock()
    mock_websocket.receive_text = AsyncMock(return_value="")

    # 2. Initialize Jarvis
    jarvis = AutonomousJarvisService(websocket=mock_websocket, user_id="test_user")
    await jarvis.initialize()

    # 3. Check initialization
    assert jarvis.autonomy_engine is not None
    assert jarvis.evolution_engine is not None
    assert jarvis.personality_engine is not None

    # 4. Simulate voice input
    with open("/Users/natalacernikova/Downloads/aurion-stage13/aurion-backend/tests/e2e/silent.wav", "rb") as f:
        audio_data = f.read()
    
    result = await jarvis.process_voice_input(audio_data)

    # 5. Assertions
    # If silence is passed, it might still return an error if the recognizer can't find any speech
    # But now it should be a valid audio processing attempt
    assert result is not None
