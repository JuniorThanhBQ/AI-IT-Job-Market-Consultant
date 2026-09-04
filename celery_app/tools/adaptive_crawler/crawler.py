import asyncio
import logging
from collections.abc import Callable

from app.modules.job.models import SQLModel
from crawlee.events import LocalEventManager
from crawlee.storage_clients import RedisStorageClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from .config_crawler import (
    DATABASE_URL,
    ITJOBS_LINK,
    ITVIEC_LINK,
    REDIS_URL,
    SITE_CRAWL_TIMEOUT_SECONDS,
    TOPDEV_LINK,
    VIETNAMWORKS_LINK,
)
from .crawler_factory import (
    ITJobsCrawlerFactory,
    ITViecCrawlerFactory,
    TopDevCrawlerFactory,
    VietnamworksCrawlerFactory,
)
from .crawler_factory.base_factory import BaseCrawlerFactory
from .helpers import check_redis_connection

logger = logging.getLogger(__name__)

CRAWLERS: dict[Callable[[], BaseCrawlerFactory], list[str]] = {
    ITViecCrawlerFactory: [ITVIEC_LINK],
    TopDevCrawlerFactory: [TOPDEV_LINK],
    ITJobsCrawlerFactory: [ITJOBS_LINK],
    VietnamworksCrawlerFactory: [VIETNAMWORKS_LINK],
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
    except TimeoutError:
        logger.error(
            f"[{site_name}] Crawling timed out after {SITE_CRAWL_TIMEOUT_SECONDS}s"
        )


async def main() -> None:
    await check_redis_connection(REDIS_URL)
    storage_client = RedisStorageClient(connection_string=REDIS_URL)
    event_manager = LocalEventManager.from_config()
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(SQLModel.metadata.create_all)

    try:
        async with event_manager:
            for factory_class, urls in CRAWLERS.items():
                factory = factory_class()
                try:
                    await run_crawler_for_site(
                        session_factory, factory, urls, storage_client, event_manager
                    )
                except Exception as result:
                    logger.error(
                        f"Crawl failed for {factory_class.__name__}: {result}",
                        exc_info=result,
                    )
    finally:
        await engine.dispose()
