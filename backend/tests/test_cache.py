"""Tests for cache module.

Тесты для Redis кэширования.
"""

# import pytest  # noqa: F401 (unused)
from cache.cache_manager import generate_cache_key


def test_generate_cache_key() -> None:
    """Test cache key generation."""
    key1 = generate_cache_key("test", "arg1", "arg2", param1="value1")
    key2 = generate_cache_key("test", "arg1", "arg2", param1="value1")
    key3 = generate_cache_key("test", "arg1", "arg2", param1="value2")

    # Same params should generate same key
    assert key1 == key2

    # Different params should generate different keys
    assert key1 != key3


# TODO: Add more cache tests when Redis is properly initialized in tests
# @pytest.mark.asyncio
# async def test_redis_get_set() -> None:
#     """Test Redis get/set operations."""
#     from cache.redis_client import cache
#
#     await cache.connect()
#     await cache.set("test_key", "test_value", ttl=60)
#     value = await cache.get("test_key")
#
#     assert value == "test_value"
#
#     await cache.delete("test_key")
#     await cache.disconnect()
