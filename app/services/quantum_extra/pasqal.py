from __future__ import annotations

import os
from typing import Any, Dict

from .base import QuantumAdapterBase, iso_now


class PasqalAdapter(QuantumAdapterBase):
    """
    Pasqal (Pulser) Explorer mock adapter.

    Pasqal предоставляет бесплатный эмулятор; здесь мы имитируем отклик без SDK.
    """

    backend = "pasqal-emulator"
    provider = "pasqal"

    def __init__(self) -> None:
        self.token = os.getenv("PASQAL_API_TOKEN", "").strip()
        self.endpoint = os.getenv("PASQAL_API_URL", "").strip() or "https://api.pasqal.cloud"

    def can_run(self) -> bool:
        # Even без токена возвращаем мокуемый ответ, но prefer configured.
        return bool(self.token)

    def run(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "backend": self.backend,
            "provider": self.provider,
            "status": "queued",
            "task_type": task_type,
            "result": {
                "summary": "Pasqal mock accepted (emulator).",
                "endpoint": self.endpoint,
                "payload_echo": payload,
            },
            "timestamp": iso_now(),
        }
