import asyncio
import logging
import random
import aiohttp
from datetime import UTC, datetime, timedelta
from typing import Any

from app.modules.job.models import Job, JobEmbedding
from app.modules.company.models import CompanyEmbedding
from app.core.enums import JobStatus, Currency
from app.utils.embeddings import generate_embedding_async, DEFAULT_EMBEDDING_MODEL
from tools.adaptive_crawler.config_crawler import (
    MAX_CONCURRENCY,
)

logger = logging.getLogger(__name__)
DATE_DELETE_THRESHOLD = timedelta(days=7)
HTTP_SEMAPHORE = asyncio.Semaphore(MAX_CONCURRENCY)


async def check_url_status(session: aiohttp.ClientSession, url: str) -> int:
    try:
        async with HTTP_SEMAPHORE:
            await asyncio.sleep(random.SystemRandom().uniform(0.2, 0.8))
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10), allow_redirects=True
            ) as response:
                return response.status
    except Exception as e:
        logger.debug(f"Unable to connect URL {url}: {e}")
        return 0


async def update_embeddings(job: Job, repo: Any) -> bool:
    is_modified = False

    if job.vector_context:
        needs_job_emb = False
        if not job.embedding:
            needs_job_emb = True
        else:
            if (
                job.updated_date > job.embedding.updated_date
                and (job.updated_date - job.embedding.updated_date).total_seconds()
                >= 86400
            ):
                needs_job_emb = True

        if needs_job_emb:
            try:
                vector = await generate_embedding_async(
                    job.vector_context, model_name=DEFAULT_EMBEDDING_MODEL
                )
                if job.embedding:
                    job.embedding.embedding = vector
                    job.embedding.embedding_model = DEFAULT_EMBEDDING_MODEL
                    job.embedding.token_used = getattr(vector, "token_used", 0.0)
                    job.embedding.latency = getattr(vector, "latency", 0.0)
                    job.embedding.log = getattr(vector, "log", None)
                    job.embedding.updated_date = datetime.now(
                        job.updated_date.tzinfo or UTC
                    )
                else:
                    job.embedding = JobEmbedding(
                        embedding=vector,
                        embedding_model=DEFAULT_EMBEDDING_MODEL,
                        token_used=getattr(vector, "token_used", 0.0),
                        latency=getattr(vector, "latency", 0.0),
                        log=getattr(vector, "log", None),
                    )
                is_modified = True
            except Exception as e:
                logger.error(f"Failed to update job embedding: {e}")

    if job.company and job.company.vector_context:
        needs_comp_emb = False
        if not job.company.embedding:
            needs_comp_emb = True
        else:
            if (
                job.company.updated_date > job.company.embedding.updated_date
                and (
                    job.company.updated_date - job.company.embedding.updated_date
                ).total_seconds()
                >= 86400
            ):
                needs_comp_emb = True

        if needs_comp_emb:
            try:
                vector = await generate_embedding_async(
                    job.company.vector_context, model_name=DEFAULT_EMBEDDING_MODEL
                )
                if job.company.embedding:
                    job.company.embedding.embedding = vector
                    job.company.embedding.embedding_model = DEFAULT_EMBEDDING_MODEL
                    job.company.embedding.token_used = getattr(
                        vector, "token_used", 0.0
                    )
                    job.company.embedding.latency = getattr(vector, "latency", 0.0)
                    job.company.embedding.log = getattr(vector, "log", None)
                    job.company.embedding.updated_date = datetime.now(
                        job.company.updated_date.tzinfo or UTC
                    )
                else:
                    job.company.embedding = CompanyEmbedding(
                        embedding=vector,
                        embedding_model=DEFAULT_EMBEDDING_MODEL,
                        token_used=getattr(vector, "token_used", 0.0),
                        latency=getattr(vector, "latency", 0.0),
                        log=getattr(vector, "log", None),
                    )
                is_modified = True
            except Exception as e:
                logger.error(f"Failed to update company embedding: {e}")

    return is_modified


async def process_job(job: Job, session: aiohttp.ClientSession, repo: Any) -> bool:
    is_modified = False

    if (
        job.title == "Unknown Title"
        and (
            job.job_description == ""
            or job.job_description == "Responsibilities: - No description provided"
        )
        and job.company
        and job.company.name in ["Unknown Company", "Vietnamworks"]
    ):
        logger.info(
            f"Deleting unknown job and company (IDs: job={job.id}, company={job.company.id})"
        )
        company = job.company
        await repo.drop(job)
        await repo.session.delete(company)
        await repo.session.flush()
        return True

    if job.title and (
        "Trang bạn đang tìm kiếm" in job.title
        or "Tất cả danh mục" in job.job_description
    ):
        logger.info(
            f"Deleting job {job.id} due to deleted or generic page title pattern."
        )
        await repo.drop(job)
        await repo.session.flush()
        return True

    if not job.url:
        job.status = JobStatus.CLOSED
        return True

    if job.expired_date and job.expired_date < datetime.now():
        job.status = JobStatus.CLOSED
        is_modified = True

    if (
        job.min_salary != 0
        and job.max_salary != 0
        and job.min_salary < 100000
        and job.max_salary < 100000
        and job.currency == Currency.VND
    ):
        job.currency = Currency.USD
        is_modified = True

    if job.status == JobStatus.CLOSED:
        if (
            job.expired_date
            and (job.expired_date + DATE_DELETE_THRESHOLD) < datetime.now()
        ):
            await repo.drop(job)
            return True
        return is_modified

    status_code = await check_url_status(session, job.url)
    if status_code in (404, 410):
        job.status = JobStatus.CLOSED
        is_modified = True

    elif status_code in (401, 403, 406, 429):
        logger.debug(f"Update being blocked (Status {status_code}) at {job.url}.")

    emb_modified = await update_embeddings(job, repo)
    if emb_modified:
        is_modified = True

    return is_modified
