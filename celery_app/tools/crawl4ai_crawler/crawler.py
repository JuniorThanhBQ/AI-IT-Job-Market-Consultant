import json
import logging
from urllib.parse import urljoin

from app.core.config import settings
from app.modules.job.models import SQLModel
from app.utils.utils import clean_json_string
from crawl4ai import AsyncWebCrawler
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from tools.adaptive_crawler.crawler_repository.job_repository import (
    JobRepository,
)

from .adapter import crawl4ai_adapter
from .config_crawler import (
    BROWSER_CONFIG,
    DETAIL_RUN_CONFIG,
    LIST_RUN_CONFIG,
    MAX_JOBS_TO_CRAWL,
    URLS,
)

logger = logging.getLogger(__name__)


async def run_crawl4ai_main() -> None:
    engine = create_async_engine(
        str(settings.database.ASYNC_SQLALCHEMY_DATABASE_URI), echo=False
    )
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncWebCrawler(config=BROWSER_CONFIG) as crawler:
        for base_url in URLS:
            logger.info(f"Fetching list page: {base_url}")
            list_result = await crawler.arun(url=base_url, config=LIST_RUN_CONFIG)

            if not list_result.extracted_content:
                continue

            try:
                raw_links = clean_json_string(list_result.extracted_content)
                links_data = json.loads(raw_links)

                job_links = []
                for item in links_data:
                    ext_url = item.get("url")
                    if ext_url:
                        abs_url = urljoin(base_url, ext_url)
                        job_links.append(abs_url)

                job_links = job_links[:MAX_JOBS_TO_CRAWL]
                logger.info(f"Found links. Crawling top {len(job_links)} detail pages.")

                async with session_factory() as session:
                    repo = JobRepository(session)

                    for detail_url in job_links:
                        logger.info(f"Crawling detail: {detail_url}")
                        detail_result = await crawler.arun(
                            url=detail_url, config=DETAIL_RUN_CONFIG
                        )

                        if detail_result.extracted_content:
                            raw_detail = clean_json_string(
                                detail_result.extracted_content
                            )
                            detail_data = json.loads(raw_detail)

                            if isinstance(detail_data, list):
                                if len(detail_data) > 0:
                                    job_raw = detail_data[0]
                                else:
                                    continue
                            else:
                                job_raw = detail_data

                            job_raw["apply_url"] = detail_url
                            logger.info(f"Saving job: {job_raw.get('title')}")

                            try:
                                job_model = crawl4ai_adapter(job_raw, detail_url)
                                await repo.save_or_update(
                                    job_model, generate_embedding=True
                                )
                                await session.commit()
                                logger.info(
                                    f"Successfully committed job: {job_raw.get('title')}"
                                )
                            except Exception as db_err:
                                await session.rollback()
                                logger.error(
                                    f"Database error for {detail_url}: {db_err}"
                                )

            except Exception as e:
                logger.error(f"Error processing {base_url}: {e}")

    await engine.dispose()
