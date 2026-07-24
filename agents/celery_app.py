import asyncio
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from agents.tools.adaptive_crawler.crawler import main as run_crawler_main

app = Celery(
    "jobs_crawler",
    broker=settings.RABBITMQ_URL,
    backend="rpc://",
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    worker_max_tasks_per_child=settings.CELERY_WORKER_MAX_TASKS_PER_CHILD,
    beat_schedule_filename="/tmp/celerybeat-schedule",
)
app.conf.beat_schedule = {
    "run-crawler-every-6-hours": {
        "task": "agents.celery_app.run_crawler_task",
        "schedule": crontab(minute=0, hour="*/6"),
    },
}


@app.task
def run_crawler_task():
    asyncio.run(run_crawler_main())
