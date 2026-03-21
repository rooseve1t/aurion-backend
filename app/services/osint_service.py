"""
Сервис OSINT и разведки по открытым источникам
"""
import asyncio
import aiohttp
import json
import hashlib
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from ..models.osint import AuditLog
from ..database import get_db

# Redis для кэширования
redis_client: Optional[redis.Redis] = None


class OSINTService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.redis = redis_client
        
        # API ключи
        self.censys_api_id = os.getenv("CENSYS_API_ID", "")
        self.censys_api_secret = os.getenv("CENSYS_API_SECRET", "")
        self.shodan_api_key = os.getenv("SHODAN_API_KEY", "")
        self.apify_api_token = os.getenv("APIFY_API_TOKEN", "")
    
    async def search_ip(self, user_id: str, ip_address: str) -> Dict[str, Any]:
        """Поиск информации по IP адресу"""
        
        # Проверка лимитов
        if not await self._check_rate_limit(user_id, "ip", 100):
            return {
                "status": "error",
                "error": "Rate limit exceeded",
                "limit": 100
            }
        
        # Проверка кэша
        cache_key = f"osint:ip:{ip_address}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                result = json.loads(cached)
                await self._log_search(user_id, "ip", ip_address, result)
                return result
        
        result = {"status": "pending"}
        
        # Censys поиск
        if self.censys_api_id and self.censys_api_secret:
            censys_data = await self._search_censys_ip(ip_address)
            result["censys"] = censys_data
        
        # Shodan поиск
        if self.shodan_api_key:
            shodan_data = await self._search_shodan_ip(ip_address)
            result["shodan"] = shodan_data
        
        # Базовая информация
        basic_info = self._get_basic_ip_info(ip_address)
        result["basic"] = basic_info
        
        # Агрегация результатов
        aggregated = self._aggregate_ip_results(result)
        
        # Кэширование
        if self.redis:
            await self.redis.setex(cache_key, 3600, json.dumps(aggregated))
        
        # Логирование
        await self._log_search(user_id, "ip", ip_address, aggregated)
        
        return aggregated
    
    async def search_email(self, user_id: str, email: str) -> Dict[str, Any]:
        """Поиск информации по email адресу"""
        
        # Проверка лимитов
        if not await self._check_rate_limit(user_id, "email", 50):
            return {
                "status": "error", 
                "error": "Rate limit exceeded",
                "limit": 50
            }
        
        # Проверка кэша
        cache_key = f"osint:email:{hashlib.md5(email.encode()).hexdigest()}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                result = json.loads(cached)
                await self._log_search(user_id, "email", email, result)
                return result
        
        result = {"status": "pending"}
        
        # Apify holehe для поиска аккаунтов
        if self.apify_api_token:
            apify_data = await self._search_apify_email(email)
            result["apify"] = apify_data
        
        # Базовая валидация email
        basic_info = self._validate_email(email)
        result["basic"] = basic_info
        
        # Агрегация
        aggregated = self._aggregate_email_results(result)
        
        # Кэширование
        if self.redis:
            await self.redis.setex(cache_key, 7200, json.dumps(aggregated))
        
        # Логирование
        await self._log_search(user_id, "email", email, aggregated)
        
        return aggregated
    
    async def search_domain(self, user_id: str, domain: str) -> Dict[str, Any]:
        """Поиск информации по домену"""
        
        # Проверка лимитов
        if not await self._check_rate_limit(user_id, "domain", 30):
            return {
                "status": "error",
                "error": "Rate limit exceeded", 
                "limit": 30
            }
        
        # Проверка кэша
        cache_key = f"osint:domain:{domain}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                result = json.loads(cached)
                await self._log_search(user_id, "domain", domain, result)
                return result
        
        result = {"status": "pending"}
        
        # Censys поиск домена
        if self.censys_api_id and self.censys_api_secret:
            censys_data = await self._search_censys_domain(domain)
            result["censys"] = censys_data
        
        # Shodan поиск домена
        if self.shodan_api_key:
            shodan_data = await self._search_shodan_domain(domain)
            result["shodan"] = shodan_data
        
        # DNS информация
        dns_info = await self._get_dns_info(domain)
        result["dns"] = dns_info
        
        # Агрегация
        aggregated = self._aggregate_domain_results(result)
        
        # Кэширование
        if self.redis:
            await self.redis.setex(cache_key, 3600, json.dumps(aggregated))
        
        # Логирование
        await self._log_search(user_id, "domain", domain, aggregated)
        
        return aggregated
    
    async def _search_censys_ip(self, ip_address: str) -> Dict[str, Any]:
        """Поиск в Censys по IP"""
        
        if not self.censys_api_id or not self.censys_api_secret:
            return {"status": "error", "error": "Censys credentials not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                # Аутентификация
                auth = aiohttp.BasicAuth(self.censys_api_id, self.censys_api_secret)
                
                url = f"https://search.censys.io/api/v2/hosts/{ip_address}"
                
                async with session.get(url, auth=auth) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "data": {
                                "ip": data.get("ip"),
                                "services": data.get("services", []),
                                "location": data.get("location", {}),
                                "autonomous_system": data.get("autonomous_system", {}),
                                "metadata": data.get("metadata", {})
                            }
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"Censys API error: {response.status}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Censys search failed: {str(e)}"
            }
    
    async def _search_shodan_ip(self, ip_address: str) -> Dict[str, Any]:
        """Поиск в Shodan по IP"""
        
        if not self.shodan_api_key:
            return {"status": "error", "error": "Shodan API key not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.shodan.io/shodan/host/{ip_address}?key={self.shodan_api_key}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "data": {
                                "ip_str": data.get("ip_str"),
                                "ports": data.get("ports", []),
                                "services": data.get("services", []),
                                "location": data.get("location", {}),
                                "country_name": data.get("country_name"),
                                "org": data.get("org"),
                                "vulns": data.get("vulns", [])
                            }
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"Shodan API error: {response.status}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Shodan search failed: {str(e)}"
            }
    
    async def _search_apify_email(self, email: str) -> Dict[str, Any]:
        """Поиск аккаунтов по email через Apify holehe"""
        
        if not self.apify_api_token:
            return {"status": "error", "error": "Apify API token not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                # Запуск holehe актора
                url = "https://api.apify.com/v2/acts/streaming~holehe/runs"
                
                headers = {
                    "Authorization": f"Bearer {self.apify_api_token}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "email": email,
                    "timeout": 300
                }
                
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 201:
                        run_data = await response.json()
                        
                        # Ожидание завершения
                        run_id = run_data["data"]["id"]
                        results = await self._wait_for_apify_results(run_id)
                        
                        return {
                            "status": "success",
                            "data": results
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"Apify API error: {response.status}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Apify search failed: {str(e)}"
            }
    
    async def _search_censys_domain(self, domain: str) -> Dict[str, Any]:
        """Поиск в Censys по домену"""
        
        if not self.censys_api_id or not self.censys_api_secret:
            return {"status": "error", "error": "Censys credentials not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                auth = aiohttp.BasicAuth(self.censys_api_id, self.censys_api_secret)
                
                # Поиск сертификатов и хостов
                url = "https://search.censys.io/api/v2/certificates/search"
                query = f"names: {domain}"
                
                params = {"q": query, "per_page": 100}
                
                async with session.get(url, auth=auth, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "data": {
                                "certificates": data.get("result", {}).get("hits", []),
                                "total": data.get("result", {}).get("total", 0)
                            }
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"Censys API error: {response.status}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Censys domain search failed: {str(e)}"
            }
    
    async def _search_shodan_domain(self, domain: str) -> Dict[str, Any]:
        """Поиск в Shodan по домену"""
        
        if not self.shodan_api_key:
            return {"status": "error", "error": "Shodan API key not configured"}
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"https://api.shodan.io/shodan/host/search?key={self.shodan_api_key}&filter=hostname:{domain}"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "status": "success",
                            "data": {
                                "matches": data.get("matches", []),
                                "total": data.get("total", 0)
                            }
                        }
                    else:
                        return {
                            "status": "error",
                            "error": f"Shodan API error: {response.status}"
                        }
                        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Shodan domain search failed: {str(e)}"
            }
    
    async def _get_dns_info(self, domain: str) -> Dict[str, Any]:
        """Получение DNS информации"""
        
        try:
            import dns.resolver
            
            info = {}
            
            # A записи
            try:
                answers = dns.resolver.resolve(domain, 'A')
                info["a_records"] = [str(answer) for answer in answers]
            except:
                info["a_records"] = []
            
            # MX записи
            try:
                answers = dns.resolver.resolve(domain, 'MX')
                info["mx_records"] = [{"preference": answer.preference, "exchange": str(answer.exchange)} for answer in answers]
            except:
                info["mx_records"] = []
            
            # TXT записи
            try:
                answers = dns.resolver.resolve(domain, 'TXT')
                info["txt_records"] = [str(answer).strip('"') for answer in answers]
            except:
                info["txt_records"] = []
            
            # NS записи
            try:
                answers = dns.resolver.resolve(domain, 'NS')
                info["ns_records"] = [str(answer) for answer in answers]
            except:
                info["ns_records"] = []
            
            return {
                "status": "success",
                "data": info
            }
            
        except ImportError:
            return {
                "status": "error",
                "error": "DNS library not available"
            }
        except Exception as e:
            return {
                "status": "error",
                "error": f"DNS lookup failed: {str(e)}"
            }
    
    def _get_basic_ip_info(self, ip_address: str) -> Dict[str, Any]:
        """Базовая информация об IP"""
        
        import ipaddress
        
        try:
            ip = ipaddress.ip_address(ip_address)
            
            info = {
                "ip": str(ip),
                "version": ip.version,
                "is_private": ip.is_private,
                "is_loopback": ip.is_loopback,
                "is_multicast": ip.is_multicast,
                "is_reserved": ip.is_reserved
            }
            
            # Определение типа
            if ip.is_private:
                info["type"] = "private"
            elif ip.is_loopback:
                info["type"] = "loopback"
            elif ip.is_multicast:
                info["type"] = "multicast"
            else:
                info["type"] = "public"
            
            return {
                "status": "success",
                "data": info
            }
            
        except ValueError:
            return {
                "status": "error",
                "error": "Invalid IP address"
            }
    
    def _validate_email(self, email: str) -> Dict[str, Any]:
        """Валидация email"""
        
        import re
        
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
        
        if not email_pattern.match(email):
            return {
                "status": "error",
                "error": "Invalid email format"
            }
        
        # Извлечение домена
        domain = email.split('@')[1]
        
        return {
            "status": "success",
            "data": {
                "email": email,
                "domain": domain,
                "local_part": email.split('@')[0],
                "valid": True
            }
        }
    
    def _aggregate_ip_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация результатов поиска IP"""
        
        aggregated = {
            "status": "completed",
            "ip": None,
            "services": [],
            "location": {},
            "autonomous_system": {},
            "vulnerabilities": [],
            "risk_score": 0
        }
        
        # Объединение данных из разных источников
        for source, data in results.items():
            if source == "basic" and data.get("status") == "success":
                aggregated["ip"] = data["data"]["ip"]
                aggregated["type"] = data["data"]["type"]
            
            elif source == "censys" and data.get("status") == "success":
                censys_data = data["data"]
                aggregated["services"].extend(censys_data.get("services", []))
                aggregated["location"].update(censys_data.get("location", {}))
                aggregated["autonomous_system"].update(censys_data.get("autonomous_system", {}))
            
            elif source == "shodan" and data.get("status") == "success":
                shodan_data = data["data"]
                aggregated["ports"] = shodan_data.get("ports", [])
                aggregated["vulnerabilities"].extend(shodan_data.get("vulns", []))
        
        # Расчет риска
        if aggregated.get("vulnerabilities"):
            aggregated["risk_score"] = len(aggregated["vulnerabilities"]) * 10
        
        return aggregated
    
    def _aggregate_email_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация результатов поиска email"""
        
        aggregated = {
            "status": "completed",
            "email": None,
            "accounts": [],
            "valid": False,
            "risk_score": 0
        }
        
        for source, data in results.items():
            if source == "basic" and data.get("status") == "success":
                aggregated["email"] = data["data"]["email"]
                aggregated["valid"] = data["data"]["valid"]
                aggregated["domain"] = data["data"]["domain"]
            
            elif source == "apify" and data.get("status") == "success":
                aggregated["accounts"] = data["data"].get("accounts", [])
        
        return aggregated
    
    def _aggregate_domain_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Агрегация результатов поиска домена"""
        
        aggregated = {
            "status": "completed",
            "domain": None,
            "hosts": [],
            "certificates": [],
            "dns_records": {},
            "risk_score": 0
        }
        
        for source, data in results.items():
            if source == "dns" and data.get("status") == "success":
                aggregated["dns_records"] = data["data"]
            
            elif source == "censys" and data.get("status") == "success":
                aggregated["certificates"] = data["data"].get("certificates", [])
            
            elif source == "shodan" and data.get("status") == "success":
                aggregated["hosts"] = data["data"].get("matches", [])
        
        return aggregated
    
    async def _wait_for_apify_results(self, run_id: str, timeout: int = 300) -> Dict[str, Any]:
        """Ожидание результатов Apify"""
        
        start_time = datetime.now()
        
        while (datetime.now() - start_time).seconds < timeout:
            try:
                async with aiohttp.ClientSession() as session:
                    url = f"https://api.apify.com/v2/acts/streaming~holehe/runs/{run_id}"
                    headers = {"Authorization": f"Bearer {self.apify_api_token}"}
                    
                    async with session.get(url, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            status = data["data"]["status"]
                            
                            if status == "SUCCEEDED":
                                return data["data"].get("defaultDatasetId", {})
                            elif status == "FAILED":
                                return {"error": "Apify run failed"}
                            elif status == "ABORTED":
                                return {"error": "Apify run aborted"}
                            else:
                                # Продолжаем ожидание
                                await asyncio.sleep(5)
                        else:
                            await asyncio.sleep(5)
                            
            except Exception:
                await asyncio.sleep(5)
        
        return {"error": "Apify run timeout"}
    
    async def _check_rate_limit(self, user_id: str, query_type: str, limit: int) -> bool:
        """Проверка rate limiting"""
        
        if not self.redis:
            return True  # Без Redis нет лимитов
        
        key = f"rate_limit:{user_id}:{query_type}"
        
        # Получение текущего счетчика
        current = await self.redis.get(key)
        
        if current and int(current) >= limit:
            return False
        
        # Увеличение счетчика
        await self.redis.incr(key)
        await self.redis.expire(key, 86400)  # 24 часа
        
        return True
    
    async def _log_search(
        self,
        user_id: str,
        service: str,
        query: str,
        result: Dict[str, Any]
    ):
        """Логирование OSINT запроса"""
        
        log_entry = AuditLog(
            user_id=user_id,
            service=service,
            query_type=service,
            query=query,
            result_count=1 if result.get("status") == "success" else 0,
            results=result if result.get("status") == "success" else None,
            success=result.get("status") == "success",
            error_message=result.get("error"),
            response_time_ms=100  # Заглушка
        )
        
        self.db.add(log_entry)
        await self.db.commit()


async def get_osint_service(db: AsyncSession = Depends(get_db)) -> OSINTService:
    """Зависимость для получения OSINT сервиса"""
    return OSINTService(db)


async def init_osint_service():
    """Инициализация OSINT сервиса"""
    global redis_client
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        redis_client = redis.from_url(redis_url, decode_responses=True)
        await redis_client.ping()
    except Exception as e:
        print(f"Redis connection failed for OSINT service: {e}")
        redis_client = None
