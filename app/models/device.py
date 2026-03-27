"""
Модель устройства умного дома
"""
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from ..database_final import Base, UUIDType, JSONType


class Device(Base):
    __tablename__ = "devices"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUIDType, ForeignKey("users.id"), nullable=False, index=True)
    
    # Основная информация
    name = Column(String(200), nullable=False)
    device_type = Column(String(50), nullable=False)  # light, switch, thermostat, lock, sensor, camera, etc.
    manufacturer = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    
    # Расположение
    room = Column(String(100), nullable=True)
    location = Column(JSONType, nullable=True)  # Координаты, зона в комнате
    
    # Подключение
    protocol = Column(String(20), default="mqtt", nullable=False)  # mqtt, matter, zigbee, wifi, etc.
    address = Column(String(200), nullable=True)  # MAC, IP, MQTT topic
    topic = Column(String(200), nullable=True)
    status_topic = Column(String(200), nullable=True)
    
    # Состояние
    state = Column(JSONType, default=dict, nullable=True)
    capabilities = Column(JSONType, default=list, nullable=True)  # Доступные команды и параметры
    settings = Column(JSONType, default=dict, nullable=True)  # Настройки устройства
    
    # Статус
    is_online = Column(Boolean, default=False, nullable=False)
    is_enabled = Column(Boolean, default=True, nullable=False)
    battery_level = Column(Integer, nullable=True)  # 0-100 для батарейных устройств
    
    # Энергопотребление
    power_consumption = Column(Integer, nullable=True)  # Вт
    energy_usage = Column(JSONType, nullable=True)  # История потребления
    
    # Безопасность
    is_secure = Column(Boolean, default=True, nullable=False)
    encryption_enabled = Column(Boolean, default=False, nullable=False)
    
    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    last_command_at = Column(DateTime(timezone=True), nullable=True)
    
    # Связи
    user = relationship("User", back_populates="devices")
    command_logs = relationship("DeviceCommandLog", back_populates="device", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Device(id={self.id}, name={self.name}, type={self.device_type}, online={self.is_online})>"


class DeviceCommandLog(Base):
    __tablename__ = "device_command_log"

    id = Column(UUIDType, primary_key=True, default=uuid.uuid4, index=True)
    device_id = Column(UUIDType, ForeignKey("devices.id"), nullable=False, index=True)
    user_id = Column(UUIDType, ForeignKey("users.id"), nullable=False, index=True)
    
    # Команда
    command = Column(String(100), nullable=False)
    parameters = Column(JSONType, default=dict, nullable=True)
    
    # Результат
    success = Column(Boolean, nullable=False)
    response = Column(JSONType, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Время
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time_ms = Column(Integer, nullable=True)
    
    # Источник
    source = Column(String(50), nullable=True)  # voice, app, automation, schedule
    
    # Связи
    device = relationship("Device", back_populates="command_logs")
    
    def __repr__(self):
        return f"<DeviceCommandLog(id={self.id}, device_id={self.device_id}, command={self.command}, success={self.success})>"
