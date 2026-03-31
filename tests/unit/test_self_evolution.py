"""
Smoke-тесты для SelfEvolution.
"""
import pytest
from app.services.self_evolution import SelfEvolution, EvolutionProposal, get_self_evolution


def test_get_self_evolution_singleton():
    s1 = get_self_evolution()
    s2 = get_self_evolution()
    assert s1 is s2


def test_self_evolution_instantiation():
    svc = SelfEvolution()
    assert svc is not None
    assert svc._redis is None


def test_set_redis():
    svc = SelfEvolution()
    svc.set_redis("fake_redis")
    assert svc._redis == "fake_redis"


def test_evolution_proposal_fields():
    proposal = EvolutionProposal(
        id="test-id",
        description="A test",
        diff="--- a\n+++ b",
        test_command="pytest",
        status="pending",
    )
    assert proposal.id == "test-id"
    assert proposal.status == "pending"
    assert proposal.description == "A test"
    assert proposal.diff == "--- a\n+++ b"


@pytest.mark.asyncio
async def test_apply_proposal_nonexistent():
    """apply_proposal с несуществующим ID — возвращает False."""
    svc = SelfEvolution()
    result = await svc.apply_proposal("nonexistent-proposal-id")
    assert result is False


@pytest.mark.asyncio
async def test_rollback_proposal_nonexistent():
    """rollback_proposal с несуществующим ID — возвращает False."""
    svc = SelfEvolution()
    result = await svc.rollback_proposal("nonexistent-proposal-id")
    assert result is False


@pytest.mark.asyncio
async def test_reject_proposal_nonexistent():
    """reject_proposal с несуществующим ID — возвращает False."""
    svc = SelfEvolution()
    result = await svc.reject_proposal("nonexistent-proposal-id")
    assert result is False


@pytest.mark.asyncio
async def test_get_history_empty():
    """get_history для нового пользователя — возвращает список или бросает HTTPException."""
    from fastapi import HTTPException
    svc = SelfEvolution()
    try:
        history = await svc.get_history("user_nonexistent_xyz")
        assert isinstance(history, list)
    except HTTPException as exc:
        # Ожидаемо: пользователь не creator
        assert exc.status_code == 403
