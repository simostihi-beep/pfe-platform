"""Exportation centralisée des modèles ORM et de la base déclarative."""
from app.core.database import Base
from app.models.user import User, UserRole
from app.models.project import Project, ProjectStatus
from app.models.milestone import Milestone
from app.models.defense import Defense, defense_jury

__all__ = [
    "Base",
    "User",
    "UserRole",
    "Project",
    "ProjectStatus",
    "Milestone",
    "Defense",
    "defense_jury",
]
