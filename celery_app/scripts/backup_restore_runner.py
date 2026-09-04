import asyncio
import getpass
import logging
import os
import sys
import tempfile
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "celery_app"))
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from app.core.security import verify_password
from tools.backup_tool.backup_services import (
    check_rclone_login,
    list_remote_backups,
    restore_override,
    run_backup_pipeline,
    verify_latest_backup,
)
from utils.backup_utils import format_utc_modtime

logger = logging.getLogger(__name__)


def prompt_password(prompt_text: str = "Enter backup admin password: ") -> str:
    try:
        if sys.stdin.isatty():
            return getpass.getpass(prompt_text)
        return input(prompt_text)
    except Exception:
        return ""


def print_status_report(action: str, success: bool, message: str = "") -> None:
    status_label = "SUCCESS" if success else "FAILED"
    border = "=" * 60
    print(border)
    print(f"ACTION: {action.upper()}")
    print(f"STATUS: {status_label}")
    if message:
        print(f"DETAILS: {message}")
    print(border)


async def execute_list() -> bool:
    try:
        backups = await list_remote_backups()
        if not backups:
            print("No backups found.")
            return True

        print(f"{'Filename':<50} | {'Size (MB)':<12} | {'Modified Time':<25}")
        print("-" * 93)
        for backup_item in backups:
            mod_time = format_utc_modtime(backup_item.get("ModTime", ""))
            size_mb = backup_item.get("Size", 0) / (1024 * 1024)
            print(
                f"{backup_item.get('Name', ''):<50} | {size_mb:<12.2f} | {mod_time:<25}"
            )
        return True
    except Exception as exc:
        logger.error(f"Failed to fetch backups: {exc}")
        return False


async def execute_backup() -> bool:
    try:
        return await run_backup_pipeline()
    except Exception as exc:
        logger.error(f"Backup pipeline execution failed: {exc}")
        return False


async def execute_restore() -> bool:
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        try:
            return await verify_latest_backup(temp_dir)
        except Exception as exc:
            logger.error(f"Latest backup restore verification failed: {exc}")
            return False


async def execute_restore_override(configured_password: str) -> bool:
    if settings.ENVIRONMENT not in {"local", "development"}:
        print(
            "Destructive restore-override is only allowed in local or development environments."
        )
        return False

    confirm_password = prompt_password(
        "Enter admin password again to confirm database overwrite: "
    )
    is_valid, _ = verify_password(confirm_password, configured_password)
    if not is_valid:
        print("Invalid confirmation password. Operation cancelled.")
        return False

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        try:
            return await restore_override(temp_dir)
        except Exception as exc:
            logger.error(f"Database restore override failed: {exc}")
            return False


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("Usage: make backup-restore CMD=[list|backup|restore|restore-override]")
        sys.exit(1)

    cmd = sys.argv[1].strip()
    allowed_cmds = {"list", "backup", "restore", "restore-override"}
    if cmd not in allowed_cmds:
        print(f"Error: Invalid command '{cmd}'. Must be one of {allowed_cmds}")
        sys.exit(1)

    configured_password = settings.backup.BACKUP_RESTORE_ADMIN_PASSWORD
    if not configured_password or not configured_password.strip():
        print("Error: BACKUP_RESTORE_ADMIN_PASSWORD is not configured.")
        sys.exit(1)

    entered_password = prompt_password()
    if not entered_password:
        print_status_report(cmd, False, "No password entered.")
        sys.exit(1)

    is_valid, _ = verify_password(entered_password, configured_password)
    if not is_valid:
        print_status_report(cmd, False, "Invalid admin password.")
        sys.exit(1)

    logged_in, err_msg = asyncio.run(check_rclone_login())
    if not logged_in:
        print_status_report(
            cmd, False, f"Remote storage authentication failed: {err_msg}"
        )
        sys.exit(1)

    success = False
    if cmd == "list":
        success = asyncio.run(execute_list())
    elif cmd == "backup":
        success = asyncio.run(execute_backup())
    elif cmd == "restore":
        success = asyncio.run(execute_restore())
    elif cmd == "restore-override":
        success = asyncio.run(execute_restore_override(configured_password))

    report_message = (
        f"Operation '{cmd}' finished."
        if success
        else f"Operation '{cmd}' encountered errors."
    )
    print_status_report(cmd, success, report_message)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
