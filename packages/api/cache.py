"""
Redis caching layer using Upstash (free tier).
Provides caching for trips, users, and expensive computations.
"""
import json
import functools
from typing import Optional, Any, Callable
from redis import Redis
from . import config

# Initialize Redis client (Upstash)
redis_client: Optional[Redis] = None

def init_redis():
    """Initialize Redis client if URL is provided."""
    global redis_client
    redis_url = config.settings.REDIS_URL if hasattr(config.settings, 'REDIS_URL') else None

    if redis_url:
        try:
            redis_client = Redis.from_url(
                redis_url,
                decode_responses=True,
                socket_timeout=5,
                socket_connect_timeout=5
            )
            redis_client.ping()
            print("✅ Redis cache connected")
        except Exception as e:
            print(f"⚠️ Redis connection failed: {e}")
            redis_client = None
    else:
        print("⚠️ Redis URL not configured, caching disabled")

def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    if not redis_client:
        return None

    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
    except Exception as e:
        print(f"Cache get error: {e}")
    return None

def cache_set(key: str, value: Any, ttl: int = 60) -> bool:
    """Set value in cache with TTL in seconds."""
    if not redis_client:
        return False

    try:
        redis_client.setex(key, ttl, json.dumps(value))
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False

def cache_delete(key: str) -> bool:
    """Delete value from cache."""
    if not redis_client:
        return False

    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False

def cache_delete_pattern(pattern: str) -> int:
    """Delete all keys matching pattern."""
    if not redis_client:
        return 0

    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
    except Exception as e:
        print(f"Cache delete pattern error: {e}")
    return 0

def cached(key_prefix: str, ttl: int = 60):
    """Decorator to cache function results."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not redis_client:
                return func(*args, **kwargs)

            cache_key = f"{key_prefix}:{args[0] if args else 'default'}"

            cached_value = cache_get(cache_key)
            if cached_value is not None:
                return cached_value

            result = func(*args, **kwargs)
            cache_set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator
