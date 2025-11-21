"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import get_settings
from backend.api import chat, visualize

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(chat.router)
app.include_router(visualize.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Medical Analytics AI Agent API", "version": settings.VERSION}


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok"}
