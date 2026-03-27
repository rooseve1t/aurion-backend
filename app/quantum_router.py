from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

try:
    from .services import quantum_extra # type: ignore
    IBMQuantumAdapter: Any = getattr(quantum_extra, "IBMQuantumAdapter", None)
    PasqalAdapter: Any = getattr(quantum_extra, "PasqalAdapter", None)
    AlibabaQuantumAdapter: Any = getattr(quantum_extra, "AlibabaQuantumAdapter", None)
except Exception:
    # Fallback if optional package structure unavailable in older stage builds.
    IBMQuantumAdapter = PasqalAdapter = AlibabaQuantumAdapter = None


@dataclass
class QuantumRouter:
    quantum_token: str = ""
    hpc_url: str = ""
    hpc_user: str = ""
    hpc_password: str = ""

    def _now(self) -> str:
        return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    def _can_use_quantum(self) -> bool:
        return bool(self.quantum_token.strip())

    def _can_use_hpc(self) -> bool:
        return bool(self.hpc_url.strip() and self.hpc_user.strip() and self.hpc_password.strip())

    def _extra_adapters(self) -> list[Any]:
        adapters: list[Any] = []
        if IBMQuantumAdapter:
            adapters.append(IBMQuantumAdapter())
        if PasqalAdapter:
            adapters.append(PasqalAdapter())
        if AlibabaQuantumAdapter:
            adapters.append(AlibabaQuantumAdapter())
        return adapters

    def _run_quantum(self, task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "backend": "quantum-rings",
            "status": "queued",
            "task_type": task_type,
            "result": {
                "summary": "Квантовая задача поставлена в очередь.",
                "estimated_latency_sec": 12,
                "payload_echo": payload,
            },
            "timestamp": self._now(),
        }

    def _run_hpc(self, task_type: str, payload: dict[str, Any]) -> dict[str, Any]:
        # PyUNICORE подключается только при наличии настроек HPC.
        try:
            import pyunicore.client as unicore_client  # type: ignore

            _ = unicore_client  # suppress lint-like warnings in minimal setup
            provider = "pyunicore"
            note = "HPC job prepared for UNICORE submission."
        except Exception:
            provider = "mvp-fallback"
            note = "PyUNICORE недоступен в рантайме, возвращён fallback-ответ."
        return {
            "backend": "hpc-lumi",
            "provider": provider,
            "status": "queued",
            "task_type": task_type,
            "result": {
                "summary": note,
                "target_cluster": self.hpc_url,
                "payload_echo": payload,
            },
            "timestamp": self._now(),
        }

    def route_task(self, task_type: str, payload: dict[str, Any], preferred_backend: str = "auto") -> dict[str, Any]:
        target = (preferred_backend or "auto").strip().lower()

        # Extra adapters (IBM/Pasqal/Alibaba mocks)
        for adapter in self._extra_adapters():
            if target in {adapter.backend, adapter.provider} and adapter.can_run():
                return adapter.run(task_type, payload)

        if target == "quantum" and self._can_use_quantum():
            return self._run_quantum(task_type, payload)
        if target == "hpc" and self._can_use_hpc():
            return self._run_hpc(task_type, payload)

        if target == "auto":
            heavy_task = task_type.lower() in {"simulation", "train", "batch", "hpc"}

            # Prefer configured extra adapters before falling back to legacy backends
            for adapter in self._extra_adapters():
                if adapter.can_run():
                    return adapter.run(task_type, payload)

            if heavy_task and self._can_use_hpc():
                return self._run_hpc(task_type, payload)
            if self._can_use_quantum():
                return self._run_quantum(task_type, payload)
            if self._can_use_hpc():
                return self._run_hpc(task_type, payload)
        return {
            "backend": "local-mvp",
            "status": "completed",
            "task_type": task_type,
            "result": {
                "summary": "Внешние бэкенды не настроены, задача выполнена локально в MVP-режиме.",
                "payload_echo": payload,
            },
            "timestamp": self._now(),
        }
