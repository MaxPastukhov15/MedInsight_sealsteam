"""Chat API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.database.connection import get_db
from backend.agent.simple_agent import create_simple_agent

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    """Chat response model."""

    response: str
    sources: list[str] = []


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Chat with AI agent."""
    try:
        agent = create_simple_agent(db)
        result = agent.invoke({"question": request.message})
        return ChatResponse(
            response=result.get("answer", "No response"),
            sources=result.get("sources", []),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
