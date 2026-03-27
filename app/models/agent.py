"""
Модели агентов и роевого интеллекта
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database_final import Base, UUIDType, JSONType


class Agent(Base):
    __tablename__ = "agents"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUIDType, ForeignKey("users.id"), nullable=False, index=True)
    
    # Основная информация
    name = Column(String(200), nullable=False)
    agent_type = Column(String(50), nullable=False)  # financial, smarthome, osint, memory, etc.
    description = Column(Text, nullable=True)
    
    # Конфигурация
    config = Column(JSONType, default=dict, nullable=True)
    capabilities = Column(JSONType, default=list, nullable=True)
    model = Column(String(100), nullable=True)  # Используемая AI модель
    
    # Статус
    is_active = Column(Boolean, default=True, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    status = Column(String(20), default="idle", nullable=False)  # idle, busy, error, offline
    
    # Производительность
    tasks_completed = Column(Integer, default=0, nullable=False)
    success_rate = Column(Float, default=0.0, nullable=False)
    avg_response_time_ms = Column(Integer, nullable=True)
    
    # Настройки
    priority = Column(Integer, default=5, nullable=False)  # 1-10
    max_concurrent_tasks = Column(Integer, default=1, nullable=False)
    timeout_seconds = Column(Integer, default=60, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_task_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    user = relationship("User", back_populates="agents")
    tasks = relationship("AgentTask", back_populates="agent", cascade="all, delete-orphan")
    logs = relationship("AgentLog", back_populates="agent", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Agent(id={self.id}, name={self.name}, type={self.agent_type}, status={self.status})>"


class AgentTask(Base):
    __tablename__ = "agent_tasks"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(UUIDType, ForeignKey("agents.id"), nullable=False, index=True)
    user_id = Column(UUIDType, ForeignKey("users.id"), nullable=False, index=True)
    
    # Задача
    task_type = Column(String(50), nullable=False)
    input_data = Column(JSONType, nullable=False)
    output_data = Column(JSONType, nullable=True)
    
    # Статус
    status = Column(String(20), default="pending", nullable=False)  # pending, running, completed, failed, cancelled
    progress = Column(Integer, default=0, nullable=False)  # 0-100
    
    # Результаты
    result = Column(JSONType, nullable=True)
    error_message = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    
    # Оркестрация
    parent_task_id = Column(UUIDType, ForeignKey("agent_tasks.id"), nullable=True)
    swarm_task_id = Column(String(100), nullable=True)  # ID роевой задачи
    priority = Column(Integer, default=5, nullable=False)
    
    # Время
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    timeout_at = Column(DateTime(timezone=True), nullable=True)
    
    # Метрики
    tokens_used = Column(Integer, nullable=True)
    cost_estimate = Column(Float, nullable=True)
    
    # Связи
    agent = relationship("Agent", back_populates="tasks")
    parent_task = relationship("AgentTask", remote_side=[id])
    
    def __repr__(self):
        return f"<AgentTask(id={self.id}, type={self.task_type}, status={self.status})>"


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    agent_id = Column(UUIDType, ForeignKey("agents.id"), nullable=False, index=True)
    task_id = Column(UUIDType, ForeignKey("agent_tasks.id"), nullable=True, index=True)
    
    # Лог
    level = Column(String(10), default="info", nullable=False)  # debug, info, warning, error
    message = Column(Text, nullable=False)
    details = Column(JSONType, nullable=True)
    
    # Метаданные
    event_type = Column(String(50), nullable=True)  # task_start, task_complete, error, etc.
    context = Column(JSONType, nullable=True)
    
    # Время
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Связи
    agent = relationship("Agent", back_populates="logs")
    task = relationship("AgentTask")
    
    def __repr__(self):
        return f"<AgentLog(id={self.id}, agent_id={self.agent_id}, level={self.level})>"
