"""Utilitaires de hachage de mots de passe et de gestion des JWT."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union
from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings

# Configuration du contexte de hachage de mots de passe (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si un mot de passe en clair correspond au hash stocké."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hache un mot de passe avec l'algorithme bcrypt."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    role: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Génère un token JWT signé contenant l'ID ou l'email utilisateur et son rôle."""
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": str(subject),
        "role": role,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Décode et valide un token JWT. Renvoie le payload ou None si invalide."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
