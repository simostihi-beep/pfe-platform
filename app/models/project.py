"""Modèle SQLAlchemy représentant un projet PFE."""
import enum
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class ProjectStatus(str, enum.Enum):
    """Workflow de validation d'un sujet PFE (Section 1.2)."""
    DRAFT = "draft"          # Brouillon
    SUBMITTED = "submitted"  # Soumis pour examen
    VALIDATED = "validated"  # Validé par l'encadrant
    REJECTED = "rejected"    # Refusé avec motif/commentaire


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    company = Column(String(255), nullable=True)
    status = Column(
        Enum(ProjectStatus, name="project_status", create_type=False),
        default=ProjectStatus.DRAFT,
        nullable=False,
    )
    student_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    supervisor_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relations
    student = relationship(
        "User",
        foreign_keys=[student_id],
        back_populates="student_projects",
    )
    supervisor = relationship(
        "User",
        foreign_keys=[supervisor_id],
        back_populates="supervised_projects",
    )
    milestones = relationship(
        "Milestone",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Milestone.due_date",
    )
    defense = relationship(
        "Defense",
        back_populates="project",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} title={self.title} status={self.status}>"
