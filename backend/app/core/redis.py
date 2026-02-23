from typing import Optional, Any
import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool
import json
from app.core.config import settings
import structlog

logger = structlog.get_logger(__name__)


class RedisClient:
    """Async Redis client wrapper"""
    
    def __init__(self):
        self.pool: Optional[ConnectionPool] = None
        self.client: Optional[redis.Redis] = None
    
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
        if not self.client:
            return False
        return await self.client.set(key, value, ex=ex)
    
    async def delete(self, key: str) -> int:
        """Delete key"""
        if not self.client:
            return 0
        return await self.client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        return await self.client.exists(key) > 0
    
    async def incr(self, key: str) -> int:
        """Increment value"""
        if not self.client:
            return 0
        return await self.client.incr(key)
    
    async def expire(self, key: str, seconds: int) -> bool:
        """Set key expiration"""
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
    ) -> bool:
        """Set task progress in Redis"""
        data = {
            "progress": progress,
            "status": status,
            "message": message,
            "stage": stage,
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
