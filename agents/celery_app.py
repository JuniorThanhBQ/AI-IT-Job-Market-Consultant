import asyncio
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from agents.tools.adaptive_crawler.crawler import main as run_crawler_main
from agents.tools.adaptive_crawler.job_updater import main_updater as run_job_updater
from agents.tools.crawl4ai_crawler.tasks import run_crawl4ai_task_sync

app = Celery(
    "jobs_crawler",
    broker=settings.RABBITMQ_URL,
    backend="rpc://",
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=False,
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    beat_schedule_filename="/tmp/celerybeat-schedule",
)

app.conf.beat_schedule = {
    "run-crawler-every-day": {
        "task": "agents.celery_app.run_crawler_task",
        "schedule": crontab(hour=0, minute=0),
        "options": {"expires": 21600},
    },
    "run-crawler-update-every-15-minutes": {
        "task": "agents.celery_app.run_jobs_update_task",
        "schedule": crontab(minute="*/15"),
        "options": {"expires": 600},
    },
    "run-crawl4ai-every-day": {
        "task": "agents.celery_app.run_crawl4ai_task",
        "schedule": crontab(hour=2, minute=30),
        "options": {"expires": 21600},
    },
}


@app.task
def run_crawler_task():
    asyncio.run(run_crawler_main())


@app.task
def run_jobs_update_task():
    run_job_updater()


@app.task
def run_crawl4ai_task():
    run_crawl4ai_task_sync()
