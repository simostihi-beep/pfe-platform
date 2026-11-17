"""Modèle SQLAlchemy représentant un utilisateur de la plateforme."""
import enum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserRole(str, enum.Enum):
    """Rôles définis dans le cahier des charges (Section 1.1)."""
    STUDENT = "student"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(
        Enum(UserRole, name="user_role", create_type=False),
        default=UserRole.STUDENT,
        nullable=False,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relations : un étudiant possède des projets PFE
    student_projects = relationship(
        "Project",
        foreign_keys="Project.student_id",
        back_populates="student",
        cascade="all, delete-orphan",
    )

    # Relations : un encadrant supervise des projets PFE
    supervised_projects = relationship(
        "Project",
        foreign_keys="Project.supervisor_id",
        back_populates="supervisor",
    )

    # Relations : un enseignant/utilisateur peut être membre de jury
    defenses_as_jury = relationship(
        "Defense",
        secondary="defense_jury",
        back_populates="jury_members",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"
