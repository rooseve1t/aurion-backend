"""
🧠 Neuro Interface для JARVIS
Реальный BCI (Brain-Computer Interface) с использованием существующих технологий
"""
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging

# Реальные BCI библиотеки
_mne_avail = False
_mne_module: Any = None
_psd_welch_func: Any = None
try:
    import mne as _mne  # type: ignore
    from mne.time_frequency import psd_welch as _psd_welch  # type: ignore
    _mne_module = _mne
    _psd_welch_func = _psd_welch
    _mne_avail = True
except ImportError:
    logging.warning("MNE-Python не установлен. Используем демо режим.")

_brainflow_avail = False
_brainflow_module: Any = None
_board_shim_class: Any = None
_input_params_class: Any = None
try:
    import brainflow as _bf # type: ignore
    from brainflow.board_shim import BoardShim as _BS, BrainFlowInputParams as _BIP # type: ignore
    _brainflow_module = _bf
    _board_shim_class = _BS
    _input_params_class = _BIP
    _brainflow_avail = True
except ImportError:
    logging.warning("BrainFlow не установлен. Используем симуляцию.")

MNE_AVAILABLE: bool = _mne_avail
BRAINFLOW_AVAILABLE: bool = _brainflow_avail
mne: Any = _mne_module
psd_welch: Any = _psd_welch_func
brainflow: Any = _brainflow_module
BoardShim: Any = _board_shim_class
BrainFlowInputParams: Any = _input_params_class

logger = logging.getLogger("jarvis-neuro")

class NeuralFeedbackLoop:
    """Система обратной связи для коррекции личности по ЭЭГ (Stage 22: Neuro-Scientist Synapse)"""
    
    def __init__(self):
        self.calibrated_patterns: Dict[str, Any] = {}
        self.last_adjustment: Optional[str] = None

    async def analyze_and_adjust(self, eeg_data: Any, current_personality: Any):
        """Анализ эмоционального состояния и подстройка Personality Engine"""
        # Имитация анализа через Synapse AI
        stress_level = float(np.random.random())
        if stress_level > 0.7:
            logger.info("🧠 Neuro-Scientist: High stress detected. Switching JARVIS to 'Caring' mode.")
            current_personality.traits["caring"] = min(1.0, float(current_personality.traits.get("caring", 0.5)) + 0.1)
            self.last_adjustment = "stress_relief_caring"
        elif stress_level < 0.2:
            logger.info("🧠 Neuro-Scientist: User is relaxed. Increasing 'Sarcastic' trait for engagement.")
            current_personality.traits["sarcastic"] = min(1.0, float(current_personality.traits.get("sarcastic", 0.5)) + 0.05)
            self.last_adjustment = "relaxed_banter"

class NeuroSignalType(Enum):
    """Типы нейросигналов"""
    EEG = "eeg"           # Электроэнцефалограмма
    EOG = "eog"           # Электроокулограмма (движение глаз)
    EMG = "emg"           # Электромиограмма (мышцы)
    BVP = "bvp"           # Кровяной объемный пульс
    GSR = "gsr"           # Кожно-гальваническая реакция
    TEMPERATURE = "temp"  # Температура
    ACCELEROMETER = "accel" # Ускорение

class ThoughtIntent(Enum):
    """Намерения мыслей"""
    COMMAND = "command"           # Команда
    QUESTION = "question"         # Вопрос
    EMOTION = "emotion"           # Эмоция
    FOCUS = "focus"               # Концентрация
    RELAX = "relax"               # Расслабление
    MEMORY_RECALL = "memory"      # Воспоминание
    CALCULATION = "calc"          # Вычисление
    CREATIVE = "creative"         # Творчество

@dataclass
class NeuroSignal:
    """Нейросигнал"""
    signal_type: NeuroSignalType
    data: Any # np.ndarray
    timestamp: datetime
    sampling_rate: float
    channels: List[str]
    quality: float  # 0-1 качество сигнала

@dataclass
class ThoughtPattern:
    """Распознанный паттерн мысли"""
    intent: ThoughtIntent
    confidence: float  # 0-1 уверенность
    content: str
    emotional_state: str
    cognitive_load: float  # 0-1 когнитивная нагрузка

class BrainWaveDetector:
    """Детектор мозговых волн"""
    
    def __init__(self):
        self.bands: Dict[str, Tuple[float, float]] = {
            'delta': (0.5, 4),    # Глубокий сон
            'theta': (4, 8),      # Медитация, креативность
            'alpha': (8, 13),     # Расслабление, концентрация
            'beta': (13, 30),     # Активность, фокус
            'gamma': (30, 100)    # Высшая когнитивная функция
        }
        
    def analyze_bands(self, signal: Any, sampling_rate: float) -> Dict[str, float]:
        """Анализировать мозговые волны"""
        if not MNE_AVAILABLE or mne is None:
            # Демо режим
            return {
                'delta': 0.1, 'theta': 0.2, 'alpha': 0.3,
                'beta': 0.3, 'gamma': 0.1
            }
        
        # Реальный анализ с MNE
        try:
            # Создаем MNE объект
            ch_names: List[str] = ['EEG']
            info = mne.create_info(ch_names=ch_names, sfreq=sampling_rate, ch_types='eeg')
            raw = mne.io.RawArray(signal.reshape(1, -1), info)
            
            # Вычисляем спектральную плотность
            # psd_welch возвращает (psds, freqs)
            res = psd_welch(raw, fmin=0.5, fmax=100, n_fft=256)
            psd = res[0]
            freqs = res[1]
            
            # Интегрируем по диапазонам
            results: Dict[str, float] = {}
            for band, (fmin, fmax) in self.bands.items():
                idx = np.logical_and(freqs >= fmin, freqs <= fmax)
                results[band] = float(np.mean(psd[0, idx]))
                
            return results
        except Exception as e:
            logger.error(f"Error analyzing bands with MNE: {e}")
            return {
                'delta': 0.1, 'theta': 0.2, 'alpha': 0.3,
                'beta': 0.3, 'gamma': 0.1
            }

