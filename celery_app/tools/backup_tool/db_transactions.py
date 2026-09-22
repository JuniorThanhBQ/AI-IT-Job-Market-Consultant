import logging
import os
from pathlib import Path

from app.core.config import settings
from utils.backup_utils import _safe_identifier, pipeline_lock, run_cmd

logger = logging.getLogger(__name__)


def _get_pg_env() -> dict:
    env = os.environ.copy()
    if settings.database.POSTGRES_PASSWORD:
        env["PGPASSWORD"] = settings.database.POSTGRES_PASSWORD
    return env


async def _run_psql(
    sql: str, db: str = "postgres", extra_args: list[str] | None = None
) -> tuple[int, str, str]:
    cmd = [
        "psql",
        "-h",
        settings.database.POSTGRES_SERVER,
        "-p",
        str(settings.database.POSTGRES_PORT),
        "-U",
        settings.database.POSTGRES_USER,
        "-d",
        db,
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.extend(["-c", sql])
    return await run_cmd(cmd, env=_get_pg_env())


async def _drop_db_if_exists(db_ident: str) -> tuple[int, str, str]:
    return await _run_psql(f"DROP DATABASE IF EXISTS {db_ident};")


async def _create_db(db_ident: str) -> tuple[int, str, str]:
    return await _run_psql(f"CREATE DATABASE {db_ident};")


async def _rename_db(old_ident: str, new_ident: str) -> tuple[int, str, str]:
    return await _run_psql(f"ALTER DATABASE {old_ident} RENAME TO {new_ident};")


async def _disallow_connections(db_ident: str) -> tuple[int, str, str]:
    return await _run_psql(f"ALTER DATABASE {db_ident} WITH ALLOW_CONNECTIONS false;")


async def _allow_connections(db_ident: str) -> tuple[int, str, str]:
    return await _run_psql(f"ALTER DATABASE {db_ident} WITH ALLOW_CONNECTIONS true;")


async def _check_db_exists(db_name: str) -> bool:
    code, stdout, _ = await _run_psql(
        f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';",  # nosec B608
        extra_args=["-t", "-A"],
    )
    return code == 0 and stdout.strip() == "1"


async def _terminate_connections(db_name: str) -> tuple[int, str, str]:
    sql = f"""
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '{db_name}'
      AND pid <> pg_backend_pid();
    """  # nosec B608
    return await _run_psql(sql)


async def _restore_dump(
    decompressed_dump: Path, target_db: str
) -> tuple[int, str, str]:
    cmd = [
        "pg_restore",
        "-h",
        settings.database.POSTGRES_SERVER,
        "-p",
        str(settings.database.POSTGRES_PORT),
        "-U",
        settings.database.POSTGRES_USER,
        "-d",
        target_db,
        "--no-owner",
        "--no-privileges",
        str(decompressed_dump),
    ]
    return await run_cmd(cmd, env=_get_pg_env())


async def verify_backup(decompressed_dump: Path) -> bool:
    temp_db_ident = _safe_identifier(
        "temp_restore_verify", "temporary verification database"
    )
    code, _, stderr = await _drop_db_if_exists(temp_db_ident)
    if code != 0:
        logger.warning(f"Pre-cleanup drop of verification database failed: {stderr}")

    code, stdout, stderr = await _create_db(temp_db_ident)
    if code != 0:
        logger.error(f"Failed to create temporary validation database: {stderr}")
        return False

    logger.info("Restoring database backup to verification database...")
    restore_code, stdout_r, stderr_r = await _restore_dump(
        decompressed_dump, "temp_restore_verify"
    )
    logger.info(f"pg_restore exited with code: {restore_code}")
    if restore_code != 0:
        logger.error(f"Restore verification failed: {stderr_r}")

    logger.info("Cleaning up temporary verification database...")
    code, _, stderr = await _drop_db_if_exists(temp_db_ident)
    if code != 0:
        logger.warning(f"Failed to clean up verification database: {stderr}")

    return restore_code == 0


async def restore_override(decompressed_dump: Path) -> bool:
    with pipeline_lock("restore-override"):
        logger.info("Starting database RESTORE-OVERRIDE pipeline...")
        main_db_name = settings.database.POSTGRES_DB
        backup_db_name = f"{main_db_name}_backup_before_restore"

        main_db_ident = _safe_identifier(main_db_name, "main database")
        backup_db_ident = _safe_identifier(backup_db_name, "backup database")

        db_exists = await _check_db_exists(main_db_name)

        if db_exists:
            await _disallow_connections(main_db_ident)
            await _terminate_connections(main_db_name)

            code, _, stderr = await _drop_db_if_exists(backup_db_ident)
            if code != 0:
                await _allow_connections(main_db_ident)
                logger.error(f"Failed to drop old backup database: {stderr}")
                return False

            code, _, stderr = await _rename_db(main_db_ident, backup_db_ident)
            if code != 0:
                await _allow_connections(main_db_ident)
                logger.error(f"Failed to rename main database to backup: {stderr}")
                return False

        code, stdout, stderr = await _create_db(main_db_ident)
        if code != 0:
            logger.error(f"Failed to recreate main database: {stderr}")
            if db_exists:
                await _rename_db(backup_db_ident, main_db_ident)
                await _allow_connections(main_db_ident)
            return False

        logger.info(f"Restoring backup onto database: {main_db_name}")
        restore_code, stdout_r, stderr_r = await _restore_dump(
            decompressed_dump, main_db_name
        )
        logger.info(f"pg_restore exited with code: {restore_code}")

        if restore_code != 0:
            logger.error(f"Restore failed: {stderr_r}")
            await _terminate_connections(main_db_name)
            await _drop_db_if_exists(main_db_ident)

            if db_exists:
                await _terminate_connections(backup_db_name)
                await _rename_db(backup_db_ident, main_db_ident)
                await _allow_connections(main_db_ident)
            return False

        if db_exists:
            await _terminate_connections(backup_db_name)
            code, _, stderr = await _drop_db_if_exists(backup_db_ident)
            if code != 0:
                logger.warning(f"Failed to drop backup database: {stderr}")

        return True
