"""
SelfEvolution API — роутер /api/v2/evolution/
Все эндпоинты доступны ТОЛЬКО пользователю с role='creator'.
"""
import logging
from dataclasses import asdict
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from ..api.auth import get_current_user
from ..models.user import User
from ..services.self_evolution import get_self_evolution

logger = logging.getLogger("aurion-self-evolution-api")

router = APIRouter(tags=["evolution-v2"])


def _require_creator(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "creator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Доступ только для создателя системы.",
        )
    return current_user


@router.get("/proposals")
async def get_proposals(current_user: User = Depends(_require_creator)) -> Dict[str, Any]:
    proposals = await get_self_evolution().get_history(str(current_user.id))
    return {"proposals": [asdict(p) for p in proposals]}


@router.post("/proposals/analyze")
async def analyze_and_propose(current_user: User = Depends(_require_creator)) -> Dict[str, Any]:
    proposal = await get_self_evolution().analyze_patterns(str(current_user.id))
    if proposal is None:
        return {"status": "not_enough_data", "message": "Нужно минимум 100 взаимодействий."}
    return {"status": "proposed", "proposal": asdict(proposal)}


@router.post("/proposals/{proposal_id}/apply")
async def apply_proposal(
    proposal_id: str, current_user: User = Depends(_require_creator)
) -> Dict[str, Any]:
    success = await get_self_evolution().apply_proposal(proposal_id)
    if success:
        return {"status": "applied", "proposal_id": proposal_id}
    return {"status": "rolled_back", "proposal_id": proposal_id,
            "message": "Тесты не прошли — изменения откатаны."}


@router.post("/proposals/{proposal_id}/reject")
async def reject_proposal(
    proposal_id: str, current_user: User = Depends(_require_creator)
) -> Dict[str, Any]:
    success = await get_self_evolution().reject_proposal(proposal_id)
    return {"status": "rejected" if success else "not_found", "proposal_id": proposal_id}


@router.post("/proposals/{proposal_id}/rollback")
async def rollback_proposal(
    proposal_id: str, current_user: User = Depends(_require_creator)
) -> Dict[str, Any]:
    success = await get_self_evolution().rollback_proposal(proposal_id)
    return {"status": "rolled_back" if success else "error", "proposal_id": proposal_id}
