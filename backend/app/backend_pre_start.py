import logging
from pathlib import Path

from sqlalchemy import Engine
from sqlmodel import Session, select
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.core.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5
wait_seconds = 1


def check_migrations_exist() -> None:
    possible_paths = [
        Path(__file__).resolve().parent.parent.parent / "database" / "versions",
        Path("/app/backend/database/versions"),
        Path("database/versions"),
        Path("../database/versions"),
    ]

    versions_dir = next((p for p in possible_paths if p.is_dir()), None)

    if versions_dir is not None:
        py_files = [f for f in versions_dir.glob("*.py") if f.name != "__init__.py"]
        if not py_files:
            logger.warning(
                "CAUTION: No migration files found in '%s'. "
                "Database migrations have not been generated yet! "
                "Run 'make db-migration-docker MSG=\"initial_schema\"' to autogenerate migration scripts.",
                versions_dir,
            )
    else:
        logger.warning("CAUTION: Could not locate database/versions directory.")


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init(db_engine: Engine) -> None:
    try:
        with Session(db_engine) as session:
            session.exec(select(1))
    except Exception as e:
        logger.error(e)
        raise e


def main() -> None:
    logger.info("Initializing service")
    check_migrations_exist()
    init(engine)
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
