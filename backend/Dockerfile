ARG PYTHON_VERSION=3.14.6-slim-trixie@sha256:311ea5bb79f1a238ee9e38f8d5f09cb3b4b244575cf49e27cf365ea7e60f11d4
ARG UV_VERSION=0.11.28@sha256:0f36cb9361a3346885ca3677e3767016687b5a170c1a6b88465ec14aefec90aa

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv_bin

# Stage 1: App build
FROM python:${PYTHON_VERSION} AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY --from=uv_bin /uv /uvx /bin/

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
        --frozen \
        --no-install-workspace \
        --package backend \
        --no-editable \
        --no-dev

COPY backend/scripts backend/scripts
COPY backend/README.md backend/pyproject.toml backend/
COPY backend/app backend/app
COPY ./database backend/database
COPY agents agents

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
        --frozen \
        --package backend \
        --no-editable \
        --no-dev

# Stage 2: App runtime
FROM python:${PYTHON_VERSION} AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/app" \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN groupadd -r -g 10001 app && useradd -r -u 10001 -g app app

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --from=builder --chown=app:app /app/backend /app/backend
COPY --from=builder --chown=app:app /app/agents /app/agents

RUN chmod +x /app/backend/scripts/start.sh

USER 10001

WORKDIR /app/backend

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]

CMD ["/app/backend/scripts/start.sh"]
