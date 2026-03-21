from __future__ import annotations

import os
from typing import Any, Dict

from .base import QuantumAdapterBase, iso_now


class IBMQuantumAdapter(QuantumAdapterBase):
    """
    Mocked IBM Quantum Open Plan adapter (REST stub).

    We intentionally avoid pulling heavy qiskit dependency. When an IBM token is
    supplied, we return a queued response structure; without a token we skip the
    adapter.
    """

    backend = "ibm-quantum"
    provider = "ibm"

    def __init__(self) -> None:
        self.token = os.getenv("IBM_QUANTUM_TOKEN", "").strip()
        self.instance = os.getenv("IBM_QUANTUM_INSTANCE", "").strip() or "ibm-q/open/main"
        self.api_url = os.getenv("IBM_QUANTUM_API_URL", "").strip() or "https://api.quantum-computing.ibm.com"

    def can_run(self) -> bool:
        return bool(self.token)

    def run(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Minimal mock; real call would sign request with self.token and submit circuit/QUBO.
        return {
            "backend": self.backend,
            "provider": self.provider,
            "status": "queued",
            "task_type": task_type,
            "instance": self.instance,
            "result": {
                "summary": "IBM Quantum mock submission accepted.",
                "api_url": self.api_url,
                "payload_echo": payload,
            },
            "timestamp": iso_now(),
        }
