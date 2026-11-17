"""Modèles SQLAlchemy pour la gestion des soutenances et des jurys."""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.core.database import Base

# Table d'association Many-to-Many entre Soutenances et Enseignants/Jurys
defense_jury = Table(
    "defense_jury",
    Base.metadata,
    Column(
        "defense_id",
        Integer,
        ForeignKey("defenses.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Defense(Base):
    __tablename__ = "defenses"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    date_time = Column(DateTime(timezone=True), nullable=False)
    room = Column(String(100), nullable=False)

    # Relations
    project = relationship("Project", back_populates="defense")
    jury_members = relationship(
        "User",
        secondary=defense_jury,
        back_populates="defenses_as_jury",
    )

    def __repr__(self) -> str:
        return f"<Defense id={self.id} project_id={self.project_id} room={self.room}>"
