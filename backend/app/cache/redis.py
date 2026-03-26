"""
Redis cache layer with decorator support for caching function results.
"""
import json
import hashlib
from functools import wraps
from redis.asyncio import Redis
from typing import Any, Callable, Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)

# Global Redis client instance
redis_client: Optional[Redis] = None


async def init_redis():
    """Initialize Redis connection."""
    global redis_client
    try:
        redis_client = Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # Test connection
        await redis_client.ping()
        logger.info(f"Redis connected: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        redis_client = None
        raise


async def close_redis():
    """Close Redis connection."""
    global redis_client
    if redis_client:
        await redis_client.close()
        logger.info("Redis connection closed")
        redis_client = None


def redis_cache(ttl: int = 3600, namespace: str = "default"):
    """
    Decorator to cache function results in Redis.
    
    Args:
        ttl: Time to live in seconds (default 3600 = 1 hour)
        namespace: Cache namespace for key organization (default "default")
    
    Returns:
        Decorated function that caches results in Redis
    
    Example:
        @redis_cache(ttl=600, namespace="analytics")
        async def calculate_consistency(driver_id: str, year: str):
            # expensive calculation
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key from function name and arguments
            raw = f"{func.__module__}.{func.__name__}:{args}:{sorted(kwargs.items())}"
            params_hash = hashlib.md5(raw.encode()).hexdigest()
            key = f"cache:{namespace}:{func.__name__}:{params_hash}"
            
            # Try to get from cache
            if redis_client:
                try:
                    cached = await redis_client.get(key)
                    if cached:
                        logger.debug(f"Cache HIT: {key}")
                        return json.loads(cached)
                except Exception as e:
                    logger.warning(f"Cache read error for {key}: {e}")
            
            # Cache miss - execute function
            logger.debug(f"Cache MISS: {key}")
            result = await func(*args, **kwargs)
            
            # Store in cache
            if redis_client:
                try:
                    await redis_client.setex(
                        key,
                        ttl,
                        json.dumps(result, default=str)
                    )
                    logger.debug(f"Cached: {key} (TTL: {ttl}s)")
                except Exception as e:
                    logger.warning(f"Cache write error for {key}: {e}")
            
            return result
        
        return wrapper
    return decorator


async def invalidate_cache_pattern(pattern: str) -> int:
    """
    Invalidate all cache keys matching the given pattern.
    
    Args:
        pattern: Redis key pattern (e.g., "cache:jolpica:*" or "cache:analytics:consistency:*")
    
    Returns:
        Number of keys deleted
    
    Example:
        # Invalidate all Jolpica cache entries
        await invalidate_cache_pattern("cache:jolpica:*")
        
        # Invalidate specific driver's analytics
        await invalidate_cache_pattern("cache:analytics:*:verstappen:*")
    """
    if not redis_client:
        logger.warning("Redis not available, cannot invalidate cache")
        return 0
    
    try:
        deleted_count = 0
        cursor = 0
        
        # Use SCAN to iterate through keys matching pattern
        while True:
            cursor, keys = await redis_client.scan(
                cursor=cursor,
                match=pattern,
                count=100
            )
            
            if keys:
                deleted = await redis_client.delete(*keys)
                deleted_count += deleted
                logger.info(f"Deleted {deleted} keys matching pattern: {pattern}")
            
            if cursor == 0:
                break
        
        logger.info(f"Total deleted: {deleted_count} keys for pattern: {pattern}")
        return deleted_count
        
    except Exception as e:
        logger.error(f"Error invalidating cache pattern {pattern}: {e}")
        return 0


async def get_cache_stats() -> dict:
    """
    Get Redis cache statistics.
    
    Returns:
        Dictionary with cache statistics (keys count, memory usage, etc.)
    """
    if not redis_client:
        return {"status": "unavailable"}
    
    try:
        info = await redis_client.info("stats")
        keyspace = await redis_client.info("keyspace")
        
        return {
            "status": "connected",
            "total_keys": sum(
                int(db_info.get("keys", 0))
                for db_info in keyspace.values()
                if isinstance(db_info, dict)
            ),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "hit_rate": (
                info.get("keyspace_hits", 0) / 
                (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1))
            ) * 100
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"status": "error", "error": str(e)}
