import argparse
import asyncio
import sys
import tempfile
from pathlib import Path

from app.core.config import settings
from app.db.backup.service import (
    check_rclone_login,
    list_remote_backups,
    restore_override,
    run_backup_pipeline,
    verify_latest_backup,
)


async def list_backups_cli():
    print("Fetching backup list from Google Drive...")
    try:
        backups = await list_remote_backups()
        if not backups:
            print("No backups found.")
            return
        print(f"{'Filename':<50} | {'Size (Bytes)':<12} | {'Modified Time':<25}")
        print("-" * 93)
        for b in backups:
            print(
                f"{b.get('Name', ''):<50} | {b.get('Size', 0):<12} | {b.get('ModTime', ''):<25}"
            )
    except Exception as e:
        print(f"Error fetching backups: {e}", file=sys.stderr)
        sys.exit(1)


async def run_backup_cli():
    print("Starting manual database backup pipeline...")
    success = await run_backup_pipeline()
    if success:
        print("Database backup pipeline completed successfully!")
    else:
        print("Database backup pipeline failed! See logs for details.", file=sys.stderr)
        sys.exit(1)


async def verify_restore_cli():
    print("Starting verification of latest database backup...")
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        success = await verify_latest_backup(temp_dir)
        if success:
            print("Latest backup restore verification completed successfully (PASS)!")
        else:
            print(
                "Latest backup restore verification failed (FAIL)! See logs for details.",
                file=sys.stderr,
            )
            sys.exit(1)


async def run_restore_override_cli():
    print("\n[WARNING] This will drop and overwrite your active main database!")
    confirm = input("Are you absolutely sure you want to proceed? (y/n): ")
    if confirm.strip().lower() != "y":
        print("Operation cancelled.")
        sys.exit(0)

    print("Starting database restore override...")
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        success = await restore_override(temp_dir)
        if success:
            print("Main database restored successfully from Google Drive!")
        else:
            print("Database restore failed! See logs for details.", file=sys.stderr)
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="AI IT Job Market Consultant - Backup Restore CLI"
    )
    parser.add_argument(
        "--password",
        required=True,
        help="Admin password required to run backup/restore operations",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("list", help="Get the list of backup files on Google Drive")
    subparsers.add_parser("backup", help="Trigger a database backup and upload it")
    subparsers.add_parser(
        "restore",
        help="Restore and verify the latest backup on a temporary DB container",
    )
    subparsers.add_parser(
        "restore-override",
        help="Download and restore the latest backup, overwriting the main database",
    )

    args = parser.parse_args()

    configured_pwd = settings.backup.BACKUP_RESTORE_ADMIN_PASSWORD
    if not configured_pwd:
        print(
            "Error: BACKUP_RESTORE_ADMIN_PASSWORD is not configured in Settings.",
            file=sys.stderr,
        )
        sys.exit(1)

    if args.password != configured_pwd:
        print("Error: Invalid backup admin password.", file=sys.stderr)
        sys.exit(1)

    logged_in, err_msg = asyncio.run(check_rclone_login())
    if not logged_in:
        print(
            f"\n[WARNING] Google Drive account is not configured or authenticated: {err_msg}"
        )
        choice = input("Would you like to log in / configure Rclone now? (y/n): ")
        if choice.strip().lower() == "y":
            import subprocess

            try:
                subprocess.run(["rclone", "config"])
            except FileNotFoundError:
                print(
                    "\n[ERROR] 'rclone' executable could not be found on your system PATH.",
                    file=sys.stderr,
                )
                if sys.platform == "win32":
                    print(
                        "Please install it using: winget install Rclone.Rclone",
                        file=sys.stderr,
                    )
                    print(
                        "Make sure to restart your terminal session so the PATH environment variable updates.",
                        file=sys.stderr,
                    )
                else:
                    print(
                        "Please install it using your system package manager (e.g., apt install rclone or brew install rclone).",
                        file=sys.stderr,
                    )
                sys.exit(1)

            logged_in_recheck, recheck_err = asyncio.run(check_rclone_login())
            if not logged_in_recheck:
                print(
                    f"Error: Google Drive authentication check failed again: {recheck_err}",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
            print("Operation aborted.", file=sys.stderr)
            sys.exit(1)

    if args.command == "list":
        asyncio.run(list_backups_cli())
    elif args.command == "backup":
        asyncio.run(run_backup_cli())
    elif args.command == "restore":
        asyncio.run(verify_restore_cli())
    elif args.command == "restore-override":
        asyncio.run(run_restore_override_cli())


if __name__ == "__main__":
    main()
