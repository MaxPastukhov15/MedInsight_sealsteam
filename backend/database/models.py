"""Database models using SQLAlchemy ORM."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Disease(Base):
    """Disease statistics model."""

    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, nullable=False, index=True)
    disease_name = Column(String(255), nullable=False, index=True)
    cases_count = Column(Integer, nullable=False, default=0)
    deaths = Column(Integer, default=0)
    recovered = Column(Integer, default=0)
    region = Column(String(100), nullable=False, index=True)
    age_group = Column(String(50), index=True)  # "0-18", "18-65", "65+"
    source_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    forecasts = relationship("Forecast", back_populates="disease")


class Forecast(Base):
    """Forecast results model."""

    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True, index=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=False)
    forecast_date = Column(DateTime, nullable=False, index=True)
    predicted_cases = Column(Float, nullable=False)
    confidence_lower = Column(Float)
    confidence_upper = Column(Float)
    model_name = Column(String(50))  # "prophet", "arima", "ensemble"
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    disease = relationship("Disease", back_populates="forecasts")


class AnalysisCache(Base):
    """Cache for analysis results."""

    __tablename__ = "analysis_cache"

    id = Column(Integer, primary_key=True, index=True)
    analysis_type = Column(String(100), nullable=False, index=True)
    query_hash = Column(String(64), nullable=False, unique=True, index=True)
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)


class ChatHistory(Base):
    """Chat conversation history."""

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    metadata = Column(JSON)  # Store tools used, latency, etc.
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
