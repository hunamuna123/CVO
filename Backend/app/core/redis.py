"""
Redis connection and caching utilities.
"""

import asyncio
import json
import pickle
from typing import Any, Optional, Union
from urllib.parse import urlparse

import redis.asyncio as redis
import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

# Global Redis connection pool
redis_pool: Optional[redis.ConnectionPool] = None
redis_client: Optional[redis.Redis] = None


async def create_redis_connection() -> None:
    """
    Create Redis connection pool and client.
    """
    global redis_pool, redis_client

    try:
        settings = get_settings()
        # Parse Redis URL
        parsed_url = urlparse(settings.get_redis_url())

        # Create connection pool with simplified parameters
        redis_pool = redis.ConnectionPool(
            host=parsed_url.hostname or "localhost",
            port=parsed_url.port or 6379,
            db=int(parsed_url.path.lstrip("/")) if parsed_url.path else 0,
            password=settings.redis_password or "password",  # Default from docker-compose
            max_connections=20,
            retry_on_timeout=True,
        )

        # Create Redis client
        redis_client = redis.Redis(connection_pool=redis_pool)

        # Test the connection with a simple ping
        await redis_client.ping()

        logger.info("Redis connection established successfully")

    except Exception as e:
        logger.error("Failed to create Redis connection", error=str(e))
        raise


async def close_redis_connection() -> None:
    """
    Close Redis connection.
    """
    global redis_pool, redis_client

    if redis_client:
        await redis_client.close()

    if redis_pool:
        await redis_pool.disconnect()

    logger.info("Redis connection closed")


def get_redis() -> redis.Redis:
    """
    Get Redis client instance.
    """
    if not redis_client:
        raise RuntimeError("Redis not initialized")

    return redis_client


class RedisCache:
    """
    Redis cache manager with utilities for common caching patterns.
    """

    def __init__(self, client: Optional[redis.Redis] = None):
        self.client = client or get_redis()

    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        """
        try:
            value = await self.client.get(key)
            if value is None:
                return default

            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # If not JSON, try pickle
                try:
                    return pickle.loads(value.encode("latin1"))
                except (pickle.UnpicklingError, AttributeError):
                    # Return as string
                    return value
        except Exception as e:
            logger.error("Error getting value from cache", key=key, error=str(e))
            return default

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
        serialize: str = "json",
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds
            serialize: Serialization method ('json' or 'pickle')
        """
        try:
            # Serialize value
            if serialize == "json":
                serialized_value = json.dumps(value, default=str)
            elif serialize == "pickle":
                serialized_value = pickle.dumps(value).decode("latin1")
            else:
                serialized_value = str(value)

            # Set with expiration
            if expire:
                return await self.client.setex(key, expire, serialized_value)
            else:
                return await self.client.set(key, serialized_value)

        except Exception as e:
            logger.error("Error setting value in cache", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.
        """
        try:
            result = await self.client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error("Error deleting key from cache", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        """
        try:
            return bool(await self.client.exists(key))
        except Exception as e:
            logger.error("Error checking key existence", key=key, error=str(e))
            return False

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration for key.
        """
        try:
            return bool(await self.client.expire(key, seconds))
        except Exception as e:
            logger.error("Error setting expiration", key=key, error=str(e))
            return False

    async def ttl(self, key: str) -> int:
        """
        Get time to live for key.
        """
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error("Error getting TTL", key=key, error=str(e))
            return -1

    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment counter.
        """
        try:
            return await self.client.incrby(key, amount)
        except Exception as e:
            logger.error("Error incrementing counter", key=key, error=str(e))
            return None

    async def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Decrement counter.
        """
        try:
            return await self.client.decrby(key, amount)
        except Exception as e:
            logger.error("Error decrementing counter", key=key, error=str(e))
            return None

    async def get_or_set(
        self,
        key: str,
        callable_func,
        expire: Optional[int] = None,
        serialize: str = "json",
    ) -> Any:
        """
        Get value from cache or set it if not exists.

        Args:
            key: Cache key
            callable_func: Function to call if key doesn't exist
            expire: Expiration time in seconds
            serialize: Serialization method
        """
        # Try to get from cache first
        value = await self.get(key)
        if value is not None:
            return value

        # Get value from callable
        try:
            if asyncio.iscoroutinefunction(callable_func):
                value = await callable_func()
            else:
                value = callable_func()

            # Set in cache
            await self.set(key, value, expire, serialize)
            return value

        except Exception as e:
            logger.error("Error in get_or_set", key=key, error=str(e))
            return None

    async def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all keys matching pattern.
        """
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error("Error invalidating pattern", pattern=pattern, error=str(e))
            return 0

    async def health_check(self) -> bool:
        """
        Check Redis health.
        """
        try:
            pong = await self.client.ping()
            return pong == "PONG"
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False


class SessionManager:
    """
    Redis-based session manager.
    """

    def __init__(self, client: Optional[redis.Redis] = None, prefix: str = "session:"):
        self.client = client or get_redis()
        self.prefix = prefix

    def _get_key(self, session_id: str) -> str:
        """Get full session key."""
        return f"{self.prefix}{session_id}"

    async def create_session(
        self, session_id: str, data: dict, expire: int = 3600
    ) -> bool:
        """
        Create a new session.
        """
        try:
            key = self._get_key(session_id)
            serialized_data = json.dumps(data, default=str)
            return await self.client.setex(key, expire, serialized_data)
        except Exception as e:
            logger.error("Error creating session", session_id=session_id, error=str(e))
            return False

    async def get_session(self, session_id: str) -> Optional[dict]:
        """
        Get session data.
        """
        try:
            key = self._get_key(session_id)
            data = await self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error("Error getting session", session_id=session_id, error=str(e))
            return None

    async def update_session(self, session_id: str, data: dict) -> bool:
        """
        Update session data.
        """
        try:
            key = self._get_key(session_id)
            ttl = await self.client.ttl(key)
            serialized_data = json.dumps(data, default=str)

            if ttl > 0:
                return await self.client.setex(key, ttl, serialized_data)
            else:
                return await self.client.set(key, serialized_data)
        except Exception as e:
            logger.error("Error updating session", session_id=session_id, error=str(e))
            return False

    async def delete_session(self, session_id: str) -> bool:
        """
        Delete session.
        """
        try:
            key = self._get_key(session_id)
            result = await self.client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error("Error deleting session", session_id=session_id, error=str(e))
            return False

    async def extend_session(self, session_id: str, expire: int = 3600) -> bool:
        """
        Extend session expiration.
        """
        try:
            key = self._get_key(session_id)
            return bool(await self.client.expire(key, expire))
        except Exception as e:
            logger.error("Error extending session", session_id=session_id, error=str(e))
            return False


# Global instances - will be initialized when Redis connection is created
cache: Optional[RedisCache] = None
session_manager: Optional[SessionManager] = None


def initialize_redis_globals() -> None:
    """Initialize global Redis instances after connection is created."""
    global cache, session_manager
    cache = RedisCache()
    session_manager = SessionManager()


# Cache decorators
def cache_result(expire: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results.
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            import hashlib

            key_data = f"{key_prefix}{func.__name__}{args}{kwargs}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # Try to get from cache
            result = await cache.get(cache_key)
            if result is not None:
                return result

            # Execute function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Cache result
            await cache.set(cache_key, result, expire)
            return result

        return wrapper

    return decorator
