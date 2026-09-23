import argparse
import configparser
import os
import shutil
import subprocess
import sys
from pathlib import Path


def find_system_rclone_config() -> Path | None:
    try:
        res = subprocess.run(
            ["rclone", "config", "file"],
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                stripped = line.strip()
                if stripped.endswith("rclone.conf") and Path(stripped).exists():
                    return Path(stripped)
    except FileNotFoundError:
        pass

    candidates: list[Path] = []
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA")
        if appdata:
            candidates.append(Path(appdata) / "rclone" / "rclone.conf")
    else:
        home = Path.home()
        candidates.extend(
            [
                home / ".config" / "rclone" / "rclone.conf",
                home / ".rclone.conf",
            ]
        )

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return None


def get_target_config_paths() -> list[Path]:
    root_dir = Path(__file__).resolve().parent.parent
    return [
        root_dir / "celery_app" / "rclone.conf",
        root_dir / "server" / "rclone.conf",
    ]


def validate_rclone_content(content: str) -> bool:
    parser = configparser.ConfigParser()
    try:
        parser.read_string(content)
        if not parser.has_section("gdrive"):
            return False

        section = parser["gdrive"]
        return "type" in section and "token" in section
    except Exception:
        return False


def sync_from_system_config(source_path: Path, target_paths: list[Path]) -> bool:
    content = source_path.read_text(encoding="utf-8")
    if not validate_rclone_content(content):
        print(f"Warning: {source_path} does not contain valid [gdrive] section.")
        return False

    for target in target_paths:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target)
        print(f"Synced {source_path} -> {target}")

    return True


def prompt_manual_config(target_paths: list[Path]) -> bool:
    print("\n--- Manual Rclone Config Input ---")
    client_id = input("Enter client_id: ").strip()
    client_secret = input("Enter client_secret: ").strip()
    token = input("Enter token JSON: ").strip()

    if not client_id or not client_secret or not token:
        return False

    config_template = f"""[gdrive]
type = drive
scope = drive
client_id = {client_id}
client_secret = {client_secret}
token = {token}
team_drive =
"""

    if not validate_rclone_content(config_template):
        return False

    for target in target_paths:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(config_template, encoding="utf-8")
        print(f"Wrote configuration to {target}")

    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()
    target_paths = get_target_config_paths()
    if args.interactive:
        success = prompt_manual_config(target_paths)
        if not success:
            sys.exit(1)
        print("Rclone configuration remade successfully.")
        return

    source = find_system_rclone_config()
    if source:
        print(f"Detected system rclone configuration at: {source}")
        success = sync_from_system_config(source, target_paths)
        if success:
            return

    success = prompt_manual_config(target_paths)
    if not success:
        sys.exit(1)

    print("Rclone configuration remade successfully.")


if __name__ == "__main__":
    main()
