import logging
import aiohttp
from datetime import datetime

from app.modules.job.models import Job
from app.core.enums import JobStatus, Currency

logger = logging.getLogger(__name__)


async def check_url_status(session: aiohttp.ClientSession, url: str) -> int:
    try:
        async with session.get(url, timeout=10, allow_redirects=True) as response:
            return response.status
    except Exception as e:
        logger.debug(f"Unable to connect URL {url}: {e}")
        return 0


async def process_job(job: Job, session: aiohttp.ClientSession) -> bool:
    is_modified = False

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
        return is_modified

    status_code = await check_url_status(session, job.url)
    if status_code in (404, 410):
        job.status = JobStatus.CLOSED
        is_modified = True

    elif status_code in (401, 403, 406):
        logger.debug(
            f"Update being blocked (Status {status_code}) at {job.url}. Skip..."
        )

    return is_modified
