# Celery Service

This package contains the background worker and scheduler for the AI IT Job Market Consultant platform. It runs Celery tasks for crawling, job refreshes, database backups, and email reporting.

## What is in this folder

- `celery_app.py` - Celery application instance, task registration, and beat schedule
- `tools/adaptive_crawler/` - adaptive crawler workflow entrypoints
- `tools/crawl4ai_crawler/` - crawl4ai-based crawling implementation
- `tools/crawler_update_tool/` - job update workflow for refreshing existing records
- `tools/backup_tool/` - backup pipeline used by the scheduled backup task
- `tools/email_report_tool/` - email reporting task definitions
- `scripts/` - worker startup helpers and utility scripts
- `tests/` - application-level tests for the Celery service
- `Dockerfile` - container image for the worker runtime

## Registered tasks

The app registers the following tasks:

- `run_crawler_task` - executes the adaptive crawler workflow once per day at 00:00
- `run_crawl4ai_task` - executes the crawl4ai crawler once per day at 02:30
- `run_jobs_update_task` - refreshes job data every 30 minutes
- `run_database_backup_task` - runs the database backup pipeline every 3 hours

The email reporting tools are imported into the Celery app so their tasks are available to the worker.

## Runtime configuration

- Broker: RabbitMQ via `settings.rabbitmq.RABBITMQ_URL`
- Result backend: RPC
- Timezone: `Asia/Ho_Chi_Minh`
- Beat schedule file: temporary directory location managed by Celery
- Worker concurrency: derived from the startup helper and falls back to CPU count

## Local development

From the repository root, install the workspace environment and start the worker:

```bash
uv sync --package celery-app
cd celery
celery -A celery_app worker --loglevel=info
```

To run the scheduler as well:

```bash
celery -A celery_app beat --loglevel=info
```

A helper script is also available for launching the worker with adaptive concurrency:

```bash
sh scripts/start_worker.sh
```

## Container usage

The Docker image builds the Celery runtime and starts the worker entrypoint by default. It includes the dependencies needed for crawling and reporting tasks.
