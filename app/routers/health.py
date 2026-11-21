"""Route de santé (Healthcheck) pour Docker, Kubernetes et le monitoring."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

router = APIRouter(tags=["monitoring"])


@router.get(
    "/health",
    summary="Vérification de l'état de l'application et de la base de données",
)
def healthcheck(db: Session = Depends(get_db)):
    """
    Endpoint appelé par le HEALTHCHECK Docker et le système de monitoring.
    Vérifie que l'application répond et que PostgreSQL est joignable.
    """
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "environment": settings.ENVIRONMENT,
                "database": db_status,
            },
        )

    return {
        "status": "ok",
        "environment": settings.ENVIRONMENT,
        "database": db_status,
    }
