import pytest
import numpy as np
from app.services.jarvis.neuro_interface import NeuroInterface, NeuroSignal, NeuroSignalType, ThoughtIntent
from datetime import datetime

@pytest.mark.asyncio
async def test_neuro_interface_basic():
    """Тест базовой функциональности Neuro Interface"""
    interface = NeuroInterface()
    
    # 1. Запуск сессии
    await interface.start_session()
    assert interface.is_active is True
    
    # 2. Инъекция сигнала
    # Создаем фиктивные данные ЭЭГ (1000 сэмплов)
    eeg_data = np.random.random(1000)
    signal = NeuroSignal(
        signal_type=NeuroSignalType.EEG,
        data=eeg_data,
        timestamp=datetime.now(),
        sampling_rate=250.0,
        channels=["Fp1"],
        quality=1.0
    )
    
    # Инъектируем 10 сигналов для запуска процессора
    for _ in range(10):
        await interface.inject_signal(signal)
    
    assert len(interface.session_data) == 10
    
    # 3. Остановка сессии
    await interface.stop_session()
    assert interface.is_active is False

@pytest.mark.asyncio
async def test_thought_processor_logic():
    """Тест логики распознавания мыслей"""
    from app.services.jarvis.neuro_interface import ThoughtProcessor
    processor = ThoughtProcessor()
    
    # Создаем 10 сигналов с высокой гамма-активностью (имитация команды)
    signals = []
    for _ in range(10):
        # В демо-режиме analyze_bands возвращает фиксированные значения, 
        # но мы можем протестировать структуру
        signal = NeuroSignal(
            signal_type=NeuroSignalType.EEG,
            data=np.random.random(100),
            timestamp=datetime.now(),
            sampling_rate=250.0,
            channels=["EEG"],
            quality=1.0
        )
        signals.append(signal)
        
    pattern = await processor.process_signals(signals)
    assert pattern is not None
    assert isinstance(pattern.intent, ThoughtIntent)
    assert 0 <= pattern.confidence <= 1.0
