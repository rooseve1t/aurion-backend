from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict


def iso_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class QuantumAdapterBase:
    """Lightweight base for mock adapters to keep signatures aligned."""

    backend: str = "unknown"
    provider: str = "unknown"

    def can_run(self) -> bool:
        """Return True if adapter has enough config to attempt execution."""
        return False

    def run(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task and return result payload."""
        raise NotImplementedError
