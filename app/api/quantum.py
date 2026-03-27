"""
API роутер квантовых вычислений
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel

from ..database_final import get_db
from ..services.quantum_service import get_quantum_service
from ..services.jarvis.personality_engine import get_personality_engine
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter(tags=["quantum"])


class QuboRequest(BaseModel):
    matrix: List[List[float]]
    backend: str = "auto"
    shots: int = 1000


class PortfolioRequest(BaseModel):
    assets: List[Dict[str, Any]]
    constraints: Dict[str, Any] = {}
    backend: str = "auto"


class VQERequest(BaseModel):
    hamiltonian: Dict[str, Any]
    ansatz: str = "hardware_efficient"
    backend: str = "auto"


@router.post("/solve_qubo")
async def solve_qubo(
    request: QuboRequest,
    current_user: User = Depends(get_current_user),
    quantum_service = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Решение QUBO задачи"""
    
    # Проверка прав доступа (только creator и admin)
    if current_user.role not in ["creator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Quantum computations require creator or admin role"
        )
    
    result = await quantum_service.solve_qubo(
        user_id=str(current_user.id),
        qubo_matrix=request.matrix,
        backend=request.backend,
        shots=request.shots
    )
    
    return result


@router.post("/solve")
async def solve_qubo_compat(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    quantum_service = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Backward-compatible alias for QUBO solving."""
    matrix = payload.get("qubo_matrix") or payload.get("matrix")
    if not isinstance(matrix, list):
        raise HTTPException(status_code=400, detail="qubo_matrix is required")
    request = QuboRequest(matrix=matrix)
    return await solve_qubo(
        request=request,
        current_user=current_user,
        quantum_service=quantum_service,
    )


@router.post("/optimize_portfolio")
async def optimize_portfolio(
    request: PortfolioRequest,
    current_user: User = Depends(get_current_user),
    quantum_service = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Оптимизация инвестиционного портфеля"""
    
    result = await quantum_service.optimize_portfolio(
        user_id=str(current_user.id),
        assets=request.assets,
        constraints=request.constraints,
        backend=request.backend
    )
    
    return result


@router.post("/run_vqe")
async def run_vqe(
    request: VQERequest,
    current_user: User = Depends(get_current_user),
    quantum_service = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Запуск VQE алгоритма"""
    
    # Проверка прав доступа
    if current_user.role not in ["creator", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="Quantum computations require creator or admin role"
        )
    
    result = await quantum_service.run_vqe(
        user_id=str(current_user.id),
        hamiltonian=request.hamiltonian,
        ansatz=request.ansatz,
        backend=request.backend
    )
    
    return result


@router.post("/vqe")
async def run_vqe_compat(
    payload: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    quantum_service = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Backward-compatible alias for VQE endpoint."""
    hamiltonian = payload.get("hamiltonian")
    if hamiltonian is None:
        hamiltonian = {
            "molecule": payload.get("molecule", "H2"),
            "basis": payload.get("basis", "sto-3g"),
        }
    request = VQERequest(hamiltonian=hamiltonian)
    return await run_vqe(
        request=request,
        current_user=current_user,
        quantum_service=quantum_service,
    )


@router.get("/backends")
async def get_quantum_backends(
    current_user: User = Depends(get_current_user),
    quantum_service = Depends(get_quantum_service)
) -> List[Dict[str, Any]]:
    """Получение доступных квантовых бэкендов"""
    
    backends = await quantum_service.get_quantum_backends()
    
    return backends


@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    quantum_service = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Получение статуса квантовой задачи"""
    
    status = await quantum_service.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Проверка доступа
    # TODO: проверить что job принадлежит текущему пользователю
    
    return status


@router.post("/biometric/sync")
async def sync_biometric_data(
    data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Синхронизация биометрических данных (Stage 15 Mock)"""
    heart_rate = data.get("heart_rate", 70)
    stress_level = data.get("stress_level", 0.2)
    
    # Реакция JARVIS
    personality = await get_personality_engine()
    response = "Все показатели в норме, сэр."
    
    if heart_rate > 100 or stress_level > 0.7:
        response = "Сэр, ваш пульс зашкаливает. Я активирую протокол 'Тишина' и приглушу уведомления. Подышите."
    elif heart_rate < 50:
        response = "Сэр, вы еще живы? Пульс подозрительно низкий. Может, чашку кофе?"

    return {
        "status": "synced",
        "jarvis_comment": response,
        "metrics_received": {
            "heart_rate": heart_rate,
            "stress_level": stress_level
        }
    }

@router.delete("/jobs/{job_id}")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    quantum_service = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Отмена квантовой задачи"""
    
    # TODO: реализовать отмену задачи
    
    return {"message": "Job cancellation requested"}
