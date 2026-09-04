ARG PYTHON_VERSION=3.14-slim-bookworm@sha256:23c59390fc717bf09f9336908199a0ae75d9c4264bf296123f94ad772fea3b52
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
COPY celery_app/pyproject.toml celery_app/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
        --frozen \
        --no-install-workspace \
        --package celery-app \
        --no-editable \
        --no-dev

COPY backend backend
COPY celery_app celery_app
COPY scripts scripts

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync \
        --frozen \
        --package celery-app \
        --no-editable \
        --no-dev \
    && chmod +x celery_app/scripts/start_worker.sh


# Stage 2: App runtime
FROM python:${PYTHON_VERSION} AS runtime

ENV PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH="/app/.cache/ms-playwright"

WORKDIR /app

RUN groupadd -r -g 10001 app && useradd -r -u 10001 -g app app && chown app:app /app

COPY --from=builder --chown=app:app /app/.venv /app/.venv

# hadolint ignore=DL3008,DL4006
RUN DEBIAN_FRONTEND=noninteractive \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tini \
    rclone \
    gnupg2 \
    ca-certificates \
    && install -d /etc/apt/keyrings \
    && curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc -o /tmp/pg.asc \
    && gpg --dearmor -o /etc/apt/keyrings/postgresql.gpg /tmp/pg.asc \
    && rm /tmp/pg.asc \
    && . /etc/os-release && echo "deb [signed-by=/etc/apt/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt/ ${VERSION_CODENAME}-pgdg main" > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update && apt-get install -y --no-install-recommends \
        postgresql-client-18 \
    && /app/.venv/bin/python -m playwright install-deps chromium \
    && apt-get purge -y --auto-remove gnupg2 curl \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/celery /app/.cache/ms-playwright && chown -R app:app /var/run/celery /app/.cache

RUN --mount=type=cache,target=/root/.cache/ms-playwright \
    PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright python -m playwright install chromium \
    && cp -rp /root/.cache/ms-playwright/. /app/.cache/ms-playwright/ \
    && chown -R app:app /app/.cache/ms-playwright

COPY --from=builder --chown=app:app /app/backend/app /app/backend/app
COPY --from=builder --chown=app:app /app/celery_app /app/celery_app
COPY --from=builder --chown=app:app /app/scripts /app/scripts

HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD ["sh", "-c", "celery -A celery_app inspect ping -d celery@$HOSTNAME | grep -q pong || exit 1"]

USER 10001

ENTRYPOINT ["tini", "--"]
CMD ["/app/celery_app/scripts/start_worker.sh"]
