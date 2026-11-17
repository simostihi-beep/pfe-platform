"""Configuration de la connexion PostgreSQL et session SQLAlchemy."""
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# Création du moteur SQLAlchemy
# pool_pre_ping=True vérifie la santé de la connexion avant chaque requête
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Fabrique de sessions de base de données
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Classe de base déclarative pour tous les modèles ORM
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """Dépendance FastAPI injectant une session de base de données par requête."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
