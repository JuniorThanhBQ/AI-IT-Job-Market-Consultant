import asyncio
import os
from celery import Celery
from celery.schedules import crontab

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672//")

app = Celery(
    "jobs_crawler",
    broker=RABBITMQ_URL,
    backend="rpc://",
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
app.conf.beat_schedule = {
    "run-crawler-every-6-hours": {
        "task": "agents.celery_app.run_crawler_task",
        "schedule": crontab(minute=0, hour="*/6"),
    },
    "run-updater-every-30-min": {
        "task": "agents.celery_app.run_jobs_updater_task",
        "schedule": crontab(minute="*/30"),
    },
}


@app.task
def run_portal_crawler_task(portal_name: str):
    from agents.analysis_agent.adaptive_crawler.crawler import crawl_portal

    try:
        asyncio.run(crawl_portal(portal_name))
    except Exception as e:
        print(f"Portal Crawler Failed [{portal_name}]: {e}")
        raise


@app.task
def run_crawler_task():
    portals = ["itviec"]
    for portal in portals:
        run_portal_crawler_task.apply_async(args=[portal])


@app.task
def run_jobs_updater_task():
    from agents.analysis_agent.adaptive_crawler.updater import main as run_updater

    try:
        asyncio.run(run_updater())
    except Exception as e:
        print(f"Jobs Updater Failed: {e}")
        raise
