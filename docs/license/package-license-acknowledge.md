# Package and Dependency License Acknowledgment

This document provides a comprehensive inventory and license acknowledgment for all third-party dependencies, libraries, tools, and actions utilized across the AI-IT-Job-Market-Consultant (AIJMC) platform.

## 1. Root Utilities (`pyproject.toml`)

| Name | Purpose | License | Link |
| :--- | :--- | :--- | :--- |
| **httpx** | Next-generation HTTP client supporting HTTP/1.1 and HTTP/2 for asynchronous and synchronous network requests | BSD-3-Clause | [https://github.com/encode/httpx](https://github.com/encode/httpx) |
| **openpyxl** | Python library for reading and writing Excel 2010 xlsx/xlsm/xltx/xltm files | MIT | [https://openpyxl.readthedocs.io](https://openpyxl.readthedocs.io) |
| **pandas** | Data manipulation, analysis, and tabular data extraction for test reports and datasets | BSD-3-Clause | [https://pandas.pydata.org](https://pandas.pydata.org) |
| **python-dotenv** | Reads key-value pairs from `.env` files and sets them as environment variables | BSD-3-Clause | [https://github.com/theskumar/python-dotenv](https://github.com/theskumar/python-dotenv) |
| **pre-commit** | Framework for managing and maintaining multi-language pre-commit git hooks | MIT | [https://github.com/pre-commit/pre-commit](https://github.com/pre-commit/pre-commit) |

## 2. Backend  Production Dependencies (`backend/pyproject.toml`)

| Name | Purpose | License | Link |
| :--- | :--- | :--- | :--- |
| **fastapi[standard]** | High-performance, asynchronous web API framework with automatic OpenAPI documentation | MIT | [https://github.com/fastapi/fastapi](https://github.com/fastapi/fastapi) |
| **pydantic** | Data validation, settings management, and serialization using Python type annotations | MIT | [https://github.com/pydantic/pydantic](https://github.com/pydantic/pydantic) |
| **pydantic-settings** | Dedicated settings and secret environment configuration management for Pydantic v2 | MIT | [https://github.com/pydantic/pydantic-settings](https://github.com/pydantic/pydantic-settings) |
| **sqlmodel** | High-level library for interacting with SQL databases from Python code using Pydantic and SQLAlchemy | MIT | [https://github.com/fastapi/sqlmodel](https://github.com/fastapi/sqlmodel) |
| **alembic** | Database migration environment and schema management engine for SQLAlchemy | MIT | [https://github.com/sqlalchemy/alembic](https://github.com/sqlalchemy/alembic) |
| **psycopg[binary]** | Modern, high-performance PostgreSQL database adapter for Python | LGPL-3.0-or-later | [https://github.com/psycopg/psycopg](https://github.com/psycopg/psycopg) |
| **pgvector** | Vector similarity search extension driver for PostgreSQL | PostgreSQL | [https://github.com/pgvector/pgvector-python](https://github.com/pgvector/pgvector-python) |
| **google-genai** | Official Google GenAI SDK for interacting with Gemini multimodal generative AI models | Apache-2.0 | [https://github.com/googleapis/python-genai](https://github.com/googleapis/python-genai) |
| **langchain** | Building applications and agents with LLMs through composability and chains | MIT | [https://github.com/langchain-ai/langchain](https://github.com/langchain-ai/langchain) |
| **langgraph** | Multi-agent coordination, cyclical orchestration, and stateful graph workflows | MIT | [https://github.com/langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) |
| **pyjwt** | JSON Web Token (JWT) encode, decode, and cryptographic signature verification | MIT | [https://github.com/jpadilla/pyjwt](https://github.com/jpadilla/pyjwt) |
| **pwdlib[argon2,bcrypt]** | Secure password hashing library supporting modern Argon2 and Bcrypt algorithms | MIT | [https://github.com/frankie567/pwdlib](https://github.com/frankie567/pwdlib) |
| **sqladmin[full]** | Admin dashboard interface for SQLAlchemy and SQLModel models with authentication support | BSD-3-Clause | [https://github.com/aminalaee/sqladmin](https://github.com/aminalaee/sqladmin) |
| **jinja2** | Expressive, modern, and designer-friendly templating engine for Python email rendering | BSD-3-Clause | [https://github.com/pallets/jinja](https://github.com/pallets/jinja) |
| **emails** | Modern python library for parsing and sending rich HTML emails | BSD-3-Clause | [https://github.com/lavr/python-emails](https://github.com/lavr/python-emails) |
| **email-validator** | Robust email address validation and syntax/deliverability checker | CC0-1.0 | [https://github.com/JoshData/python-email-validator](https://github.com/JoshData/python-email-validator) |
| **python-multipart** | Streaming multipart form-data parser for asynchronous file uploads in ASGI applications | Apache-2.0 | [https://github.com/Kludex/python-multipart](https://github.com/Kludex/python-multipart) |
| **tenacity** | Retrying library for handling transient failures and resilient network integrations | Apache-2.0 | [https://github.com/jd/tenacity](https://github.com/jd/tenacity) |
| **pypdf** | Pure-python PDF library capable of extracting text and metadata from uploaded CV documents | BSD-3-Clause | [https://github.com/py-pdf/pypdf](https://github.com/py-pdf/pypdf) |
| **python-docx** | Document processing library to read and extract text from Microsoft Word (.docx) files | MIT | [https://github.com/python-openxml/python-docx](https://github.com/python-openxml/python-docx) |
| **rank-bm25** | Collection of BM25 algorithms for text retrieval, keyword matching, and candidate ranking | Apache-2.0 | [https://github.com/dorianbrown/rank_bm25](https://github.com/dorianbrown/rank_bm25) |

## 3. Backend Development (`backend/pyproject.toml`)

| Name | Purpose | License | Link |
| :--- | :--- | :--- | :--- |
| **pytest** | Robust test runner and testing framework for unit and integration testing | MIT | [https://github.com/pytest-dev/pytest](https://github.com/pytest-dev/pytest) |
| **pytest-cov** | Pytest plugin for measuring code coverage and producing execution metrics | MIT | [https://github.com/pytest-dev/pytest-cov](https://github.com/pytest-dev/pytest-cov) |
| **pytest-asyncio** | Pytest support for asyncio coroutines and asynchronous test suites | Apache-2.0 | [https://github.com/pytest-dev/pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) |
| **coverage[toml]** | Code coverage measurement tool with pyproject.toml configuration support | Apache-2.0 | [https://github.com/nedbat/coveragepy](https://github.com/nedbat/coveragepy) |
| **mypy** | Static type checker for Python to enforce type safety across backend and celery modules | MIT | [https://github.com/python/mypy](https://github.com/python/mypy) |
| **ruff** | Extremely fast Python linter and code formatter written in Rust | MIT / Apache-2.0 | [https://github.com/astral-sh/ruff](https://github.com/astral-sh/ruff) |
| **pylint** | Static code analysis tool checking for programming errors and duplicate code | GPL-2.0-or-later | [https://github.com/pylint-dev/pylint](https://github.com/pylint-dev/pylint) |
| **bandit** | Security linter designed to find common security issues in Python code | Apache-2.0 | [https://github.com/PyCQA/bandit](https://github.com/PyCQA/bandit) |
| **radon** | Code metrics tool computing Cyclomatic Complexity and Maintainability Index | MIT | [https://github.com/rubik/radon](https://github.com/rubik/radon) |
| **typos** | Source code spell checker discovering and fixing typos across code and docs | MIT / Apache-2.0 | [https://github.com/crate-ci/typos](https://github.com/crate-ci/typos) |

## 4. Celery Worker Dependencies (`celery_app/pyproject.toml`)

| Name | Purpose | License | Link |
| :--- | :--- | :--- | :--- |
| **celery** | Distributed asynchronous task queue and job scheduler based on distributed message passing | BSD-3-Clause | [https://github.com/celery/celery](https://github.com/celery/celery) |
| **redis** | Python interface to the Redis in-memory data structure store used as Celery broker | MIT | [https://github.com/redis/redis-py](https://github.com/redis/redis-py) |
| **crawlee[all]** | Web scraping and browser automation library for Python | Apache-2.0 | [https://github.com/apify/crawlee-python](https://github.com/apify/crawlee-python) |
| **crawl4ai** | Open-source LLM-friendly web crawler and data extractor | Apache-2.0 | [https://github.com/unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) |
| **aiohttp** | Asynchronous HTTP client/server framework for Python and asyncio | Apache-2.0 | [https://github.com/aio-libs/aiohttp](https://github.com/aio-libs/aiohttp) |
| **asyncpg** | Fast, asynchronous PostgreSQL database client library for Python and asyncio | Apache-2.0 | [https://github.com/MagicStack/asyncpg](https://github.com/MagicStack/asyncpg) |

## 5. Frontend Production Dependencies (`frontend/package.json`)

| Name | Purpose | License | Link |
| :--- | :--- | :--- | :--- |
| **next** | The React framework for the web supporting server-side rendering and static generation | MIT | [https://github.com/vercel/next.js](https://github.com/vercel/next.js) |
| **react** | JavaScript library for building interactive user interfaces | MIT | [https://github.com/facebook/react](https://github.com/facebook/react) |
| **react-dom** | React package for working with the DOM in web browser applications | MIT | [https://github.com/facebook/react](https://github.com/facebook/react) |
| **next-intl** | Internationalization library for Next.js applications supporting localized routing | MIT | [https://github.com/amannn/next-intl](https://github.com/amannn/next-intl) |
| **@base-ui/react** | Unstyled UI components providing foundation accessibility primitives | MIT | [https://github.com/mui/base-ui](https://github.com/mui/base-ui) |
| **shadcn** | CLI and accessible component library primitives designed for Tailwind CSS | MIT | [https://github.com/shadcn-ui/ui](https://github.com/shadcn-ui/ui) |
| **lucide-react** | Open-source icon library providing customizable SVG icons for React | ISC | [https://github.com/lucide-icons/lucide](https://github.com/lucide-icons/lucide) |
| **motion** | Production-ready animation and gesture library for React interfaces | MIT | [https://github.com/motiondivision/motion](https://github.com/motiondivision/motion) |
| **tailwind-merge** | Utility function to efficiently merge Tailwind CSS classes without style conflicts | MIT | [https://github.com/dcastil/tailwind-merge](https://github.com/dcastil/tailwind-merge) |
| **class-variance-authority** | Declarative variant configuration management for CSS component styles | Apache-2.0 | [https://github.com/joe-bell/cva](https://github.com/joe-bell/cva) |
| **clsx** | Utility for constructing `className` strings conditionally | MIT | [https://github.com/lukeed/clsx](https://github.com/lukeed/clsx) |
| **react-markdown** | Markdown component for React using syntax trees to safely render markdown | MIT | [https://github.com/remarkjs/react-markdown](https://github.com/remarkjs/react-markdown) |
| **remark-gfm** | Remark plugin to support GitHub Flavored Markdown (autolink literals, footnotes, tables) | MIT | [https://github.com/remarkjs/remark-gfm](https://github.com/remarkjs/remark-gfm) |
| **tw-animate-css** | CSS animation utilities plugin designed for Tailwind CSS | MIT | [https://github.com/Wick-Studio/tw-animate-css](https://github.com/Wick-Studio/tw-animate-css) |
| **validator** | Library of string validators and sanitizers (email, URL, phone number) | MIT | [https://github.com/validatorjs/validator.js](https://github.com/validatorjs/validator.js) |

## 6. Frontend Development Dependencies (`frontend/package.json`)

| Name | Purpose | License | Link |
| :--- | :--- | :--- | :--- |
| **tailwindcss** | Utility-first CSS framework for rapid and responsive UI development | MIT | [https://github.com/tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) |
| **@tailwindcss/postcss** | PostCSS integration plugin for Tailwind CSS v4 | MIT | [https://github.com/tailwindlabs/tailwindcss](https://github.com/tailwindlabs/tailwindcss) |
| **eslint** | Pluggable static code analysis and linting utility for JavaScript and TypeScript | MIT | [https://github.com/eslint/eslint](https://github.com/eslint/eslint) |
| **eslint-config-next** | Standard ESLint configuration package maintained by Next.js | MIT | [https://github.com/vercel/next.js](https://github.com/vercel/next.js) |
| **eslint-config-prettier** | Turns off all rules that are unnecessary or might conflict with Prettier | MIT | [https://github.com/prettier/eslint-config-prettier](https://github.com/prettier/eslint-config-prettier) |
| **prettier** | Opinionated code formatter for consistent frontend formatting | MIT | [https://github.com/prettier/prettier](https://github.com/prettier/prettier) |
| **vitest** | Next generation unit test framework powered by Vite | MIT | [https://github.com/vitest-dev/vitest](https://github.com/vitest-dev/vitest) |
| **@playwright/test** | End-to-end testing framework for modern web apps across Chromium, Firefox, and WebKit | Apache-2.0 | [https://github.com/microsoft/playwright](https://github.com/microsoft/playwright) |
| **babel-plugin-react-compiler** | Automatic compiler optimizing React components and memoization | MIT | [https://github.com/facebook/react](https://github.com/facebook/react) |
| **@commitlint/cli** | Lint commit messages according to conventional commit guidelines | MIT | [https://github.com/conventional-changelog/commitlint](https://github.com/conventional-changelog/commitlint) |
| **@commitlint/config-conventional** | Conventional commit configuration shareable preset for commitlint | MIT | [https://github.com/conventional-changelog/commitlint](https://github.com/conventional-changelog/commitlint) |

## 7. Pre-commit Hooks and Git Linters (`.pre-commit-config.yaml`)

| Name | Purpose | License | Link |
| :--- | :--- | :--- | :--- |
| **pre-commit-hooks** | Out-of-the-box git hooks for basic file checks, trailing whitespace, and syntax validation | MIT | [https://github.com/pre-commit/pre-commit-hooks](https://github.com/pre-commit/pre-commit-hooks) |
| **gitleaks** | Secret detection scanner protecting against leaking passwords, tokens, and private keys | MIT | [https://github.com/gitleaks/gitleaks](https://github.com/gitleaks/gitleaks) |
| **hadolint** | Haskell-based Dockerfile linter ensuring container best practices | GPL-3.0 | [https://github.com/hadolint/hadolint](https://github.com/hadolint/hadolint) |
| **checkov** | Static code analysis tool for Infrastructure as Code (IaC) and Docker Compose security | Apache-2.0 | [https://github.com/bridgecrewio/checkov](https://github.com/bridgecrewio/checkov) |
| **zizmor** | Static analysis tool finding security vulnerabilities in GitHub Actions CI/CD workflows | AGPL-3.0 | [https://github.com/zizmorcore/zizmor](https://github.com/zizmorcore/zizmor) |

## 8. CI/CD GitHub Actions Workflow (`.github/workflows/`)

| Name | Purpose | License | Link |
| :--- | :--- | :--- | :--- |
| **actions/checkout** | Checks out repository under `$GITHUB_WORKSPACE` so workflows can access code | MIT | [https://github.com/actions/checkout](https://github.com/actions/checkout) |
| **actions/setup-node** | Sets up a Node.js environment with npm cache integration | MIT | [https://github.com/actions/setup-node](https://github.com/actions/setup-node) |
| **actions/cache** | Caches dependencies and build outputs to accelerate workflow execution | MIT | [https://github.com/actions/cache](https://github.com/actions/cache) |
| **astral-sh/setup-uv** | Installs and configures the uv Python package manager with runner caching | MIT / Apache-2.0 | [https://github.com/astral-sh/setup-uv](https://github.com/astral-sh/setup-uv) |
| **gitleaks/gitleaks-action** | GitHub Action wrapper for automated secret detection in commits and PRs | MIT | [https://github.com/gitleaks/gitleaks-action](https://github.com/gitleaks/gitleaks-action) |
| **bridgecrewio/checkov-action** | GitHub Action scanning Docker Compose, Kubernetes, and IaC files for misconfigurations | Apache-2.0 | [https://github.com/bridgecrewio/checkov-action](https://github.com/bridgecrewio/checkov-action) |
| **semgrep/semgrep** | Static analysis engine for finding bugs, enforcing standards, and security audits | LGPL-2.1 / Commercial rules | [https://github.com/semgrep/semgrep](https://github.com/semgrep/semgrep) |
| **aquasecurity/trivy-action** | Vulnerability scanner for container images, filesystems, and code repositories | Apache-2.0 | [https://github.com/aquasecurity/trivy-action](https://github.com/aquasecurity/trivy-action) |
| **SonarSource/sonarqube-scan-action** | GitHub Action analyzing code quality, maintainability, and code smells via SonarQube | LGPL-3.0 | [https://github.com/SonarSource/sonarqube-scan-action](https://github.com/SonarSource/sonarqube-scan-action) |
| **zizmorcore/zizmor-action** | Action wrapper for running the Zizmor GitHub Actions security scanner | AGPL-3.0 | [https://github.com/zizmorcore/zizmor-action](https://github.com/zizmorcore/zizmor-action) |
| **docker/setup-qemu-action** | Sets up QEMU static binaries for multi-architecture container builds | Apache-2.0 | [https://github.com/docker/setup-qemu-action](https://github.com/docker/setup-qemu-action) |
| **docker/setup-buildx-action** | Creates and configures a Docker Buildx builder instance | Apache-2.0 | [https://github.com/docker/setup-buildx-action](https://github.com/docker/setup-buildx-action) |
| **docker/build-push-action** | Builds and pushes Docker container images using Buildx | Apache-2.0 | [https://github.com/docker/build-push-action](https://github.com/docker/build-push-action) |
| **docker/login-action** | Logs into Docker registries (Docker Hub, GHCR) for automated image publishing | Apache-2.0 | [https://github.com/docker/login-action](https://github.com/docker/login-action) |
| **jlumbroso/free-disk-space** | Maximizes available disk space on GitHub-hosted Linux runners | MIT | [https://github.com/jlumbroso/free-disk-space](https://github.com/jlumbroso/free-disk-space) |
| **tiangolo/latest-changes** | Automatically generates and manages release notes and changelogs from merged PRs | MIT | [https://github.com/tiangolo/latest-changes](https://github.com/tiangolo/latest-changes) |
| **eps1lon/actions-label-merge-conflict** | Automatically checks PRs for merge conflicts and applies issue labels | MIT | [https://github.com/eps1lon/actions-label-merge-conflict](https://github.com/eps1lon/actions-label-merge-conflict) |
