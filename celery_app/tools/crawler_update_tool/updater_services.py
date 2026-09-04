import asyncio
import logging
import random
from datetime import UTC, datetime
from typing import Any

import aiohttp
from app.core.enums import Currency, JobStatus
from app.modules.job.models import Job
from utils.job_updater_utils import has_duplicate_job_description, is_garbage_job

from tools.adaptive_crawler.config_crawler import (
    CRAWLER_UPDATE_MAX_DELAY_SECONDS,
    CRAWLER_UPDATE_MIN_DELAY_SECONDS,
    MAX_CONCURRENCY,
)

logger = logging.getLogger(__name__)
HTTP_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENCY)


async def check_url_status(session: aiohttp.ClientSession, url: str) -> int:
    try:
        async with HTTP_SEMAPHORE:
            await asyncio.sleep(
                random.SystemRandom().uniform(
                    CRAWLER_UPDATE_MIN_DELAY_SECONDS, CRAWLER_UPDATE_MAX_DELAY_SECONDS
                )
            )
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True
            ) as response:
                return response.status
    except (aiohttp.ClientError, TimeoutError, OSError) as e:
        logger.debug(f"Unable to connect URL {url}: {e}")
        return 0


async def process_job(job: Job, session: aiohttp.ClientSession, repo: Any) -> bool:
    is_modified = False
    if is_garbage_job(job) or has_duplicate_job_description(job.job_description):
        logger.info(f"Deleting garbage or duplicate job {job.id}.")
        company = job.company
        await repo.drop(job)
        if company and company.name in ["Unknown Company", "Vietnamworks"]:
            await repo.session.delete(company)
            await repo.session.flush()
        return True

    is_expired = bool(
        job.expired_date
        and job.expired_date < datetime.now(job.expired_date.tzinfo or UTC)
    )
    is_closed_url = False
    if job.url and not is_expired:
        status_code = await check_url_status(session, job.url)
        if status_code in (404, 410):
            is_closed_url = True
        elif status_code in (401, 403, 406, 429):
            logger.debug(f"Update being blocked (Status {status_code}) at {job.url}.")

    if not job.url or is_expired or is_closed_url:
        job.status = JobStatus.CLOSED
        is_modified = True

    if (
        job.min_salary is not None
        and job.max_salary is not None
        and job.min_salary != 0
        and job.max_salary != 0
        and job.min_salary < 100000
        and job.max_salary < 100000
        and job.currency == Currency.VND
    ):
        job.currency = Currency.USD
        is_modified = True

    return is_modified
