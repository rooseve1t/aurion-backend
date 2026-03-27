"""
Property-тесты для EvolutionEngine:
- XP никогда не убывает при начислении
- Стадия никогда не понижается
"""
import pytest
from hypothesis import given, settings as h_settings, strategies as st
from unittest.mock import MagicMock, AsyncMock


def make_engine():
    """Создаёт EvolutionEngine с моками зависимостей."""
    from app.services.jarvis.evolution_engine import EvolutionEngine, EvolutionStage

    personality = MagicMock()
    personality.traits = {}
    autonomy = MagicMock()
    autonomy.registered_actions = {}

    engine = EvolutionEngine(
        personality_engine=personality,
        autonomy_engine=autonomy,
        redis_client=None,  # без Redis для тестов
    )
    return engine


@pytest.mark.asyncio
async def test_xp_never_decreases_on_add():
    """XP не убывает при начислении положительных очков."""
    engine = make_engine()
    assert engine.experience_points == 0

    for points in [10, 25, 5, 15, 50, 1, 100]:
        before = engine.experience_points
        await engine.add_experience(points)
        assert engine.experience_points >= before, (
            f"XP уменьшился: было {before}, стало {engine.experience_points}"
        )


@pytest.mark.asyncio
async def test_stage_never_decreases():
    """Стадия эволюции никогда не понижается."""
    from app.services.jarvis.evolution_engine import EvolutionStage

    engine = make_engine()
    stage_order = [
        EvolutionStage.SEED,
        EvolutionStage.LEARNING,
        EvolutionStage.ADAPTIVE,
        EvolutionStage.AUTONOMOUS,
        EvolutionStage.TRANSCENDENT,
    ]

    prev_index = 0
    # Начисляем XP большими порциями и проверяем что стадия только растёт
    for xp_chunk in [500, 1500, 3000, 5000, 10000]:
        await engine.add_experience(xp_chunk)
        current_index = stage_order.index(engine.stage)
        assert current_index >= prev_index, (
            f"Стадия понизилась: {stage_order[prev_index].value} → {engine.stage.value}"
        )
        prev_index = current_index


@pytest.mark.asyncio
@given(points_list=st.lists(st.integers(min_value=1, max_value=1000), min_size=1, max_size=50))
@h_settings(max_examples=30)
async def test_xp_monotonically_increases_property(points_list):
    """Property-тест: при любой последовательности начислений XP монотонно растёт."""
    import asyncio
    engine = make_engine()
    prev_xp = 0

    for points in points_list:
        await engine.add_experience(points)
        assert engine.experience_points >= prev_xp
        prev_xp = engine.experience_points
