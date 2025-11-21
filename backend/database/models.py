"""Database models."""

# from typing import Optional  # F401: unused import

from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class DiseaseCase(Base):
    """Disease case record."""

    __tablename__ = "disease_cases"

    id = Column(Integer, primary_key=True, index=True)
    disease_name = Column(String(100), nullable=False, index=True)
    region = Column(String(100), index=True)
    date = Column(Date, nullable=False, index=True)
    cases = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    age_group = Column(String(20))
    gender = Column(String(10))

    __table_args__ = (
        Index("ix_disease_region_date", "disease_name", "region", "date"),
    )


class ChatHistory(Base):
    """Chat history record."""

    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user or assistant
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tokens_used = Column(Integer)
    latency_ms = Column(Float)


class ToolUsage(Base):
    """Tool usage tracking."""

    __tablename__ = "tool_usage"

    id = Column(Integer, primary_key=True, index=True)
    chat_history_id = Column(Integer, ForeignKey("chat_history.id"))
    tool_name = Column(String(50), nullable=False)
    parameters = Column(Text)
    result = Column(Text)
    execution_time_ms = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    chat_history = relationship("ChatHistory")
