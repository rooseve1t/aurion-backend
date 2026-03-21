from __future__ import annotations

import os
from typing import Any, Dict

from .base import QuantumAdapterBase, iso_now


class AlibabaQuantumAdapter(QuantumAdapterBase):
    """
    Alibaba Cloud Quantum (mock) adapter.

    Заглушка для демонстрации подключения к Aliyun Quantum. Реальный REST-эндпоинт
    и токен подставляются через переменные окружения.
    """

    backend = "alibaba-quantum"
    provider = "alibaba"

    def __init__(self) -> None:
        self.token = os.getenv("ALIBABA_QUANTUM_TOKEN", "").strip()
        self.endpoint = os.getenv("ALIBABA_QUANTUM_API_URL", "").strip() or "https://quantum.aliyun.com/api"

    def can_run(self) -> bool:
        return bool(self.token)

    def run(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "backend": self.backend,
            "provider": self.provider,
            "status": "queued",
            "task_type": task_type,
            "result": {
                "summary": "Alibaba Quantum mock submission accepted.",
                "endpoint": self.endpoint,
                "payload_echo": payload,
            },
            "timestamp": iso_now(),
        }
