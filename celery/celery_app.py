import asyncio
import os
import tempfile
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from tools.backup_tool.service import run_backup_pipeline
from tools.adaptive_crawler.crawler import main as run_crawler_main
from tools.crawler_update_tool.job_updater import update_jobs_workflow
from tools.crawl4ai_crawler.crawler import run_crawl4ai_main
import tools.email_report_tool.tasks  # noqa: F401 # pylint: disable=unused-import

app = Celery(
    "jobs_crawler",
    broker=settings.rabbitmq.RABBITMQ_URL,
    backend="rpc://",
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=False,
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    beat_schedule_filename=os.path.join(tempfile.gettempdir(), "celerybeat-schedule"),
    task_routes={
        "celery_app.run_crawler_task": {"queue": "crawler"},
        "celery_app.run_crawl4ai_task": {"queue": "crawler"},
    },
)

app.conf.beat_schedule = {
    "run-crawler-every-day": {
        "task": "celery_app.run_crawler_task",
        "schedule": crontab(hour=0, minute=0),
        "options": {"expires": 21600},
    },
    "run-crawler-update-every-hours": {
        "task": "celery_app.run_jobs_update_task",
        "schedule": crontab(minute=0, hour="*/1"),
        "options": {"expires": 720},
    },
    "run-crawl4ai-every-day": {
        "task": "celery_app.run_crawl4ai_task",
        "schedule": crontab(hour=2, minute=30),
        "options": {"expires": 21600},
    },
    "run-database-backup-every-3-hours": {
        "task": "celery_app.run_database_backup_task",
        "schedule": crontab(minute=0, hour="*/3"),
    },
}


@app.task(time_limit=28800, soft_time_limit=28000)
def run_crawler_task():
    return asyncio.run(run_crawler_main())


@app.task
def run_crawl4ai_task():
    return asyncio.run(run_crawl4ai_main())


@app.task
def run_jobs_update_task():
    return asyncio.run(update_jobs_workflow())


@app.task
def run_database_backup_task():
    return asyncio.run(run_backup_pipeline())
