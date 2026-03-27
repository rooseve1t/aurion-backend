"""
Сервис умного дома с MQTT и квантовой оптимизацией
"""
import asyncio
import json
import uuid
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

# MQTT библиотека
try:
    import asyncio_mqtt as aiomqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

from ..models.device import Device, DeviceCommandLog
from ..database_final import get_db

# Redis для кэширования
redis_client: Optional[redis.Redis] = None


class SmartHomeService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis = redis_client
        self.mqtt_client = None
        self.device_states = {}  # Локальное кэширование состояний
        self._mqtt_task: Optional[asyncio.Task] = None  # Ссылка на задачу MQTT
        
        # MQTT настройки
        self.mqtt_host = os.getenv("MQTT_HOST", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.mqtt_username = os.getenv("MQTT_USERNAME", "")
        self.mqtt_password = os.getenv("MQTT_PASSWORD", "")
        
        # Инициализация MQTT с сохранением ссылки
        self._mqtt_task = asyncio.create_task(self._init_mqtt())
    
    async def _init_mqtt(self):
        """Инициализация MQTT клиента"""
        if not MQTT_AVAILABLE:
            print("MQTT library not available")
            return
        
        try:
            if self.mqtt_username and self.mqtt_password:
                self.mqtt_client = aiomqtt.Client(
                    hostname=self.mqtt_host,
                    port=self.mqtt_port,
                    username=self.mqtt_username,
                    password=self.mqtt_password
                )
            else:
                self.mqtt_client = aiomqtt.Client(
                    hostname=self.mqtt_host,
                    port=self.mqtt_port
                )
            
            # Запуск прослушивания
            asyncio.create_task(self._mqtt_listener())
            
        except Exception as e:
            print(f"MQTT initialization failed: {e}")
    
    async def _mqtt_listener(self):
        """Прослушивание MQTT сообщений"""
        if not self.mqtt_client:
            return
        
        try:
            async with self.mqtt_client:
                await self.mqtt_client.subscribe("aurion/devices/+/status")
                
                async for message in self.mqtt_client.messages:
                    await self._handle_mqtt_message(message)
                    
        except Exception as e:
            print(f"MQTT listener error: {e}")
    
    async def _handle_mqtt_message(self, message):
        """Обработка входящего MQTT сообщения"""
        try:
            topic = str(message.topic)
            payload = json.loads(message.payload.decode())
            
            # Извлечение device_id из топика
            topic_parts = topic.split("/")
            if len(topic_parts) >= 4:
                device_id = topic_parts[2]
                
                # Обновление состояния устройства
                await self._update_device_state(device_id, payload)
                
        except Exception as e:
            print(f"MQTT message handling error: {e}")
    
    async def _update_device_state(self, device_id: str, state: Dict[str, Any]):
        """Обновление состояния устройства"""
        
        # Кэширование состояния
        self.device_states[device_id] = state
        
        # Обновление в базе данных
        from sqlalchemy import select, update
        
        stmt = (
            update(Device)
            .where(Device.id == device_id)
            .values(
                state=state,
                last_seen_at=datetime.now(timezone.utc)
            )
        )
        
        await self.db.execute(stmt)
        await self.db.commit()
    
    async def add_device(
        self,
        user_id: str,
        name: str,
        device_type: str,
        room: str,
        protocol: str = "mqtt",
        address: Optional[str] = None,
        topic: Optional[str] = None,
        capabilities: Optional[List[str]] = None
    ) -> Device:
        """Добавление нового устройства"""
        
        device = Device(
            user_id=user_id,
            name=name,
            device_type=device_type,
            room=room,
            protocol=protocol,
            address=address,
            topic=topic,
            status_topic=f"{topic}/status" if topic else None,
            capabilities=capabilities or [],
            is_online=False
        )
        
        self.db.add(device)
        await self.db.commit()
        await self.db.refresh(device)
        
        # Подписка на статус устройства
        if device.status_topic and self.mqtt_client:
            asyncio.create_task(self._subscribe_device_status(device.status_topic))
        
        return device
    
    async def control_device(
        self,
        user_id: str,
        device_id: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Управление устройством"""
        
        # Получение устройства
        device = await self._get_device(user_id, device_id)
        if not device:
            return {
                "status": "error",
                "error": "Device not found"
            }
        
        # Проверка доступности
        if not device.is_online:
            return {
                "status": "error",
                "error": "Device is offline"
            }
        
        # Формирование команды
        command_payload = {
            "command": command,
            "parameters": parameters or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "request_id": str(uuid.uuid4())
        }
        
        # Отправка команды
        if device.protocol == "mqtt" and device.topic and self.mqtt_client:
            try:
                await self.mqtt_client.publish(device.topic, json.dumps(command_payload))
                
                # Ожидание ответа
                response = await self._wait_for_device_response(device_id, command_payload["request_id"])
                
                # Логирование команды
                await self._log_device_command(
                    user_id,
                    device_id,
                    command,
                    parameters,
                    response.get("success", False),
                    response.get("response"),
                    response.get("error")
                )
                
                return response
                
            except Exception as e:
                return {
                    "status": "error",
                    "error": f"MQTT command failed: {str(e)}"
                }
        
        else:
            # Заглушка для других протоколов
            return await self._simulate_device_control(device, command, parameters)
    
    async def control_multiple_devices(
        self,
        user_id: str,
        commands: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Групповое управление устройствами"""
        
        results = []
        
        # Параллельное выполнение команд
        tasks = []
        for cmd in commands:
            task = self.control_device(
                user_id,
                cmd["device_id"],
                cmd["command"],
                cmd.get("parameters")
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Форматирование результатов
        formatted_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                formatted_results.append({
                    "device_id": commands[i]["device_id"],
                    "status": "error",
                    "error": str(result)
                })
            else:
                formatted_results.append(result)
        
        return formatted_results
    
    async def get_devices(self, user_id: str, room: Optional[str] = None) -> List[Device]:
        """Получение списка устройств"""
        
        from sqlalchemy import select
        
        stmt = select(Device).where(Device.user_id == user_id)
        
        if room:
            stmt = stmt.where(Device.room == room)
        
        stmt = stmt.order_by(Device.room, Device.name)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_device_status(self, user_id: str, device_id: str) -> Optional[Dict[str, Any]]:
        """Получение статуса устройства"""
        
        device = await self._get_device(user_id, device_id)
        if not device:
            return None
        
        # Получение состояния из кэша
        state = self.device_states.get(device_id, device.state or {})
        
        return {
            "device": {
                "id": str(device.id),
                "name": device.name,
                "type": device.device_type,
                "room": device.room,
                "is_online": device.is_online,
                "last_seen": device.last_seen_at.isoformat() if device.last_seen_at else None
            },
            "state": state,
            "capabilities": device.capabilities
        }
    
    async def optimize_energy_consumption(
        self,
        user_id: str,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Квантовая оптимизация энергопотребления"""
        
        # Получение всех устройств
        devices = await self.get_devices(user_id)
        
        # Фильтрация управляемых устройств
        controllable_devices = [
            device for device in devices
            if device.is_enabled and device.device_type in ["light", "thermostat", "switch"]
        ]
        
        if not controllable_devices:
            return {
                "status": "error",
                "error": "No controllable devices found"
            }
        
        # Построение QUBO для оптимизации
        qubo_matrix = self._build_energy_qubo(controllable_devices, constraints or {})
        
        # Решение через квантовый сервис
        # Заглушка - в реальности здесь интеграция с quantum_service
        solution = await self._solve_energy_optimization(qubo_matrix)
        
        # Интерпретация решения
        optimization_plan = self._interpret_energy_solution(solution, controllable_devices)
        
        # Применение оптимизации
        results = []
        for device_command in optimization_plan["commands"]:
            result = await self.control_device(
                user_id,
                device_command["device_id"],
                device_command["command"],
                device_command["parameters"]
            )
            results.append(result)
        
        return {
            "status": "completed",
            "optimization_plan": optimization_plan,
            "applied_commands": results,
            "estimated_savings": optimization_plan.get("estimated_savings", 0)
        }
    
    async def _get_device(self, user_id: str, device_id: str) -> Optional[Device]:
        """Получение устройства с проверкой доступа"""
        
        from sqlalchemy import select
        
        stmt = select(Device).where(
            Device.id == device_id,
            Device.user_id == user_id
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _subscribe_device_status(self, status_topic: str):
        """Подписка на статус устройства"""
        if self.mqtt_client:
            try:
                await self.mqtt_client.subscribe(status_topic)
            except Exception as e:
                print(f"Failed to subscribe to {status_topic}: {e}")
    
    async def _wait_for_device_response(
        self,
        device_id: str,
        request_id: str,
        timeout: int = 5
    ) -> Dict[str, Any]:
        """Ожидание ответа от устройства"""
        
        # Заглушка - в реальности ожидание по request_id
        await asyncio.sleep(1)
        
        return {
            "status": "success",
            "success": True,
            "response": {"state": "updated"},
            "request_id": request_id
        }
    
    async def _simulate_device_control(
        self,
        device: Device,
        command: str,
        parameters: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Симуляция управления устройством"""
        
        # Симуляция разных типов устройств
        if device.device_type == "light":
            if command == "turn_on":
                new_state = {"power": True, "brightness": parameters.get("brightness", 100)}
            elif command == "turn_off":
                new_state = {"power": False}
            elif command == "set_brightness":
                new_state = {"brightness": parameters.get("brightness", 50)}
            else:
                new_state = {}
        
        elif device.device_type == "thermostat":
            if command == "set_temperature":
                new_state = {"temperature": parameters.get("temperature", 22)}
            else:
                new_state = {}
        
        elif device.device_type == "switch":
            if command == "turn_on":
                new_state = {"power": True}
            elif command == "turn_off":
                new_state = {"power": False}
            else:
                new_state = {}
        
        else:
            new_state = {}
        
        # Обновление состояния
        if new_state:
            await self._update_device_state(str(device.id), new_state)
        
        return {
            "status": "success",
            "success": True,
            "response": new_state,
            "device_id": str(device.id),
            "simulated": True  # Флаг симуляции — реального устройства нет
        }
    
    async def _log_device_command(
        self,
        user_id: str,
        device_id: str,
        command: str,
        parameters: Optional[Dict[str, Any]],
        success: bool,
        response: Optional[Dict[str, Any]],
        error_message: Optional[str]
    ):
        """Логирование команды устройства"""
        
        log_entry = DeviceCommandLog(
            device_id=device_id,
            user_id=user_id,
            command=command,
            parameters=parameters or {},
            success=success,
            response=response,
            error_message=error_message,
            execution_time_ms=100,  # Заглушка
            source="api"
        )
        
        self.db.add(log_entry)
        await self.db.commit()
    
    def _build_energy_qubo(
        self,
        devices: List[Device],
        constraints: Dict[str, Any]
    ) -> List[List[float]]:
        """Построение QUBO матрицы для оптимизации энергопотребления"""
        
        n = len(devices)
        qubo = [[0.0] * n for _ in range(n)]
        
        # Целевая функция - минимизация потребления
        for i, device in enumerate(devices):
            # Базовое потребление
            base_consumption = device.power_consumption or 10
            
            # Штраф за включенное состояние
            qubo[i][i] = base_consumption
        
        # Ограничения
        max_power = constraints.get("max_power", 1000)
        comfort_level = constraints.get("comfort_level", 0.8)
        
        # Штраф за превышение мощности
        penalty_power = 100.0
        for i in range(n):
            for j in range(n):
                if i != j:
                    qubo[i][j] += penalty_power
        
        return qubo
    
    async def _solve_energy_optimization(self, qubo_matrix: List[List[float]]) -> Dict[str, Any]:
        """Решение задачи оптимизации"""
        
        # Заглушка - в реальности интеграция с quantum_service
        n = len(qubo_matrix)
        solution = [0] * n
        
        # Простая эвристика - включить самые эффективные устройства
        for i in range(n):
            solution[i] = 1 if qubo_matrix[i][i] < 50 else 0
        
        return {
            "status": "completed",
            "solution": solution,
            "energy": sum(qubo_matrix[i][i] * solution[i] for i in range(n))
        }
    
    def _interpret_energy_solution(
        self,
        solution: Dict[str, Any],
        devices: List[Device]
    ) -> Dict[str, Any]:
        """Интерпретация решения оптимизации"""
        
        commands = []
        solution_vector = solution["solution"]
        
        for i, device in enumerate(devices):
            if i < len(solution_vector):
                should_be_on = solution_vector[i] == 1
                
                if device.device_type == "light":
                    command = "turn_on" if should_be_on else "turn_off"
                    commands.append({
                        "device_id": str(device.id),
                        "command": command,
                        "parameters": {}
                    })
                
                elif device.device_type == "thermostat":
                    if should_be_on:
                        commands.append({
                            "device_id": str(device.id),
                            "command": "set_temperature",
                            "parameters": {"temperature": 22}
                        })
        
        # Расчет экономии
        current_consumption = sum(device.power_consumption or 10 for device in devices)
        optimized_consumption = solution.get("energy", current_consumption)
        savings = current_consumption - optimized_consumption
        
        return {
            "commands": commands,
            "estimated_savings": savings,
            "current_consumption": current_consumption,
            "optimized_consumption": optimized_consumption
        }


async def get_smarthome_service(db: AsyncSession = Depends(get_db)) -> SmartHomeService:
    """Зависимость для получения сервиса умного дома"""
    return SmartHomeService(db)


async def init_smarthome_service():
    """Инициализация сервиса умного дома"""
    global redis_client
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
    except Exception as e:
        print(f"Redis connection failed for smarthome service: {e}")
        redis_client = None
