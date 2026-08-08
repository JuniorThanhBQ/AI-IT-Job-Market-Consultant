#!/bin/sh
set -e

CONCURRENCY=$(python -m scripts.get_concurrency 2>/dev/null || python -c "import os; print(os.cpu_count() or 1)")

echo "Starting Celery worker with adaptive concurrency: ${CONCURRENCY}..."
exec celery -A celery_app worker --loglevel=info --concurrency="${CONCURRENCY}" "$@"
