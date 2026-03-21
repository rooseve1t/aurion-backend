"""
Модели эволюционной системы
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class EvolutionExperiment(Base):
    __tablename__ = "evolution_experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Эксперимент
    experiment_type = Column(String(50), nullable=False)  # code_generation, optimization, testing, etc.
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Цель
    objective = Column(Text, nullable=False)
    success_criteria = Column(JSONB, nullable=False)
    baseline_metrics = Column(JSONB, nullable=True)
    
    # Генерация кода
    prompt = Column(Text, nullable=False)
    generated_code = Column(Text, nullable=True)
    language = Column(String(20), default="python", nullable=False)
    framework = Column(String(50), nullable=True)
    
    # Валидация
    validation_status = Column(String(20), default="pending", nullable=False)  # pending, passed, failed
    validation_errors = Column(JSONB, default=list, nullable=True)
    security_issues = Column(JSONB, default=list, nullable=True)
    
    # Тестирование
    test_status = Column(String(20), default="pending", nullable=False)  # pending, passed, failed, running
    test_results = Column(JSONB, nullable=True)
    coverage_percent = Column(Float, nullable=True)
    performance_metrics = Column(JSONB, nullable=True)
    
    # Выполнение
    execution_status = Column(String(20), default="pending", nullable=False)  # pending, running, completed, failed
    execution_result = Column(JSONB, nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    resource_usage = Column(JSONB, nullable=True)  # cpu, memory, etc.
    
    # Git интеграция
    git_branch = Column(String(100), nullable=True)
    commit_hash = Column(String(40), nullable=True)
    diff_content = Column(Text, nullable=True)
    pr_url = Column(String(500), nullable=True)
    merge_status = Column(String(20), nullable=True)  # pending, merged, rejected
    
    # Оценка
    overall_score = Column(Float, nullable=True)  # 0-100
    innovation_score = Column(Float, nullable=True)
    efficiency_score = Column(Float, nullable=True)
    safety_score = Column(Float, nullable=True)
    
    # Статус
    status = Column(String(20), default="pending", nullable=False)  # pending, running, completed, failed, cancelled
    is_successful = Column(Boolean, nullable=True)
    can_deploy = Column(Boolean, default=False, nullable=False)
    
    # Песочница
    sandbox_id = Column(String(100), nullable=True)
    container_image = Column(String(200), nullable=True)
    timeout_seconds = Column(Integer, default=60, nullable=False)
    
    # Безопасность
    risk_level = Column(String(20), default="medium", nullable=False)  # low, medium, high, critical
    blocked_operations = Column(JSONB, default=list, nullable=True)
    
    # Время
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    timeout_at = Column(DateTime(timezone=True), nullable=True)
    
    # Метаданные
    evolution_metadata = Column(JSONB, nullable=True)
    tags = Column(JSONB, default=list, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="evolution_experiments")
    
    def __repr__(self):
        return f"<EvolutionExperiment(id={self.id}, type={self.experiment_type}, status={self.status})>"
