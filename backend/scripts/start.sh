#!/bin/sh
set -e

if [ -n "$WEB_CONCURRENCY" ]; then
    WORKERS="$WEB_CONCURRENCY"
else
    WORKERS=$(python -c "import os; print(os.cpu_count() or 1)")
fi

echo "Starting FastAPI backend with ${WORKERS} worker(s)..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers "$WORKERS"
