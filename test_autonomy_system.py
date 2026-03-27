"""
🧪 Тесты автономной системы JARVIS
"""
import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from app.services.jarvis.autonomy_engine import (
    AutonomyEngine, 
    AutonomyLevel, 
    ActionType,
    AutonomousAction
)
from app.services.jarvis.autonomous_jarvis import AutonomousJarvisService

class TestAutonomyEngine:
    """Тесты движка автономности"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.engine = AutonomyEngine()
        
    def test_initial_setup(self):
        """Тест начальной настройки"""
        assert self.engine.current_level == AutonomyLevel.ASSISTIVE
        assert len(self.engine.registered_actions) == 8
        assert len(self.engine.thresholds) == 6
        
    def test_autonomy_levels(self):
        """Тест уровней автономности"""
        levels = list(AutonomyLevel)
        assert len(levels) == 4
        assert AutonomyLevel.MANUAL.value == 0
        assert AutonomyLevel.FULL_AUTO.value == 3
        
    def test_action_registration(self):
        """Тест регистрации действий"""
        test_action = AutonomousAction(
            id="test_action",
            action_type=ActionType.SYSTEM_OPTIMIZATION,
            description="Тестовое действие",
            priority=5,
            autonomy_required=AutonomyLevel.SEMI_AUTO,
            conditions=["cpu_usage > 80"],
            execution_func=AsyncMock(),
            estimated_time=60
        )
        
        self.engine.register_action(test_action)
        assert "test_action" in self.engine.registered_actions
        assert len(self.engine.registered_actions) == 9
        
    def test_condition_evaluation(self):
        """Тест оценки условий"""
        # Установить метрики
        self.engine.system_metrics = {
            "cpu_usage": 85.0,
            "memory_usage": 60.0,
            "disk_usage": 75.0
        }
        
        # Тест простых условий
        asyncio.run(self._test_conditions_async())
        
    async def _test_conditions_async(self):
        """Асинхронные тесты условий"""
        # Условие CPU > 80 должно быть истинным
        assert await self.engine._evaluate_condition("cpu_usage > 80")
        
        # Условие memory > 80 должно быть ложным
        assert not await self.engine._evaluate_condition("memory_usage > 80")
        
        # Условие system_stable должно быть истинным
        assert await self.engine._evaluate_condition("system_stable")
        
    def test_thresholds(self):
        """Тест порогов"""
        assert self.engine.thresholds["cpu_usage"] == 80.0
        assert self.engine.thresholds["memory_usage"] == 85.0
        assert self.engine.thresholds["disk_usage"] == 90.0
        
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    async def test_metrics_collection(self, mock_disk, mock_memory, mock_cpu):
        """Тест сбора метрик"""
        # Мокируем psutil
        mock_cpu.return_value = 75.0
        mock_memory.return_value.percent = 65.0
        mock_disk.return_value.percent = 70.0
        
        await self.engine._collect_system_metrics()
        
        assert self.engine.system_metrics["cpu_usage"] == 75.0
        assert self.engine.system_metrics["memory_usage"] == 65.0
        assert self.engine.system_metrics["disk_usage"] == 70.0
        
    def test_action_prioritization(self):
        """Тест приоритизации действий"""
        actions = [
            {"action": AutonomousAction(
                id="low_priority",
                action_type=ActionType.SYSTEM_OPTIMIZATION,
                description="Low",
                priority=2,
                autonomy_required=AutonomyLevel.SEMI_AUTO,
                conditions=[],
                execution_func=AsyncMock()
            ), "scheduled_time": datetime.now()},
            {"action": AutonomousAction(
                id="high_priority",
                action_type=ActionType.SECURITY_SCAN,
                description="High",
                priority=8,
                autonomy_required=AutonomyLevel.SEMI_AUTO,
                conditions=[],
                execution_func=AsyncMock()
            ), "scheduled_time": datetime.now()}
        ]
        
        # Сортировка по приоритету
        actions.sort(key=lambda x: x["action"].priority, reverse=True)
        
        assert actions[0]["action"].id == "high_priority"
        assert actions[1]["action"].id == "low_priority"

class TestAutonomousJarvisService:
    """Тесты автономного JARVIS сервиса"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.mock_websocket = Mock()
        self.service = AutonomousJarvisService(self.mock_websocket, "test_user")
        
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Тест инициализации"""
        await self.service.initialize()
        
        assert self.service.autonomy_engine is not None
        assert self.service.autonomy_enabled == False
        assert self.service.autonomy_engine.current_level == AutonomyLevel.ASSISTIVE
        
    @pytest.mark.asyncio
    async def test_enable_autonomy(self):
        """Тест включения автономности"""
        await self.service.initialize()
        
        result = await self.service.enable_autonomy(AutonomyLevel.SEMI_AUTO)
        
        assert result["success"] is True
        assert result["autonomy_level"] == 2
        assert self.service.autonomy_enabled == True
        
    @pytest.mark.asyncio
    async def test_disable_autonomy(self):
        """Тест отключения автономности"""
        await self.service.initialize()
        await self.service.enable_autonomy()
        
        result = await self.service.disable_autonomy()
        
        assert result["success"] is True
        assert self.service.autonomy_enabled == False
        assert self.service.autonomy_engine.current_level == AutonomyLevel.MANUAL
        
    @pytest.mark.asyncio
    async def test_autonomy_status(self):
        """Тест получения статуса автономности"""
        await self.service.initialize()
        
        status = await self.service.get_autonomy_status()
        
        assert "enabled" in status
        assert "current_level" in status
        assert "active_actions" in status
        assert "system_metrics" in status
        assert "available_actions" in status
        
    @pytest.mark.asyncio
    async def test_trigger_autonomous_action(self):
        """Тест запуска автономного действия"""
        await self.service.initialize()
        
        result = await self.service.trigger_autonomous_action("security_scan")
        
        assert result["success"] is True
        assert result["action_triggered"] == "security_scan"
        assert "description" in result
        assert "estimated_time" in result
        
    @pytest.mark.asyncio
    async def test_trigger_invalid_action(self):
        """Тест запуска несуществующего действия"""
        await self.service.initialize()
        
        result = await self.service.trigger_autonomous_action("invalid_action")
        
        assert "error" in result
        assert "not found" in result["error"]
        
    @pytest.mark.asyncio
    async def test_autonomy_recommendations(self):
        """Тест получения рекомендаций"""
        await self.service.initialize()
        
        # Установить плохие метрики для получения рекомендаций
        self.service.autonomy_engine.system_metrics = {
            "cpu_usage": 85.0,
            "memory_usage": 90.0,
            "disk_usage": 95.0,
            "last_scan": datetime.now() - timedelta(hours=30)
        }
        
        recommendations = await self.service.get_autonomy_recommendations()
        
        assert "recommendations" in recommendations
        assert "total_recommendations" in recommendations
        assert "system_health_score" in recommendations
        
        # Должны быть рекомендации для высоких метрик
        rec_types = [r["type"] for r in recommendations["recommendations"]]
        assert "optimization" in rec_types
        assert "cleanup" in rec_types
        
    @pytest.mark.asyncio
    async def test_health_score_calculation(self):
        """Тест расчета оценки здоровья"""
        await self.service.initialize()
        
        # Идеальные метрики
        metrics = {
            "cpu_usage": 30.0,
            "memory_usage": 40.0,
            "disk_usage": 50.0,
            "error_rate": 0.5,
            "response_time": 200.0
        }
        
        score = self.service._calculate_health_score(metrics)
        assert score == 100
        
        # Плохие метрики
        metrics = {
            "cpu_usage": 90.0,
            "memory_usage": 95.0,
            "disk_usage": 98.0,
            "error_rate": 8.0,
            "response_time": 1500.0
        }
        
        score = self.service._calculate_health_score(metrics)
        assert score < 50
        
    @pytest.mark.asyncio
    async def test_set_autonomy_preferences(self):
        """Тест установки предпочтений автономности"""
        await self.service.initialize()
        
        preferences = {
            "level": 2,
            "thresholds": {
                "cpu_usage": 75.0,
                "memory_usage": 80.0
            },
            "learning_enabled": False
        }
        
        result = await self.service.set_autonomy_preferences(preferences)
        
        assert result["success"] is True
        assert result["current_settings"]["level"] == 2
        assert result["current_settings"]["thresholds"]["cpu_usage"] == 75.0
        assert result["current_settings"]["learning_enabled"] == False
        
    @pytest.mark.asyncio
    async def test_autonomous_assistance_on_error(self):
        """Тест автономной помощи при ошибке"""
        await self.service.initialize()
        
        # Симуляция ошибки
        error_result = {"error": "VPN connection failed"}
        
        assistance = await self.service._offer_autonomous_assistance(error_result["error"])
        
        assert "error_detected" in assistance
        assert "suggestions" in assistance
        assert "can_auto_fix" in assistance
        
        # Должны быть предложения для VPN ошибки
        suggestions = assistance["suggestions"]
        assert len(suggestions) > 0
        assert any(s["action"] == "restart_vpn" for s in suggestions)

class TestIntegration:
    """Интеграционные тесты"""
    
    @pytest.mark.asyncio
    async def test_full_autonomy_workflow(self):
        """Тест полного рабочего процесса автономности"""
        mock_websocket = Mock()
        service = AutonomousJarvisService(mock_websocket, "test_user")
        
        # 1. Инициализация
        await service.initialize()
        assert service.autonomy_engine is not None
        
        # 2. Включение автономности
        await service.enable_autonomy(AutonomyLevel.SEMI_AUTO)
        assert service.autonomy_enabled == True
        
        # 3. Получение статуса
        status = await service.get_autonomy_status()
        assert status["enabled"] == True
        
        # 4. Получение рекомендаций
        recommendations = await service.get_autonomy_recommendations()
        assert "recommendations" in recommendations
        
        # 5. Запуск действия
        result = await service.trigger_autonomous_action("auto_cleanup_temp")
        assert result["success"] == True
        
        # 6. Отключение автономности
        await service.disable_autonomy()
        assert service.autonomy_enabled == False

# Performance тесты
class TestPerformance:
    """Тесты производительности"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.engine = AutonomyEngine()
        
    def test_condition_evaluation_speed(self):
        """Тест скорости оценки условий"""
        import time
        
        conditions = [
            "cpu_usage > 80",
            "memory_usage > 85",
            "disk_usage > 90",
            "system_stable",
            "error_rate > 5"
        ]
        
        # Установить метрики
        self.engine.system_metrics = {
            "cpu_usage": 75.0,
            "memory_usage": 60.0,
            "disk_usage": 70.0,
            "error_rate": 2.0
        }
        
        start_time = time.time()
        
        # Выполнить 1000 оценок условий
        for _ in range(1000):
            for condition in conditions:
                asyncio.run(self.engine._evaluate_condition(condition))
                
        end_time = time.time()
        avg_time = (end_time - start_time) / (1000 * len(conditions))
        
        # Должно быть быстрее 1ms на оценку
        assert avg_time < 0.001, f"Too slow: {avg_time:.4f}s per evaluation"
        
    def test_action_lookup_speed(self):
        """Тест скорости поиска действий"""
        import time
        
        start_time = time.time()
        
        # Выполнить 10000 поисков действий
        for _ in range(10000):
            _ = self.engine.registered_actions.get("security_scan")
            
        end_time = time.time()
        avg_time = (end_time - start_time) / 10000
        
        # Должно быть быстрее 0.01ms на поиск
        assert avg_time < 0.00001, f"Too slow: {avg_time:.6f}s per lookup"

# Запуск тестов
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
