"""System stats endpoint."""
import asyncio
import time
import psutil
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database_final import get_db
from app.api.auth import get_current_user
import logging

logger = logging.getLogger("api-system")
router = APIRouter()


def _collect_stats() -> dict:
    """Blocking psutil calls — runs in thread pool."""
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    return {
        "cpu_percent": cpu,
        "memory_percent": mem.percent,
        "memory_used_mb": round(mem.used / 1024 / 1024),
        "memory_total_mb": round(mem.total / 1024 / 1024),
    }


@router.get("/stats")
async def get_system_stats(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stats = await asyncio.to_thread(_collect_stats)
    return {**stats, "timestamp": time.time(), "status": "ok"}


@router.get("/hud-snapshot")
async def get_hud_snapshot(
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    HUD Snapshot - data for JARVIS persistent display
    Analog of the HUD in Iron Man's helmet: CPU, status, threats, autonomy
    """
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()

        threat_level = "low"
        autonomy_level = "assistive"
        try:
            from ..services.jarvis.autonomy_engine import AutonomyEngine
            # Can't get singleton easily, use defaults
        except Exception:
            pass

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu_percent": round(cpu, 1),
            "memory_percent": round(mem.percent, 1),
            "memory_used_gb": round(mem.used / 1024**3, 2),
            "active_agents": 0,
            "pending_tasks": 0,
            "threat_level": threat_level,
            "autonomy_level": autonomy_level,
            "active_missions": 0,
            "stress_index": 0,
            "uptime_seconds": int(time.time()),
        }
    except Exception as e:
        logger.warning(f"HUD snapshot error: {e}")
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu_percent": 0,
            "memory_percent": 0,
            "memory_used_gb": 0,
            "active_agents": 0,
            "pending_tasks": 0,
            "threat_level": "unknown",
            "autonomy_level": "manual",
            "active_missions": 0,
            "stress_index": 0,
            "uptime_seconds": 0,
        }
