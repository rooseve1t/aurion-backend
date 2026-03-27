"""
🛡️ Rate Limiting and Caching Middleware для Aurion OS
Реальная защита API от перегрузки и оптимизация производительности
"""
import time
import hashlib
import json
from typing import Dict, Any, Optional, Callable, Set, cast
from functools import wraps
import asyncio
import logging
from dataclasses import dataclass
from enum import Enum

# Хранилище фоновых задач для предотвращения GC
_cleanup_tasks: Set[asyncio.Task[Any]] = set()

# Redis для production-ready кэширования и rate limiting
_redis_available = False
_redis_module: Any = None
try:
    import redis.asyncio as aioredis
    _redis_available = True
    _redis_module = aioredis
except ImportError:
    logging.warning("Redis не установлен. Используем in-memory кэш.")

class RateLimitStrategy(Enum):
    """Стратегии rate limiting"""
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"

@dataclass
class RateLimitConfig:
    """Конфигурация rate limiting"""
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    requests_per_day: int = 10000
    burst_limit: int = 10
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
    block_duration: int = 300  # секунд

@dataclass  
class CacheConfig:
    """Конфигурация кэширования"""
    default_ttl: int = 300  # 5 минут
    max_size: int = 10000  # максимум записей
    cleanup_interval: int = 3600  # очистка каждый час

class SecurityGuard:
    """Security Guard для критических операций (Stage 22: Security Engineer Echo)"""
    
    def __init__(self):
        self.sensitive_endpoints = {
            "/api/v1/smarthome/devices/control",
            "/api/v1/payments/subscribe",
            "/api/v1/auth/2fa/enable",
            "/api/v1/quantum/solve"
        }

    async def verify_request(self, path: str, headers: Dict[str, str], user_id: str) -> bool:
        """Проверка безопасности запроса"""
        if path not in self.sensitive_endpoints:
            return True
            
        logger = logging.getLogger("security-guard")
        logger.info(f"🛡️ Guard: Checking security for sensitive path {path}")
        
        # 1. Проверка наличия квантового токена
        q_token = headers.get("X-Quantum-Token")
        if not q_token:
            logger.warning(f"❌ Guard: Missing X-Quantum-Token for {path}")
            return False
            
        # 2. Проверка биометрической подписи (VoiceID)
        v_signature = headers.get("X-Voice-Signature")
        if not v_signature:
            logger.warning(f"❌ Guard: Missing X-Voice-Signature for {path}")
            return False
            
        # В реальности здесь вызов quantum_service.verify_biometric_quantum
        # Для MVP имитируем успешную проверку если заголовки присутствуют
        return True


