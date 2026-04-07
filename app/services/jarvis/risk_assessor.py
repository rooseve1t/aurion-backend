"""
⚠️ RiskAssessor — Оценка рисков перед автономными действиями JARVIS
Аналог того, как JARVIS предупреждает Тони: "Сэр, структурная целостность брони не выдержит..."
Iron Man 1: предупреждения о высоте, температуре, целостности конструкции
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional

logger = logging.getLogger("jarvis-risk-assessor")

# Карта типов действий → затронутые подсистемы
ACTION_SUBSYSTEM_MAP: Dict[str, List[str]] = {
    "system_optimization": ["Файловая система", "Процессы", "Память"],
    "security_scan": ["Сеть", "Файловая система", "Процессы", "Порты"],
    "data_backup": ["База данных", "Файловая система", "Хранилище"],
    "performance_tuning": ["Процессор", "Память", "Кэш", "Сеть"],
    "user_assistance": ["Интерфейс пользователя"],
    "predictive_maintenance": ["Все подсистемы"],
    "resource_management": ["Память", "Процессор", "Диск"],
    "error_prevention": ["Логи", "Мониторинг", "Алерты"],
    "smarthome_control": ["Умный дом", "MQTT", "Устройства"],
    "finance_analysis": ["Финансовый модуль", "База данных", "API банков"],
    "osint_scan": ["Сеть", "Внешние API", "OSINT-источники"],
    "evolution_deploy": ["Кодовая база", "Git", "CI/CD", "База данных"],
    "default": ["Системные компоненты"],
}

SIDE_EFFECTS_MAP: Dict[str, List[str]] = {
    "system_optimization": ["Временное замедление системы", "Перезапуск процессов"],
    "security_scan": ["Повышение нагрузки на сеть", "Временные задержки запросов"],
    "data_backup": ["Нагрузка на I/O", "Временное замедление БД"],
    "performance_tuning": ["Перезапуск кэша", "Кратковременное прерывание соединений"],
    "user_assistance": [],
    "evolution_deploy": ["Перезапуск сервисов", "Временная недоступность API", "Изменение БД"],
    "default": ["Возможное кратковременное снижение производительности"],
}


@dataclass
class RiskReport:
    action_id: str
    action_type: str
    risk_level: int                    # 1-10
    risk_label: str                    # "Низкий" / "Средний" / "Высокий" / "Критический"
    estimated_duration_sec: int
    affected_subsystems: List[str]
    potential_side_effects: List[str]
    recommendation: str
    auto_approve: bool
    warning_message: str = ""          # JARVIS-стиль предупреждения

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RiskAssessor:
    """
    Оценивает риски автономных действий JARVIS до их выполнения.
    Правиловая логика, без LLM — быстрая и надёжная.
    """

    def assess(
        self,
        action_id: str,
        action_type: str,
        risk_level: int,
        estimated_time: int,
        autonomy_level_value: int,
        system_metrics: Optional[Dict[str, Any]] = None,
    ) -> RiskReport:
        """
        Рассчитывает полный отчёт о рисках для действия.

        Args:
            action_id: ID действия
            action_type: Тип из ActionType enum
            risk_level: Базовый уровень риска (1-10) из AutonomousAction
            estimated_time: Ожидаемое время выполнения (сек)
            autonomy_level_value: Текущий уровень автономности (0-3)
            system_metrics: Текущие метрики системы (cpu, memory, etc.)
        """
        metrics = system_metrics or {}

        # Корректируем risk_level исходя из текущих метрик
        adjusted_risk = risk_level
        cpu = float(metrics.get("cpu_percent", 0))
        mem = float(metrics.get("memory_percent", 0))

        if cpu > 80:
            adjusted_risk = min(10, adjusted_risk + 2)
        elif cpu > 60:
            adjusted_risk = min(10, adjusted_risk + 1)

        if mem > 85:
            adjusted_risk = min(10, adjusted_risk + 2)
        elif mem > 70:
            adjusted_risk = min(10, adjusted_risk + 1)

        # Лейбл риска
        if adjusted_risk <= 2:
            risk_label = "Минимальный"
        elif adjusted_risk <= 4:
            risk_label = "Низкий"
        elif adjusted_risk <= 6:
            risk_label = "Средний"
        elif adjusted_risk <= 8:
            risk_label = "Высокий"
        else:
            risk_label = "Критический"

        # Затронутые подсистемы
        subsystems = ACTION_SUBSYSTEM_MAP.get(action_type, ACTION_SUBSYSTEM_MAP["default"])

        # Побочные эффекты
        side_effects = SIDE_EFFECTS_MAP.get(action_type, SIDE_EFFECTS_MAP["default"])

        # Рекомендация
        recommendation = self._generate_recommendation(adjusted_risk, autonomy_level_value)

        # Автоподтверждение
        # - risk <= 3 И autonomy >= SEMI_AUTO (2) → авто
        # - risk <= 1 → всегда авто
        auto_approve = (adjusted_risk <= 1) or (adjusted_risk <= 3 and autonomy_level_value >= 2)

        # Предупреждение в стиле JARVIS
        warning = self._jarvis_warning(action_type, adjusted_risk, cpu, mem)

        return RiskReport(
            action_id=action_id,
            action_type=action_type,
            risk_level=adjusted_risk,
            risk_label=risk_label,
            estimated_duration_sec=estimated_time,
            affected_subsystems=subsystems,
            potential_side_effects=side_effects,
            recommendation=recommendation,
            auto_approve=auto_approve,
            warning_message=warning,
        )

    def _generate_recommendation(self, risk_level: int, autonomy_level: int) -> str:
        if risk_level >= 8:
            return "Требуется ручное подтверждение. Риск критический."
        elif risk_level >= 6:
            if autonomy_level >= 3:
                return "Высокий риск. Выполнение возможно в FULL_AUTO режиме, однако рекомендую подтверждение."
            return "Высокий риск. Требуется подтверждение."
        elif risk_level >= 4:
            if autonomy_level >= 2:
                return "Средний риск. В режиме SEMI_AUTO требуется подтверждение."
            return "Средний риск. Рекомендую проверить перед выполнением."
        else:
            return "Низкий риск. Безопасно к выполнению."

    def _jarvis_warning(self, action_type: str, risk_level: int, cpu: float, mem: float) -> str:
        """Генерирует предупреждение в стиле JARVIS из фильмов"""
        if risk_level >= 8:
            return (
                f"Сэр, должен предупредить: уровень риска {risk_level}/10. "
                f"Настоятельно рекомендую ручное подтверждение перед выполнением."
            )
        elif risk_level >= 6:
            msgs = []
            if cpu > 80:
                msgs.append(f"нагрузка на процессор {cpu:.0f}%")
            if mem > 85:
                msgs.append(f"использование памяти {mem:.0f}%")
            context = ", ".join(msgs) if msgs else "текущее состояние системы"
            return f"Уровень риска {risk_level}/10. Учитывая {context}, рекомендую осторожность."
        elif risk_level >= 4:
            return f"Риск {risk_level}/10 — умеренный. Подтверждение рекомендовано."
        else:
            return f"Риск {risk_level}/10. Всё в норме, сэр."


# Синглтон
_instance: Optional[RiskAssessor] = None


def get_risk_assessor() -> RiskAssessor:
    global _instance
    if _instance is None:
        _instance = RiskAssessor()
    return _instance
