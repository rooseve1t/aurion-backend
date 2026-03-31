"""
Smoke-тесты для DigitalTwinService.
"""
import pytest
from app.services.digital_twin import (
    DigitalTwinService,
    HealthMetrics,
    HealthPattern,
    get_digital_twin,
)


def test_get_digital_twin_singleton():
    t1 = get_digital_twin()
    t2 = get_digital_twin()
    assert t1 is t2


def test_digital_twin_instantiation():
    svc = DigitalTwinService()
    assert svc is not None
    assert svc._redis is None


def test_set_redis():
    svc = DigitalTwinService()
    svc.set_redis("fake_redis")
    assert svc._redis == "fake_redis"


def test_health_metrics_defaults():
    m = HealthMetrics()
    assert m.heart_rate is None
    assert m.steps is None
    assert m.source == "manual"


def test_health_metrics_with_values():
    m = HealthMetrics(heart_rate=72, steps=8000, sleep_hours=7.5, activity_minutes=45)
    assert m.heart_rate == 72
    assert m.steps == 8000


def test_calc_trend_improving():
    svc = DigitalTwinService()
    values = [50, 50, 50, 60, 60, 60]
    assert svc._calc_trend(values) == "improving"


def test_calc_trend_declining():
    svc = DigitalTwinService()
    values = [60, 60, 60, 50, 50, 50]
    assert svc._calc_trend(values) == "declining"


def test_calc_trend_stable():
    svc = DigitalTwinService()
    values = [60, 61, 60, 61, 60, 61]
    assert svc._calc_trend(values) == "stable"


def test_calc_trend_single_value():
    svc = DigitalTwinService()
    assert svc._calc_trend([100]) == "stable"


@pytest.mark.asyncio
async def test_get_live_metrics_no_redis_no_db():
    """get_live_metrics без Redis и без БД — возвращает None."""
    svc = DigitalTwinService()
    result = await svc.get_live_metrics("user_nonexistent_xyz")
    assert result is None


@pytest.mark.asyncio
async def test_get_patterns_no_data():
    """get_patterns без данных — возвращает пустой список."""
    svc = DigitalTwinService()
    patterns = await svc.get_patterns("user_nonexistent_xyz", "week")
    assert patterns == []


@pytest.mark.asyncio
async def test_get_recommendations_no_data():
    """get_recommendations без данных — возвращает дефолтный совет."""
    svc = DigitalTwinService()
    recs = await svc.get_recommendations("user_nonexistent_xyz")
    assert len(recs) >= 1
    assert "text" in recs[0]
