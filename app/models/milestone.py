"""Modèle SQLAlchemy représentant un jalon d'avancement d'un PFE."""

from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(255), nullable=False)
    due_date = Column(Date, nullable=True)
    progress = Column(Integer, default=0, nullable=False)  # 0 à 100 %
    comment = Column(Text, nullable=True)

    # Relation vers le projet parent
    project = relationship("Project", back_populates="milestones")

    def __repr__(self) -> str:
        return f"<Milestone id={self.id} project_id={self.project_id} progress={self.progress}%>"
