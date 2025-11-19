"""API dependencies.

FastAPI Dependency Injection:
- get_db: Database session
- get_tools: Agent tools
- get_cache: Redis cache
"""

from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from agent.tools import agent_tools
from cache.redis_client import cache


async def get_tools():
    """Get agent tools dependency."""
    return agent_tools


async def get_cache():
    """Get cache dependency."""
    return cache


__all__ = ["get_db", "get_tools", "get_cache"]
