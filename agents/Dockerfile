ARG PYTHON_VERSION=3.14.6-slim-trixie@sha256:311ea5bb79f1a238ee9e38f8d5f09cb3b4b244575cf49e27cf365ea7e60f11d4
ARG UV_VERSION=0.11.28@sha256:0f36cb9361a3346885ca3677e3767016687b5a170c1a6b88465ec14aefec90aa

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv_bin

# Stage 1: Build the virtual environment
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY --from=uv_bin /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
COPY backend/pyproject.toml backend/
COPY agents/pyproject.toml agents/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
        --frozen \
        --no-install-workspace \
        --package agents \
        --no-editable

COPY backend backend
COPY agents agents

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
        --frozen \
        --package agents \
        --no-editable

# Stage 2: App runtime
FROM python:${PYTHON_VERSION} AS runtime

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH="/app/.cache/ms-playwright"

WORKDIR /app

# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/backend /app/backend
COPY --from=builder /app/agents /app/agents

RUN python -m playwright install chromium && \
    python -m playwright install-deps chromium && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -r app && useradd -r -g app app
RUN chown -R app:app /app

USER app

WORKDIR /app

CMD ["celery", "-A", "agents.celery_app", "worker", "--loglevel=info"]
