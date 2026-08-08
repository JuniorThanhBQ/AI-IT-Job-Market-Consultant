.PHONY: app-check backup-restore backup-restore-docker clean coverage-xml db-migrate db-migrate-docker db-migration db-migration-docker dev-app-build dev-app-down dev-backend dev-frontend docker-lint generate-secret help install lint pre-commit-autoupdate pre-commit-check prod-app-build prod-app-down radon-check run-crawlfourai-celery run-crawler-celery run-crawler-update test
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make clean                      - Cleaning unused files (requires CLEAN_TYPE=\"...\" like --dist --dry-run )"
	@echo "  make generate-secret            - Generate a secure random SECRET_KEY for FastAPI"
	@echo "  make help                       - Show this help message"
	@echo "  make install                    - Install dependencies for both backend and frontend"
	@echo "  make dev-backend                - Run backend development local"
	@echo "  make dev-frontend               - Run frontend development local"
	@echo "  make dev-app-build              - Build docker in development mode"
	@echo "  make dev-app-down               - Down all Docker containers in development mode (warning: includes volumes)"
	@echo "  make prod-app-build             - Build docker in production mode"
	@echo "  make prod-app-down              - Down all Docker containers in production mode (warning: includes volumes)"
	@echo "  make db-migrate                 - Run database migrations locally"
	@echo "  make db-migrate-docker          - Run database migrations in docker backend container"
	@echo "  make db-migration               - Generate a new database migration locally (requires MSG=\"...\")"
	@echo "  make db-migration-docker        - Generate a new database migration in backend container (requires MSG=\"...\")"
	@echo "  make backup-restore             - Run backup restore locally (requires CMD=[list|backup|restore|restore-override])"
	@echo "  make backup-restore-docker      - Run backup restore Docker (requires CMD=[list|backup|restore|restore-override])"
	@echo "  make run-crawlfourai-celery     - Run Celery crawl4ai task manually in Docker container"
	@echo "  make run-crawler-celery         - Run Celery adaptive crawler task manually in Docker container"
	@echo "  make run-crawler-update         - Run Celery jobs update task manually in Docker container"
	@echo "  make app-check                  - Including lint tests for the frontend and backend"
	@echo "  make docker-lint                - Lint Dockerfiles using hadolint"
	@echo "  make lint                       - Run all linters (ruff, mypy, typos, eslint, hadolint)"
	@echo "  make pre-commit-check           - Run pre-commit hooks on all files"
	@echo "  make pre-commit-autoupdate      - Auto-update pre-commit hook versions"
	@echo "  make radon-check                - Run radon complexity and maintainability index checks"
	@echo "  make coverage-xml               - Generate XML coverage report"
	@echo "  make test                       - Run tests"

clean:
	python scripts/clean_temporary_files.py ${CLEAN_TYPE}

generate-secret:
	uv run python scripts/generate_secret_key.py

install:
	uv sync --all-packages
	cd frontend && npm install

dev-backend:
	uv run --project backend fastapi dev backend/app/main.py

dev-frontend:
	npm --prefix frontend run dev

dev-app-build:
	docker compose up -d --build

dev-app-down:
	docker compose down -v

prod-app-build:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build

prod-app-down:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down -v

db-migrate:
	uv run --project backend alembic -c database/alembic.ini upgrade head

db-migrate-docker:
	docker compose exec backend alembic -c database/alembic.ini upgrade head

db-migration:
	uv run --project backend alembic -c database/alembic.ini revision --autogenerate -m "$(MSG)"

db-migration-docker:
	docker compose exec backend alembic -c database/alembic.ini revision --autogenerate -m "$(MSG)"

backup-restore:
	uv run --project backend python celery/scripts/backup_restore_runner.py "$(CMD)"

backup-restore-docker:
	docker compose exec celery-worker-default python celery/scripts/backup_restore_runner.py "$(CMD)"

run-crawlfourai-celery:
	docker compose exec celery-worker-default celery -A celery_app call celery_app.run_crawl4ai_task

run-crawler-celery:
	docker compose exec celery-worker-default celery -A celery_app call celery_app.run_crawler_task

run-crawler-update:
	docker compose exec celery-worker-default celery -A celery_app call celery_app.run_jobs_update_task

app-check: lint test

docker-lint:
	docker run --rm -i hadolint/hadolint < backend/Dockerfile
	docker run --rm -i hadolint/hadolint < frontend/Dockerfile
	docker run --rm -i hadolint/hadolint < celery/Dockerfile

lint:
	uv run --project backend ruff check backend celery
	uv run --project backend mypy backend/app celery
	uv run --project backend typos
	uv run --project backend pylint --rcfile=backend/pyproject.toml backend celery/tools celery/scripts
	npm --prefix frontend run lint
	docker run --rm -i hadolint/hadolint < backend/Dockerfile
	docker run --rm -i hadolint/hadolint < frontend/Dockerfile
	docker run --rm -i hadolint/hadolint < celery/Dockerfile

pre-commit-check:
	uv run pre-commit run --all-files

pre-commit-autoupdate:
	uv run pre-commit autoupdate

radon-check:
	uv run --project backend radon cc backend celery
	uv run --project backend radon mi backend celery

coverage-xml:
	uv run --project backend pytest --cov=app --cov-report=xml:coverage.xml

test:
	uv run --project backend bandit -c backend/pyproject.toml -r backend celery -ll
	uv run --project backend pytest --cov=app --cov-report=term-missing
	uv run --project backend pytest celery/tests/adaptive_crawler --cov=celery/tools/adaptive_crawler --cov-report=term-missing
	npm --prefix frontend audit --audit-level=critical
	npm --prefix frontend run test:e2e
