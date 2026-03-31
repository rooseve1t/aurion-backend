"""
Модель предложений самоэволюции JARVIS (только для Creator)
"""
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database_final import Base, UUIDType, JSONType


class EvolutionProposal(Base):
    __tablename__ = "evolution_proposals"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    description = Column(Text, nullable=False)
    diff = Column(Text, nullable=False)
    affected_files = Column(JSONType, default=list, nullable=False)  # list[str]
    test_command = Column(String(500), nullable=False, default="pytest")

    # pending | applied | rolled_back | rejected
    status = Column(String(20), nullable=False, default="pending")

    commit_hash = Column(String(40), nullable=True)
    error_log = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Связи
    user = relationship("User", back_populates="evolution_proposals")

    def __repr__(self):
        return f"<EvolutionProposal(id={self.id}, status={self.status})>"
