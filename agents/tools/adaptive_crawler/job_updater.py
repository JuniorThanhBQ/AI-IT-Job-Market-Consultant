import asyncio
import logging
import aiohttp
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession

from .config_crawler import DATABASE_URL
from .crawler_repository.job_repository import JobRepository
from .updater_services import process_job

logger = logging.getLogger(__name__)


async def update_jobs_workflow() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    batch_size = 50
    offset = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
    }

    try:
        async with session_factory() as db_session:
            repo = JobRepository(db_session)

            async with aiohttp.ClientSession(headers=headers) as http_session:
                while True:
                    jobs_batch = await repo.get_open_jobs_batch(
                        limit=batch_size, offset=offset
                    )

                    if not jobs_batch:
                        logger.info("Check all Jobs status completed.")
                        break

                    logger.info(
                        f"Processing {len(jobs_batch)} jobs, from offset {offset}..."
                    )
                    tasks = [process_job(job, http_session) for job in jobs_batch]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    has_modifications = any(
                        res is True for res in results if not isinstance(res, Exception)
                    )

                    if has_modifications:
                        try:
                            await db_session.commit()
                        except Exception as e:
                            logger.error(
                                f"Unable to do commit batch offset {offset}: {e}"
                            )
                            await db_session.rollback()

                    offset += batch_size

    except Exception as e:
        logger.error(f"Error found in Job Updater: {e}")
    finally:
        await engine.dispose()


def main_updater():
    asyncio.run(update_jobs_workflow())


if __name__ == "__main__":
    main_updater()
