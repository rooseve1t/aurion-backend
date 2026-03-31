"""
Модель доверенных устройств для 2FA
"""
import uuid
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..database_final import Base, UUIDType


class TrustedDevice(Base):
    __tablename__ = "trusted_devices"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUIDType, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    device_fingerprint = Column(String(255), nullable=False)
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6

    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)

    # Связи
    user = relationship("User", back_populates="trusted_devices")

    def __repr__(self):
        return f"<TrustedDevice(id={self.id}, user_id={self.user_id}, revoked={self.revoked})>"
