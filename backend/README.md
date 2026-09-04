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
├── app/                  # FastAPI Application core
│   ├── core/             # Security, configuration, dependencies, and enums
│   ├── db/               # Database session setup and Base class definitions
│   ├── google_genai/     # Gemini client manager and prompt templates
│   ├── modules/          # Business modules (user, company, consultant, job, consultee_profile)
│   └── utils/            # Validators, embeddings generator, and common helpers
├── agents/               # LangGraph Orchestration & Tools
│   ├── hybrid_rag/       # Vector retrieval and BM25 indexing search
│   ├── subagents/        # Active subagents (market_analysis_agent)
│   ├── supervisor/       # Orchestrator, Graph definition, registry, and state management
│   └── tools/            # Custom agent actions and integrations
├── tests/                # Testing Suite (Unit, Integration, and Mock configurations)
├── database/             # Alembic migration configurations and versions
├── scripts/              # Startup scripts and database seed operations
├── pyproject.toml        # Ruff exclusions, Python version, dependencies, and metadata
├── Dockerfile            # Container production and staging builder stages
└── README.md             # Development environment docs and references
```

## API docs
Available in local/dev mode:
- `/docs`
- `/redoc`
- `/api/v1/openapi.json`

## Notes
- Entry point: `backend/app/main.py`
- Main router: `backend/app/modules/routers.py`
- Full platform also includes the sibling `celery_app/` workers and the frontend app.
