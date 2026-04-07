"""
House Party Protocol API — Iron Man 3
"JARVIS, it's time for a little House Party Protocol"
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from ..api.auth import get_current_user
from ..models.user import User

logger = logging.getLogger("api-house-party")
router = APIRouter(prefix="/jarvis/house-party", tags=["house-party"])


class ActivateRequest(BaseModel):
    goal: str


@router.post("/activate")
async def activate_house_party(
    request: ActivateRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Activate House Party Protocol.
    Deploys all 8 JARVIS agents simultaneously to solve a task.
    """
    try:
        from ..services.jarvis.house_party_protocol import get_house_party_protocol
        from ..services.memory_service import redis_client

        hpp = get_house_party_protocol()
        session_id = await hpp.activate(
            user_id=str(current_user.id),
            goal=request.goal,
            redis_client=redis_client,
        )

        return {
            "session_id": session_id,
            "status": "deploying",
            "message": "House Party Protocol activated! Deploying 8 agents...",
            "goal": request.goal,
        }
    except Exception as e:
        logger.error(f"House Party activation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions")
async def list_sessions(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """List all House Party Protocol sessions for the current user"""
    try:
        from ..services.jarvis.house_party_protocol import get_house_party_protocol

        hpp = get_house_party_protocol()
        sessions = hpp.list_sessions(str(current_user.id))
        return {"sessions": [s.to_dict() for s in sessions], "count": len(sessions)}
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        return {"sessions": [], "count": 0}


@router.get("/{session_id}")
async def get_session_status(
    session_id: str,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get the current status of a House Party Protocol session"""
    try:
        from ..services.jarvis.house_party_protocol import get_house_party_protocol

        hpp = get_house_party_protocol()
        session = hpp.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        if session.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")
        return session.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session {session_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
