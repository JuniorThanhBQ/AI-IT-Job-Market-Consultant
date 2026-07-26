import asyncio
import logging
from crawlee.events import LocalEventManager
from crawlee.storage_clients import RedisStorageClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.job.models import SQLModel
from .config_crawler import DATABASE_URL, REDIS_URL, SITE_CRAWL_TIMEOUT_SECONDS
from .crawler_factory import (
    # FPTJobsCrawlerFactory,
    # ITJobsCrawlerFactory,
    ITViecCrawlerFactory,
    TopDevCrawlerFactory,
    # VieclamOUCrawlerFactory,
)
from .helpers import check_redis_connection

logger = logging.getLogger(__name__)

CRAWLERS = {
    ITViecCrawlerFactory: ["https://itviec.com/it-jobs"],
    TopDevCrawlerFactory: [
        "https://topdev.vn/jobs/search?job_categories_ids=2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C67"
    ],
    # ITJobsCrawlerFactory: ["https://itjobs.com.vn"],
    # VieclamOUCrawlerFactory: [
    #     "https://vieclam.ou.edu.vn/tim-viec-lam/nganh-cntt-phan-mem.1/vi",
    #     "https://vieclam.ou.edu.vn/tim-viec-lam/nganh-cntt-phan-cung-mang.63/vi",
    # ],
    # FPTJobsCrawlerFactory: [
    #     "https://fptjobs.com/tuyen-dung?tukhoa=&nganhnghe=5&khuvuc=",
    #     "https://fptjobs.com/tuyen-dung?tukhoa=&nganhnghe=4&khuvuc=",
    # ],
}


async def run_crawler_for_site(
    session_factory,
    factory,
    urls,
    storage_client: RedisStorageClient,
    event_manager: LocalEventManager,
) -> None:
    site_name = factory.__class__.__name__.lower().replace("crawlerfactory", "")
    crawler = await factory.create_crawler(
        session_factory, storage_client=storage_client, event_manager=event_manager
    )
    try:
        await asyncio.wait_for(
            crawler.run(urls), timeout=float(SITE_CRAWL_TIMEOUT_SECONDS)
        )
    except asyncio.TimeoutError:
        logger.error(
            f"[{site_name}] Crawling timed out after {SITE_CRAWL_TIMEOUT_SECONDS}s"
        )


async def main() -> None:
    await check_redis_connection(REDIS_URL)
    logger.info("Redis ping successful.")

    storage_client = RedisStorageClient(connection_string=REDIS_URL)
    event_manager = LocalEventManager.from_config()

    engine = create_async_engine(DATABASE_URL, echo=False)
    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(SQLModel.metadata.create_all)

    try:
        async with event_manager:
            tasks = []
            for factory_cls, urls in CRAWLERS.items():
                factory = factory_cls()
                task = asyncio.create_task(
                    run_crawler_for_site(
                        session_factory, factory, urls, storage_client, event_manager
                    )
                )
                tasks.append(task)

            results = await asyncio.gather(*tasks, return_exceptions=True)

            for factory_cls, result in zip(CRAWLERS.keys(), results):
                if isinstance(result, Exception):
                    logger.error(f"Crawl failed for {factory_cls.__name__}: {result}")
    finally:
        await engine.dispose()
