"""
API роутер квантовых вычислений
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, List
from pydantic import BaseModel

from ..database import get_db
from ..services.quantum_service import get_quantum_service
from ..api.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/v1/quantum", tags=["quantum"])


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


@router.get("/jobs")
async def list_user_jobs(
    current_user: User = Depends(get_current_user),
    quantum_service = Depends(get_quantum_service)
) -> List[Dict[str, Any]]:
    """Получение списка задач пользователя"""
    
    # TODO: реализовать получение списка задач из базы данных
    
    return []


@router.delete("/jobs/{job_id}")
async def cancel_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    quantum_service = Depends(get_quantum_service)
) -> Dict[str, Any]:
    """Отмена квантовой задачи"""
    
    # TODO: реализовать отмену задачи
    
    return {"message": "Job cancellation requested"}
