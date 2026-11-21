"""Tests du workflow et CRUD des projets PFE (US1, US2, US3)."""

from fastapi.testclient import TestClient


def test_student_can_create_project(client: TestClient, student_auth_headers):
    payload = {
        "title": "Système de Télémédecine avec Vision par Ordinateur",
        "description": "Développement d'une solution complète d'analyse médicale en temps réel avec IA et FastAPI.",
        "company": "Centre Hospitalier",
    }
    response = client.post("/projects", json=payload, headers=student_auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["status"] == "draft"
    assert data["student_id"] is not None


def test_supervisor_cannot_create_project(client: TestClient, supervisor_auth_headers):
    payload = {
        "title": "Projet créé par encadrant non autorisé",
        "description": "Description valide pour le test de restriction des rôles sur la création.",
    }
    response = client.post("/projects", json=payload, headers=supervisor_auth_headers)
    assert response.status_code == 403


def test_student_can_submit_project(client: TestClient, student_auth_headers):
    # 1. Création en brouillon
    create_res = client.post(
        "/projects",
        json={
            "title": "Plateforme DevOps Automatisée pour PFE",
            "description": "Automatisation complète du déploiement avec Prometheus, Grafana, Docker et CI/CD.",
        },
        headers=student_auth_headers,
    )
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # 2. Soumission du projet
    submit_res = client.patch(
        f"/projects/{project_id}/status",
        json={"status": "submitted"},
        headers=student_auth_headers,
    )
    assert submit_res.status_code == 200
    assert submit_res.json()["status"] == "submitted"


def test_student_cannot_validate_own_project(client: TestClient, student_auth_headers):
    # Création et soumission
    create_res = client.post(
        "/projects",
        json={
            "title": "Tentative de fraude de statut étudiant",
            "description": "Description valide pour le test d'escalade de privilèges sur le statut.",
        },
        headers=student_auth_headers,
    )
    project_id = create_res.json()["id"]

    client.patch(
        f"/projects/{project_id}/status",
        json={"status": "submitted"},
        headers=student_auth_headers,
    )

    # L'étudiant essaie de s'auto-valider
    val_res = client.patch(
        f"/projects/{project_id}/status",
        json={"status": "validated"},
        headers=student_auth_headers,
    )
    assert val_res.status_code == 403


def test_supervisor_can_validate_submitted_project(
    client: TestClient, student_auth_headers, supervisor_auth_headers
):
    # Création et soumission
    create_res = client.post(
        "/projects",
        json={
            "title": "Projet PFE Valide pour Test Encadrant",
            "description": "Description valide détaillée pour le workflow complet d'approbation.",
        },
        headers=student_auth_headers,
    )
    project_id = create_res.json()["id"]

    client.patch(
        f"/projects/{project_id}/status",
        json={"status": "submitted"},
        headers=student_auth_headers,
    )

    # Validation par l'encadrant
    val_res = client.patch(
        f"/projects/{project_id}/status",
        json={"status": "validated", "comment": "Excellent sujet, validé"},
        headers=supervisor_auth_headers,
    )
    assert val_res.status_code == 200
    assert val_res.json()["status"] == "validated"
    assert val_res.json()["supervisor_id"] is not None


def test_supervisor_can_reject_submitted_project(
    client: TestClient, student_auth_headers, supervisor_auth_headers
):
    create_res = client.post(
        "/projects",
        json={
            "title": "Projet à rejeter pour sujet incomplet",
            "description": "Description valide pour tester le rejet avec motif obligatoire.",
        },
        headers=student_auth_headers,
    )
    project_id = create_res.json()["id"]

    client.patch(
        f"/projects/{project_id}/status",
        json={"status": "submitted"},
        headers=student_auth_headers,
    )

    # Rejet sans commentaire -> Doit échouer (400)
    rej_fail = client.patch(
        f"/projects/{project_id}/status",
        json={"status": "rejected"},
        headers=supervisor_auth_headers,
    )
    assert rej_fail.status_code == 400

    # Rejet avec commentaire -> Doit réussir
    rej_ok = client.patch(
        f"/projects/{project_id}/status",
        json={"status": "rejected", "comment": "Périmètre trop flou, à reformuler"},
        headers=supervisor_auth_headers,
    )
    assert rej_ok.status_code == 200
    assert rej_ok.json()["status"] == "rejected"


def test_admin_can_assign_supervisor(
    client: TestClient, student_auth_headers, admin_auth_headers, test_supervisor
):
    create_res = client.post(
        "/projects",
        json={
            "title": "Projet pour affectation administrative",
            "description": "Description valide pour l'affectation par l'administrateur.",
        },
        headers=student_auth_headers,
    )
    project_id = create_res.json()["id"]

    assign_res = client.post(
        f"/projects/{project_id}/assign-supervisor",
        json={"supervisor_id": test_supervisor.id},
        headers=admin_auth_headers,
    )
    assert assign_res.status_code == 200
    assert assign_res.json()["supervisor_id"] == test_supervisor.id


def test_web_routes_render_html(client: TestClient):
    res_list = client.get("/web/projects")
    assert res_list.status_code == 200
    assert "Catalogue des Sujets PFE" in res_list.text

    res_new = client.get("/web/projects/new")
    assert res_new.status_code == 200
    assert "Déposer un Sujet de PFE" in res_new.text
