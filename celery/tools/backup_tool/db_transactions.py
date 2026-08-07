import os
import logging
from pathlib import Path

from app.core.config import settings
from app.utils.backup_utils import _safe_identifier, pipeline_lock, run_cmd

logger = logging.getLogger(__name__)


async def verify_backup(decompressed_dump: Path) -> bool:
    temp_db_ident = _safe_identifier(
        "temp_restore_verify", "temporary verification database"
    )
    env = os.environ.copy()
    if settings.database.POSTGRES_PASSWORD:
        env["PGPASSWORD"] = settings.database.POSTGRES_PASSWORD

    drop_cmd = [
        "psql",
        "-h",
        settings.database.POSTGRES_SERVER,
        "-p",
        str(settings.database.POSTGRES_PORT),
        "-U",
        settings.database.POSTGRES_USER,
        "-d",
        "postgres",
        "-c",
        f"DROP DATABASE IF EXISTS {temp_db_ident};",
    ]
    code, _, stderr = await run_cmd(drop_cmd, env=env)
    if code != 0:
        logger.warning(f"Pre-cleanup drop of verification database failed: {stderr}")

    create_cmd = [
        "psql",
        "-h",
        settings.database.POSTGRES_SERVER,
        "-p",
        str(settings.database.POSTGRES_PORT),
        "-U",
        settings.database.POSTGRES_USER,
        "-d",
        "postgres",
        "-c",
        f"CREATE DATABASE {temp_db_ident};",
    ]
    code, stdout, stderr = await run_cmd(create_cmd, env=env)
    if code != 0:
        logger.error(f"Failed to create temporary validation database: {stderr}")
        return False

    logger.info("Restoring database backup to verification database...")
    restore_cmd = [
        "pg_restore",
        "-h",
        settings.database.POSTGRES_SERVER,
        "-p",
        str(settings.database.POSTGRES_PORT),
        "-U",
        settings.database.POSTGRES_USER,
        "-d",
        "temp_restore_verify",
        "--no-owner",
        "--no-privileges",
        str(decompressed_dump),
    ]
    restore_code, stdout_r, stderr_r = await run_cmd(restore_cmd, env=env)
    logger.info(f"pg_restore exited with code: {restore_code}")
    if restore_code != 0:
        logger.error(f"Restore verification failed: {stderr_r}")

    logger.info("Cleaning up temporary verification database...")
    cleanup_cmd = [
        "psql",
        "-h",
        settings.database.POSTGRES_SERVER,
        "-p",
        str(settings.database.POSTGRES_PORT),
        "-U",
        settings.database.POSTGRES_USER,
        "-d",
        "postgres",
        "-c",
        f"DROP DATABASE IF EXISTS {temp_db_ident};",
    ]
    code, _, stderr = await run_cmd(cleanup_cmd, env=env)
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

        env = os.environ.copy()
        if settings.database.POSTGRES_PASSWORD:
            env["PGPASSWORD"] = settings.database.POSTGRES_PASSWORD

        terminate_conn_sql = """
        SELECT pg_terminate_backend(pg_stat_activity.pid)
        FROM pg_stat_activity
        WHERE pg_stat_activity.datname = :'dbname'
          AND pid <> pg_backend_pid();
        """

        async def terminate_db_connections(db: str):
            await run_cmd(
                [
                    "psql",
                    "-h",
                    settings.database.POSTGRES_SERVER,
                    "-p",
                    str(settings.database.POSTGRES_PORT),
                    "-U",
                    settings.database.POSTGRES_USER,
                    "-d",
                    "postgres",
                    "-v",
                    f"dbname={db}",
                    "-c",
                    terminate_conn_sql,
                ],
                env=env,
            )

        db_exists_cmd = [
            "psql",
            "-h",
            settings.database.POSTGRES_SERVER,
            "-p",
            str(settings.database.POSTGRES_PORT),
            "-U",
            settings.database.POSTGRES_USER,
            "-d",
            "postgres",
            "-t",
            "-A",
            "-v",
            f"dbname={main_db_name}",
            "-c",
            "SELECT 1 FROM pg_database WHERE datname = :'dbname';",
        ]
        code, stdout, stderr = await run_cmd(db_exists_cmd, env=env)
        db_exists = code == 0 and stdout.strip() == "1"

        if db_exists:
            await terminate_db_connections(main_db_name)

            drop_backup_cmd = [
                "psql",
                "-h",
                settings.database.POSTGRES_SERVER,
                "-p",
                str(settings.database.POSTGRES_PORT),
                "-U",
                settings.database.POSTGRES_USER,
                "-d",
                "postgres",
                "-c",
                f"DROP DATABASE IF EXISTS {backup_db_ident};",
            ]
            code, _, stderr = await run_cmd(drop_backup_cmd, env=env)
            if code != 0:
                logger.error(f"Failed to drop old backup database: {stderr}")
                return False

            rename_cmd = [
                "psql",
                "-h",
                settings.database.POSTGRES_SERVER,
                "-p",
                str(settings.database.POSTGRES_PORT),
                "-U",
                settings.database.POSTGRES_USER,
                "-d",
                "postgres",
                "-c",
                f"ALTER DATABASE {main_db_ident} RENAME TO {backup_db_ident};",
            ]
            code, _, stderr = await run_cmd(rename_cmd, env=env)
            if code != 0:
                logger.error(f"Failed to rename main database to backup: {stderr}")
                return False

        create_cmd = [
            "psql",
            "-h",
            settings.database.POSTGRES_SERVER,
            "-p",
            str(settings.database.POSTGRES_PORT),
            "-U",
            settings.database.POSTGRES_USER,
            "-d",
            "postgres",
            "-c",
            f"CREATE DATABASE {main_db_ident};",
        ]
        code, stdout, stderr = await run_cmd(create_cmd, env=env)
        if code != 0:
            logger.error(f"Failed to recreate main database: {stderr}")
            if db_exists:
                rename_back_cmd = [
                    "psql",
                    "-h",
                    settings.database.POSTGRES_SERVER,
                    "-p",
                    str(settings.database.POSTGRES_PORT),
                    "-U",
                    settings.database.POSTGRES_USER,
                    "-d",
                    "postgres",
                    "-c",
                    f"ALTER DATABASE {backup_db_ident} RENAME TO {main_db_ident};",
                ]
                await run_cmd(rename_back_cmd, env=env)
            return False

        logger.info(f"Restoring backup onto database: {main_db_name}")
        restore_cmd = [
            "pg_restore",
            "-h",
            settings.database.POSTGRES_SERVER,
            "-p",
            str(settings.database.POSTGRES_PORT),
            "-U",
            settings.database.POSTGRES_USER,
            "-d",
            main_db_name,
            "--no-owner",
            "--no-privileges",
            str(decompressed_dump),
        ]
        restore_code, stdout_r, stderr_r = await run_cmd(restore_cmd, env=env)
        logger.info(f"pg_restore exited with code: {restore_code}")

        if restore_code != 0:
            logger.error(f"Restore failed: {stderr_r}")
            await terminate_db_connections(main_db_name)
            drop_failed_cmd = [
                "psql",
                "-h",
                settings.database.POSTGRES_SERVER,
                "-p",
                str(settings.database.POSTGRES_PORT),
                "-U",
                settings.database.POSTGRES_USER,
                "-d",
                "postgres",
                "-c",
                f"DROP DATABASE IF EXISTS {main_db_ident};",
            ]
            await run_cmd(drop_failed_cmd, env=env)

            if db_exists:
                await terminate_db_connections(backup_db_name)
                rename_back_cmd = [
                    "psql",
                    "-h",
                    settings.database.POSTGRES_SERVER,
                    "-p",
                    str(settings.database.POSTGRES_PORT),
                    "-U",
                    settings.database.POSTGRES_USER,
                    "-d",
                    "postgres",
                    "-c",
                    f"ALTER DATABASE {backup_db_ident} RENAME TO {main_db_ident};",
                ]
                await run_cmd(rename_back_cmd, env=env)
            return False

        if db_exists:
            await terminate_db_connections(backup_db_name)
            drop_backup_cmd = [
                "psql",
                "-h",
                settings.database.POSTGRES_SERVER,
                "-p",
                str(settings.database.POSTGRES_PORT),
                "-U",
                settings.database.POSTGRES_USER,
                "-d",
                "postgres",
                "-c",
                f"DROP DATABASE IF EXISTS {backup_db_ident};",
            ]
            code, _, stderr = await run_cmd(drop_backup_cmd, env=env)
            if code != 0:
                logger.warning(f"Failed to drop backup database: {stderr}")

        return True