class RateLimiter:
    """Rate Limiter с multiple strategies"""
    
    def __init__(self, config: Optional[RateLimitConfig] = None):
        self.config = config or RateLimitConfig()
        self.redis_client: Any = None
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        
        if _redis_available and _redis_module:
            try:
                self.redis_client = _redis_module.Redis.from_url(
                    "redis://localhost:6379",
                    decode_responses=True
                )
            except Exception as e:
                logging.error(f"Redis connection failed: {e}")
    
    async def is_allowed(self, key: str) -> tuple[bool, Dict[str, Any]]:
        """Проверить, разрешен ли запрос"""
        if self.config.strategy == RateLimitStrategy.SLIDING_WINDOW:
            return await self._sliding_window_check(key)
        elif self.config.strategy == RateLimitStrategy.TOKEN_BUCKET:
            return await self._token_bucket_check(key)
        else:
            return await self._fixed_window_check(key)
    
    async def _sliding_window_check(self, key: str) -> tuple[bool, Dict[str, Any]]:
        """Sliding window rate limiting"""
        now = time.time()
        window_start = now - 60  # 1 минута окно
        
        if self.redis_client:
            # Redis implementation
            pipe = self.redis_client.pipeline()
            pipe.zremrangebyscore(f"ratelimit:{key}", 0, window_start)
            pipe.zcard(f"ratelimit:{key}")
            pipe.zadd(f"ratelimit:{key}", {str(now): now})
            pipe.expire(f"ratelimit:{key}", 120)
            
            results = await pipe.execute()
            current_count = results[1]
        else:
            # In-memory implementation
            if key not in self._memory_store:
                self._memory_store[key] = {"requests": []}
            
            # Очищаем старые запросы
            self._memory_store[key]["requests"] = [
                req for req in self._memory_store[key]["requests"]
                if req > window_start
            ]
            
            current_count = len(self._memory_store[key]["requests"])
            self._memory_store[key]["requests"].append(now)
        
        allowed = current_count < self.config.requests_per_minute
        remaining = max(0, self.config.requests_per_minute - current_count)
        
        headers = {
            "X-RateLimit-Limit": str(self.config.requests_per_minute),
            "X-RateLimit-Remaining": str(remaining),
            "X-RateLimit-Reset": str(int(now + 60))
        }
        
        return allowed, headers
    
    async def _token_bucket_check(self, key: str) -> tuple[bool, Dict[str, Any]]:
        """Token bucket rate limiting"""
        now = time.time()
        bucket_key = f"bucket:{key}"
        
        if self.redis_client:
            # Получаем текущее состояние бакета
            bucket_data = await self.redis_client.hgetall(bucket_key)
            
            if not bucket_data:
                tokens = self.config.burst_limit - 1
                last_update = now
            else:
                tokens = float(bucket_data.get("tokens", self.config.burst_limit))
                last_update = float(bucket_data.get("last_update", now))
                
                # Добавляем токены со временем
                time_passed = now - last_update
                tokens_to_add = time_passed * (self.config.requests_per_minute / 60)
                tokens = min(self.config.burst_limit, tokens + tokens_to_add)
            
            allowed = tokens >= 1
            if allowed:
                tokens -= 1
            
            # Сохраняем состояние
            await self.redis_client.hset(bucket_key, mapping={
                "tokens": tokens,
                "last_update": now
            })
            await self.redis_client.expire(bucket_key, 120)
            
        else:
            # In-memory
            if bucket_key not in self._memory_store:
                self._memory_store[bucket_key] = {
                    "tokens": self.config.burst_limit,
                    "last_update": now
                }
            
            bucket = self._memory_store[bucket_key]
            time_passed = now - bucket["last_update"]
            tokens_to_add = time_passed * (self.config.requests_per_minute / 60)
            bucket["tokens"] = min(self.config.burst_limit, bucket["tokens"] + tokens_to_add)
            bucket["last_update"] = now
            
            allowed = bucket["tokens"] >= 1
            if allowed:
                bucket["tokens"] -= 1
            
            tokens = bucket["tokens"]
        
        headers = {
            "X-RateLimit-Limit": str(self.config.burst_limit),
            "X-RateLimit-Remaining": str(int(tokens)),
            "X-RateLimit-Reset": str(int(now + 60))
        }
        
        return allowed, headers
    
    async def _fixed_window_check(self, key: str) -> tuple[bool, Dict[str, Any]]:
        """Fixed window rate limiting"""
        now = time.time()
        window = int(now / 60)
        key_window = f"{key}:{window}"
        
        if self.redis_client:
            current = await self.redis_client.incr(f"ratelimit:{key_window}")
            if current == 1:
                await self.redis_client.expire(f"ratelimit:{key_window}", 60)
        else:
            if key_window not in self._memory_store:
                self._memory_store[key_window] = {"count": 0}
            self._memory_store[key_window]["count"] = self._memory_store[key_window].get("count", 0) + 1
            current = self._memory_store[key_window]["count"]
        
        allowed = current <= self.config.requests_per_minute
        remaining = max(0, self.config.requests_per_minute - current)
        
        return allowed, {
            "limit": self.config.requests_per_minute,
            "remaining": remaining,
            "reset": (window + 1) * 60 - now
        }

