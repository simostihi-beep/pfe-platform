"""Fixtures pytest pour l'ensemble des tests applicatifs et d'intégration."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.security import create_access_token, get_password_hash
from app.main import app
from app.models.user import User, UserRole

# Utilisation d'une base SQLite en mémoire avec StaticPool pour les tests rapides et isolés
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Initialise le schéma de base de données pour les tests."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Fournit une session de base de données rollbackée après chaque test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """Client de test FastAPI avec injection de la session de test."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def test_student(db_session) -> User:
    """Fixture créant un étudiant de test."""
    user = User(
        email="student@ensa-fes.ma",
        password_hash=get_password_hash("password123"),
        full_name="Étudiant Test",
        role=UserRole.STUDENT,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_supervisor(db_session) -> User:
    """Fixture créant un enseignant encadrant de test."""
    user = User(
        email="supervisor@ensa-fes.ma",
        password_hash=get_password_hash("password123"),
        full_name="Encadrant Test",
        role=UserRole.SUPERVISOR,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session) -> User:
    """Fixture créant un administrateur de test."""
    user = User(
        email="admin@ensa-fes.ma",
        password_hash=get_password_hash("password123"),
        full_name="Admin Test",
        role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def student_auth_headers(test_student) -> dict[str, str]:
    """Headers d'authentification pour l'étudiant."""
    token = create_access_token(subject=test_student.id, role=test_student.role.value)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def supervisor_auth_headers(test_supervisor) -> dict[str, str]:
    """Headers d'authentification pour l'enseignant encadrant."""
    token = create_access_token(
        subject=test_supervisor.id, role=test_supervisor.role.value
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_auth_headers(test_admin) -> dict[str, str]:
    """Headers d'authentification pour l'admin."""
    token = create_access_token(subject=test_admin.id, role=test_admin.role.value)
    return {"Authorization": f"Bearer {token}"}
