"""
Модели платежной системы и подписок
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # Основная информация
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Ценообразование
    price = Column(Float, nullable=False)  # Цена в рублях
    currency = Column(String(3), default="RUB", nullable=False)
    billing_interval = Column(String(20), default="month", nullable=False)  # month, year, lifetime
    trial_days = Column(Integer, default=0, nullable=False)
    
    # Функции
    features = Column(JSONB, default=dict, nullable=True)  # {voice: true, memory_limit: 1000, ...}
    limits = Column(JSONB, default=dict, nullable=True)  # Лимиты по функциям
    
    # Статус
    is_active = Column(Boolean, default=True, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    
    # Маркетинг
    badge = Column(String(50), nullable=True)  # popular, new, recommended
    color = Column(String(20), nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    subscriptions = relationship("Subscription", back_populates="tariff")
    
    def __repr__(self):
        return f"<Tariff(id={self.id}, name={self.name}, price={self.price})>"


class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tariff_id = Column(UUID(as_uuid=True), ForeignKey("tariffs.id"), nullable=False, index=True)
    
    # Статус
    status = Column(String(20), default="active", nullable=False)  # active, cancelled, expired, trial
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Период
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    trial_end = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Автопродление
    auto_renew = Column(Boolean, default=True, nullable=False)
    next_billing_amount = Column(Float, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Метаданные
    payment_metadata = Column(JSONB, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="subscriptions")
    tariff = relationship("Tariff", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")
    
    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status={self.status})>"


class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id"), nullable=True, index=True)
    
    # Платежная система
    provider = Column(String(20), default="yookassa", nullable=False)  # yookassa, stripe, etc.
    external_id = Column(String(100), nullable=True)  # ID в платежной системе
    
    # Сумма
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="RUB", nullable=False)
    
    # Статус
    status = Column(String(20), default="pending", nullable=False)  # pending, succeeded, failed, cancelled, refunded
    paid = Column(Boolean, default=False, nullable=False)
    
    # Описание
    description = Column(Text, nullable=False)
    transaction_metadata = Column(JSONB, nullable=True)
    
    # Способ оплаты
    payment_method = Column(String(50), nullable=True)  # card, sbp, etc.
    payment_method_details = Column(JSONB, nullable=True)
    
    # Время
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Возвраты
    refunded_amount = Column(Float, default=0.0, nullable=False)
    refunds = Column(JSONB, default=list, nullable=True)
    
    # Комиссии
    fee = Column(Float, nullable=True)
    net_amount = Column(Float, nullable=True)
    
    # Связи
    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status})>"
