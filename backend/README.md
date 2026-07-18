# AI-IT-Job-Market-Consultant - Backend

This is the backend service for the **AI IT Job Market Consultant (AIJMC)** platform. It provides the REST API, database access, vector similarity search, and multi-agent execution orchestrators.

---

## I. Architectural Decisions & Tech Stack

Following the system's Architecture Decision Records (ADRs):
*   **Core Framework:** **FastAPI** (Python 3.14) providing high-performance, asynchronous REST API endpoints.
*   **Package Management:** **uv** workspace manager for speed, package locking (`uv.lock`), and virtual environment synchronization.
*   **Database:** **PostgreSQL** with the **pgvector** extension (ADR-06), enabling hybrid relational and vector database functionality.
*   **Package Structure:** Organized **by business feature module** (ADR-03) rather than technical layer alone. Inside each feature (e.g., jobs, consulting), the code is layered into:
    `routers/` ➡️ `services/` ➡️ `models/` (schemas/tables) ➡️ `crud/` (database interactions).

---

## II. Development Workflow

Ensure you have [uv](https://docs.astral.sh/uv/) installed.

### 1. Local Setup
Sync workspace packages and activate the virtual environment:
```console
# From the repository root or ./backend/
$ uv sync --locked
$ source .venv/bin/activate  # On Linux/macOS
$ .venv\Scripts\activate     # On Windows
```

Make sure your IDE/editor is configured to use the python interpreter located at `backend/.venv/bin/python`.

### 2. Database Migrations (Alembic)
Database tables are managed dynamically via SQLModel and Alembic migrations.

*   **Generate a new migration revision** after modifying models in `backend/app/models.py`:
    ```console
    $ docker compose exec backend alembic revision --autogenerate -m "Describe migration here"
    ```
*   **Apply migrations** to update the database schema:
    ```console
    $ docker compose exec backend alembic upgrade head
    ```

---

## III. Running Tests

Automated testing is configured with `pytest` and runs inside our CI/CD pipelines (ADR-04).

*   **Run all tests locally:**
    ```console
    # Sync environment and run pytest
    $ uv run --package backend pytest
    ```
*   **Run tests inside Docker containers:**
    ```console
    $ docker compose exec backend bash scripts/tests-start.sh
    ```
*   **Test Coverage:** Coverage files are generated automatically. Open `htmlcov/index.html` in your browser to inspect test coverage statistics.
