.PHONY: help dev-backend dev-frontend db-migrate db-migration db-migrate-docker db-migration-docker install dev-app-build dev-app-down prod-app-build lint docker-lint test app-check pre-commit-check generate-secret clean full-clean
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make dev-backend          - Run backend development local"
	@echo "  make dev-frontend         - Run frontend development local"
	@echo "  make db-migrate           - Run database migrations locally"
	@echo "  make db-migration         - Generate a new database migration locally (requires MSG=\"...\")"
	@echo "  make db-migrate-docker    - Run database migrations in docker backend container"
	@echo "  make db-migration-docker  - Generate a new database migration in docker backend container (requires MSG=\"...\")"
	@echo "  make install              - Install dependencies for both backend and frontend"
	@echo "  make dev-app-build        - Build docker in development mode"
	@echo "  make dev-app-down         - Down all Docker containers in development mode (warning: includes volumes)."
	@echo "  make prod-app-build       - Build docker in production mode"
	@echo "  make lint                 - Run all linters (ruff, mypy, typos, eslint, hadolint)"
	@echo "  make docker-lint          - Lint Dockerfiles using hadolint"
	@echo "  make app-check            - Including lint tests for the frontend and backend"
	@echo "  make pre-commit-check     - Run pre-commit hooks on all files"
	@echo "  make generate-secret      - Generate a secure random SECRET_KEY for FastAPI"
	@echo "  make clean                - Cleaning unused temporary files (not include node_modules and .venv)"
	@echo "  make full-clean           - Cleaning almost all unused temporary files"

install:
	uv sync --all-packages
	cd frontend && npm install

dev-backend:
	uv run --project backend fastapi dev backend/app/main.py

dev-frontend:
	npm --prefix frontend run dev

db-migrate:
	uv run --project backend alembic -c database/alembic.ini upgrade head

db-migration:
	uv run --project backend alembic -c database/alembic.ini revision --autogenerate -m "$(MSG)"

db-migrate-docker:
	docker compose exec backend alembic -c database/alembic.ini upgrade head

db-migration-docker:
	docker compose exec backend alembic -c database/alembic.ini revision --autogenerate -m "$(MSG)"

dev-app-build:
	docker compose up -d --build

dev-app-down:
	docker compose down -v

prod-app-build:
	docker compose -f docker-compose.prod.yml up -d --build

prod-app-build-remove:
	docker compose -f docker-compose.prod.yml down -v

docker-lint:
	docker run --rm -i hadolint/hadolint < backend/Dockerfile
	docker run --rm -i hadolint/hadolint < frontend/Dockerfile
	docker run --rm -i hadolint/hadolint < agents/Dockerfile

lint:
	uv run --project backend ruff check backend agents
	uv run --project backend mypy backend/app
	uv run --project backend typos
	npm --prefix frontend run lint
	docker run --rm -i hadolint/hadolint < backend/Dockerfile
	docker run --rm -i hadolint/hadolint < frontend/Dockerfile
	docker run --rm -i hadolint/hadolint < agents/Dockerfile

test:
	uv run --project backend pytest --cov=app --cov-report=term-missing
	npm --prefix frontend run test:e2e

app-check: lint test

pre-commit-check:
	uv run pre-commit run --all-files

generate-secret:
	uv run python scripts/generate_secret_key.py

clean:
	python scripts/clean_temporary_files.py

full-clean:
	python scripts/clean_temporary_files.py --dist
