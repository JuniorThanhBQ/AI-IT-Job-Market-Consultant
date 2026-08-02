import asyncio
import datetime
import hashlib
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)


def calculate_sha256(file_path: Path) -> str:
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


async def run_cmd(cmd: list[str], env: dict | None = None) -> tuple[int, str, str]:
    logger.info(f"Running command: {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )
    stdout, stderr = await proc.communicate()
    return (
        proc.returncode if proc.returncode is not None else -1,
        stdout.decode().strip(),
        stderr.decode().strip(),
    )


async def backup_db(temp_dir: Path) -> tuple[Path, Path]:
    timestamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d_%H%M%S")
    dump_filename = f"db_backup_{timestamp}.dump"
    dump_path = temp_dir / dump_filename
    gzip_path = temp_dir / f"{dump_filename}.gz"
    sha_path = temp_dir / f"{dump_filename}.gz.sha256"

    pg_dump_cmd = [
        "pg_dump",
        "-h",
        settings.database.POSTGRES_SERVER,
        "-p",
        str(settings.database.POSTGRES_PORT),
        "-U",
        settings.database.POSTGRES_USER,
        "-d",
        settings.database.POSTGRES_DB,
        "-Fc",
        "-f",
        str(dump_path),
    ]
    env = os.environ.copy()
    if settings.database.POSTGRES_PASSWORD:
        env["PGPASSWORD"] = settings.database.POSTGRES_PASSWORD

    code, stdout, stderr = await run_cmd(pg_dump_cmd, env=env)
    if code != 0:
        raise RuntimeError(f"pg_dump failed with code {code}: {stderr}")

    import gzip

    with open(dump_path, "rb") as f_in:
        with gzip.open(gzip_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    if dump_path.exists():
        dump_path.unlink()

    sha256_val = calculate_sha256(gzip_path)
    with open(sha_path, "w") as f:
        f.write(f"{sha256_val}  {gzip_path.name}\n")

    logger.info(f"Backup created successfully: {gzip_path.name}")
    return gzip_path, sha_path


async def upload_to_gdrive(dump_path: Path, sha_path: Path):
    remote_path = settings.backup.RCLONE_REMOTE_PATH
    logger.info(f"Uploading backup to remote path: {remote_path}")

    code, stdout, stderr = await run_cmd(
        ["rclone", "copy", str(dump_path), remote_path]
    )
    if code != 0:
        raise RuntimeError(f"rclone copy dump failed with code {code}: {stderr}")

    code, stdout, stderr = await run_cmd(["rclone", "copy", str(sha_path), remote_path])
    if code != 0:
        raise RuntimeError(f"rclone copy checksum failed with code {code}: {stderr}")

    logger.info("Upload to Google Drive complete.")


async def enforce_retention_policy():
    remote_path = settings.backup.RCLONE_REMOTE_PATH
    max_stacks = settings.backup.BACKUP_MAX_STACKS
    logger.info(f"Enforcing retention policy on {remote_path} (max: {max_stacks})")

    code, stdout, stderr = await run_cmd(["rclone", "lsjson", remote_path])
    if code != 0:
        logger.warning(f"Failed to list remote files with rclone: {stderr}")
        return

    try:
        files = json.loads(stdout)
    except Exception as e:
        logger.warning(f"Failed to parse rclone output: {e}")
        return

    dump_files = [f for f in files if f.get("Name", "").endswith(".dump.gz")]

    dump_files.sort(key=lambda x: x.get("ModTime", ""))

    if len(dump_files) > max_stacks:
        to_delete = dump_files[: len(dump_files) - max_stacks]
        logger.info(f"Deleting {len(to_delete)} oldest backup files from GDrive...")
        for f in to_delete:
            filename = f["Name"]
            sha_filename = f"{filename}.sha256"

            logger.info(f"Deleting remote file: {filename}")
            await run_cmd(["rclone", "deletefile", f"{remote_path}/{filename}"])

            logger.info(f"Deleting remote file: {sha_filename}")
            await run_cmd(["rclone", "deletefile", f"{remote_path}/{sha_filename}"])


async def list_remote_backups() -> list[dict]:
    remote_path = settings.backup.RCLONE_REMOTE_PATH
    code, stdout, stderr = await run_cmd(["rclone", "lsjson", remote_path])
    if code != 0:
        if "directory not found" in stderr.lower():
            return []
        raise RuntimeError(f"Failed to list remote backups: {stderr}")
    try:
        files = json.loads(stdout)
        dump_files = [f for f in files if f.get("Name", "").endswith(".dump.gz")]
        dump_files.sort(key=lambda x: x.get("ModTime", ""), reverse=True)
        return dump_files
    except Exception as e:
        raise RuntimeError(f"Failed to parse rclone JSON output: {e}")


async def check_rclone_login() -> tuple[bool, str]:
    if not shutil.which("rclone"):
        return False, "rclone executable not found on system PATH."
    remote_path = settings.backup.RCLONE_REMOTE_PATH
    remote_name = remote_path.split(":")[0]

    code, stdout, stderr = await run_cmd(["rclone", "about", f"{remote_name}:"])
    if code != 0:
        return False, stderr or f"rclone exited with code {code}"
    return True, ""


async def verify_latest_backup(temp_dir: Path) -> bool:
    remote_path = settings.backup.RCLONE_REMOTE_PATH
    logger.info("Starting verification pipeline for latest backup...")

    backups = await list_remote_backups()
    if not backups:
        logger.error("No backups found on Google Drive to verify.")
        return False

    latest_filename = backups[0]["Name"]
    latest_sha_filename = f"{latest_filename}.sha256"

    local_dump = temp_dir / latest_filename
    local_sha = temp_dir / latest_sha_filename

    code, stdout, stderr = await run_cmd(
        ["rclone", "copyto", f"{remote_path}/{latest_filename}", str(local_dump)]
    )
    if code != 0:
        logger.error(f"Failed to download dump: {stderr}")
        return False

    code, stdout, stderr = await run_cmd(
        ["rclone", "copyto", f"{remote_path}/{latest_sha_filename}", str(local_sha)]
    )
    if code != 0:
        logger.error(f"Failed to download checksum: {stderr}")
        return False

    downloaded_sha = calculate_sha256(local_dump)
    with open(local_sha) as f:
        expected_sha = f.read().split()[0].strip()

    if downloaded_sha != expected_sha:
        logger.error(
            f"SHA256 mismatch! Downloaded: {downloaded_sha}, Expected: {expected_sha}"
        )
        return False
    logger.info("Checksum validation passed.")

    import gzip

    decompressed_dump = temp_dir / latest_filename.replace(".gz", "")
    with gzip.open(local_dump, "rb") as f_in:
        with open(decompressed_dump, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    temp_db_name = "temp_restore_verify"
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
        f"DROP DATABASE IF EXISTS {temp_db_name};",
    ]
    await run_cmd(drop_cmd, env=env)

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
        f"CREATE DATABASE {temp_db_name};",
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
        temp_db_name,
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
        f"DROP DATABASE IF EXISTS {temp_db_name};",
    ]
    await run_cmd(cleanup_cmd, env=env)

    return restore_code == 0


async def restore_override(temp_dir: Path) -> bool:
    remote_path = settings.backup.RCLONE_REMOTE_PATH
    logger.info("Starting database RESTORE-OVERRIDE pipeline...")

    backups = await list_remote_backups()
    if not backups:
        logger.error("No backups found on Google Drive to restore.")
        return False

    latest_filename = backups[0]["Name"]
    latest_sha_filename = f"{latest_filename}.sha256"

    local_dump = temp_dir / latest_filename
    local_sha = temp_dir / latest_sha_filename

    await run_cmd(
        ["rclone", "copyto", f"{remote_path}/{latest_filename}", str(local_dump)]
    )
    await run_cmd(
        ["rclone", "copyto", f"{remote_path}/{latest_sha_filename}", str(local_sha)]
    )

    downloaded_sha = calculate_sha256(local_dump)
    with open(local_sha) as f:
        expected_sha = f.read().split()[0].strip()

    if downloaded_sha != expected_sha:
        logger.error("SHA256 mismatch! Restore aborted.")
        return False

    import gzip

    decompressed_dump = temp_dir / latest_filename.replace(".gz", "")
    with gzip.open(local_dump, "rb") as f_in:
        with open(decompressed_dump, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    main_db_name = settings.database.POSTGRES_DB
    env = os.environ.copy()
    if settings.database.POSTGRES_PASSWORD:
        env["PGPASSWORD"] = settings.database.POSTGRES_PASSWORD

    logger.info(f"Force-terminating connections and dropping database: {main_db_name}")
    terminate_conn_sql = f"""
    SELECT pg_terminate_backend(pg_stat_activity.pid)
    FROM pg_stat_activity
    WHERE pg_stat_activity.datname = '{main_db_name}'
      AND pid <> pg_backend_pid();
    """
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
            "-c",
            terminate_conn_sql,
        ],
        env=env,
    )

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
            "-c",
            f"DROP DATABASE IF EXISTS {main_db_name};",
        ],
        env=env,
    )

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
        f"CREATE DATABASE {main_db_name};",
    ]
    code, stdout, stderr = await run_cmd(create_cmd, env=env)
    if code != 0:
        logger.error(f"Failed to recreate main database: {stderr}")
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

    return restore_code == 0


async def run_backup_pipeline() -> bool:
    logger.info("=== Starting Database Backup and Verification Pipeline ===")
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        try:
            dump_path, sha_path = await backup_db(temp_dir)
            await upload_to_gdrive(dump_path, sha_path)
            await enforce_retention_policy()
            success = await verify_latest_backup(temp_dir)

            if success:
                logger.info("Backup pipeline healthcheck status: SUCCESS")
                return True
            else:
                logger.error(
                    "Backup pipeline healthcheck status: FAILED (Restore Check failed)"
                )
                return False
        except Exception as e:
            logger.exception(f"Backup pipeline failed with exception: {e}")
            return False
