import argparse
import shutil
from pathlib import Path

CACHE_DIRS: set[str] = {
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "agents.egg-info",
    ".vercel",
}

DIST_DIRS: set[str] = {
    "node_modules",
    "dist",
}

FIXED_PATHS: list[str] = [
    "frontend/.next",
]

DIST_FIXED_PATHS: list[str] = [
    ".venv",
    "frontend/node_modules",
    "frontend/dist",
]


def remove(path: Path, dry_run: bool) -> None:
    if dry_run:
        print(f"would remove: {path}")
    else:
        shutil.rmtree(path, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dist", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    target_names = CACHE_DIRS | (DIST_DIRS if args.dist else set())

    seen: set[Path] = set()
    for p in sorted(Path(".").rglob("*")):
        if (
            p.name in target_names
            and p.is_dir()
            and not any(parent in seen for parent in p.parents)
        ):
            seen.add(p)
            remove(p, args.dry_run)

    fixed = FIXED_PATHS + (DIST_FIXED_PATHS if args.dist else [])
    for path_str in fixed:
        p = Path(path_str)
        if p.exists():
            remove(p, args.dry_run)


if __name__ == "__main__":
    main()
