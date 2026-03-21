"""
Модель векторной памяти
"""
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from typing import List, Optional
import uuid

# Импортируем VECTOR из pgvector
try:
    from pgvector.sqlalchemy import VECTOR
except ImportError:
    # Заглушка если pgvector не установлен
    class VECTOR:
        def __init__(self, *args, **kwargs):
            pass

from ..database import Base


class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    
    # Контент
    content = Column(Text, nullable=False)
    content_type = Column(String(50), default="text", nullable=False)  # text, image, audio, etc.
    title = Column(String(500), nullable=True)
    
    # Векторное представление (pgvector)
    embedding = Column(VECTOR(384), nullable=True)  # Для paraphrase-multilingual-MiniLM-L12-v2
    
    # Метаданные
    tags = Column(JSONB, default=list, nullable=True)
    categories = Column(JSONB, default=list, nullable=True)
    entry_metadata = Column(JSONB, default=dict, nullable=True)  # Переименовано из metadata
    
    # Важность и приоритет
    importance = Column(Integer, default=5, nullable=False)  # 1-10
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, urgent
    
    # Эмоциональная окраска
    sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    emotion = Column(JSONB, nullable=True)  # Детальные эмоции
    
    # Контекст
    context = Column(JSONB, nullable=True)  # Связанный контекст
    source = Column(String(100), nullable=True)  # Источник: chat, voice, manual, etc.
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Автоудаление
    
    # Статистика доступа
    access_count = Column(Integer, default=0, nullable=False)
    last_accessed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    user = relationship("User", back_populates="memory_entries")
    
    def __repr__(self):
        return f"<MemoryEntry(id={self.id}, user_id={self.user_id}, importance={self.importance})>"
