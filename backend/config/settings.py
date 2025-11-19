"""Application settings and configuration."""

import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://user:password@localhost:5432/medical_analytics",
    )

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")

    # LLM Configuration
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")
    LLM_BASE_URL: str = os.getenv("LLM_BASE_URL", "http://localhost:11434")

    # API Keys (optional)
    TOGETHER_API_KEY: str = os.getenv("TOGETHER_API_KEY", "")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")

    # Application
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv(
        "ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173"
    ).split(",")

    # Cache TTL
    CACHE_TTL_REALTIME: int = int(os.getenv("CACHE_TTL_REALTIME", "120"))
    CACHE_TTL_FORECAST: int = int(os.getenv("CACHE_TTL_FORECAST", "1800"))
    CACHE_TTL_RECOMMENDATIONS: int = int(os.getenv("CACHE_TTL_RECOMMENDATIONS", "3600"))

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = True


settings = Settings()
