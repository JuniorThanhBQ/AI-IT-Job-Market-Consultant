import asyncio
import logging
from typing import Any

import aiohttp
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from tools.adaptive_crawler.config_crawler import (
    CRAWLER_UPDATE_BATCH_SIZE,
    DATABASE_URL,
)
from tools.adaptive_crawler.crawler_repository.job_repository import JobRepository
from tools.adaptive_crawler.helpers import generate_session_fingerprint

from .updater_services import process_job

logger = logging.getLogger(__name__)


async def update_jobs_workflow() -> dict[str, Any]:
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    offset = 0
    batch_size = CRAWLER_UPDATE_BATCH_SIZE
    finger_print = generate_session_fingerprint()
    headers = finger_print["extra_http_headers"]

    try:
        async with session_factory() as db_session:
            repo = JobRepository(db_session)
            all_modified_job_ids: list[int] = []

            async with aiohttp.ClientSession(headers=headers) as http_session:
                while True:
                    jobs_batch = await repo.get_open_jobs_batch(
                        limit=batch_size, offset=offset
                    )
                    if not jobs_batch:
                        if all_modified_job_ids:
                            logger.info(
                                f"Total modifications: {len(all_modified_job_ids)} jobs (IDs: {all_modified_job_ids})"
                            )
                        else:
                            logger.info("No modifications detected.")
                        break

                    logger.info(
                        f"The pipeline is processing {len(jobs_batch)} jobs, from offset {offset}"
                    )
                    tasks = [process_job(job, http_session, repo) for job in jobs_batch]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    has_modifications = False
                    for job, result in zip(jobs_batch, results, strict=False):
                        if result is True:
                            has_modifications = True
                            if job.id is not None:
                                all_modified_job_ids.append(job.id)

                    if has_modifications:
                        try:
                            await db_session.commit()
                        except (SQLAlchemyError, RuntimeError) as e:
                            logger.error(
                                f"Unable to do commit batch offset {offset}: {e}"
                            )
                            await db_session.rollback()
                    offset += batch_size
            return {
                "status": "success",
                "modified_jobs_count": len(all_modified_job_ids),
                "modified_job_ids": all_modified_job_ids,
            }
    except Exception as e:
        logger.error(f"Error found in Job Updater: {e}")
        raise
    finally:
        await engine.dispose()
