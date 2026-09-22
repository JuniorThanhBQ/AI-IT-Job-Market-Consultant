import datetime
import gzip
import json
import logging
import os
import shutil
from pathlib import Path

from app.core.config import settings
from utils.backup_utils import calculate_sha256, run_cmd

from tools.backup_tool.db_transactions import (
    verify_backup as db_verify_backup,
)

logger = logging.getLogger(__name__)


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

    with open(dump_path, "rb") as f_in, gzip.open(gzip_path, "wb") as f_out:
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
    except Exception as exc:
        logger.warning(f"Failed to parse rclone output: {exc}")
        return

    dump_files = [item for item in files if item.get("Name", "").endswith(".dump.gz")]
    dump_files.sort(key=lambda item: item.get("ModTime", ""))
    if len(dump_files) > max_stacks:
        to_delete = dump_files[: len(dump_files) - max_stacks]
        logger.info(f"Deleting {len(to_delete)} oldest backup files from GDrive...")
        for file_info in to_delete:
            filename = file_info["Name"]
            sha_filename = f"{filename}.sha256"

            logger.info(f"Deleting remote file: {filename}")
            code, _, stderr = await run_cmd(
                ["rclone", "deletefile", f"{remote_path}/{filename}"]
            )
            if code != 0:
                logger.warning(f"Failed to delete remote file {filename}: {stderr}")

            logger.info(f"Deleting remote file: {sha_filename}")
            code, _, stderr = await run_cmd(
                ["rclone", "deletefile", f"{remote_path}/{sha_filename}"]
            )
            if code != 0:
                logger.warning(f"Failed to delete remote file {sha_filename}: {stderr}")


async def download_and_decompress_backup(
    temp_dir: Path, backups: list[dict]
) -> Path | None:
    if not backups:
        logger.error("No backups found on Google Drive.")
        return None

    remote_path = settings.backup.RCLONE_REMOTE_PATH
    latest_filename = backups[0]["Name"]
    latest_sha_filename = f"{latest_filename}.sha256"

    local_dump = temp_dir / latest_filename
    local_sha = temp_dir / latest_sha_filename

    code, _, stderr = await run_cmd(
        ["rclone", "copyto", f"{remote_path}/{latest_filename}", str(local_dump)]
    )
    if code != 0:
        logger.error(f"Failed to download dump: {stderr}")
        return None

    code, _, stderr = await run_cmd(
        ["rclone", "copyto", f"{remote_path}/{latest_sha_filename}", str(local_sha)]
    )
    if code != 0:
        logger.error(f"Failed to download checksum: {stderr}")
        return None

    downloaded_sha = calculate_sha256(local_dump)
    with open(local_sha) as f:
        expected_sha = f.read().split()[0].strip()

    if downloaded_sha != expected_sha:
        logger.error(
            f"SHA256 mismatch! Downloaded: {downloaded_sha}, Expected: {expected_sha}"
        )
        return None

    logger.info("Checksum validation passed.")
    decompressed_dump = temp_dir / latest_filename.replace(".gz", "")
    with gzip.open(local_dump, "rb") as f_in, open(decompressed_dump, "wb") as f_out:
        shutil.copyfileobj(f_in, f_out)

    return decompressed_dump


async def verify_latest_backup_impl(temp_dir: Path, backups: list[dict]) -> bool:
    logger.info("Starting verification pipeline for latest backup...")
    decompressed_dump = await download_and_decompress_backup(temp_dir, backups)
    if not decompressed_dump:
        return False
    return await db_verify_backup(decompressed_dump)
