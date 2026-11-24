"""Routeur API REST pour la gestion des projets PFE."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_roles
from app.models.project import ProjectStatus
from app.models.user import User, UserRole
from app.schemas.project import (
    ProjectAssignSupervisor,
    ProjectCreate,
    ProjectResponse,
    ProjectStatusUpdate,
    ProjectUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Déposer un nouveau sujet PFE (Étudiant uniquement)",
)
def create_project(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.STUDENT])),
):
    """US1 : en tant qu'étudiant, je dépose un sujet pour qu'il soit examiné."""
    return ProjectService.create_project(db, project_in, current_user)


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="Lister les projets (filtrés selon le rôle)",
)
def list_projects(
    status: ProjectStatus | None = Query(None, description="Filtrer par statut"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ProjectService.list_projects_for_user(
        db, current_user, status_filter=status, skip=skip, limit=limit
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Consulter le détail d'un projet",
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = ProjectService.get_project_by_id(db, project_id)
    # Vérification d'accès si étudiant
    if current_user.role == UserRole.STUDENT and project.student_id != current_user.id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès interdit à ce projet",
        )
    return project


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Modifier un projet (brouillon)",
)
def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ProjectService.update_project(db, project_id, project_in, current_user)


@router.patch(
    "/{project_id}/status",
    response_model=ProjectResponse,
    summary="Faire évoluer le statut d'un projet (soumission, validation, refus)",
)
def update_project_status(
    project_id: int,
    status_in: ProjectStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    US2 : en tant qu'encadrant, je valide ou refuse un sujet avec un commentaire.
    US1 : en tant qu'étudiant, je soumets mon sujet.
    """
    return ProjectService.update_project_status(db, project_id, status_in, current_user)


@router.post(
    "/{project_id}/assign-supervisor",
    response_model=ProjectResponse,
    summary="Affecter un encadrant à un projet (Admin uniquement)",
)
def assign_supervisor(
    project_id: int,
    assignment: ProjectAssignSupervisor,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles([UserRole.ADMIN])),
):
    """US3 : en tant qu'administrateur, j'affecte un encadrant à un projet validé."""
    return ProjectService.assign_supervisor(
        db, project_id, assignment.supervisor_id, current_user
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un projet",
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ProjectService.delete_project(db, project_id, current_user)
