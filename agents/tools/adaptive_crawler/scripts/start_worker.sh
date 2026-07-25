#!/bin/sh
set -e

CONCURRENCY=$(python -m agents.tools.adaptive_crawler.scripts.get_concurrency 2>/dev/null || python -c "import os; print(os.cpu_count() or 1)")

echo "Starting Celery worker with adaptive concurrency: ${CONCURRENCY}..."
exec celery -A agents.celery_app worker --loglevel=info --concurrency="${CONCURRENCY}" "$@"
