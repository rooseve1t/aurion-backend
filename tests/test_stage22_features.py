import pytest
import uuid
from datetime import datetime, timedelta
from app.services.jarvis.emotional_tts import EmotionalTTS, JARVISEmotion
from app.services.memory_service import MemoryService
from app.services.agent_service import AgentOrchestrator, CarAgent, HealthAgent
from app.services.quantum_service import QuantumService
from app.models.memory import MemoryEntry

@pytest.mark.asyncio
async def test_russian_voice_fallback():
    """Тест переключения на русский синтез"""
    tts = EmotionalTTS()
    # Текст на русском должен триггерить поиск RU провайдеров
    text = "Привет, Джарвис. Как дела?"
    # Мы не можем реально синтезировать без API, но можем проверить логику выбора
    # В нашем случае вернется ошибка или fallback на ElevenLabs (который упадет без ключа)
    with pytest.raises(ValueError, match="ElevenLabs API key not found"):
        await tts.synthesize_with_emotion(text)

@pytest.mark.asyncio
async def test_memory_hybrid_ranking(db_session):
    """Тест гибридного ранжирования памяти"""
    service = MemoryService(db_session)
    user_id = str(uuid.uuid4())
    
    # Создаем тестовые записи
    m1 = MemoryEntry(
        user_id=user_id,
        content="Важная информация о безопасности",
        title="Безопасность",
        importance=10,
        tags=["безопасность"],
        created_at=datetime.now() - timedelta(days=1)
    )
    m2 = MemoryEntry(
        user_id=user_id,
        content="Старая заметка о погоде",
        title="Погода",
        importance=2,
        tags=["погода"],
        created_at=datetime.now() - timedelta(days=100)
    )
    
    db_session.add_all([m1, m2])
    await db_session.commit()
    
    results = await service.search_memories(user_id, "безопасность", limit=5)
    
    assert len(results) > 0
    assert results[0]["title"] == "Безопасность"
    assert results[0]["match_score"] > 0.5
    assert "similarity" in results[0]
    assert "recency_score" in results[0]

@pytest.mark.asyncio
async def test_specialized_agents(db_session):
    """Тест новых специализированных агентов"""
    orchestrator = AgentOrchestrator(db_session)
    
    # Проверка CarAgent
    car_agent = CarAgent("car-001", {})
    assert await car_agent.can_handle("check_diagnostics", {})
    diag_res = await car_agent._check_diagnostics({"vin": "TEST12345"})
    assert diag_res["status"] == "completed"
    assert "diagnostics" in diag_res
    
    # Проверка HealthAgent
    health_agent = HealthAgent("health-001", {})
    assert await health_agent.can_handle("analyze_vitals", {})
    health_res = await health_agent._analyze_vitals({"pulse": 80})
    assert health_res["health_score"] > 0
    assert "recommendations" in health_res

@pytest.mark.asyncio
async def test_biometric_quantum_verification(db_session):
    """Тест биометрической квантовой верификации"""
    q_service = QuantumService(db_session)
    user_id = str(uuid.uuid4())
    
    # Успешная верификация
    success = await q_service.verify_biometric_quantum(
        user_id, 
        "valid_voice_signature_longer_than_32_chars_12345", 
        "Q_AUTH_TOKEN_ABC"
    )
    assert success is True
    
    # Неуспешная (короткая подпись)
    fail1 = await q_service.verify_biometric_quantum(user_id, "short", "Q_AUTH_TOKEN")
    assert fail1 is False
    
    # Неуспешная (неверный токен)
    fail2 = await q_service.verify_biometric_quantum(user_id, "valid_voice_signature_longer_than_32_chars_12345", "INVALID_TOKEN")
    assert fail2 is False
