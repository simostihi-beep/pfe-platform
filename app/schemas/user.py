"""Schémas Pydantic pour la gestion des utilisateurs."""
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    role: UserRole = UserRole.STUDENT


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=255)
    email: EmailStr | None = None
    role: UserRole | None = None


class UserResponse(UserBase):
    id: int
    created_at: datetime

    # Permet à Pydantic de lire directement les objets SQLAlchemy
    model_config = ConfigDict(from_attributes=True)
