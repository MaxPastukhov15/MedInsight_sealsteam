"""Database models."""
from sqlalchemy import Column, Integer, String, Date
from backend.database.connection import Base


class DiseaseCase(Base):
    """Disease case model."""

    __tablename__ = "disease_cases"

    id = Column(Integer, primary_key=True, index=True)
    district = Column(String(100), index=True)
    disease = Column(String(100), index=True)
    date = Column(Date, index=True)
    age = Column(Integer)
    gender = Column(String(10))
