# AIJMC Backend Structure
AIJIMC's backend is built on the FastAPI web framework with a modular and layered functional organization. The API design follows a RESTful model, and migration management is handled by Alembic.

## API docs
The system's API documentation is available in two forms are docs or redoc. Access is only possible when the backend is running in local/dev mode:
- `/docs`
- `/redoc`
- `/api/v1/openapi.json`

## AI Agent and Hybrid Retrieval
The AI ​​Agent is based on the ReAct model developed on the LangChain framework. The LLM library used is the Google GenAI SDK, with the following main models:

1. Gemini-embedding-001: To serve as data embedding.
2. Gemini-flash-3.6: To serve as the LLM brain for the AI ​​Agent.
3. Gemini-flash-3.5: Backup when Gemini-flash-3.6 encounters error code 529 or 429.

For hybrid retrevia, the project uses the following three techniques:

1. Semantic search: Uses cosine similarity between the user input vector and the job posting vector.
2. Lexical search: Uses keywords in the user input to match job postings.
3. Reranking: Based on the Reciprocal Rank Fusion technique to select the best list of job postings from the two techniques above.

## Notes
- Entry point: `backend/app/main.py`
- Main router: `backend/app/modules/routers.py`
- The backend component that depends on the platform but can run independently is `celery_app/`.

## Backend structure
```text
backend/
├── Dockerfile
├── README.md
├── pyproject.toml
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── hybrid_rag/
│   │   ├── embeddings.py
│   │   └── retriever.py
│   ├── subagents/
│   │   ├── __init__.py
│   │   └── market_analysis_agent/
│   └── supervisor/
│       ├── __init__.py
│       ├── graph.py
│       ├── orchestrator.py
│       ├── registry.py
│       └── state.py
├── app/
│   ├── __init__.py
│   ├── admin.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── deps.py
│   │   ├── enums.py
│   │   ├── middlewares.py
│   │   └── security.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── base_model.py
│   ├── fixtures/
│   │   ├── __init__.py
│   │   └── initial_data.py
│   ├── genai/
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── routers.py
│   │   ├── company/
│   │   ├── consultant/
│   │   ├── consultee_profile/
│   │   ├── job/
│   │   ├── shared/
│   │   └── user/
│   ├── static/
│   │   ├── __init__.py
│   │   └── css/
│   ├── templates/
│   │   ├── __init__.py
│   │   └── index.html
│   └── utils/
│       ├── __init__.py
│       ├── embeddings.py
│       ├── job_utils.py
│       ├── utils.py
│       ├── utils_configs.py
│       └── validators.py
├── scripts/
│   └── start.sh
└── tests/
    ├── conftest.py
    ├── test_base.py
    ├── integration_test/
    └── unit_test/
```
