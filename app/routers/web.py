"""Vues web rendues via Jinja2."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.project import Project, ProjectStatus

router = APIRouter(prefix="/web", tags=["web"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/projects", response_class=HTMLResponse)
def web_projects_list(
    request: Request,
    status: ProjectStatus | None = None,
    db: Session = Depends(get_db),
):
    """Affiche le catalogue des projets PFE."""
    query = db.query(Project)
    if status:
        query = query.filter(Project.status == status)
    projects = query.order_by(Project.created_at.desc()).all()

    return templates.TemplateResponse(
        request=request,
        name="projects_list.html",
        context={"projects": projects, "current_status": status},
    )


@router.get("/projects/new", response_class=HTMLResponse)
def web_project_new(request: Request):
    """Affiche le formulaire de création d'un sujet."""
    return templates.TemplateResponse(
        request=request, name="project_form.html", context={}
    )
