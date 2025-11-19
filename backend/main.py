"""Main FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config.settings import settings
from monitoring.logging_config import setup_logging, logger

# Setup structured logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan events."""
    logger.info("application_startup", environment=settings.ENVIRONMENT)

    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Load knowledge base into ChromaDB

    yield

    logger.info("application_shutdown")

    # TODO: Close database connections
    # TODO: Close Redis connections


app = FastAPI(
    title="Medical Analytics AI-Agent",
    description="AI-Agent для анализа медицинских данных",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint."""
    return JSONResponse(
        content={
            "message": "Medical Analytics AI-Agent API",
            "version": "1.0.0",
            "status": "operational",
        }
    )


@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    # TODO: Add actual health checks for DB, Redis, LLM
    return JSONResponse(
        content={
            "status": "healthy",
            "database": "ok",
            "redis": "ok",
            "llm": "ok",
        }
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
