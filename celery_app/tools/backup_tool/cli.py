import argparse
import asyncio
import logging
import os
import sys
import tempfile
from pathlib import Path

from app.core.config import settings
from app.core.security import verify_password
from utils.backup_utils import format_utc_modtime

from tools.backup_tool.service import (
    check_rclone_login,
    list_remote_backups,
    restore_override,
    run_backup_pipeline,
    verify_latest_backup,
)

logger = logging.getLogger(__name__)
PASSWORD_ENV_VAR = "BACKUP_RESTORE_ADMIN_" + "PASSWORD"


def _non_interactive() -> bool:
    try:
        return not sys.stdin.isatty()
    except Exception:
        return True


def _confirm(prompt: str) -> bool:
    if _non_interactive():
        logger.error(
            f"Confirmation required ('{prompt.strip()}') but no interactive "
            f"Re-run with --yes if you intend to skip confirmation."
        )
        return False
    answer = input(prompt)
    return answer.strip().lower() == "y"


async def list_backups_cli():
    logger.info("Fetching backup list from Google Drive")
    try:
        backups = await list_remote_backups()
        if not backups:
            logger.info("No backups found.")
            return

        print(f"{'Filename':<50} | {'Size (MB)':<12} | {'Modified Time':<25}")
        print("-" * 93)
        for b in backups:
            mod_time = format_utc_modtime(b.get("ModTime", ""))
            size_mb = b.get("Size", 0) / (1024 * 1024)
            print(f"{b.get('Name', ''):<50} | {size_mb:<12.2f} | {mod_time:<25}")
    except Exception:
        logger.error("Failed to fetch backups.")
        sys.exit(1)


async def run_backup_cli():
    logger.info("Starting manual database backup pipeline...")
    try:
        success = await run_backup_pipeline()
    except RuntimeError:
        logger.error("Database backup pipeline failed.")
        sys.exit(1)

    if success:
        logger.info("Database backup pipeline completed successfully!")
    else:
        logger.error("Database backup pipeline failed! See logs for details.")
        sys.exit(1)


async def verify_restore_cli():
    logger.info("Starting verification of latest database backup...")
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        try:
            success = await verify_latest_backup(temp_dir)
        except RuntimeError:
            logger.error("Latest backup restore verification failed.")
            sys.exit(1)
        if success:
            logger.info(
                "Latest backup restore verification completed successfully (PASS)!"
            )
        else:
            logger.error(
                "Latest backup restore verification failed (FAIL)! See logs for details."
            )
            sys.exit(1)


async def run_restore_override_cli(configured_pwd: str):
    if settings.ENVIRONMENT not in {"local", "development"}:
        logger.error(
            "Destructive restore-override is only allowed in local or development environments."
        )
        sys.exit(1)

    logger.warning("This will drop and overwrite your active main database!")
    if _non_interactive():
        logger.error(
            "Destructive restore-override cannot be run in non-interactive environments."
        )
        sys.exit(1)

    confirm_pwd = input(
        "Please enter the admin password again to confirm database overwrite: "
    )
    is_valid, _ = verify_password(confirm_pwd, configured_pwd)
    if not is_valid:
        logger.error("Invalid confirmation password. Operation cancelled.")
        sys.exit(1)

    logger.info("Starting database restore override...")
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        try:
            success = await restore_override(temp_dir)
        except RuntimeError:
            logger.error("Database restore failed.")
            sys.exit(1)
        if success:
            logger.info("Main database restored successfully from Google Drive!")
        else:
            logger.error("Database restore failed! See logs for details.")
            sys.exit(1)


def main():
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--password",
        default=None,
        help="Admin password required to run backup/restore operations.",
    )

    parser = argparse.ArgumentParser(
        parents=[parent_parser],
        description="AI IT Job Market Consultant - Backup Restore CLI",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "list", parents=[parent_parser], help="Get the list of backup files"
    )
    subparsers.add_parser(
        "backup",
        parents=[parent_parser],
        help="Trigger a database backup and upload it",
    )
    subparsers.add_parser(
        "restore",
        parents=[parent_parser],
        help="Restore and verify the latest backup on a temporary DB",
    )
    subparsers.add_parser(
        "restore-override",
        parents=[parent_parser],
        help="Download and restore the latest backup, overwriting the main database",
    )

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

    configured_pwd = settings.backup.BACKUP_RESTORE_ADMIN_PASSWORD
    if not configured_pwd:
        logger.error("BACKUP_RESTORE_ADMIN_PASSWORD is not configured in Settings.")
        sys.exit(1)

    supplied_pwd = args.password or os.environ.get(PASSWORD_ENV_VAR)
    if not supplied_pwd:
        logger.error(
            f"No password supplied. Set {PASSWORD_ENV_VAR} (preferred for "
            f"automated/production use) or pass --password."
        )
        sys.exit(1)

    is_valid, _ = verify_password(supplied_pwd, configured_pwd)
    if not is_valid:
        logger.error("Invalid backup admin password.")
        sys.exit(1)

    logged_in, err_msg = asyncio.run(check_rclone_login())
    if not logged_in:
        logger.error(
            f"Google Drive account is not configured or authenticated: {err_msg}"
        )
        sys.exit(1)

    if args.command == "list":
        asyncio.run(list_backups_cli())
    elif args.command == "backup":
        asyncio.run(run_backup_cli())
    elif args.command == "restore":
        asyncio.run(verify_restore_cli())
    elif args.command == "restore-override":
        asyncio.run(run_restore_override_cli(configured_pwd))


if __name__ == "__main__":
    main()
