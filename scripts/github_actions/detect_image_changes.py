import os
import subprocess
from fnmatch import fnmatchcase
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUILD_INPUTS = {
    "backend": ("backend/*", "database/*", "pyproject.toml", "uv.lock"),
    "frontend": ("frontend/*",),
    "celery": (
        "celery_app/*",
        "backend/*",
        "scripts/*",
        "pyproject.toml",
        "uv.lock",
    ),
}


def main() -> None:
    before = os.environ.get("BEFORE", "")
    rebuild_all = (
        os.environ["EVENT_NAME"] == "workflow_dispatch"
        or not before
        or set(before) == {"0"}
    )
    if not rebuild_all:
        rebuild_all = (
            subprocess.run(
                ["git", "cat-file", "-e", f"{before}^{{commit}}"],
                cwd=ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            ).returncode
            != 0
        )

    changes = dict.fromkeys(BUILD_INPUTS, True)
    if not rebuild_all:
        diff = subprocess.check_output(
            [
                "git",
                "diff",
                "--name-only",
                "--no-renames",
                "-z",
                before,
                os.environ["GITHUB_SHA"],
                "--",
            ],
            cwd=ROOT,
        )
        files = [os.fsdecode(path) for path in diff.split(b"\0") if path]
        changes = {
            image: any(
                fnmatchcase(path, pattern) for path in files for pattern in patterns
            )
            for image, patterns in BUILD_INPUTS.items()
        }

    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
        output.writelines(
            f"{image}={str(changed).lower()}\n" for image, changed in changes.items()
        )


if __name__ == "__main__":
    main()
