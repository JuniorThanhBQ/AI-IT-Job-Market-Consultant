# ADR-06: Decision on frontend, backend and multi-agent technology

## Status
Pending

## Context
Our IT job market consulting system requires parsing diverse, unstructured recruitment websites, processing sensitive user profiles, and executing complex semantic matching between them. Because this flow is highly sequential and relies on large language models (LLMs) and vector search, we need a high-performance, type-safe, and modular stack. The frontend must deliver a premium, fluid user experience; the backend must support async data pipelines and AI dependencies; the database must handle both relational data and vector embeddings; and the multi-agent system must support stateful, predictable coordination.

## Decision
Adopt the following idealized technology stack for the project:
1. **Frontend:** Next.js (TypeScript, React) styled with Shadcn UI and Tailwind CSS.
2. **Backend:** FastAPI (Python) managed by `uv` for workspace and dependency management.
3. **Database & Vector Search:** PostgreSQL with the `pgvector` extension for hybrid relational/semantic data storage.
4. **Multi-Agent Orchestration:** LangGraph (LangChain) for stateful, graph-based agent coordination.
5. **Data Crawling & Extraction:** Playwright and Crawl4AI for resilient browser scraping and HTML-to-Markdown cleaning.

## Rationale
1. **Stateful Graph Orchestration (LangGraph):** LangGraph allows building stateful multi-agent graphs with cycles, state sharing, and human-in-the-loop checks. This gives the coordinator agent precise control over task execution (HMAS) compared to linear frameworks.
2. **Unified Data Storage (PostgreSQL + pgvector):** Using `pgvector` allows storing relational schemas (users, jobs) and high-dimensional semantic embeddings (resumes, job listings) in a single database, eliminating the cost and complexity of a separate vector database.
3. **High Performance and Speed (FastAPI + uv):** FastAPI offers high-performance asynchronous routing and automatic OpenAPI schemas. `uv` is a blazing-fast Python package manager that reduces sync and CI/CD install times.
4. **Premium UX and SSR (Next.js + TypeScript):** Next.js App Router provides Server-Side Rendering (SSR) for fast initial loads, SEO performance, and type-safety via TypeScript.
5. **Resilient Data Extraction (Playwright + Crawl4AI):** Playwright executes headless browsers to easily crawl Single Page Applications (SPAs). Crawl4AI cleans raw web pages directly into LLM-ready markdown formats, reducing prompt token usage.

## Consequences
### Positive
* **Unified Database Infrastructure:** Storing relational tables and vector embeddings in PostgreSQL simplifies backups, migrations (Alembic), and local docker-compose configurations.
* **Deterministic Agent Flows:** LangGraph ensures the supervisor agent retains strict control over sub-agent execution paths, preventing infinite loops or hallucinated task calls.
* **High Type-Safety and Autocomplete:** End-to-end type-safety (TypeScript on frontend, Pydantic on backend) minimizes runtime errors and accelerates coding.
* **Rapid Build Pipelines:** `uv` reduces Docker build times and GitHub Actions package installation phases to seconds.

### Negative
* **Steep Graph Learning Curve:** Designing stateful nodes, edges, channels, and conditional transitions in LangGraph requires more advanced coding skills than simple linear pipelines.
* **Complex Database Configuration:** Setting up PostgreSQL with `pgvector` locally requires custom Docker files and migration scripts to register vector types.
* **Upfront Configuration Overhead:** Implementing standalone Next.js outputs, FastAPI structures, and agent states requires more initial configuration before functional code runs.

## Decision Date
Pending Approved until 26/07/2026
