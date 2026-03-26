"""
API роутер Mission Control JARVIS (Stage 19)
"""
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..api.auth import get_current_user
from ..services.agent_service import get_agent_service
from ..services.cognitive_engine import get_cognitive_engine
from ..services.mission_control import get_mission_control
from ..services.jarvis.personality_engine import get_personality_engine
from ..services.memory_service import get_memory_service
from ..services.project_fabricator import get_project_fabricator
from ..services.quantum_service import get_quantum_service

router = APIRouter(tags=["jarvis_mission_control"])


class MissionLaunchRequest(BaseModel):
    objective: str = Field(..., min_length=3, max_length=500)


class FabricateProjectRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    tech_stack: str = Field(default="generic", max_length=120)
    description: str = Field(default="", max_length=4000)


async def get_mission_control_service(
    agent_service=Depends(get_agent_service),
    personality=Depends(get_personality_engine),
    memory=Depends(get_memory_service),
    quantum=Depends(get_quantum_service),
):
    """Сборка Mission Control с корректными зависимостями FastAPI."""
    cognitive = await get_cognitive_engine(
        db_session=None,
        personality=personality,
        memory=memory,
        quantum=quantum,
    )
    return await get_mission_control(agent_service, cognitive)


@router.post("/launch")
async def launch_mission(
    payload: MissionLaunchRequest,
    current_user=Depends(get_current_user),
    mission_control=Depends(get_mission_control_service),
):
    """Запуск миссии с роевым исполнением."""
    return await mission_control.launch_mission(
        user_id=str(current_user.id),
        objective=payload.objective,
    )


@router.get("/{mission_id}")
async def mission_status(
    mission_id: str,
    current_user=Depends(get_current_user),
    mission_control=Depends(get_mission_control_service),
):
    """Получение статуса миссии."""
    _ = current_user
    status: Optional[Dict[str, Any]] = await mission_control.get_mission_status(mission_id)
    if not status:
        raise HTTPException(status_code=404, detail="Mission not found")
    return status


@router.post("/fabricate")
async def fabricate_new_project(
    data: FabricateProjectRequest,
    current_user = Depends(get_current_user),
    fabricator = Depends(get_project_fabricator)
):
    """Синтез нового проекта JARVIS (Stage 22)"""
    _ = current_user
    result = await fabricator.fabricate_project(data.name, data.tech_stack, data.description)
    return result
