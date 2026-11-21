"""Exportation centralisée des routeurs de l'application."""

from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.projects import router as projects_router
from app.routers.web import router as web_router

__all__ = ["health_router", "auth_router", "projects_router", "web_router"]
