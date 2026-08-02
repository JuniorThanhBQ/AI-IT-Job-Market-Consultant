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
COPY scripts scripts

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

RUN groupadd -r -g 10001 app && useradd -r -u 10001 -g app app && chown app:app /app

# hadolint ignore=DL3008,DL4006
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    rclone \
    gnupg2 \
    ca-certificates \
    && install -d /etc/apt/keyrings \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/keyrings/postgresql.gpg \
    && . /etc/os-release && echo "deb [signed-by=/etc/apt/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt/ ${VERSION_CODENAME}-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        postgresql-client-18 \
    && apt-get purge -y --auto-remove gnupg2 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/backend /app/backend
COPY --from=builder --chown=app:app /app/agents /app/agents
COPY --from=builder --chown=app:app /app/scripts /app/scripts

RUN python -m playwright install chromium && \
    python -m playwright install-deps chromium && \
    apt-get clean && rm -rf /var/lib/apt/lists/* && \
    chown -R app:app /app/.cache

RUN chmod +x /app/agents/tools/adaptive_crawler/scripts/start_worker.sh

USER 10001

ENTRYPOINT ["tini", "--"]
CMD ["/app/agents/tools/adaptive_crawler/scripts/start_worker.sh"]
