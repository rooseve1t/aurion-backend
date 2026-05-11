"""
🧠 Автономная система JARVIS
Принятие решений без прямых команд пользователя
"""
import logging
import asyncio
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from sqlalchemy import text

# Импорты для работы с БД (нужно быть аккуратным с циклическими импортами)
from ...database_final import AsyncSessionLocal
from .evolution_engine import EvolutionEngine

logger = logging.getLogger("jarvis-autonomy")

class AutonomyLevel(Enum):
    """Уровни автономности"""
    MANUAL = 0          # Только по команде
    ASSISTIVE = 1       # Подсказки и предложения
    SEMI_AUTO = 2       # Автоматические действия с подтверждением
    FULL_AUTO = 3       # Полная автономность

class ActionType(Enum):
    """Типы автономных действий"""
    SYSTEM_OPTIMIZATION = "system_optimization"
    SECURITY_SCAN = "security_scan"
    DATA_BACKUP = "data_backup"
    PERFORMANCE_TUNING = "performance_tuning"
    USER_ASSISTANCE = "user_assistance"
    PREDICTIVE_MAINTENANCE = "predictive_maintenance"
    RESOURCE_MANAGEMENT = "resource_management"
    ERROR_PREVENTION = "error_prevention"

@dataclass
class AutonomousAction:
    """Описание автономного действия"""
    id: str
    action_type: ActionType
    description: str
    priority: int  # 1-10
    autonomy_required: AutonomyLevel
    conditions: List[str]
    execution_func: Callable[..., Awaitable[Any]]
    rollback_func: Optional[Callable[..., Awaitable[Any]]] = None
    estimated_time: int = 0  # секунды
    risk_level: int = 1  # 1-10
    user_notification: bool = True
    auto_confirm_threshold: int = 8  # приоритет выше этого - без подтверждения

