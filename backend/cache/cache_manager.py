"""Cache management utilities."""

import hashlib
from functools import wraps
from typing import Any, Callable  # , Optional  # F401: unused import

from cache.redis_client import cache
from config.cache_config import CACHE_TTL_REALTIME
from monitoring.logging_config import logger


def generate_cache_key(prefix: str, *args: Any, **kwargs: Any) -> str:
    """Generate cache key from function arguments.

    Args:
        prefix: Key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Cache key string
    """
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    key_string = ":".join([prefix] + key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def cache_result(prefix: str, ttl: int = CACHE_TTL_REALTIME) -> Callable:
    """Decorator to cache function results.

    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds

    Returns:
        Decorated function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key
            cache_key = generate_cache_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value is not None:
                logger.info(
                    "cache_hit",
                    function=func.__name__,
                    key=cache_key,
                )
                return cached_value

            # Execute function
            logger.info(
                "cache_miss",
                function=func.__name__,
                key=cache_key,
            )
            result = await func(*args, **kwargs)

            # Store in cache
            await cache.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator
