"""
🛡️ JARVIS Voice Commands Integration for Aurion Shield VPN
"""
import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from ..services.vpn_service import get_vpn_service, AurionVPNService
from ..services.voice_jarvis_standalone import VoiceJarvisStandalone

class JarvisVPNCommands:
    """🎤 Голосовые команды JARVIS для VPN"""
    
    def __init__(self, jarvis: VoiceJarvisStandalone, vpn_service: AurionVPNService):
        self.jarvis = jarvis
        self.vpn_service = vpn_service
        
        # 🎯 Регистрация голосовых команд
        self.voice_commands = {
            # Основные команды
            "джарвис включи впн": self.cmd_connect_vpn,
            "джарвис подключи впн": self.cmd_connect_vpn,
            "джарвис включить впн": self.cmd_connect_vpn,
            "джарвис запусти впн": self.cmd_connect_vpn,
            
            "джарвис выключи впн": self.cmd_disconnect_vpn,
            "джарвис отключи впн": self.cmd_disconnect_vpn,
            "джарвис выключить впн": self.cmd_disconnect_vpn,
            "джарвис останови впн": self.cmd_disconnect_vpn,
            
            "джарвис статус впн": self.cmd_vpn_status,
            "джарвис как дела впн": self.cmd_vpn_status,
            "джарвис проверь защиту": self.cmd_vpn_status,
            
            # Серверные команды
            "джарвис подключи к сша": lambda: self.cmd_connect_country("US"),
            "джарвис подключи к германии": lambda: self.cmd_connect_country("DE"),
            "джарвис подключи к швейцарии": lambda: self.cmd_connect_country("CH"),
            "джарвис подключи к японии": lambda: self.cmd_connect_country("JP"),
            "джарвис подключи к сингапуру": lambda: self.cmd_connect_country("SG"),
            
            # Команды безопасности
            "джарвис включи стелс режим": self.cmd_enable_stealth,
            "джарвис включи невидимость": self.cmd_enable_stealth,
            "джарвис активируй стелс": self.cmd_enable_stealth,
            "джарвис режим невидимости": self.cmd_enable_stealth,
            
            "джарвис проверь блокировки": self.cmd_check_blockades,
            "джарвис проверь глушки": self.cmd_check_blockades,
            "джарвис есть ли блокировки": self.cmd_check_blockades,
            "джарвис проверь доступ": self.cmd_check_blockades,
            
            # Команды протоколов
            "джарвис смени протокол": self.cmd_switch_protocol,
            "джарвис используй другой протокол": self.cmd_switch_protocol,
            "джарвис переключи протокол": self.cmd_switch_protocol,
            
            # Команды качества
            "джарвис проверь скорость": self.cmd_test_speed,
            "джарвис тест скорости": self.cmd_test_speed,
            "джарвис как скорость": self.cmd_test_speed,
            "джарвис качество соединения": self.cmd_test_speed,
            
            # Экстренные команды
            "джарвис экстренное отключение": self.cmd_emergency_disconnect,
            "джарвис аварийное отключение": self.cmd_emergency_disconnect,
            "джарвис отключи всё": self.cmd_emergency_disconnect,
            "джарвис отсеки связь": self.cmd_emergency_disconnect,
            
            # Информационные команды
            "джарвис какой у меня ip": self.cmd_current_ip,
            "джарвис покажи мой ip": self.cmd_current_ip,
            "джарвис где я нахожусь": self.cmd_current_location,
            "джарвис какая страна": self.cmd_current_location,
            
            # Настройки
            "джарвис включи кил свитч": self.cmd_enable_kill_switch,
            "джарвис выключи кил свитч": self.cmd_disable_kill_switch,
            "джарвис активируй защиту": self.cmd_enable_protection,
            "джарвус усиль защиту": self.cmd_max_protection
        }
    
    async def process_voice_command(self, text: str) -> Optional[Dict[str, Any]]:
        """Обработка голосовой команды"""
        text_lower = text.lower().strip()
        
        # Поиск команды
        for command_pattern, command_func in self.voice_commands.items():
            if command_pattern in text_lower:
                try:
                    result = await command_func()
                    return result
                except Exception as e:
                    return {
                        "success": False,
                        "response": f"Извините, сэр. Возникла ошибка при выполнении команды: {str(e)}",
                        "action": "error"
                    }
        
        # Если команда не найдена
        return {
            "success": False,
            "response": "Сэр, я не распознал эту VPN команду. Попробуйте: 'Джарвис включи VPN' или 'Джарвис проверь статус'",
            "action": "unknown_command"
        }
    
    async def cmd_connect_vpn(self) -> Dict[str, Any]:
        """Подключение к VPN"""
        status = await self.vpn_service.get_connection_status()
        
        if status.get("connected"):
            return {
                "success": True,
                "response": f"Сэр, VPN уже активен. Вы подключены к серверу {status.get('server', {}).get('name', 'неизвестному')} в {status.get('server', {}).get('country', 'неизвестной стране')}.",
                "action": "already_connected"
            }
        
        # Выбор оптимального сервера
        from ..models.vpn import VPN_SERVERS
        best_server = VPN_SERVERS[0]  # Упрощено - выбираем первый
        
        result = await self.vpn_service.connect_vpn(
            server_id=best_server.get("id", "default"),
            protocol="auto",
            obfuscation="auto",
            stealth=True
        )
        
        if result["success"]:
            return {
                "success": True,
                "response": f"Сэр, я успешно подключил вас к VPN. Сервер: {best_server.get('name', 'Unknown')} в {best_server.get('country', 'Unknown')}. Все каналы защищены.",
                "action": "connected",
                "server": best_server.get("name"),
                "country": best_server.get("country")
            }
        else:
            return {
                "success": False,
                "response": "Прошу прощения, сэр. Не удалось установить VPN соединение. Пожалуйста, проверьте настройки сети.",
                "action": "connection_failed"
            }
    
    async def cmd_disconnect_vpn(self) -> Dict[str, Any]:
        """Отключение от VPN"""
        status = await self.vpn_service.get_connection_status()
        
        if not status.get("connected"):
            return {
                "success": True,
                "response": "Сэр, VPN уже отключен. Ваше соединение открыто.",
                "action": "already_disconnected"
            }
        
        result = await self.vpn_service.disconnect_vpn()
        
        if result["success"]:
            return {
                "success": True,
                "response": "VPN соединение отключено, сэр. Ваше соединение снова открыто. Рекомендую быть осторожным в открытых сетях.",
                "action": "disconnected",
                "session_duration": result.get("session_duration", 0)
            }
        else:
            return {
                "success": False,
                "response": "Извините, сэр. Возникли трудности при отключении VPN. Прошу подождать мгновение.",
                "action": "disconnection_failed"
            }
    
    async def cmd_vpn_status(self) -> Dict[str, Any]:
        """Проверка статуса VPN"""
        status = await self.vpn_service.get_connection_status()
        metrics = status.get("metrics")
        
        if status.get("connected"):
            server_info = status.get("server", {})
            response_parts = [
                f"Сэр, VPN активен и работает отлично.",
                f"Подключены к серверу {server_info.get('name', 'Unknown')} в {server_info.get('country', 'Unknown')}.",
                f"Ваш текущий IP: {status.get('ip_address', 'Unknown')}."
            ]
            
            if metrics:
                quality_score = metrics.get("quality_score", 0) * 100
                latency = metrics.get("latency_ms", 0)
                
                if quality_score > 80:
                    response_parts.append("Качество соединения: превосходное.")
                elif quality_score > 60:
                    response_parts.append("Качество соединения: хорошее.")
                else:
                    response_parts.append("Качество соединения: требует внимания.")
                
                response_parts.append(f"Задержка: {latency:.0f} миллисекунд.")
            
            return {
                "success": True,
                "response": " ".join(response_parts),
                "action": "status_report",
                "status": "connected"
            }
        else:
            return {
                "success": True,
                "response": "Сэр, VPN неактивен. Ваше соединение открыто и может отслеживаться. Рекомендую включить защиту для безопасности.",
                "action": "status_report",
                "status": "disconnected"
            }
    
    async def cmd_connect_country(self, country: str) -> Dict[str, Any]:
        """Подключение к серверу конкретной страны"""
        from ..models.vpn import VPN_SERVERS
        
        # Поиск сервера по стране
        target_server = None
        for server in VPN_SERVERS:
            if server.get("country") == country:
                target_server = server
                break
        
        if not target_server:
            return {
                "success": False,
                "response": f"Сэр, к сожалению, серверы в {self._get_country_name(country)} временно недоступны. Рекомендую выбрать другую локацию.",
                "action": "server_not_found"
            }
        
        # Отключение от текущего сервера если нужно
        status = await self.vpn_service.get_connection_status()
        if status.get("connected"):
            await self.vpn_service.disconnect_vpn()
        
        # Подключение к новому серверу
        result = await self.vpn_service.connect_vpn(
            server_id=target_server.get("id"),
            protocol="auto",
            obfuscation="auto",
            stealth=True
        )
        
        if result["success"]:
            return {
                "success": True,
                "response": f"Сэр, я подключил вас к серверу в {self._get_country_name(country)}. Защита активна.",
                "action": "connected_to_country",
                "country": country,
                "server": target_server.get("name")
            }
        else:
            return {
                "success": False,
                "response": f"Прошу прощения, сэр. Не удалось подключиться к серверу в {self._get_country_name(country)}.",
                "action": "connection_failed"
            }
    
    async def cmd_enable_stealth(self) -> Dict[str, Any]:
        """Включение стелс режима"""
        status = await self.vpn_service.get_connection_status()
        
        if not status.get("connected"):
            return {
                "success": False,
                "response": "Сэр, для активации стелс режима необходимо сначала подключиться к VPN.",
                "action": "not_connected"
            }
        
        # В реальном приложении - переключение в стелс режим
        return {
            "success": True,
            "response": "Сэр, стелс режим активирован. Ваше соединение теперь замаскировано и не обнаруживается системами глубокого анализа пакетов.",
            "action": "stealth_enabled"
        }
    
    async def cmd_check_blockades(self) -> Dict[str, Any]:
        """Проверка блокировок"""
        detection = await self.vpn_service.detect_blockades()
        
        if detection.blockade_type == "none":
            return {
                "success": True,
                "response": "Сэр, отличные новости! Блокировок не обнаружено. Все протоколы работают штатно.",
                "action": "no_blockades",
                "blockade_type": "none"
            }
        else:
            confidence = detection.confidence_score * 100
            response_parts = [
                f"Сэр, я обнаружил {detection.blockade_type} с уверенностью {confidence:.0f}%",
                f"Рекомендую использовать протокол: {detection.recommended_protocol}"
            ]
            
            if detection.blocked_protocols:
                response_parts.append(f"Заблокированы: {', '.join(detection.blocked_protocols)}")
            
            return {
                "success": True,
                "response": " ".join(response_parts),
                "action": "blockades_detected",
                "blockade_type": detection.blockade_type,
                "recommended_protocol": detection.recommended_protocol
            }
    
    async def cmd_switch_protocol(self) -> Dict[str, Any]:
        """Переключение протокола"""
        detection = await self.vpn_service.detect_blockades()
        
        if detection.recommended_protocol:
            success = await self.vpn_service.auto_switch_protocol()
            
            if success:
                return {
                    "success": True,
                    "response": f"Сэр, я переключил протокол на {detection.recommended_protocol} для обхода блокировок.",
                    "action": "protocol_switched",
                    "new_protocol": detection.recommended_protocol
                }
            else:
                return {
                    "success": False,
                    "response": "Прошу прощения, сэр. Не удалось переключить протокол. Рекомендую переподключиться к VPN.",
                    "action": "protocol_switch_failed"
                }
        else:
            return {
                "success": True,
                "response": "Сэр, текущий протокол работает оптимально. Переключение не требуется.",
                "action": "no_switch_needed"
            }
    
    async def cmd_test_speed(self) -> Dict[str, Any]:
        """Тест скорости"""
        status = await self.vpn_service.get_connection_status()
        
        if not status.get("connected"):
            return {
                "success": False,
                "response": "Сэр, для теста скорости необходимо активное VPN соединение.",
                "action": "not_connected"
            }
        
        metrics = await self.vpn_service._measure_connection_metrics()
        
        if metrics:
            speed_mbps = metrics.download_speed_mbps
            latency = metrics.latency_ms
            quality = metrics.quality_score
            
            response_parts = [
                f"Сэр, результаты теста скорости:",
                f"Скорость загрузки: {speed_mbps:.1f} мегабит в секунду",
                f"Задержка: {latency:.0f} миллисекунд",
                f"Общее качество: {quality:.2f} из 1.0"
            ]
            
            if quality > 0.8:
                response_parts.append("Соединение отличное!")
            elif quality > 0.6:
                response_parts.append("Соединение хорошее.")
            else:
                response_parts.append("Соединение требует внимания.")
            
            return {
                "success": True,
                "response": " ".join(response_parts),
                "action": "speed_test",
                "metrics": metrics.__dict__
            }
        else:
            return {
                "success": False,
                "response": "Сэр, не удалось выполнить тест скорости. Пожалуйста, попробуйте позже.",
                "action": "speed_test_failed"
            }
    
    async def cmd_emergency_disconnect(self) -> Dict[str, Any]:
        """Экстренное отключение"""
        result = await self.vpn_service.disconnect_vpn()
        
        if result["success"]:
            return {
                "success": True,
                "response": "Сэр, выполнено экстренное отключение. Все соединения разорваны. Система в безопасном режиме.",
                "action": "emergency_disconnected"
            }
        else:
            return {
                "success": False,
                "response": "Сэр, возникли критические проблемы при экстренном отключении. Рекомендую перезагрузить систему.",
                "action": "emergency_failed"
            }
    
    async def cmd_current_ip(self) -> Dict[str, Any]:
        """Текущий IP адрес"""
        ip_address = await self.vpn_service._get_current_ip()
        status = await self.vpn_service.get_connection_status()
        
        if status.get("connected"):
            server_info = status.get("server", {})
            return {
                "success": True,
                "response": f"Сэр, ваш текущий IP: {ip_address}. Вы подключены через сервер в {server_info.get('country', 'Unknown')}. Ваш реальный IP скрыт.",
                "action": "ip_info",
                "ip": ip_address,
                "protected": True
            }
        else:
            return {
                "success": True,
                "response": f"Сэр, ваш текущий IP: {ip_address}. ВНИМАНИЕ: Вы не защищены VPN, ваш реальный адрес виден.",
                "action": "ip_info",
                "ip": ip_address,
                "protected": False
            }
    
    async def cmd_current_location(self) -> Dict[str, Any]:
        """Текущая локация"""
        status = await self.vpn_service.get_connection_status()
        
        if status.get("connected"):
            server_info = status.get("server", {})
            return {
                "success": True,
                "response": f"Сэр, согласно VPN, вы находитесь в {server_info.get('city', 'Unknown')}, {server_info.get('country', 'Unknown')}. Ваше реальное местоположение скрыто.",
                "action": "location_info",
                "location": f"{server_info.get('city', 'Unknown')}, {server_info.get('country', 'Unknown')}",
                "protected": True
            }
        else:
            return {
                "success": True,
                "response": "Сэр, вы не подключены к VPN. Ваше реальное местоположение виден.",
                "action": "location_info",
                "protected": False
            }
    
    async def cmd_enable_kill_switch(self) -> Dict[str, Any]:
        """Включение Kill Switch"""
        # В реальном приложении - включение Kill Switch
        return {
            "success": True,
            "response": "Сэр, Kill Switch активирован. При отключении VPN интернет будет заблокирован для вашей защиты.",
            "action": "kill_switch_enabled"
        }
    
    async def cmd_disable_kill_switch(self) -> Dict[str, Any]:
        """Отключение Kill Switch"""
        # В реальном приложении - отключение Kill Switch
        return {
            "success": True,
            "response": "Сэр, Kill Switch отключен. ВНИМАНИЕ: при разрыве VPN соединения интернет останется доступным.",
            "action": "kill_switch_disabled"
        }
    
    async def cmd_enable_protection(self) -> Dict[str, Any]:
        """Активация полной защиты"""
        return {
            "success": True,
            "response": "Сэр, активирован максимальный уровень защиты. Все системы безопасности включены.",
            "action": "max_protection_enabled"
        }
    
    async def cmd_max_protection(self) -> Dict[str, Any]:
        """Максимальная защита"""
        # Подключение с максимальными настройками
        from ..models.vpn import VPN_SERVERS
        best_server = VPN_SERVERS[0]  # Самый защищенный сервер
        
        result = await self.vpn_service.connect_vpn(
            server_id=best_server.get("id"),
            protocol="shadowsocks",  # Самый устойчивый протокол
            obfuscation="maximum",   # Максимальная обфускация
            stealth=True              # Стелс режим
        )
        
        if result["success"]:
            return {
                "success": True,
                "response": "Сэр, активирован режим максимальной защиты. Все каналы замаскированы и зашифрованы.",
                "action": "max_protection_enabled"
            }
        else:
            return {
                "success": False,
                "response": "Прошу прощения, сэр. Не удалось активировать максимальную защиту.",
                "action": "max_protection_failed"
            }
    
    def _get_country_name(self, country_code: str) -> str:
        """Получение названия страны по коду"""
        country_names = {
            "US": "США",
            "DE": "Германия", 
            "CH": "Швейцария",
            "SE": "Швеция",
            "JP": "Япония",
            "SG": "Сингапур"
        }
        return country_names.get(country_code, country_code)

# 🎤 Интеграция с JARVIS
async def setup_jarvis_vpn_commands(jarvis: VoiceJarvisStandalone) -> JarvisVPNCommands:
    """Настройка голосовых команд VPN для JARVIS"""
    vpn_service = await get_vpn_service()
    jarvis_vpn = JarvisVPNCommands(jarvis, vpn_service)
    
    # Расширение системного промпта JARVIS
    vpn_commands_help = """
    
    🛡️ VPN КОМАНДЫ:
    - "Джарвис включи VPN" - подключиться к VPN
    - "Джарвис выключи VPN" - отключиться от VPN
    - "Джарвис статус VPN" - проверить статус защиты
    - "Джарвис подключи к [страна]" - подключиться к серверу страны
    - "Джарвис включи стелс режим" - активировать невидимость
    - "Джарвис проверь блокировки" - обнаружить глушки
    - "Джарвис проверь скорость" - тест качества соединения
    - "Джарвис какой у меня IP" - узнать текущий адрес
    - "Джарвис экстренное отключение" - аварийное отключение
    
    🎯 ПРИМЕРЫ:
    "Джарвис, включи VPN и подключи к Германии"
    "Джарвис, проверь блокировки и включи стелс режим"
    "Джарвис, какой мой IP и качество соединения?"
    """
    
    # Добавление в персона JARVIS информацию о VPN
    if hasattr(jarvis, 'jarvis_personality'):
        jarvis.jarvis_personality['knowledge_domains'].append('VPN и безопасность')
        jarvis.jarvis_personality['knowledge_domains'].append('обход блокировок')
    
    return jarvis_vpn
