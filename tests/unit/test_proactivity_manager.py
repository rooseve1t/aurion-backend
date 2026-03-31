"""
Smoke-тесты для ProactiveEngine (proactivity_manager).
"""
import pytest
from app.services.jarvis.proactivity_manager import ProactiveEngine, get_proactive_engine


def test_get_proactive_engine_singleton():
    e1 = get_proactive_engine()
    e2 = get_proactive_engine()
    assert e1 is e2


def test_proactive_engine_instantiation():
    engine = ProactiveEngine()
    assert engine is not None
    assert engine._redis is None
    assert engine._ws_manager is None


def test_set_redis():
    engine = ProactiveEngine()
    engine.set_redis("fake_redis")
    assert engine._redis == "fake_redis"


def test_set_ws_manager():
    engine = ProactiveEngine()
    engine.set_ws_manager("fake_ws")
    assert engine._ws_manager == "fake_ws"


@pytest.mark.asyncio
async def test_subscribe_unsubscribe():
    """subscribe/unsubscribe не падают без Redis."""
    engine = ProactiveEngine()
    await engine.subscribe("user1")
    await engine.unsubscribe("user1")


@pytest.mark.asyncio
async def test_check_rate_limit_no_redis():
    """_check_rate_limit без Redis — разрешает (True)."""
    engine = ProactiveEngine()
    result = await engine._check_rate_limit("user1")
    assert result is True
