"""Point d'entrée principal de l'application FastAPI."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import settings
from app.routers import auth_router, health_router, projects_router, web_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "Plateforme de gestion des projets de fin d'études (PFE) "
        "avec CI/CD, sécurité et observabilité. (ENSA Fès)"
    ),
    version="1.0.0",
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enregistrement des routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(web_router)

# Instrumentation Prometheus pour les métriques (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


@app.get("/", tags=["Root"])
def root():
    """Page d'accueil racine de l'API."""
    return {
        "message": f"Bienvenue sur l'API {settings.PROJECT_NAME}",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }
