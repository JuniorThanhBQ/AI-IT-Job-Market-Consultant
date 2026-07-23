import os
import logging
import shutil
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from crawlee.configuration import Configuration
from crawlee import Request

from app.modules.job.models import Job
from .config_crawler import DATABASE_URL
from .crawler_factory import (
    ITViecCrawlerFactory,
    TopDevCrawlerFactory,
    ITJobsCrawlerFactory,
)

logger = logging.getLogger(__name__)


async def run_updater_for_site(async_session, factory, urls) -> None:
    site_name = (
        factory.__class__.__name__.lower().replace("crawlerfactory", "") + "_updater"
    )
    storage_dir = os.path.join(os.getcwd(), "storage", site_name)
    if os.path.exists(storage_dir):
        try:
            shutil.rmtree(storage_dir)
        except Exception as e:
            logger.warning(f"Failed to clear storage dir {storage_dir}: {e}")

    config = Configuration(storage_dir=storage_dir)

    crawler = factory.create_crawler(
        async_session, storage_dir=storage_dir, configuration=config
    )
    requests = [Request.from_url(url=url, label="updater_detail") for url in urls]
    await crawler.run(requests)


async def main() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        statement = select(Job).where(Job.status != "Closed")
        results = await session.execute(statement)
        jobs = results.scalars().all()

    itviec_urls = []
    topdev_urls = []
    itjobs_urls = []
    for job in jobs:
        source_lower = job.source.lower().strip() if job.source else ""
        if source_lower == "itviec":
            itviec_urls.append(job.url)
        elif source_lower == "topdev":
            topdev_urls.append(job.url)
        elif source_lower == "itjobs":
            itjobs_urls.append(job.url)

    if itviec_urls:
        await run_updater_for_site(async_session, ITViecCrawlerFactory(), itviec_urls)
    if topdev_urls:
        await run_updater_for_site(async_session, TopDevCrawlerFactory(), topdev_urls)
    if itjobs_urls:
        await run_updater_for_site(async_session, ITJobsCrawlerFactory(), itjobs_urls)

    await engine.dispose()
