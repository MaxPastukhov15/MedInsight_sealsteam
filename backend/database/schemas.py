"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message request schema."""

    message: str = Field(..., min_length=1, max_length=5000)
    chat_history: Optional[List[Dict[str, str]]] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Chat response schema."""

    response: str
    visualizations: Optional[List[Dict[str, Any]]] = None
    metrics: Dict[str, Any] = Field(default_factory=dict)
    tools_used: Optional[List[str]] = None


class DiseaseAnalysisRequest(BaseModel):
    """Disease analysis request schema."""

    disease_name: str
    region: Optional[str] = None
    age_group: Optional[str] = None
    days: int = Field(default=7, ge=1, le=90)


class DiseaseAnalysisResponse(BaseModel):
    """Disease analysis response schema."""

    disease_name: str
    current_cases: int
    deaths: int
    mortality_rate: float
    status: str  # "RISING", "FALLING", "STABLE"
    trend_percentage: float


class ForecastRequest(BaseModel):
    """Forecast request schema."""

    disease_name: str
    region: Optional[str] = None
    forecast_days: int = Field(default=14, ge=1, le=30)


class ForecastResponse(BaseModel):
    """Forecast response schema."""

    predictions: List[float]
    confidence_lower: List[float]
    confidence_upper: List[float]
    dates: List[str]
    model: str


class HealthCheckResponse(BaseModel):
    """Health check response schema."""

    status: str
    database: str
    redis: str
    llm: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
