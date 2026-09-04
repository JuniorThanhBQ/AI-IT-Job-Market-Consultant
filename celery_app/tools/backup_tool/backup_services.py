import json
import logging
import shutil
import tempfile
from pathlib import Path

from app.core.config import settings
from utils.backup_utils import pipeline_lock, run_cmd

from tools.backup_tool.backup_helpers import (
    backup_db,
    download_and_decompress_backup,
    enforce_retention_policy,
    upload_to_gdrive,
    verify_latest_backup_impl,
)
from tools.backup_tool.db_transactions import (
    restore_override as db_restore_override,
)
from tools.backup_tool.db_transactions import (
    verify_backup as db_verify_backup,
)

logger = logging.getLogger(__name__)


async def check_rclone_login() -> tuple[bool, str]:
    if not shutil.which("rclone"):
        return False, "rclone executable not found on system PATH."

    remote_path = settings.backup.RCLONE_REMOTE_PATH
    remote_name = remote_path.split(":")[0]

    code, stdout, stderr = await run_cmd(["rclone", "about", f"{remote_name}:"])
    if code != 0:
        return False, stderr or f"rclone exited with code {code}"
    return True, ""


async def list_remote_backups() -> list[dict]:

    remote_path = settings.backup.RCLONE_REMOTE_PATH
    code, stdout, stderr = await run_cmd(["rclone", "lsjson", remote_path])
    if code != 0:
        if "directory not found" in stderr.lower():
            return []
        raise RuntimeError(f"Failed to list remote backups: {stderr}")
    try:
        files = json.loads(stdout)
        dump_files = [
            item for item in files if item.get("Name", "").endswith(".dump.gz")
        ]
        dump_files.sort(key=lambda item: item.get("ModTime", ""), reverse=True)
        return dump_files
    except Exception as exc:
        raise RuntimeError(f"Failed to parse rclone JSON output: {exc}")


async def verify_latest_backup(temp_dir: Path) -> bool:
    backups = await list_remote_backups()
    with pipeline_lock("verify"):
        return await verify_latest_backup_impl(temp_dir, backups)


async def restore_override(temp_dir: Path) -> bool:
    backups = await list_remote_backups()
    decompressed_dump = await download_and_decompress_backup(temp_dir, backups)
    if not decompressed_dump:
        return False

    logger.info("Verifying backup integrity on temporary database before override.")
    verified = await db_verify_backup(decompressed_dump)
    if not verified:
        logger.error(
            "Pre-restore backup verification failed. Aborting restore override."
        )
        return False

    logger.info(
        "Pre-restore verification passed. Proceeding with database restore override."
    )
    return await db_restore_override(decompressed_dump)


async def run_backup_pipeline() -> bool:
    logger.info("Starting Database Backup and Verification Pipeline")
    with pipeline_lock("backup"), tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        try:
            dump_path, sha_path = await backup_db(temp_dir)
            await upload_to_gdrive(dump_path, sha_path)
            await enforce_retention_policy()

            backups = await list_remote_backups()
            success = await verify_latest_backup_impl(temp_dir, backups)
            if success:
                logger.info("Backup pipeline healthcheck status: SUCCESS")
                return True
            else:
                logger.error("Backup pipeline healthcheck status: FAILED")
                return False
        except Exception:
            logger.exception("Backup pipeline failed")
            return False
