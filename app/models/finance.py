"""
Модели финансового модуля
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database import Base


class BankConnection(Base):
    __tablename__ = "bank_connections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Банк
    bank_code = Column(String(20), nullable=False)  # sber, tinkoff, alpha, etc.
    bank_name = Column(String(100), nullable=False)
    
    # OAuth и токены
    client_id = Column(String(100), nullable=True)
    client_secret = Column(Text, nullable=True)  # Зашифрован
    access_token = Column(Text, nullable=True)  # Зашифрован
    refresh_token = Column(Text, nullable=True)  # Зашифрован
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Статус
    is_active = Column(Boolean, default=True, nullable=False)
    is_connected = Column(Boolean, default=False, nullable=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    
    # Настройки
    sync_enabled = Column(Boolean, default=True, nullable=False)
    sync_frequency = Column(Integer, default=3600, nullable=False)  # секунды
    accounts_limit = Column(Integer, nullable=True)
    
    # Безопасность
    webhook_secret = Column(String(100), nullable=True)
    encryption_key_id = Column(String(50), nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Связи
    user = relationship("User", back_populates="bank_connections")
    accounts = relationship("BankAccount", back_populates="bank_connection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BankConnection(id={self.id}, bank={self.bank_code}, connected={self.is_connected})>"


class BankAccount(Base):
    __tablename__ = "bank_accounts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    bank_connection_id = Column(UUID(as_uuid=True), ForeignKey("bank_connections.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Информация о счете
    external_id = Column(String(100), nullable=False)  # ID в системе банка
    account_number = Column(String(50), nullable=True)  # Маскированный номер
    account_name = Column(String(200), nullable=False)
    account_type = Column(String(50), nullable=False)  # checking, savings, credit, etc.
    currency = Column(String(3), default="RUB", nullable=False)
    
    # Балансы
    balance = Column(Float, default=0.0, nullable=False)
    available_balance = Column(Float, nullable=True)
    credit_limit = Column(Float, nullable=True)
    
    # Статус
    is_active = Column(Boolean, default=True, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default="active", nullable=False)
    
    # Метаданные
    bank_metadata = Column(JSONB, nullable=True)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    bank_connection = relationship("BankConnection", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BankAccount(id={self.id}, name={self.account_name}, balance={self.balance})>"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("bank_accounts.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Основная информация
    external_id = Column(String(100), nullable=True)  # ID в системе банка
    description = Column(Text, nullable=False)
    merchant_name = Column(String(200), nullable=True)
    category = Column(String(100), nullable=True)
    mcc_code = Column(Integer, nullable=True)  # Merchant Category Code
    
    # Сумма
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="RUB", nullable=False)
    balance_after = Column(Float, nullable=True)
    
    # Тип операции
    transaction_type = Column(String(20), nullable=False)  # debit, credit, transfer, etc.
    status = Column(String(20), default="completed", nullable=False)  # pending, completed, failed
    
    # Время
    transaction_date = Column(DateTime(timezone=True), nullable=False, index=True)
    posted_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Геолокация
    location = Column(JSONB, nullable=True)  # {lat, lng, address}
    
    # Метаданные
    bank_metadata = Column(JSONB, nullable=True)
    tags = Column(JSONB, default=list, nullable=True)
    notes = Column(Text, nullable=True)
    is_recurring = Column(Boolean, default=False, nullable=False)
    
    # Классификация
    confidence_score = Column(Float, nullable=True)  # Уверенность классификации
    ai_category = Column(String(100), nullable=True)  # Категория от AI
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    
    # Связи
    account = relationship("BankAccount", back_populates="transactions")
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, amount={self.amount}, type={self.transaction_type})>"
