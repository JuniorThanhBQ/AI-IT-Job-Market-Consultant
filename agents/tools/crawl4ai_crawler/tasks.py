import asyncio
from .crawler import run_crawl4ai_main


def run_crawl4ai_task_sync():
    asyncio.run(run_crawl4ai_main())
