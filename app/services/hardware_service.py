"""
🛠️ Hardware Abstraction Layer (HAL) JARVIS (Stage 20)
Управление физическим оборудованием сервера и периферией.
"""
import logging
import psutil
import platform
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger("jarvis-hal")

class HardwareService:
    """Сервис управления оборудованием (HAL)"""
    
    def __init__(self):
        self.system_info = self._get_base_info()
        self.active_peripherals: List[str] = []
        self.thermal_status = "normal"

    def _get_base_info(self) -> Dict[str, Any]:
        return {
            "os": platform.system(),
            "processor": platform.processor(),
            "architecture": platform.machine(),
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat()
        }

    async def get_system_health(self) -> Dict[str, Any]:
        """Расширенный мониторинг здоровья оборудования"""
        cpu_usage: List[float] = psutil.cpu_percent(interval=0.1, percpu=True)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Температурные датчики (если доступны)
        temps: Dict[str, Any] = {}
        try:
            # Используем getattr для избежания ошибок линтера на разных платформах
            sensors_temperatures = getattr(psutil, "sensors_temperatures", None)
            if sensors_temperatures:
                temps = sensors_temperatures()
        except Exception:
            pass

        health: Dict[str, Any] = {
            "cpu": {
                "overall": sum(cpu_usage) / len(cpu_usage) if cpu_usage else 0,
                "cores": cpu_usage,
                "load_avg": psutil.getloadavg()
            },
            "memory": {
                "percent": memory.percent,
                "available_gb": round(memory.available / (1024**3), 2)
            },
            "disk": {
                "percent": disk.percent,
                "free_gb": round(disk.free / (1024**3), 2)
            },
            "temperatures": temps,
            "status": self._evaluate_thermal_status(temps)
        }
        return health

    def _evaluate_thermal_status(self, temps: Dict[str, Any]) -> str:
        # Простая логика оценки перегрева
        for sensor in temps.values():
            for entry in sensor:
                if hasattr(entry, 'current'):
                    if entry.current > 80:
                        return "critical"
                    if entry.current > 70:
                        return "high"
        return "normal"

    async def control_peripheral(self, device_name: str, action: str) -> Dict[str, Any]:
        """Управление периферийными устройствами (Камеры, Микрофоны)"""
        logger.info(f"🔌 HAL: Executing {action} on {device_name}")
        # В реальности здесь вызовы системных команд или драйверов
        return {"status": "success", "device": device_name, "action": action}

async def get_hardware_service():
    return HardwareService()
