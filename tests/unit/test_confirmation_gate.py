"""
Smoke-тесты для ConfirmationGate.
"""
import pytest
from app.services.confirmation_gate import ConfirmationGate, get_confirmation_gate, CONFIRMATION_TTL


def test_get_confirmation_gate_singleton():
    g1 = get_confirmation_gate()
    g2 = get_confirmation_gate()
    assert g1 is g2


def test_confirmation_gate_instantiation():
    gate = ConfirmationGate()
    assert gate is not None
    assert gate._redis is None


def test_set_redis():
    gate = ConfirmationGate()
    gate.set_redis("fake_redis")
    assert gate._redis == "fake_redis"


def test_confirmation_ttl():
    assert CONFIRMATION_TTL == 300


@pytest.mark.asyncio
async def test_create_and_is_pending():
    """Создать подтверждение — is_pending возвращает True."""
    gate = ConfirmationGate()
    action_id = await gate.create_confirmation(
        "user1", "order_taxi", {"destination": "Airport"}
    )
    assert action_id is not None
    assert len(action_id) > 0
    pending = await gate.is_pending(action_id)
    assert pending is True


@pytest.mark.asyncio
async def test_confirm_action():
    """Подтвердить действие — is_pending становится False."""
    gate = ConfirmationGate()
    action_id = await gate.create_confirmation(
        "user1", "send_message", {"to": "Alice", "text": "Hello"}
    )
    result = await gate.confirm(action_id, "user1")
    assert result is True
    pending = await gate.is_pending(action_id)
    assert pending is False


@pytest.mark.asyncio
async def test_confirm_wrong_user():
    """Подтверждение от другого пользователя — отклоняется."""
    gate = ConfirmationGate()
    action_id = await gate.create_confirmation(
        "user1", "make_purchase", {"item": "laptop"}
    )
    result = await gate.confirm(action_id, "user2")
    assert result is False


@pytest.mark.asyncio
async def test_cancel_action():
    """Отменить действие — is_pending становится False."""
    gate = ConfirmationGate()
    action_id = await gate.create_confirmation(
        "user1", "reschedule_meeting", {"meeting_id": "abc"}
    )
    result = await gate.cancel(action_id, "user1")
    assert result is True
    pending = await gate.is_pending(action_id)
    assert pending is False


@pytest.mark.asyncio
async def test_confirm_nonexistent():
    """Подтверждение несуществующего action_id — False."""
    gate = ConfirmationGate()
    result = await gate.confirm("nonexistent-id", "user1")
    assert result is False


@pytest.mark.asyncio
async def test_is_pending_nonexistent():
    gate = ConfirmationGate()
    result = await gate.is_pending("nonexistent-id")
    assert result is False
