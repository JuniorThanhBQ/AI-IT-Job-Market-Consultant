import logging
import os
import shutil
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.job.models import SQLModel
from .config_crawler import DATABASE_URL
from .crawler_factory import (
    FPTJobsCrawlerFactory,
    ITJobsCrawlerFactory,
    ITViecCrawlerFactory,
    TopDevCrawlerFactory,
    VieclamOUCrawlerFactory,
)

logger = logging.getLogger(__name__)

PORTAL_FACTORIES = {
    "itviec": (
        ITViecCrawlerFactory,
        ["https://itviec.com/it-jobs"],
    ),
    "topdev": (
        TopDevCrawlerFactory,
        [
            "https://topdev.vn/jobs/search?job_categories_ids=2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C67"
        ],
    ),
    "itjobs": (
        ITJobsCrawlerFactory,
        ["https://itjobs.com.vn"],
    ),
    "vieclam_ou": (
        VieclamOUCrawlerFactory,
        [
            "https://vieclam.ou.edu.vn/tim-viec-lam/nganh-cntt-phan-mem.1/vi",
            "https://vieclam.ou.edu.vn/tim-viec-lam/nganh-cntt-phan-cung-mang.63/vi",
        ],
    ),
    "fptjobs": (
        FPTJobsCrawlerFactory,
        [
            "https://fptjobs.com/tuyen-dung?tukhoa=&nganhnghe=5&khuvuc=",
            "https://fptjobs.com/tuyen-dung?tukhoa=&nganhnghe=4&khuvuc=",
        ],
    ),
}


async def run_crawler_for_site(async_session, factory, urls) -> None:
    site_name = factory.__class__.__name__.lower().replace("crawlerfactory", "")
    storage_dir = os.path.join(os.getcwd(), "storage", site_name)
    if os.path.exists(storage_dir):
        try:
            shutil.rmtree(storage_dir)
        except Exception as e:
            logger.warning(f"Failed to clear storage dir {storage_dir}: {e}")

    crawler = factory.create_crawler(async_session, storage_dir=storage_dir)
    await crawler.run(urls)


async def crawl_portal(portal_name: str) -> None:
    portal_key = portal_name.lower().strip()
    if portal_key not in PORTAL_FACTORIES:
        raise ValueError(f"Unknown portal key: {portal_name}")

    factory_cls, urls = PORTAL_FACTORIES[portal_key]
    factory = factory_cls()

    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        await run_crawler_for_site(async_session, factory, urls)
    finally:
        await engine.dispose()


async def main() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    try:
        for portal_key, (factory_cls, urls) in PORTAL_FACTORIES.items():
            factory = factory_cls()
            try:
                await run_crawler_for_site(async_session, factory, urls)
            except Exception as e:
                logger.error(f"Crawl failed for {portal_key}: {e}")
    finally:
        await engine.dispose()
