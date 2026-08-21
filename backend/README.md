# AIJMC Backend

FastAPI backend for the AI IT Job Market Consultant platform.

## Stack
- FastAPI + SQLModel + Pydantic
- PostgreSQL + pgvector
- Alembic migrations
- JWT auth, admin UI, BM25/semantic retrieval
- Google GenAI + agent orchestration
- uv for package management

## Structure
```text
backend/
├── app/          # API, config, modules, DB, templates
├── agents/       # supervisor/subagents/hybrid_rag tooling
├── tests/        # backend tests
├── database/     # migration config
├── scripts/      # startup helpers
├── pyproject.toml
├── Dockerfile
└── README.md
```

## API docs
Available in local/dev mode:
- `/docs`
- `/redoc`
- `/api/v1/openapi.json`

## Notes
- Entry point: `backend/app/main.py`
- Main router: `backend/app/modules/routers.py`
- Full platform also includes the sibling `celery/` workers and the frontend app.
