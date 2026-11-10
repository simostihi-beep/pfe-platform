# Plateforme de Gestion des Projets PFE avec CI/CD et Monitoring

Projet académique réalisé dans le cadre du module **DevOps et Conteneurisation** – **ENSA Fès, Génie Informatique**.

---

## 🛠️ Stack Technique
- **Backend :** FastAPI, SQLAlchemy, Alembic, Pydantic
- **Base de données :** PostgreSQL 16
- **Conteneurisation :** Docker (Multi-stage, non-root), Docker Compose
- **CI/CD :** GitHub Actions, GitHub Container Registry (GHCR)
- **Qualité & Sécurité :** Ruff, Black, Pytest, Coverage, Bandit, pip-audit, Trivy
- **Observabilité :** Prometheus, Grafana, Alertmanager, Loki, Promtail, cAdvisor, Node Exporter

---

## 🌿 Stratégie Git & Workflow
- **`main`** : Branche de production, protégée (déploiement / tags de version).
- **`develop`** : Branche principale d'intégration, protégée.
- **`feature/<issue>-<nom>`** : Branches dérivées de `develop` pour chaque fonctionnalité.
- **Commits :** Respect strict de la convention **Conventional Commits** (`feat:`, `fix:`, `ci:`, `docs:`, `chore:`).

---

## 🚀 Démarrage Rapide (Environnement local)

### 1. Prérequis
- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- Python 3.12+ (optionnel si exécution via Docker)
- Git

### 2. Cloner le projet
```bash
git clone <URL_DU_DEPOT>
cd pfe-platform
```

### 3. Configurer l'environnement
Copiez le fichier d'exemple pour initialiser vos variables locales :
```bash
cp .env.example .env
```

### 4. Lancer la stack avec Docker Compose
```bash
docker compose up -d --build
```

- **Application Web / API :** [http://localhost:8000](http://localhost:8000)
- **Documentation OpenAPI :** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Healthcheck :** [http://localhost:8000/health](http://localhost:8000/health)
