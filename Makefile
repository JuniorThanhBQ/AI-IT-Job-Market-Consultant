.PHONY: app-check backup-restore backup-restore-docker clean cloud-server-down cloud-server-run coverage-xml db-migrate db-migrate-docker db-migration db-migration-docker dev-app-build dev-app-down dev-backend dev-frontend docker-init-admin docker-lint export-fastapi-openapi generate-secret help init-admin install lint local-server-down local-server-run pre-commit-autoupdate pre-commit-check prod-app-build prod-app-down radon-check remake-rclone-config run-crawlfourai-celery run-crawler-celery run-crawler-update test test-backend test-celery test-frontend test-report
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make help                       - Show the list of supported commands"
	@echo "  make clean                      - Cleaning unused files (optional CLEAN_TYPE=\"...\" like --dist --dry-run )"
	@echo "  make generate-secret            - Generate a secure random SECRET_KEY"
	@echo "  make print-openapi-docs         - Export FastAPI Swagger OpenAPI JSON spec (optional NAME=\"...\")"
	@echo "  make init-admin                 - Create initial superuser admin account locally"
	@echo "  make docker-init-admin          - Create initial superuser admin account in backend container"
	@echo "  make install                    - Install dependencies for both backend and frontend"
	@echo "  make dev-backend                - Run backend development local"
	@echo "  make dev-frontend               - Run frontend development local"
	@echo "  make dev-app-build              - Build docker in development mode (Optionally specify CONTAINERS=\"...\")"
	@echo "  make dev-app-down               - Down Docker containers in development mode (warning: includes volumes)"
	@echo "  make prod-app-build             - Build docker in production mode (Optionally specify CONTAINERS=\"...\")"
	@echo "  make prod-app-down              - Down all Docker containers in production mode (warning: includes volumes)"
	@echo "  make local-server-run           - Run local server production with Ngrok"
	@echo "  make local-server-down          - Down local server containers (warning: includes volumes)"
	@echo "  make cloud-server-run           - Run cloud crawler services with Supabase"
	@echo "  make cloud-server-down          - Down cloud crawler containers (warning: includes volumes)"
	@echo "  make db-migrate                 - Run database migrations locally"
	@echo "  make db-migrate-docker          - Run database migrations in docker backend container"
	@echo "  make db-migration               - Generate a new database migration locally (requires MSG=\"...\")"
	@echo "  make db-migration-docker        - Generate a new database migration in backend container (requires MSG=\"...\")"
	@echo "  make backup-restore             - Run backup restore locally (requires CMD=[list|backup|restore|restore-override])"
	@echo "  make backup-restore-docker      - Run backup restore Docker (requires CMD=[list|backup|restore|restore-override])"
	@echo "  make remake-rclone-config       - Regenerate or sync rclone.conf from local system to celery_app"
	@echo "  make run-crawler-celery         - Run Celery adaptive crawler task manually in Docker container"
	@echo "  make run-crawler-update         - Run Celery jobs update task manually in Docker container"
	@echo "  make run-crawlfourai-celery     - Run Celery crawl4ai task manually in Docker container"
	@echo "  make app-check                  - Including lint tests for the frontend and backend"
	@echo "  make lint                       - Run all linters (ruff, mypy, typos, eslint, hadolint)"
	@echo "  make docker-lint                - Lint Dockerfiles using hadolint"
	@echo "  make pre-commit-check           - Run pre-commit hooks on all files"
	@echo "  make pre-commit-autoupdate      - Auto-update pre-commit hook versions"
	@echo "  make radon-check                - Run radon complexity and maintainability index checks"
	@echo "  make test                       - Run all tests (bandit, backend, celery, frontend)"
	@echo "  make test-backend               - Run backend unit and integration tests"
	@echo "  make test-celery                - Run celery unit and integration tests"
	@echo "  make test-frontend              - Run frontend audit and e2e tests"
	@echo "  make test-report                - Scan test-case-report.xlsx and report failures as GitHub issues"
	@echo "  make coverage-xml               - Generate XML coverage report"

clean:
	python scripts/clean_temporary_files.py ${CLEAN_TYPE}

generate-secret:
	uv run python scripts/generate_secret_key.py

