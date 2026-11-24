"""Tests du module d'authentification (register, login, me)."""

from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient):
    response = client.post(
        "/auth/register",
        json={
            "email": "newstudent@ensa-fes.ma",
            "full_name": "Nouvel Étudiant",
            "password": "password123",
            "role": "student",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newstudent@ensa-fes.ma"
    assert data["role"] == "student"
    assert "id" in data


def test_register_duplicate_email_fails(client: TestClient, test_student):
    response = client.post(
        "/auth/register",
        json={
            "email": test_student.email,
            "full_name": "Doublon",
            "password": "password123",
            "role": "student",
        },
    )
    assert response.status_code == 400
    assert "existe déjà" in response.json()["detail"]


def test_login_success(client: TestClient, test_student):
    response = client.post(
        "/auth/login",
        json={"email": test_student.email, "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password_fails(client: TestClient, test_student):
    response = client.post(
        "/auth/login",
        json={"email": test_student.email, "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_get_current_user_profile(
    client: TestClient, student_auth_headers, test_student
):
    response = client.get("/auth/me", headers=student_auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_student.id
    assert data["email"] == test_student.email
