"""
Property-тесты для PersonalityEngine:
- Веса черт личности всегда в диапазоне [0.0, 1.0]
- adapt_to_emotion корректно адаптирует черты
"""
import pytest
from hypothesis import given, settings as h_settings, strategies as st


def make_engine():
    from app.services.jarvis.personality_engine import JARVISPersonalityEngine
    return JARVISPersonalityEngine()


@pytest.mark.asyncio
async def test_adapt_to_emotion_frustrated_reduces_sarcasm():
    """При frustrated sarcastic снижается, caring повышается."""
    from app.services.jarvis.personality_engine import PersonalityTrait
    engine = make_engine()

    before_sarcastic = engine.traits[PersonalityTrait.SARCASTIC]
    before_caring = engine.traits[PersonalityTrait.CARING]

    engine.adapt_to_emotion("frustrated")

    assert engine.traits[PersonalityTrait.SARCASTIC] <= before_sarcastic
    assert engine.traits[PersonalityTrait.CARING] >= before_caring


@pytest.mark.asyncio
async def test_adapt_to_emotion_traits_stay_in_range():
    """После любой эмоции все черты остаются в [0.0, 1.0]."""
    from app.services.jarvis.personality_engine import PersonalityTrait
    engine = make_engine()

    for emotion in ["frustrated", "angry", "happy", "grateful", "neutral",
                    "frustrated", "angry", "happy", "frustrated"]:
        engine.adapt_to_emotion(emotion)
        for trait, value in engine.traits.items():
            assert 0.0 <= value <= 1.0, (
                f"Черта {trait.value} вышла за диапазон: {value}"
            )


@given(
    emotions=st.lists(
        st.sampled_from(["frustrated", "angry", "happy", "grateful", "neutral"]),
        min_size=1,
        max_size=30,
    )
)
@h_settings(max_examples=50)
def test_traits_always_in_range_property(emotions):
    """Property-тест: любая последовательность эмоций не выводит черты за [0.0, 1.0]."""
    from app.services.jarvis.personality_engine import JARVISPersonalityEngine
    engine = JARVISPersonalityEngine()

    for emotion in emotions:
        engine.adapt_to_emotion(emotion)

    for trait, value in engine.traits.items():
        assert 0.0 <= value <= 1.0, f"{trait.value} = {value}"


def test_format_response_formal_adds_sir():
    """format_response в formal стиле добавляет 'сэр' если sarcasm низкий."""
    from app.services.jarvis.personality_engine import JARVISPersonalityEngine, PersonalityTrait
    engine = JARVISPersonalityEngine()
    engine.traits[PersonalityTrait.SARCASTIC] = 0.1  # низкий сарказм

    result = engine.format_response("Задача выполнена", style="formal")
    assert "сэр" in result.lower()


def test_format_response_returns_fallback_for_empty():
    """format_response возвращает fallback для пустой строки."""
    from app.services.jarvis.personality_engine import JARVISPersonalityEngine
    engine = JARVISPersonalityEngine()
    result = engine.format_response("", style="formal")
    assert len(result) > 0
