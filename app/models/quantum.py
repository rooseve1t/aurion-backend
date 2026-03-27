"""
Модели квантовых вычислений
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database_final import Base, UUIDType, JSONType


class QuantumJob(Base):
    __tablename__ = "quantum_jobs"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUIDType, ForeignKey("users.id"), nullable=False, index=True)
    
    # Задача
    job_type = Column(String(50), nullable=False)  # optimization, sampling, vqe, qubo, etc.
    algorithm = Column(String(100), nullable=True)  # VQE, QAOA, Grover, etc.
    
    # Входные данные
    input_data = Column(JSONType, nullable=False)
    parameters = Column(JSONType, default=dict, nullable=True)
    problem_size = Column(Integer, nullable=True)  # N переменных, кубитов и т.д.
    
    # Бэкенд
    backend = Column(String(100), nullable=False)  # ionq, rigetti, dwave, quantum-rings, etc.
    backend_config = Column(JSONType, nullable=True)
    shots = Column(Integer, default=1000, nullable=False)
    
    # Статус
    status = Column(String(20), default="pending", nullable=False)  # pending, queued, running, completed, failed, cancelled
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    
    # Результаты
    result = Column(JSONType, nullable=True)
    solution = Column(JSONType, nullable=True)  # Оптимальное решение
    objective_value = Column(Float, nullable=True)  # Значение целевой функции
    execution_time_ms = Column(Integer, nullable=True)
    quantum_volume = Column(Integer, nullable=True)
    
    # Метрики качества
    fidelity = Column(Float, nullable=True)  # Качество решения
    confidence = Column(Float, nullable=True)  # Уверенность в результате
    error_rate = Column(Float, nullable=True)
    
    # Очередь и планирование
    priority = Column(Integer, default=5, nullable=False)  # 1-10
    queue_position = Column(Integer, nullable=True)
    estimated_completion = Column(DateTime(timezone=True), nullable=True)
    
    # Стоимость
    credits_used = Column(Integer, nullable=True)
    cost_estimate = Column(Float, nullable=True)
    
    # Ошибки
    error_message = Column(Text, nullable=True)
    error_code = Column(String(50), nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Время
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    timeout_at = Column(DateTime(timezone=True), nullable=True)
    
    # Кэширование
    cache_key = Column(String(100), nullable=True, index=True)
    cached_at = Column(DateTime(timezone=True), nullable=True)
    
    # Метаданные
    quantum_metadata = Column(JSONType, nullable=True)
    tags = Column(JSONType, default=list, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="quantum_jobs")
    
    def __repr__(self):
        return f"<QuantumJob(id={self.id}, type={self.job_type}, backend={self.backend}, status={self.status})>"
