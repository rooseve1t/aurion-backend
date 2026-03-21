"""
Модель пользователя
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(64), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # 2FA
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32), nullable=True)
    backup_codes = Column(JSONB, nullable=True)
    
    # Роли и статус
    role = Column(String(20), default="user", nullable=False)  # user, admin, creator
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Профиль
    display_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Настройки
    preferences = Column(JSONB, default=dict, nullable=True)
    notifications_enabled = Column(Boolean, default=True, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    memory_entries = relationship("MemoryEntry", back_populates="user", cascade="all, delete-orphan")
    devices = relationship("Device", back_populates="user", cascade="all, delete-orphan")
    agents = relationship("Agent", back_populates="user", cascade="all, delete-orphan")
    bank_connections = relationship("BankConnection", back_populates="user", cascade="all, delete-orphan")
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    quantum_jobs = relationship("QuantumJob", back_populates="user", cascade="all, delete-orphan")
    evolution_experiments = relationship("EvolutionExperiment", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