print-openapi-docs:
	uv run --project backend python scripts/generate_openapi.py $(if $(NAME),--name "$(NAME)",)

install:
	uv sync --all-packages
	cd frontend && npm install

dev-backend:
	uv run --project backend fastapi dev backend/app/main.py

dev-frontend:
	npm --prefix frontend run dev

dev-app-build:
	docker compose up -d --build $(CONTAINERS)

dev-app-down:
	docker compose down -v $(CONTAINERS)

prod-app-build:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build $(CONTAINERS)

prod-app-down:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml down -v $(CONTAINERS)

local-server-run:
	docker compose --project-directory server -f server/docker-compose.local.yml -f server/docker-compose.prod.yml up -d --build $(CONTAINERS)

local-server-down:
	docker compose --project-directory server -f server/docker-compose.local.yml -f server/docker-compose.prod.yml down -v $(CONTAINERS)

cloud-server-run:
	docker compose --project-directory server -f server/cloud/docker-compose.yml up -d --build $(CONTAINERS)

cloud-server-down:
	docker compose --project-directory server -f server/cloud/docker-compose.yml down -v $(CONTAINERS)

db-migrate:
	uv run --project backend alembic -c database/alembic.ini upgrade head

db-migrate-docker:
	docker compose exec backend alembic -c database/alembic.ini upgrade head

db-migration:
	uv run --project backend alembic -c database/alembic.ini revision --autogenerate -m "$(MSG)"

db-migration-docker:
	docker compose exec backend alembic -c database/alembic.ini revision --autogenerate -m "$(MSG)"

init-admin:
	uv run --project backend python -c "from app.core.auth import create_admin_account; create_admin_account()"

docker-init-admin:
	docker compose exec backend python -c "from app.core.auth import create_admin_account; create_admin_account()"

backup-restore:
	uv run --project backend python celery_app/scripts/backup_restore_runner.py "$(CMD)"

backup-restore-docker:
	docker compose exec celery-worker-default python celery_app/scripts/backup_restore_runner.py "$(CMD)"

remake-rclone-config:
	uv run python scripts/remake_rclone_config.py

run-crawler-celery:
	docker compose exec celery-worker-crawler celery -A celery_app call celery_app.run_crawler_task

run-crawler-update:
	docker compose exec celery-worker-default celery -A celery_app call celery_app.run_jobs_update_task

run-crawlfourai-celery:
	docker compose exec celery-worker-crawler celery -A celery_app call celery_app.run_crawl4ai_task

app-check: lint test

docker-lint:
	docker run --rm -i hadolint/hadolint < backend/Dockerfile
	docker run --rm -i hadolint/hadolint < frontend/Dockerfile
	docker run --rm -i hadolint/hadolint < celery_app/Dockerfile

lint: docker-lint
	uv run --project backend ruff check --config backend/pyproject.toml backend celery_app
	uv run --project backend mypy backend/app celery_app
	uv run --project backend typos
	uv run --project backend pylint --rcfile=backend/pyproject.toml backend celery_app/tools celery_app/scripts celery_app/utils
	npm --prefix frontend run lint

pre-commit-check:
	uv run pre-commit run --all-files

pre-commit-autoupdate:
	uv run pre-commit autoupdate --freeze

radon-check:
	uv run --project backend radon cc backend celery_app
	uv run --project backend radon mi backend celery_app

test: test-backend test-celery test-frontend

test-backend:
	uv run --project backend bandit -c backend/pyproject.toml -r backend celery_app -ll
	uv run --project backend pytest backend/tests --cov=app --cov-report=term-missing

test-celery:
	uv run --project backend pytest celery_app/tests --cov=celery_app/tools/backup_tool --cov=celery_app/tools/crawl4ai_crawler --cov=celery_app/tools/crawler_update_tool --cov=celery_app/tools/email_report_tool --cov-report=term-missing

test-frontend:
	npm --prefix frontend audit --audit-level=critical
	npm --prefix frontend run test:e2e

test-report:
	uv run python scripts/test_case_report.py

coverage-xml:
	uv run --project backend pytest --cov=app --cov-report=xml:coverage.xml
