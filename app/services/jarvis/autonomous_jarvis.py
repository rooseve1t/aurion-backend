"""
🧠 Enhanced JARVIS с автономностью
Интеграция autonomy engine в основной сервис
"""
import asyncio
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta

from .autonomy_engine import AutonomyEngine, AutonomyLevel, ActionType
from .enhanced_voice_service import EnhancedVoiceJarvisService
from .personality_engine import get_personality_engine
from .evolution_engine import EvolutionEngine
from .neuro_interface import NeuroInterface
from .proactivity_manager import ProactivityManager
from .self_coding_engine import SelfCodingEngine
from .self_repair_service import SelfRepairModule
from .quantum_ledger_service import QuantumLedger

# Хранилище фоновых задач для предотвращения GC
_background_tasks: Set[asyncio.Task[Any]] = set()


class AutonomousJarvisService(EnhancedVoiceJarvisService):
    """JARVIS с полной автономностью и самообучением"""

    def __init__(self, websocket: Any, user_id: str):
        super().__init__(websocket, user_id)
        self.autonomy_engine: Optional[AutonomyEngine] = None
        self.evolution_engine: Optional[EvolutionEngine] = None
        self.neuro_interface: Optional[NeuroInterface] = None
        self.proactivity_manager: Optional[ProactivityManager] = None
        self.self_coding_engine: Optional[SelfCodingEngine] = None
        self.self_repair_module: Optional[SelfRepairModule] = None
        self.quantum_ledger: Optional[QuantumLedger] = None
        self.context_memory: List[Dict[str, Any]] = []  # Stage 21: Neural Context Memory
        self.autonomy_enabled: bool = False

    async def initialize(self) -> None:
        """Инициализация с автономностью и эволюцией"""
        await super().initialize()

        # Инициализация quantum ledger
        self.quantum_ledger = QuantumLedger()
        await self.quantum_ledger.log_action("system_init", {"status": "initializing"})

        # Инициализация neuro interface
        self.neuro_interface = NeuroInterface()

        # Инициализация self-coding engine
        self.self_coding_engine = SelfCodingEngine()

        # Инициализация self-repair module
        self.self_repair_module = SelfRepairModule({
            "autonomy": self.autonomy_engine,
            "evolution": self.evolution_engine,
            "neuro": self.neuro_interface,
            "proactivity": self.proactivity_manager
        })
        task = asyncio.create_task(self.self_repair_module.start_monitoring())
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)

        # Инициализация autonomy engine
        from .autonomy_engine import get_autonomy_engine
        self.autonomy_engine = await get_autonomy_engine()

        # Инициализация evolution engine
        self.evolution_engine = EvolutionEngine(
            personality_engine=await get_personality_engine(),
            autonomy_engine=self.autonomy_engine
        )
        
        # Инициализация проактивности
        if self.autonomy_engine and self.neuro_interface:
            self.proactivity_manager = ProactivityManager(
                self.evolution_engine,
                self.autonomy_engine,
                self.neuro_interface
            )
            await self.proactivity_manager.start()

        # Установка уровня автономности по умолчанию
        if self.autonomy_engine:
            self.autonomy_engine.set_autonomy_level(AutonomyLevel.ASSISTIVE)

    async def enable_autonomy(self, level: AutonomyLevel = AutonomyLevel.ASSISTIVE) -> Dict[str, Any]:
        """Включить автономность"""
        if not self.autonomy_engine:
            await self.initialize()

        if self.autonomy_engine:
            self.autonomy_engine.set_autonomy_level(level)
            self.autonomy_enabled = True

            # Запуск мониторинга
            task: asyncio.Task[Any] = asyncio.create_task(self.autonomy_engine.start_monitoring())
            _background_tasks.add(task)
            task.add_done_callback(_background_tasks.discard)

        return {
            "success": True,
            "autonomy_level": level.value,
            "message": f"Автономность включена на уровне {level.value}"
        }

    async def disable_autonomy(self) -> Dict[str, Any]:
        """Отключить автономность"""
        if self.autonomy_engine:
            self.autonomy_engine.set_autonomy_level(AutonomyLevel.MANUAL)
            self.autonomy_enabled = False

        return {
            "success": True,
            "message": "Автономность отключена"
        }

    async def process_voice_input(
        self,
        audio_data: bytes,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Обработать голосовой ввод с учетом автономности и обучения"""

        # Базовая обработка
        result = await super().process_voice_input(audio_data, context or {})

        # Обновление контекстной памяти
        self.context_memory.append({
            "text": result.get("text", ""),
            "intent": result.get("intent", "unknown"),
            "timestamp": datetime.now().isoformat()
        })
        if len(self.context_memory) > 10:
            self.context_memory.pop(0)

        # Обучение на основе взаимодействия
        if self.evolution_engine:
            await self.evolution_engine.process_event("user_interaction", {
                "confidence": result.get("confidence", 0.9),
                "intent": result.get("intent", "unknown")
            })

        # Если ошибка - предложить автономную помощь
        if "error" in result and self.autonomy_enabled:
            assistance = await self._offer_autonomous_assistance(result["error"])
            result["autonomous_assistance"] = assistance

        return result

    async def _offer_autonomous_assistance(self, error: str) -> Dict[str, Any]:
        """Предложить автономную помощь при ошибке"""
        suggestions: List[Dict[str, Any]] = []

        # Запуск Self-Coding расширения для анализа
        if self.self_coding_engine:
            optimization_result = await self.self_coding_engine.run_extension(
                "system_health_optimizer", 
                metrics=self.autonomy_engine.system_metrics if self.autonomy_engine else {}
            )
            if optimization_result and optimization_result.get("suggestions"):
                for s in optimization_result["suggestions"]:
                    suggestions.append({
                        "type": "extension_suggest",
                        "description": s,
                        "action": "run_optimization",
                        "confidence": 0.85
                    })

        # Анализ ошибки и предложение решений
        if "vpn" in error.lower():
            suggestions.append({
                "type": "auto_fix",
                "description": "Автоматически перезапустить VPN",
                "action": "restart_vpn",
                "confidence": 0.8
            })

        if "память" in error.lower() or "memory" in error.lower():
            suggestions.append({
                "type": "optimization",
                "description": "Оптимизировать использование памяти",
                "action": "optimize_memory",
                "confidence": 0.9
            })

        # Проверить доступные автономные действия
        if self.autonomy_engine:
            for action_id, action in self.autonomy_engine.registered_actions.items():
                if action.action_type == ActionType.ERROR_PREVENTION:
                    suggestions.append({
                        "type": "prevention",
                        "description": action.description,
                        "action": action_id,
                        "confidence": 0.7
                    })

        return {
            "error_detected": error,
            "suggestions": suggestions,
            "can_auto_fix": len(suggestions) > 0
        }

    async def get_autonomy_status(self) -> Dict[str, Any]:
        """Получить статус автономности"""
        if not self.autonomy_engine:
            return {"error": "Autonomy engine not initialized"}

        return {
            "enabled": self.autonomy_enabled,
            "current_level": self.autonomy_engine.current_level.value,
            "active_actions": len(self.autonomy_engine.active_actions),
            "scheduled_actions": len(self.autonomy_engine.scheduled_actions),
            "action_history": len(self.autonomy_engine.action_history),
            "system_metrics": self.autonomy_engine.system_metrics,
            "available_actions": len(self.autonomy_engine.registered_actions)
        }

    async def trigger_autonomous_action(self, action_id: str) -> Dict[str, Any]:
        """Запустить автономное действие вручную"""
        if not self.autonomy_engine:
            return {"error": "Autonomy engine not initialized"}

        if action_id not in self.autonomy_engine.registered_actions:
            return {"error": f"Action {action_id} not found"}

        action = self.autonomy_engine.registered_actions[action_id]

        # Запуск действия
        task: asyncio.Task[Any] = asyncio.create_task(self.autonomy_engine.execute_action(action))
        _background_tasks.add(task)
        task.add_done_callback(_background_tasks.discard)

        return {
            "success": True,
            "action_triggered": action_id,
            "description": action.description,
            "estimated_time": action.estimated_time
        }

    async def get_autonomy_recommendations(self) -> Dict[str, Any]:
        """Получить рекомендации по автономности"""
        if not self.autonomy_engine:
            return {"error": "Autonomy engine not initialized"}

        recommendations: List[Dict[str, Any]] = []
        metrics = self.autonomy_engine.system_metrics

        # Анализ метрик и рекомендации
        if metrics.get("cpu_usage", 0) > 70:
            recommendations.append({
                "type": "optimization",
                "priority": "high",
                "description": "Высокая загрузка CPU - рекомендую оптимизацию",
                "action": "performance_tune",
                "potential_improvement": "20%"
            })

        if metrics.get("memory_usage", 0) > 80:
            recommendations.append({
                "type": "maintenance",
                "priority": "high",
                "description": "Высокое использование памяти - рекомендую очистку",
                "action": "cleanup_temp",
                "potential_improvement": "15%"
            })

        if metrics.get("disk_usage", 0) > 85:
            recommendations.append({
                "type": "cleanup",
                "priority": "medium",
                "description": "Мало места на диске - рекомендую очистку временных файлов",
                "action": "auto_cleanup_temp",
                "potential_improvement": "5GB"
            })

        if metrics.get("last_scan", datetime.min) < (datetime.now() - timedelta(hours=24)):
            recommendations.append({
                "type": "security",
                "priority": "medium",
                "description": "Последнее сканирование было более 24 часов назад",
                "action": "security_scan",
                "potential_improvement": "Повышение безопасности"
            })

        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "system_health_score": self._calculate_health_score(metrics)
        }

    def _calculate_health_score(self, metrics: Dict[str, Any]) -> int:
        """Рассчитать оценку здоровья системы"""
        score = 100

        # Вычитаем баллы за проблемы
        if metrics.get("cpu_usage", 0) > 80:
            score -= 15
        elif metrics.get("cpu_usage", 0) > 60:
            score -= 5

        if metrics.get("memory_usage", 0) > 85:
            score -= 15
        elif metrics.get("memory_usage", 0) > 70:
            score -= 5

        if metrics.get("disk_usage", 0) > 90:
            score -= 20
        elif metrics.get("disk_usage", 0) > 80:
            score -= 10

        if metrics.get("error_rate", 0) > 5:
            score -= 10
        elif metrics.get("error_rate", 0) > 2:
            score -= 5

        if metrics.get("response_time", 0) > 1000:
            score -= 10
        elif metrics.get("response_time", 0) > 500:
            score -= 5

        return max(0, score)

    async def set_autonomy_preferences(self, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Установить предпочтения автономности"""
        if not self.autonomy_engine:
            return {"error": "Autonomy engine not initialized"}

        # Установка порогов
        if "thresholds" in preferences:
            for key, value in preferences["thresholds"].items():
                if key in self.autonomy_engine.thresholds:
                    self.autonomy_engine.thresholds[key] = value

        # Установка уровня
        if "level" in preferences:
            try:
                level = AutonomyLevel(preferences["level"])
                if self.autonomy_engine:
                    self.autonomy_engine.set_autonomy_level(level)
            except ValueError:
                return {"error": f"Invalid autonomy level: {preferences['level']}"}

        # Включение/выключение обучения
        if "learning_enabled" in preferences and self.autonomy_engine:
            self.autonomy_engine.learning_enabled = preferences["learning_enabled"]

        return {
            "success": True,
            "updated_preferences": preferences,
            "current_settings": {
                "level": self.autonomy_engine.current_level.value if self.autonomy_engine else None,
                "thresholds": self.autonomy_engine.thresholds if self.autonomy_engine else {},
                "learning_enabled": self.autonomy_engine.learning_enabled if self.autonomy_engine else False
            }
        }

# Фабрика для создания автономного JARVIS
async def create_autonomous_jarvis_service(
    websocket: Any,
    user_id: str
) -> "AutonomousJarvisService":
    """Создать автономный JARVIS сервис"""
    service = AutonomousJarvisService(websocket, user_id)
    await service.initialize()
    return service
