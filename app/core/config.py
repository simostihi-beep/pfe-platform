from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================================================
    # Métadonnées Application
    # ==========================================================================
    PROJECT_NAME: str = "Plateforme de Gestion des Projets PFE"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_PORT: int = 8000

    # ==========================================================================
    # Base de données PostgreSQL
    # ==========================================================================
    POSTGRES_USER: str = "pfe_user"
    POSTGRES_PASSWORD: str = "pfe_password"
    POSTGRES_DB: str = "pfe_db"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str = "postgresql://pfe_user:pfe_password@localhost:5432/pfe_db"

    # ==========================================================================
    # Sécurité & Authentification JWT
    # ==========================================================================
    SECRET_KEY: str = "default_insecure_key_please_change_in_production_32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ==========================================================================
    # CORS
    # ==========================================================================
    ALLOWED_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Singleton réutilisable dans toute l'application
settings = Settings()
