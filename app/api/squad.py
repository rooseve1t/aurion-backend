from typing import Dict, Any
from fastapi import APIRouter, Depends
from ..services.jarvis.squad_service import get_squad_center, SquadCommandCenter, SquadRole

router = APIRouter(tags=["jarvis-squad"])

@router.get("/status")
async def get_squad_status(center: SquadCommandCenter = Depends(get_squad_center)) -> Dict[str, Any]:
    """Получить статус всего виртуального штаба"""
    return {
        "employees": center.get_all_employees(),
        "total_active": len([e for e in center.employees.values() if e.status == "working"])
    }

@router.post("/mission")
async def broadcast_mission(mission: str, center: SquadCommandCenter = Depends(get_squad_center)) -> Dict[str, Any]:
    """Разослать новую задачу всему штабу"""
    center.broadcast_mission(mission)
    return {"status": "broadcasted", "mission": mission}

@router.get("/employee/{role}")
async def get_employee_details(role: str, center: SquadCommandCenter = Depends(get_squad_center)) -> Dict[str, Any]:
    """Получить детальную информацию о сотруднике"""
    try:
        role_enum = SquadRole(role)
        emp = center.get_employee(role_enum)
        if emp:
            return emp.to_dict()
    except ValueError:
        pass
    return {"error": "Employee not found"}
