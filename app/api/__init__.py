"""
API роутеры Aurion OS
"""
from .auth import router as auth_router
from .memory import router as memory_router
from .voice import router as voice_router
from .voice_jarvis import router as voice_jarvis_router
from .quantum import router as quantum_router
from .osint import router as osint_router
from .smarthome import router as smarthome_router
from .finance import router as finance_router
from .agents import router as agents_router
from .payments import router as payments_router

__all__ = [
    "auth_router",
    "memory_router", 
    "voice_router",
    "voice_jarvis_router",
    "quantum_router",
    "osint_router",
    "smarthome_router",
    "finance_router",
    "agents_router",
    "payments_router"
]
