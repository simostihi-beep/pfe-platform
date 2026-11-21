.PHONY: help install dev lint format test coverage clean

help:
	@echo "Commandes disponibles :"
	@echo "  make install    - Installe les dépendances du projet"
	@echo "  make dev        - Lance le serveur de développement FastAPI"
	@echo "  make lint       - Vérifie le style du code (Ruff + Black)"
	@echo "  make format     - Reformate le code automatiquement"
	@echo "  make test       - Exécute les tests unitaires et d'intégration"
	@echo "  make coverage   - Exécute les tests avec rapport de couverture"
	@echo "  make clean      - Nettoie les fichiers de cache Python"

install:
	pip install -r requirements.txt -r requirements-dev.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

lint:
	ruff check .
	black --check .

format:
	ruff check --fix .
	black .

test:
	pytest

coverage:
	pytest --cov=app --cov-report=term-missing --cov-report=xml --cov-fail-under=60

clean:
	rm -rf .pytest_cache .coverage coverage.xml
	find . -type d -name __pycache__ -exec rm -rf {} +
