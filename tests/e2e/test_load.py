import asyncio
import time
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.jarvis.autonomous_jarvis import AutonomousJarvisService

@pytest.mark.asyncio
async def test_load_concurrent_requests():
    """Load test for concurrent Jarvis requests."""
    num_concurrent = 10
    
    # Mock setup
    mock_websocket = MagicMock()
    mock_websocket.send_json = AsyncMock()
    
    # Shared service
    jarvis = AutonomousJarvisService(websocket=mock_websocket, user_id="load_test_user")
    await jarvis.initialize()
    
    with open("/Users/natalacernikova/Downloads/aurion-stage13/aurion-backend/tests/e2e/silent.wav", "rb") as f:
        audio_data = f.read()
    
    async def single_request(i):
        start_time = time.time()
        result = await jarvis.process_voice_input(audio_data)
        duration = time.time() - start_time
        return i, result, duration

    # Run concurrently
    tasks = [single_request(i) for i in range(num_concurrent)]
    results = await asyncio.gather(*tasks)
    
    # Assertions
    for i, result, duration in results:
        assert result is not None
        print(f"Request {i} took {duration:.2f}s")
    
    print(f"All {num_concurrent} requests completed.")
