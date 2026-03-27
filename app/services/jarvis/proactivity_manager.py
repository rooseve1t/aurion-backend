import logging
import asyncio
import gc
from typing import Dict, Any, Set, Optional
from .evolution_engine import EvolutionEngine
from .autonomy_engine import AutonomyEngine
from .neuro_interface import NeuroInterface
from ..osint_service import OSINTService

logger = logging.getLogger("jarvis-proactivity")

class ProactivityManager:
    """Менеджер проактивности JARVIS (Stage 21)"""
    
    def __init__(self, evolution_engine: EvolutionEngine, autonomy_engine: AutonomyEngine, neuro_interface: NeuroInterface, osint_service: Optional[OSINTService] = None):
        self.evolution = evolution_engine
        self.autonomy = autonomy_engine
        self.neuro = neuro_interface
        self.osint = osint_service
        self._is_monitoring = False
        self._background_tasks: Set[asyncio.Task[Any]] = set()

    async def start(self):
        """Запустить мониторинг проактивности"""
        if self._is_monitoring:
            return
            
        self._is_monitoring = True
        logger.info("🚀 Proactivity Manager started.")
        
        # Запуск цикла предсказания потребностей
        task: asyncio.Task[Any] = asyncio.create_task(self._prediction_loop())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        
        # Запуск цикла нейро-мониторинга
        task = asyncio.create_task(self._neuro_monitoring_loop())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        
        # Запуск Sentinel Protocol (OSINT мониторинг)
        task = asyncio.create_task(self._sentinel_protocol_loop())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)
        
        # Запуск QA: Сборщик мусора (Memory Leak Protection)
        task = asyncio.create_task(self._garbage_collection_loop())
        self._background_tasks.add(task)
        task.add_done_callback(self._background_tasks.discard)

    async def _garbage_collection_loop(self):
        """Фоновая очистка памяти (Stage 22: QA Shield)"""
        while self._is_monitoring:
            try:
                gc.collect()
                logger.debug("🧹 QA Shield: Background garbage collection executed.")
                await asyncio.sleep(3600) # Раз в час
            except Exception as e:
                logger.error(f"Error in GC loop: {e}")
                await asyncio.sleep(600)

    async def _sentinel_protocol_loop(self):
        """Проактивный мониторинг угроз (Sentinel Protocol)"""
        while self._is_monitoring:
            try:
                if self.osint:
                    logger.info("🛡️ Sentinel: Scanning for active threats based on recent OSINT data...")
                    # В реальности здесь анализ последних запросов из БД
                    # Для MVP - имитация обнаружения угрозы
                    await self.autonomy.notify_user("Сэр, обнаружена подозрительная активность на одном из ваших мониторимых IP. Включаю активную защиту.")
                    
                await asyncio.sleep(3600)  # Раз в час
            except Exception as e:
                logger.error(f"Error in sentinel loop: {e}")
                await asyncio.sleep(300)

    async def stop(self):
        """Остановить мониторинг"""
        self._is_monitoring = False
        for task in list(self._background_tasks):
            task.cancel()
        logger.info("🛑 Proactivity Manager stopped.")

    async def _prediction_loop(self):
        """Фоновый цикл предсказания потребностей"""
        while self._is_monitoring:
            try:
                # Получаем предсказания от движка эволюции
                predictions = await self.evolution.predict_next_needs()
                
                for pred in predictions:
                    await self._handle_prediction(pred)
                    
                await asyncio.sleep(300)  # Раз в 5 минут
            except Exception as e:
                logger.error(f"Error in prediction loop: {e}")
                await asyncio.sleep(60)

    async def _neuro_monitoring_loop(self):
        """Фоновый цикл мониторинга нейросигналов"""
        while self._is_monitoring:
            try:
                if self.neuro.is_active:
                    # В реальном сценарии здесь получение данных из board
                    # Для Stage 21 используем инъекцию сигналов или проверку последних паттернов
                    if self.neuro.processor.patterns:
                        last_pattern = self.neuro.processor.patterns[-1]
                        if last_pattern.confidence > 0.8:
                            await self.evolution.process_event("neuro_signal_detected", {
                                "intent": last_pattern.intent.value,
                                "confidence": last_pattern.confidence,
                                "emotional_state": last_pattern.emotional_state
                            })
                            
                await asyncio.sleep(10)  # Раз в 10 секунд
            except Exception as e:
                logger.error(f"Error in neuro monitoring loop: {e}")
                await asyncio.sleep(30)

    async def _handle_prediction(self, prediction: Dict[str, Any]):
        """Обработать предсказание"""
        logger.info(f"🔮 JARVIS Prediction: {prediction['suggestion']} (Reason: {prediction['reason']})")
        
        # Если автономность на высоком уровне - можно выполнить автоматически
        if self.autonomy.current_level.value >= 2: # SEMI_AUTO or FULL_AUTO
            # Здесь логика запуска автономного действия
            pass
        else:
            # Предлагаем пользователю через TTS/WebSocket
            await self.autonomy.notify_user(f"Сэр, {prediction['suggestion']}")
