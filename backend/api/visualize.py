"""Visualization API endpoints."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from backend.database.connection import get_db
from backend.database.models import DiseaseCase

router = APIRouter(prefix="/api", tags=["visualize"])


@router.get("/trends")
async def get_trends(
    disease: str = Query(..., description="Disease name"),
    db: Session = Depends(get_db),
):
    """Get disease trends by month."""
    results = (
        db.query(
            func.date_trunc("month", DiseaseCase.date).label("month"),
            func.count(DiseaseCase.id).label("cases"),
        )
        .filter(DiseaseCase.disease == disease)
        .group_by("month")
        .order_by("month")
        .all()
    )

    return {
        "data": [
            {"month": str(r.month.date()), "cases": r.cases} for r in results
        ]
    }


@router.get("/geo")
async def get_geo_stats(
    disease: str = Query(..., description="Disease name"),
    db: Session = Depends(get_db),
):
    """Get disease stats by district."""
    results = (
        db.query(
            DiseaseCase.district, func.count(DiseaseCase.id).label("cases")
        )
        .filter(DiseaseCase.disease == disease)
        .group_by(DiseaseCase.district)
        .order_by(func.count(DiseaseCase.id).desc())
        .all()
    )

    return {"data": [{"district": r.district, "cases": r.cases} for r in results]}
