"""API dependencies.

FastAPI Dependency Injection:
- get_db: Database session
- get_tools: Agent tools
- get_cache: Redis cache
"""

from agent.tools import agent_tools
from cache.redis_client import cache
from database.connection import get_db

# from fastapi import Depends  # noqa: F401 (unused)
# from sqlalchemy.ext.asyncio import AsyncSession  # noqa: F401 (unused)
# from typing import AsyncGenerator  # noqa: F401 (unused)


async def get_tools():
    """Get agent tools dependency."""
    return agent_tools


async def get_cache():
    """Get cache dependency."""
    return cache


__all__ = ["get_db", "get_tools", "get_cache"]
