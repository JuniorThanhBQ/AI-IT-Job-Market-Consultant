import os
import shlex
import subprocess
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.core.config import settings


def main():
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print("Usage: make backup-restore CMD=[list|backup|restore]")
        sys.exit(1)

    cmd = sys.argv[1].strip()

    # Validate against allowed commands to prevent argument/command injection
    allowed_cmds = {"list", "backup", "restore"}
    if cmd not in allowed_cmds:
        print(f"Error: Invalid command '{cmd}'. Must be one of {allowed_cmds}")
        sys.exit(1)

    safe_cmd = shlex.quote(cmd)
    pwd = settings.backup.BACKUP_RESTORE_ADMIN_PASSWORD

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.db.backup.cli",
            "--password",
            pwd,
            safe_cmd,
        ]
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