class CacheManager:
    """Кэширование результатов API"""
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        self.redis_client: Any = None
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        
        if _redis_available and _redis_module:
            try:
                self.redis_client = _redis_module.Redis.from_url(
                    "redis://localhost:6379",
                    decode_responses=True
                )
            except Exception as e:
                logging.error(f"Redis cache connection failed: {e}")
        
        # Запускаем очистку если in-memory
        if not self.redis_client:
            task = asyncio.create_task(self._cleanup_loop())
            _cleanup_tasks.add(task)
            task.add_done_callback(_cleanup_tasks.discard)
    
    def generate_key(self, prefix: str, data: Any) -> str:
        """Генерация кэш-ключа"""
        if isinstance(data, dict):
            key_data = json.dumps(data, sort_keys=True)
        else:
            key_data = str(data)
        
        hash_key = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{hash_key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Получить значение из кэша"""
        try:
            if self.redis_client:
                value = await self.redis_client.get(f"cache:{key}")
                if value:
                    return json.loads(value)
                return None
            else:
                if key in self._memory_cache:
                    entry = self._memory_cache[key]
                    if entry["expires"] > time.time():
                        self._access_times[key] = time.time()
                        return entry["value"]
                    else:
                        del self._memory_cache[key]
                        del self._access_times[key]
                return None
        except Exception as e:
            logging.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохранить значение в кэш"""
        try:
            actual_ttl: int = ttl if ttl is not None else self.config.default_ttl
            
            if self.redis_client:
                await self.redis_client.setex(
                    f"cache:{key}",
                    actual_ttl,
                    json.dumps(value)
                )
                return True
            else:
                # Проверяем размер кэша
                if len(self._memory_cache) >= self.config.max_size:
                    await self._evict_lru()
                
                self._memory_cache[key] = {
                    "value": value,
                    "expires": time.time() + actual_ttl
                }
                self._access_times[key] = time.time()
                return True
                
        except Exception as e:
            logging.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Удалить значение из кэша"""
        try:
            if self.redis_client:
                await self.redis_client.delete(f"cache:{key}")
            else:
                self._memory_cache.pop(key, None)
                self._access_times.pop(key, None)
            return True
        except Exception as e:
            logging.error(f"Cache delete error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Очистить кэш по паттерну"""
        try:
            if self.redis_client:
                keys = await self.redis_client.keys(f"cache:{pattern}*")
                if keys:
                    await self.redis_client.delete(*keys)
                return len(keys)
            else:
                keys_to_delete = [
                    k for k in self._memory_cache.keys()
                    if k.startswith(pattern)
                ]
                for key in keys_to_delete:
                    del self._memory_cache[key]
                    del self._access_times[key]
                return len(keys_to_delete)
        except Exception as e:
            logging.error(f"Cache clear error: {e}")
            return 0
    
    async def _evict_lru(self):
        """Evict least recently used entries"""
        if not self._access_times:
            return
        
        # Находим наименее используемые
        sorted_keys = sorted(
            self._access_times.items(),
            key=lambda x: x[1]
        )
        
        # Удаляем 10% наименее используемых
        to_remove = int(len(sorted_keys) * 0.1) or 1
        for key, _ in sorted_keys[:to_remove]:
            del self._memory_cache[key]
            del self._access_times[key]
    
    async def _cleanup_loop(self):
        """Фоновая очистка expired записей"""
        while True:
            try:
                await asyncio.sleep(self.config.cleanup_interval)
                
                now = time.time()
                expired_keys = [
                    k for k, v in self._memory_cache.items()
                    if v["expires"] <= now
                ]
                
                for key in expired_keys:
                    del self._memory_cache[key]
                    del self._access_times[key]
                
                if expired_keys:
                    logging.info(f"Cleaned {len(expired_keys)} expired cache entries")
                    
            except Exception as e:
                logging.error(f"Cache cleanup error: {e}")

# 🎯 Декораторы для удобного использования
def rate_limit(
    requests_per_minute: int = 60,
    strategy: RateLimitStrategy = RateLimitStrategy.SLIDING_WINDOW
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор для rate limiting"""
    limiter = RateLimiter(RateLimitConfig(
        requests_per_minute=requests_per_minute,
        strategy=strategy
    ))
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Получаем ключ (обычно IP или user ID)
            key: str = str(kwargs.get("user_id", "anonymous"))
            
            allowed, headers = await limiter.is_allowed(key)
            
            if not allowed:
                raise Exception("Rate limit exceeded")
            
            result = await func(*args, **kwargs)
            
            # Добавляем headers к результату если это dict
            if isinstance(result, dict):
                res_dict = cast(Any, result)
                res_dict["_rate_limit_headers"] = headers
                return res_dict
            
            return result
        
        return wrapper
    return decorator

def cached(prefix: str, ttl: int = 300) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Декоратор для кэширования"""
    cache = CacheManager(CacheConfig(default_ttl=ttl))
    
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Генерируем ключ из аргументов
            cache_key_data: Dict[str, Any] = {
                "args": list(args),
                "kwargs": dict(kwargs)
            }
            key = cache.generate_key(prefix, cache_key_data)
            
            # Пробуем получить из кэша
            cached_value: Optional[Any] = await cache.get(key)
            if cached_value is not None:
                if isinstance(cached_value, dict):
                    # Final override for Pylance partially unknown dict
                    final_res: Any = cast(Any, cached_value)
                    final_res["_cached"] = True
                    return final_res
                return cached_value
            
            # Вызываем функцию
            result = await func(*args, **kwargs)
            
            # Сохраняем в кэш
            if isinstance(result, dict):
                await cache.set(key, cast(Any, result), ttl)
            
            return cast(Any, result)
        
        return wrapper
    return decorator

# Глобальные экземпляры
global_rate_limiter = RateLimiter()
global_cache = CacheManager()

async def get_rate_limiter() -> RateLimiter:
    """Получить глобальный rate limiter"""
    return global_rate_limiter

async def get_cache() -> CacheManager:
    """Получить глобальный cache manager"""
    return global_cache
