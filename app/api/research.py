"""
Passive Research API
"""
from __future__ import annotations

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException

from ..api.auth import get_current_user
from ..models.user import User

logger = logging.getLogger("api-research")
router = APIRouter(prefix="/jarvis/research", tags=["research"])


@router.get("/insights")
async def get_research_insights(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get the latest auto-researched insights"""
    try:
        from ..database_final import AsyncSessionLocal
        from ..services.memory_service import MemoryService

        async with AsyncSessionLocal() as db:
            svc = MemoryService(db)
            results = await svc.search_memories(
                user_id=str(current_user.id),
                query="",
                limit=limit,
                tags=["auto_research"],
            )
        return {"insights": results, "count": len(results)}
    except Exception as e:
        logger.error(f"Failed to get research insights: {e}")
        return {"insights": [], "count": 0}


@router.post("/trigger")
async def trigger_research_cycle(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Manually trigger a passive research cycle"""
    try:
        from ..database_final import AsyncSessionLocal
        from ..services.jarvis.passive_researcher import get_passive_researcher
        from ..services.memory_service import redis_client

        researcher = get_passive_researcher()
        async with AsyncSessionLocal() as db:
            count = await researcher.run_cycle(
                user_id=str(current_user.id),
                db=db,
                redis_client=redis_client,
            )

        return {
            "status": "completed",
            "insights_saved": count,
            "message": f"Research cycle complete. Saved {count} new insights.",
        }
    except Exception as e:
        logger.error(f"Research cycle failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
