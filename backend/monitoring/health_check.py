"""Health check utilities.

Проверка здоровья всех сервисов:
- Database (PostgreSQL)
- Cache (Redis)
- LLM provider
"""

from typing import Dict, Any
import asyncio

from cache.redis_client import cache
from monitoring.logging_config import logger


class HealthChecker:
    """Health check for all services."""

    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """Check database health."""
        try:
            # TODO: Import after database is properly initialized
            return {"status": "healthy", "details": "Database OK (mock)"}
        except Exception as e:
            logger.error("database_health_check_failed", error=str(e))
            return {"status": "unhealthy", "details": str(e)}

    @staticmethod
    async def check_redis() -> Dict[str, Any]:
        """Check Redis health."""
        try:
            if cache.redis:
                await cache.redis.ping()
                return {"status": "healthy", "details": "Redis connection OK"}
            return {"status": "unhealthy", "details": "Redis not initialized"}
        except Exception as e:
            logger.error("redis_health_check_failed", error=str(e))
            return {"status": "unhealthy", "details": str(e)}

    @staticmethod
    async def check_llm() -> Dict[str, Any]:
        """Check LLM provider health."""
        try:
            from config.settings import settings
            if settings.LLM_PROVIDER:
                return {
                    "status": "healthy",
                    "details": f"LLM provider: {settings.LLM_PROVIDER}",
                }
            return {"status": "unhealthy", "details": "LLM not configured"}
        except Exception as e:
            logger.error("llm_health_check_failed", error=str(e))
            return {"status": "unhealthy", "details": str(e)}

    @staticmethod
    async def check_all() -> Dict[str, Any]:
        """Check all services."""
        db_health, redis_health, llm_health = await asyncio.gather(
            HealthChecker.check_database(),
            HealthChecker.check_redis(),
            HealthChecker.check_llm(),
        )

        all_healthy = all(
            h["status"] == "healthy"
            for h in [db_health, redis_health, llm_health]
        )

        return {
            "status": "healthy" if all_healthy else "degraded",
            "database": db_health,
            "redis": redis_health,
            "llm": llm_health,
        }


health_checker = HealthChecker()
