from typing import Optional, Any
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
import json
import time
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)


class RedisClient:
    """Async Redis client wrapper"""
    _memory_store: dict[str, dict[str, Any]] = {}
    
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
        self._memory_fallback = False

    def _can_use_memory_fallback(self) -> bool:
        return self._memory_fallback or settings.ENVIRONMENT != "production" or settings.DISABLE_AUTH

    @classmethod
    def _purge_memory_store(cls) -> None:
        expired_keys = [
            key
            for key, payload in cls._memory_store.items()
            if payload.get("expires_at") is not None and payload["expires_at"] <= time.time()
        ]
        for key in expired_keys:
            cls._memory_store.pop(key, None)
    
    async def connect(self) -> None:
        """Initialize Redis connection pool"""
        try:
            self.pool = ConnectionPool.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                decode_responses=True,
            )
            self.client = redis.Redis(connection_pool=self.pool)
            
            # Test connection
            await self.client.ping()
            logger.info("redis_connected", url=settings.REDIS_URL)
        except Exception as e:
            logger.error("redis_connection_failed", error=str(e))
            self.pool = None
            self.client = None
            if self._can_use_memory_fallback():
                self._memory_fallback = True
                logger.warning("redis_memory_fallback_enabled")
                return
            raise
    
    async def close(self) -> None:
        """Close Redis connection"""
        if self.client:
            await self.client.aclose()
        if self.pool:
            await self.pool.aclose()
        logger.info("redis_disconnected")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key"""
        self._purge_memory_store()
        if not self.client and self._can_use_memory_fallback():
            payload = self._memory_store.get(key)
            return None if payload is None else str(payload.get("value"))
        if not self.client:
            return None
        return await self.client.get(key)
    
    async def set(
        self,
        key: str,
        value: str,
        ex: Optional[int] = None,
    ) -> bool:
        """Set key-value pair with optional expiration"""
        self._purge_memory_store()
        if not self.client and self._can_use_memory_fallback():
            expires_at = None
            if ex is not None:
                expires_at = time.time() + ex
            self._memory_store[key] = {"value": value, "expires_at": expires_at}
            return True
        if not self.client:
            return False
        return await self.client.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> int:
        """Delete key"""
        self._purge_memory_store()
        if not self.client and self._can_use_memory_fallback():
            return 1 if self._memory_store.pop(key, None) is not None else 0
        if not self.client:
            return 0
        return await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        self._purge_memory_store()
        if not self.client and self._can_use_memory_fallback():
            return key in self._memory_store
        if not self.client:
            return False
        return await self.client.exists(key) > 0
    
    async def incr(self, key: str) -> int:
        """Increment value"""
        self._purge_memory_store()
        if not self.client and self._can_use_memory_fallback():
            payload = self._memory_store.get(key, {"value": "0", "expires_at": None})
            next_value = int(payload.get("value", "0")) + 1
            self._memory_store[key] = {"value": str(next_value), "expires_at": payload.get("expires_at")}
            return next_value
        if not self.client:
            return 0
        return await self.client.incr(key)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set key expiration"""
        self._purge_memory_store()
        if not self.client and self._can_use_memory_fallback():
            if key not in self._memory_store:
                return False
            self._memory_store[key]["expires_at"] = time.time() + seconds
            return True
        if not self.client:
            return False
        return await self.client.expire(key, seconds)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(
        self,
        key: str,
        value: Any,
        ex: Optional[int] = None,
    ) -> bool:
        """Set JSON value"""
        try:
            json_str = json.dumps(value)
            return await self.set(key, json_str, ex=ex)
        except (TypeError, ValueError):
            return False
    
    async def set_task_progress(
        self,
        task_id: str,
        progress: int,
        status: str,
        message: Optional[str] = None,
        stage: Optional[str] = None,
        error_code: Optional[str] = None,
    ) -> bool:
        """Set task progress in Redis"""
        data = {
            "progress": progress,
            "status": status,
            "message": message,
            "stage": stage,
            "error_code": error_code,
        }
        return await self.set_json(f"task:{task_id}", data, ex=3600)
    
    async def get_task_progress(self, task_id: str) -> Optional[dict]:
        """Get task progress from Redis"""
        return await self.get_json(f"task:{task_id}")


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Get Redis client instance"""
    return redis_client
