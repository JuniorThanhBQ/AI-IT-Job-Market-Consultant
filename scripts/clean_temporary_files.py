import argparse
from pathlib import Path
import shutil


def main():
    parser = argparse.ArgumentParser(
        description="Clean temporary build and cache files."
    )
    parser.add_argument(
        "--dist",
        action="store_true",
        help="Perform a full clean including node_modules and virtual environments.",
    )
    args = parser.parse_args()

    for name in ("__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"):
        for p in Path(".").rglob(name):
            shutil.rmtree(p, ignore_errors=True)

    shutil.rmtree("frontend/.next", ignore_errors=True)

    if args.dist:
        shutil.rmtree(".venv", ignore_errors=True)
        shutil.rmtree("frontend/node_modules", ignore_errors=True)
        shutil.rmtree("frontend/dist", ignore_errors=True)
        for p in Path(".").rglob("node_modules"):
            shutil.rmtree(p, ignore_errors=True)
        for p in Path(".").rglob("dist"):
            shutil.rmtree(p, ignore_errors=True)


if __name__ == "__main__":
    main()
