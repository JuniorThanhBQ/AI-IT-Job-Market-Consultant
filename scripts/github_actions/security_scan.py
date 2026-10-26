import argparse
import os
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scanner", choices=["semgrep", "trivy-config"])
    args = parser.parse_args()
    settings = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))
    config = settings["tool"]["app-security-audit"]
    if args.scanner == "semgrep":
        config = config["semgrep"]
        options = [arg for rule in config["rules"] for arg in ("--config", rule)]
        options += [
            arg for level in config["severity"] for arg in ("--severity", level)
        ]
        options += [
            arg for path in config.get("exclude", []) for arg in ("--exclude", path)
        ]
        return subprocess.run(
            [
                "semgrep",
                "scan",
                *options,
                "--error",
                "--metrics=off",
                "--sarif-output=semgrep.sarif",
                ".",
            ],
            cwd=ROOT,
            check=False,
        ).returncode

    config = config["trivy"]
    values = {
        key: ",".join(value) if isinstance(value, list) else value
        for key, value in config.items()
    }
    if any("\n" in value or "\r" in value for value in values.values()):
        raise ValueError("Trivy configuration values must be single-line strings")
    with Path(os.environ["GITHUB_OUTPUT"]).open("a", encoding="utf-8") as output:
        output.writelines(f"{key}={value}\n" for key, value in values.items())

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
