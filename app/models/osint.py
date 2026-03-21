"""
Модели OSINT и аудита
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Запрос
    service = Column(String(50), nullable=False)  # censys, shodan, apify, etc.
    query_type = Column(String(50), nullable=False)  # ip, email, domain, etc.
    query = Column(String(1000), nullable=False)
    
    # Результат
    result_count = Column(Integer, default=0, nullable=False)
    results = Column(JSONB, nullable=True)
    summary = Column(JSONB, nullable=True)  # Агрегированные данные
    
    # Метаданные
    response_time_ms = Column(Integer, nullable=True)
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    
    # Стоимость и лимиты
    credits_used = Column(Integer, nullable=True)
    cost_estimate = Column(Float, nullable=True)
    rate_limit_remaining = Column(Integer, nullable=True)
    
    # Геолокация и контекст
    source_ip = Column(String(45), nullable=True)  # IPv6 поддержка
    user_agent = Column(String(500), nullable=True)
    
    # Время
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Кэширование
    cache_key = Column(String(100), nullable=True, index=True)
    cached_at = Column(DateTime(timezone=True), nullable=True)
    cache_ttl_seconds = Column(Integer, default=3600, nullable=False)
    
    # Классификация
    risk_level = Column(String(20), nullable=True)  # low, medium, high, critical
    categories = Column(JSONB, default=list, nullable=True)
    
    # Связи
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, service={self.service}, query_type={self.query_type}, success={self.success})>"


class OSINTTarget(Base):
    __tablename__ = "osint_targets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Цель
    target_type = Column(String(50), nullable=False)  # ip, domain, email, phone, etc.
    target_value = Column(String(500), nullable=False)
    name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    
    # Статус мониторинга
    is_monitored = Column(Boolean, default=False, nullable=False)
    monitoring_enabled = Column(Boolean, default=True, nullable=False)
    
    # Настройки мониторинга
    check_interval_hours = Column(Integer, default=24, nullable=False)
    alert_on_change = Column(Boolean, default=True, nullable=False)
    
    # Последние результаты
    last_check_at = Column(DateTime(timezone=True), nullable=True)
    last_result_hash = Column(String(64), nullable=True)
    change_count = Column(Integer, default=0, nullable=False)
    
    # Метаданные
    osint_metadata = Column(JSONB, nullable=True)
    
    # Время
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    user = relationship("User")
    
    def __repr__(self):
        return f"<OSINTTarget(id={self.id}, type={self.target_type}, value={self.target_value})>"
