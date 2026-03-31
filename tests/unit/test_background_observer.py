"""
Smoke-тесты для BackgroundObserver.
"""
import pytest
from app.services.background_observer import (
    BackgroundObserver,
    EventDomain,
    EventPriority,
    ObservedEvent,
    get_observer,
)


def test_get_observer_singleton():
    obs1 = get_observer()
    obs2 = get_observer()
    assert obs1 is obs2


def test_background_observer_instantiation():
    obs = BackgroundObserver()
    assert obs is not None
    assert obs._redis is None


def test_set_redis():
    obs = BackgroundObserver()
    obs.set_redis("fake_redis")
    assert obs._redis == "fake_redis"


def test_result_to_event_finance_no_changes():
    obs = BackgroundObserver()
    result = obs._result_to_event(EventDomain.FINANCE, "user1", {"significant_changes": []})
    assert result is None


def test_result_to_event_finance_with_changes():
    obs = BackgroundObserver()
    result = obs._result_to_event(
        EventDomain.FINANCE, "user1", {"significant_changes": ["BTC +5%"]}
    )
    assert result is not None
    assert result.domain == EventDomain.FINANCE
    assert result.priority == EventPriority.HIGH
    assert result.user_id == "user1"


def test_result_to_event_health_normal():
    obs = BackgroundObserver()
    result = obs._result_to_event(EventDomain.HEALTH, "user1", {"heart_rate": 70})
    assert result is None  # нормальный пульс — нет события


def test_result_to_event_health_high():
    obs = BackgroundObserver()
    result = obs._result_to_event(EventDomain.HEALTH, "user1", {"heart_rate": 120})
    assert result is not None
    assert result.priority == EventPriority.HIGH


def test_result_to_event_security_threats():
    obs = BackgroundObserver()
    result = obs._result_to_event(
        EventDomain.SECURITY, "user1", {"threats": ["threat1", "threat2"]}
    )
    assert result is not None
    assert result.priority == EventPriority.CRITICAL


def test_result_to_event_calendar():
    obs = BackgroundObserver()
    result = obs._result_to_event(
        EventDomain.CALENDAR, "user1", {"events": ["meeting at 10am"]}
    )
    assert result is not None
    assert result.priority == EventPriority.MEDIUM


def test_result_to_event_empty_data():
    obs = BackgroundObserver()
    result = obs._result_to_event(EventDomain.FINANCE, "user1", {})
    assert result is None


@pytest.mark.asyncio
async def test_poll_once_no_redis():
    """poll_once без Redis — возвращает пустой список (все источники недоступны)."""
    obs = BackgroundObserver()
    events = await obs.poll_once("user_test")
    assert isinstance(events, list)


@pytest.mark.asyncio
async def test_stop_no_tasks():
    """stop без запущенных задач не падает."""
    obs = BackgroundObserver()
    await obs.stop()  # не должно бросать исключение
