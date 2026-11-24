from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================================================================
    # Métadonnées Application
    # ==========================================================================
    PROJECT_NAME: str = "Plateforme de Gestion des Projets PFE"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    APP_PORT: int = 8000

    # ==========================================================================
    # Base de données PostgreSQL
    # ==========================================================================
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    DATABASE_URL: str

    # ==========================================================================
    # Sécurité & Authentification JWT
    # ==========================================================================
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

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
