"""System stats endpoint."""
import time
import psutil
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database_final import get_db
from app.api.auth import get_current_user

router = APIRouter()


@router.get("/stats")
async def get_system_stats(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    return {
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "memory_used_mb": round(mem.used / 1024 / 1024),
        "memory_total_mb": round(mem.total / 1024 / 1024),
        "timestamp": time.time(),
        "status": "ok",
    }
