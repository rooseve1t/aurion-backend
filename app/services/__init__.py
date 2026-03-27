"""
Aurion services package.

Keep imports lazy to avoid heavy side effects at package import time
(for example model downloads in memory_service).
"""

from __future__ import annotations

from importlib import import_module
from typing import Any

_EXPORTS: dict[str, tuple[str, str]] = {
    "MemoryService": ("app.services.memory_service", "MemoryService"),
    "get_memory_service": ("app.services.memory_service", "get_memory_service"),
    "VoiceService": ("app.services.voice_service", "VoiceService"),
    "init_voice_service": ("app.services.voice_service", "init_voice_service"),
    "VoiceJarvisService": ("app.services.voice_jarvis_service", "VoiceJarvisService"),
    "init_voice_jarvis_service": ("app.services.voice_jarvis_service", "init_voice_jarvis_service"),
    "get_voice_jarvis_service": ("app.services.voice_jarvis_service", "get_voice_jarvis_service"),
    "QuantumService": ("app.services.quantum_service", "QuantumService"),
    "init_quantum_service": ("app.services.quantum_service", "init_quantum_service"),
    "OSINTService": ("app.services.osint_service", "OSINTService"),
    "init_osint_service": ("app.services.osint_service", "init_osint_service"),
    "SmartHomeService": ("app.services.smarthome_service", "SmartHomeService"),
    "init_smarthome_service": ("app.services.smarthome_service", "init_smarthome_service"),
    "FinanceService": ("app.services.finance_service", "FinanceService"),
    "init_finance_service": ("app.services.finance_service", "init_finance_service"),
    "AgentOrchestrator": ("app.services.agent_service", "AgentOrchestrator"),
    "init_agent_service": ("app.services.agent_service", "init_agent_service"),
}

__all__ = list(_EXPORTS.keys())


def __getattr__(name: str) -> Any:
    target = _EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module 'app.services' has no attribute {name!r}")

    module_name, attr_name = target
    module = import_module(module_name)
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
