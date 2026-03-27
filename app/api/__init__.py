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
from .vpn import router as vpn_router
from .jarvis_whisper import router as jarvis_whisper_router
from .autonomous_jarvis import router as autonomous_jarvis_router
from .mission_control import router as mission_control_router
from .personality import router as personality_router
from .squad import router as squad_router

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
    "payments_router",
    "vpn_router",
    "jarvis_whisper_router",
    "autonomous_jarvis_router",
    "mission_control_router",
    "personality_router",
    "squad_router"
]
