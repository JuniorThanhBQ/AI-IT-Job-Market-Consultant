import os
import json
import logging
from urllib.parse import urljoin
from pydantic import BaseModel

os.environ["CRAWL4AI_BASE_DIR"] = "/tmp/.crawl4ai"
os.environ["CRAWL4AI_BASE_DIRECTORY"] = "/tmp/.crawl4ai"
if not os.access(os.path.expanduser("~"), os.W_OK):
    os.environ["HOME"] = "/tmp"

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    CacheMode,
    LLMConfig,
)
from crawl4ai.extraction_strategy import LLMExtractionStrategy

from app.core.config import settings
from agents.tools.adaptive_crawler.crawler_repository.job_repository import (
    JobRepository,
)
from app.modules.job.models import SQLModel
from app.utils.embeddings import get_gemini_api_key
from .adapter import crawl4ai_adapter

logger = logging.getLogger(__name__)


class JobLinkSchema(BaseModel):
    url: str


class JobSchema(BaseModel):
    title: str
    company_name: str
    description: str
    location: str
    salary: str
    requirements: list[str]
    benefits: list[str]
    skills: list[str]
    apply_url: str


def clean_json_string(s: str) -> str:
    s = s.strip()
    if s.startswith("```json"):
        s = s[7:]
    elif s.startswith("```"):
        s = s[3:]
    if s.endswith("```"):
        s = s[:-3]
    return s.strip()


async def run_crawl4ai_main() -> None:
    engine = create_async_engine(
        str(settings.database.ASYNC_SQLALCHEMY_DATABASE_URI), echo=False
    )
    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        await conn.run_sync(SQLModel.metadata.create_all)

    urls = [
        "https://fptjobs.com/tuyen-dung?tukhoa=&nganhnghe=4&khuvuc=",
    ]

    browser_config = BrowserConfig(
        headless=True,
        enable_stealth=True,
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/138.0.0.0 Safari/537.36"
        ),
    )

    llm_config = LLMConfig(
        provider="gemini/gemini-2.5-flash", api_token=get_gemini_api_key()
    )

    list_run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        magic=True,
        page_timeout=120000,
        extraction_strategy=LLMExtractionStrategy(
            llm_config=llm_config,
            schema=JobLinkSchema.model_json_schema(),
            instruction="Extract the URLs of the individual job detail pages. Return a list of objects containing the url.",
        ),
    )

    detail_run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        magic=True,
        page_timeout=45000,
        wait_until="commit",
        extraction_strategy=LLMExtractionStrategy(
            llm_config=llm_config,
            schema=JobSchema.model_json_schema(),
            instruction="Extract all detailed information about this specific job posting.",
        ),
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for base_url in urls:
            logger.info(f"Fetching list page: {base_url}")
            list_result = await crawler.arun(url=base_url, config=list_run_config)

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

                job_links = job_links[:5]
                logger.info(f"Found links. Crawling top {len(job_links)} detail pages.")

                async with session_factory() as session:
                    repo = JobRepository(session)

                    for detail_url in job_links:
                        logger.info(f"Crawling detail: {detail_url}")
                        detail_result = await crawler.arun(
                            url=detail_url, config=detail_run_config
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
