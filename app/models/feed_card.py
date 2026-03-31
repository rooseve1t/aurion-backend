"""
Модель карточек Activity Feed
"""
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database_final import Base, UUIDType


class FeedCard(Base):
    __tablename__ = "feed_cards"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    type = Column(String(20), nullable=False)   # observation | suggestion | alert | insight
    domain = Column(String(20), nullable=False)  # health | finance | security | calendar
    title = Column(Text, nullable=False)
    body = Column(Text, nullable=False)
    priority = Column(String(10), nullable=False, default="low")  # low | medium | high | critical

    requires_confirmation = Column(Boolean, default=False, nullable=False)
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    dismissed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Связи
    user = relationship("User", back_populates="feed_cards")

    def __repr__(self):
        return f"<FeedCard(id={self.id}, type={self.type}, domain={self.domain}, priority={self.priority})>"
