.PHONY: help dev-backend dev-frontend db-migrate db-migration install dev-app-build dev-app-down prod-app-build lint test app-check clean full-clean
.DEFAULT_GOAL := help

help:
	@echo "Available commands:"
	@echo "  make dev-backend   - Run backend development server"
	@echo "  make dev-frontend  - Run frontend development server"
	@echo "  make db-migrate    - Run database migrations"
	@echo "  make db-migration  - Generate a new database migration (requires MSG=\"...\")"
	@echo "  make install       - Install dependencies for both backend and frontend"
	@echo "  make dev-app-build - Build docker in development mode"
	@echo "  make dev-app-down  -  Down all Docker containers in development mode (warning: includes volumes)."
	@echo "  make prod-app-build - Build docker in production mode"
	@echo "  make app-check 	- Including lint tests for the frontend and backend"
	@echo "  make clean         - Cleaning unused temporary files (not include node_modules and .venv)"
	@echo "  make full-clean    - Cleaning almost all unused temporary files"

install:
	uv sync --all-packages
	cd frontend && npm install

dev-backend:
	uv run --project backend fastapi dev backend/app/main.py

dev-frontend:
	npm --prefix frontend run dev

db-migrate:
	uv run --project backend alembic upgrade head

db-migration:
	uv run --project backend alembic revision --autogenerate -m "$(MSG)"

dev-app-build:
	docker compose up -d --build

dev-app-down:
	docker compose down -v

prod-app-build:
	docker compose -f docker-compose.prod.yml up -d --build

prod-app-build-remove:
	docker compose -f docker-compose.prod.yml down -v

lint:
	uv run --project backend ruff check .
	npm --prefix frontend run lint

test:
	uv run --project backend pytest
	npm --prefix frontend test

app-check: lint test

clean:
	python scripts/clean_temporary_files.py

full-clean:
	python scripts/clean_temporary_files.py --dist