class AutonomyEngine:
    """Движок автономности JARVIS"""
    
    def __init__(self, evolution_engine: Optional[EvolutionEngine] = None) -> None:
        self.current_level: AutonomyLevel = AutonomyLevel.ASSISTIVE
        self.active_actions: Dict[str, Any] = {}
        self.action_history: List[Any] = []
        self.scheduled_actions: List[Any] = []
        self.system_metrics: Dict[str, Any] = {}
        self.user_patterns: Dict[str, Any] = {}
        self.learning_enabled: bool = True
        self.evolution_engine = evolution_engine
        
        # Пороги для автоматических действий
        self.thresholds: Dict[str, float] = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "error_rate": 5.0,
            "response_time": 2000.0,  # ms
            "security_threats": 1.0
        }
        
        # Регистрация автономных действий
        self.registered_actions: Dict[str, AutonomousAction] = {}
        self._register_core_actions()
        
    def _register_core_actions(self) -> None:
        """Зарегистрировать базовые автономные действия"""
        self.register_action(AutonomousAction(
            id="auto_cleanup_temp",
            action_type=ActionType.SYSTEM_OPTIMIZATION,
            description="Очистка временных файлов",
            priority=3,
            autonomy_required=AutonomyLevel.SEMI_AUTO,
            conditions=["disk_usage > 85"],
            execution_func=self._cleanup_temp_files,
            estimated_time=30,
            risk_level=1
        ))
        self.register_action(AutonomousAction(
            id="security_scan",
            action_type=ActionType.SECURITY_SCAN,
            description="Сканирование безопасности",
            priority=8,
            autonomy_required=AutonomyLevel.ASSISTIVE,
            conditions=["error_rate > 5"],
            execution_func=self._run_security_scan,
            estimated_time=45,
            risk_level=2
        ))
        self.register_action(AutonomousAction(
            id="data_backup",
            action_type=ActionType.DATA_BACKUP,
            description="Резервное копирование",
            priority=5,
            autonomy_required=AutonomyLevel.SEMI_AUTO,
            conditions=["system_stable"],
            execution_func=self._run_backup,
            estimated_time=90,
            risk_level=2
        ))
        self.register_action(AutonomousAction(
            id="performance_tune",
            action_type=ActionType.PERFORMANCE_TUNING,
            description="Оптимизация производительности",
            priority=6,
            autonomy_required=AutonomyLevel.SEMI_AUTO,
            conditions=["cpu_usage > 80"],
            execution_func=self._tune_performance,
            estimated_time=60,
            risk_level=3
        ))
        self.register_action(AutonomousAction(
            id="user_assistance",
            action_type=ActionType.USER_ASSISTANCE,
            description="Проактивная помощь пользователю",
            priority=4,
            autonomy_required=AutonomyLevel.ASSISTIVE,
            conditions=["system_stable"],
            execution_func=self._assist_user,
            estimated_time=15,
            risk_level=1
        ))
        self.register_action(AutonomousAction(
            id="predictive_maintenance",
            action_type=ActionType.PREDICTIVE_MAINTENANCE,
            description="Превентивная диагностика",
            priority=5,
            autonomy_required=AutonomyLevel.SEMI_AUTO,
            conditions=["disk_usage > 70"],
            execution_func=self._predictive_maintenance,
            estimated_time=35,
            risk_level=2
        ))
        self.register_action(AutonomousAction(
            id="resource_management",
            action_type=ActionType.RESOURCE_MANAGEMENT,
            description="Управление ресурсами",
            priority=5,
            autonomy_required=AutonomyLevel.ASSISTIVE,
            conditions=["memory_usage > 85"],
            execution_func=self._manage_resources,
            estimated_time=25,
            risk_level=2
        ))
        self.register_action(AutonomousAction(
            id="error_prevention",
            action_type=ActionType.ERROR_PREVENTION,
            description="Профилактика ошибок",
            priority=7,
            autonomy_required=AutonomyLevel.SEMI_AUTO,
            conditions=["error_rate > 3"],
            execution_func=self._prevent_errors,
            estimated_time=20,
            risk_level=2
        ))

    def register_action(self, action: AutonomousAction) -> None:
        self.registered_actions[action.id] = action

    def set_autonomy_level(self, level: AutonomyLevel) -> None:
        """Установить текущий уровень автономности"""
        self.current_level = level
        logger.info(f"🤖 Autonomy level set to: {level.name}")

    async def start_monitoring(self) -> None:
        """Запустить фоновый мониторинг системы"""
        logger.info("🚀 Starting JARVIS autonomy monitoring...")
        while True:
            try:
                # Сбор реальных метрик
                await self._collect_system_metrics()
                
                # Проверка порогов и запуск действий
                await self._check_thresholds()
                
                await asyncio.sleep(30)  # Интервал мониторинга сокращен для отзывчивости
            except Exception as e:
                logger.error(f"Error in autonomy monitoring: {e}")
                await asyncio.sleep(10)

    async def _check_thresholds(self) -> None:
        """Проверить метрики на превышение порогов"""
        for metric, threshold in self.thresholds.items():
            value = self.system_metrics.get(metric, 0)
            if value > threshold:
                await self._handle_threshold_breach(metric, value, threshold)

    async def _collect_system_metrics(self) -> None:
        """Собрать системные метрики через psutil (с fallback)."""
        try:
            import psutil  # type: ignore

            self.system_metrics["cpu_usage"] = float(psutil.cpu_percent(interval=None))
            self.system_metrics["memory_usage"] = float(psutil.virtual_memory().percent)
            self.system_metrics["disk_usage"] = float(psutil.disk_usage("/").percent)
            # Имитация других метрик, если нет реальных источников
            self.system_metrics.setdefault("error_rate", 0.5)
            self.system_metrics.setdefault("response_time", 150.0)
        except Exception as e:
            logger.warning(f"Failed to collect real metrics: {e}. Using deterministic fallback.")
            self.system_metrics["cpu_usage"] = 45.0
            self.system_metrics["memory_usage"] = 55.0
            self.system_metrics["disk_usage"] = 60.0

    async def _evaluate_condition(self, condition: str) -> bool:
        """Оценить простое условие автономного действия."""
        condition = condition.strip()
        if condition == "system_stable":
            return (
                float(self.system_metrics.get("cpu_usage", 0)) <= 85
                and float(self.system_metrics.get("memory_usage", 0)) < 90
                and float(self.system_metrics.get("error_rate", 0)) < 5
            )

        for operator in (">=", "<=", ">", "<", "=="):
            if operator in condition:
                left, right = [part.strip() for part in condition.split(operator, 1)]
                left_value = float(self.system_metrics.get(left, 0))
                right_value = float(right)
                if operator == ">=":
                    return left_value >= right_value
                if operator == "<=":
                    return left_value <= right_value
                if operator == ">":
                    return left_value > right_value
                if operator == "<":
                    return left_value < right_value
                return left_value == right_value
        return False

    async def _handle_threshold_breach(self, metric: str, value: float, threshold: float) -> None:
        """Обработать превышение порога"""
        logger.warning(f"⚠️ Threshold breach: {metric} = {value} (threshold: {threshold})")

        # Уведомление пользователя
        messages = {
            "cpu_usage": f"Сэр, загрузка процессора критическая: {value:.1f}%. Рекомендую оптимизацию.",
            "memory_usage": f"Сэр, оперативная память почти исчерпана: {value:.1f}%. Могу очистить кэш.",
            "disk_usage": f"Сэр, место на диске заканчивается: {value:.1f}%.",
            "error_rate": f"Сэр, зафиксирован аномальный рост ошибок в системе: {value:.1f}%.",
            "security_threats": "Сэр, обнаружена угроза безопасности! Активирую защитные протоколы."
        }

        msg = messages.get(metric, f"Сэр, метрика {metric} превысила порог: {value:.1f}.")
        await self.notify_user(msg)

        # Поиск и запуск подходящего действия
        for action in self.registered_actions.values():
            if any(metric in cond for cond in action.conditions):
                if self.current_level.value >= action.autonomy_required.value:
                    await self._execute_action(action)

    async def execute_action(self, action: AutonomousAction) -> Any:
        """Выполнить автономное действие (публичный метод)"""
        return await self._execute_action(action)

    async def _execute_action(self, action: AutonomousAction) -> Any:
        """Выполнить автономное действие"""
        logger.info(f"⚙️ Executing autonomous action: {action.id}")

        # Risk assessment before execution
        try:
            from .risk_assessor import get_risk_assessor
            assessor = get_risk_assessor()
            risk_report = assessor.assess(
                action_id=action.id,
                action_type=action.action_type.value,
                risk_level=action.risk_level,
                estimated_time=action.estimated_time,
                autonomy_level_value=self.current_level.value,
                system_metrics=self.system_metrics,
            )
            logger.info(f"Risk assessment for {action.id}: level={risk_report.risk_level}, auto_approve={risk_report.auto_approve}")

            if not risk_report.auto_approve:
                logger.warning(f"Action {action.id} requires confirmation: {risk_report.warning_message}")
                return {
                    "status": "pending_confirmation",
                    "action_id": action.id,
                    "risk_report": risk_report.to_dict(),
                    "message": risk_report.warning_message,
                }
        except Exception as _risk_exc:
            logger.warning(f"Risk assessment error (continuing): {_risk_exc}")

        try:
            result = await action.execution_func()
            self.action_history.append({
                "action_id": action.id,
                "timestamp": datetime.now(),
                "status": "success",
                "result": result
            })
            if self.evolution_engine:
                await self.evolution_engine.process_event("successful_action", {"action_id": action.id, "result": result})
            return result
        except Exception as e:
            logger.error(f"Failed to execute action {action.id}: {e}")
            self.action_history.append({
                "action_id": action.id,
                "timestamp": datetime.now(),
                "status": "failure",
                "error": str(e)
            })
            if self.evolution_engine:
                await self.evolution_engine.process_event("failed_action", {"action_id": action.id, "error": str(e)})
            if action.rollback_func:
                await action.rollback_func()
            return False

    async def _cleanup_temp_files(self) -> bool:
        logger.info("🧹 Auto-cleanup initiated...")
        return True

    async def _run_security_scan(self) -> bool:
        return True

    async def _run_backup(self) -> bool:
        return True

    async def _tune_performance(self) -> bool:
        return True

    async def _assist_user(self) -> bool:
        return True

    async def _predictive_maintenance(self) -> bool:
        return True

    async def _manage_resources(self) -> bool:
        return True

    async def _prevent_errors(self) -> bool:
        return True

    async def notify_user(self, message: str) -> None:
        """Уведомить пользователя через БД и логи"""
        logger.info(f"🎤 JARVIS: {message}")
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(
                    text("""
                        INSERT INTO proactive_suggestions (user_id, message, confidence, source, created_at)
                        VALUES (:uid, :msg, :conf, :src, :ts)
                    """),
                    {
                        "uid": "system", 
                        "msg": message,
                        "conf": 1.0,
                        "src": "jarvis_voice",
                        "ts": datetime.now().isoformat()
                    }
                )
                await session.commit()
        except Exception as e:
            logger.error(f"Failed to save notification: {e}")

async def get_autonomy_engine() -> AutonomyEngine:
    # This is a temporary solution. In a real application, you would use a proper dependency injection system.
    from .evolution_engine import EvolutionEngine
    from .personality_engine import get_personality_engine
    personality_engine = await get_personality_engine()
    # Pass None for autonomy_engine for now, it will be set later
    evolution_engine = EvolutionEngine(personality_engine, None) 
    autonomy_engine = AutonomyEngine(evolution_engine)
    # Now set the autonomy_engine in evolution_engine
    evolution_engine.autonomy = autonomy_engine
    return autonomy_engine