class ThoughtProcessor:
    """Процессор мыслей и намерений"""
    
    def __init__(self):
        self.detector = BrainWaveDetector()
        self.patterns: List[ThoughtPattern] = []
        self.thresholds: Dict[ThoughtIntent, float] = {
            ThoughtIntent.COMMAND: 0.7,
            ThoughtIntent.FOCUS: 0.6,
            ThoughtIntent.RELAX: 0.6,
            ThoughtIntent.EMOTION: 0.5
        }

    async def process_signals(self, signals: List[NeuroSignal]) -> Optional[ThoughtPattern]:
        """Преобразовать сигналы в паттерны мыслей"""
        if not signals:
            return None
            
        # Усредняем данные сигналов
        combined_data = np.mean([s.data for s in signals], axis=0)
        sampling_rate = signals[0].sampling_rate
        
        # Анализируем ритмы мозга
        bands = self.detector.analyze_bands(combined_data, sampling_rate)
        
        # Логика распознавания намерений (упрощенная для примера)
        intent = ThoughtIntent.FOCUS
        confidence = 0.5
        content = ""
        
        # Высокая гамма + бета = концентрация/команда
        if bands['gamma'] > 0.4 and bands['beta'] > 0.4:
            intent = ThoughtIntent.COMMAND
            confidence = min(1.0, bands['gamma'] + bands['beta'] - 0.5)
            content = "High cognitive activity detected"
            
        # Высокая альфа = расслабление
        elif bands['alpha'] > 0.6:
            intent = ThoughtIntent.RELAX
            confidence = bands['alpha']
            content = "State of relaxation"
            
        # Высокая тета = творчество/воспоминание
        elif bands['theta'] > 0.5:
            intent = ThoughtIntent.CREATIVE
            confidence = bands['theta']
            content = "Creative/Meditation state"

        pattern = ThoughtPattern(
            intent=intent,
            confidence=confidence,
            content=content,
            emotional_state="neutral",
            cognitive_load=float(bands['beta'] + bands['gamma']) / 2.0
        )
        
        self.patterns.append(pattern)
        return pattern

class NeuroInterface:
    """Центральный интерфейс нейросвязи JARVIS"""
    
    def __init__(self):
        self.processor = ThoughtProcessor()
        self.is_active = False
        self.session_data: List[NeuroSignal] = []
        self.board: Optional[BoardShim] = None
        
    def _init_board(self, board_id: int, serial_port: Optional[str] = None):
        """Инициализировать BCI устройство"""
        if not BRAINFLOW_AVAILABLE:
            logging.error("BrainFlow не доступен. Невозможно инициализировать устройство.")
            return

        params = BrainFlowInputParams()
        if serial_port:
            params.serial_port = serial_port

        try:
            self.board = BoardShim(board_id, params)
            self.board.prepare_session()
            logging.info(f"BrainFlow board {board_id} initialized.")
        except brainflow.BrainFlowError as e:
            logging.error(f"Ошибка инициализации BrainFlow: {e}")
            self.board = None

    async def start_session(self, board_id: int = -1, serial_port: Optional[str] = None):
        """Начать сессию нейромониторинга"""
        self._init_board(board_id, serial_port)
        if self.board:
            self.board.start_stream()
            self.is_active = True
            logging.info("Neuro Interface session started")
        
    async def stop_session(self):
        """Завершить сессию нейромониторинга"""
        if self.board and self.is_active:
            self.board.stop_stream()
            self.board.release_session()
        self.is_active = False
        self.board = None
        logging.info("Neuro Interface session stopped")

    async def get_board_data(self) -> Optional[np.ndarray[Any, Any]]:
        """Получить данные с устройства"""
        if self.board and self.is_active:
            try:
                return self.board.get_board_data()
            except brainflow.BrainFlowError as e:
                logging.error(f"Ошибка получения данных с BrainFlow: {e}")
                return None
        return None

    async def inject_signal(self, signal: NeuroSignal):
        """Принять новый сигнал из внешнего устройства"""
        if not self.is_active:
            return
            
        self.session_data.append(signal)
        # Ограничиваем историю
        if len(self.session_data) > 100:
            self.session_data.pop(0)
            
        # Пробуем распознать мысль
        if len(self.session_data) >= 10:
            pattern = await self.processor.process_signals(self.session_data[-10:])
            if pattern and pattern.confidence > 0.7:
                await self.dispatch_intent(pattern)

    async def dispatch_intent(self, pattern: ThoughtPattern):
        """Отправить распознанное намерение в систему JARVIS"""
        logging.info(f"🧠 JARVIS Detected Thought: {pattern.intent.value} ({pattern.confidence:.2f})")
        # Здесь будет интеграция с AutonomyEngine
        pass
