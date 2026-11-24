"""Schémas Pydantic pour la gestion des projets PFE."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.project import ProjectStatus
from app.schemas.user import UserResponse


class ProjectBase(BaseModel):
    title: str = Field(
        ..., min_length=5, max_length=255, description="Titre du sujet PFE"
    )
    description: str = Field(
        ..., min_length=20, description="Description détaillée du sujet"
    )
    company: str | None = Field(
        None, max_length=255, description="Entreprise d'accueil (optionnel)"
    )


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = Field(None, min_length=5, max_length=255)
    description: str | None = Field(None, min_length=20)
    company: str | None = Field(None, max_length=255)


class ProjectStatusUpdate(BaseModel):
    status: ProjectStatus = Field(
        ..., description="Nouveau statut (SUBMITTED, VALIDATED, REJECTED)"
    )
    comment: str | None = Field(
        None, description="Commentaire / motif de validation ou refus"
    )


class ProjectAssignSupervisor(BaseModel):
    supervisor_id: int = Field(..., description="ID de l'enseignant encadrant")


class ProjectResponse(ProjectBase):
    id: int
    status: ProjectStatus
    student_id: int
    supervisor_id: int | None = None
    created_at: datetime
    student: UserResponse | None = None
    supervisor: UserResponse | None = None

    model_config = ConfigDict(from_attributes=True)
