import argparse
import shutil
import subprocess
import tomllib
from pathlib import Path

from app_security_audit import semgrep, trivy, zap

ROOT = Path(__file__).resolve().parents[1]
IMAGES = {
    "trivy": "aquasec/trivy:latest@sha256:790fd66d1697395d8693d1acaa1ea702406a20f109b6fc7bac8db623eca6c06c",
    "semgrep": "semgrep/semgrep:latest@sha256:3db5c7af55eb1f512eac0abf0ab69a97b52c74b5e9a27314c221aee1a78d7ab2",
    "zap": "zaproxy/zap-stable:latest@sha256:5ccfff9a411743ab2615136a2edd7416bec9ce41572fa94e935df38c14adb2b6",
}


def npm_audit(root, _image, config, _target=None):
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        raise FileNotFoundError("npm is required for the frontend audit")
    return subprocess.run(
        [
            npm,
            "audit",
            f"--audit-level={config['audit-level']}",
        ],
        cwd=root / "frontend",
        check=False,
    ).returncode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "scanner",
        nargs="?",
        default="static",
        choices=["static", "all", "npm", *IMAGES],
    )
    parser.add_argument("--target")
    args = parser.parse_args()
    if args.scanner in ("zap", "all") and not args.target:
        parser.error("ZAP requires --target with a running application's URL")

    config = tomllib.loads((ROOT / "pyproject.toml").read_text("utf-8"))
    settings = config["tool"]["app-security-audit"]
    scanners = {
        "trivy": trivy.run,
        "semgrep": semgrep.run,
        "npm": npm_audit,
        "zap": zap.run,
    }
    selected = (
        list(scanners)
        if args.scanner == "all"
        else (
            ["trivy", "semgrep", "npm"] if args.scanner == "static" else [args.scanner]
        )
    )
    results = []
    for name in selected:
        try:
            code = scanners[name](ROOT, IMAGES.get(name), settings[name], args.target)
        except (OSError, ValueError, KeyError) as error:
            print(f"{name}: {error}", flush=True)
            code = 2
        results.append(code)
        print(f"{name}: exit {code}", flush=True)
    return int(any(results))


if __name__ == "__main__":
    raise SystemExit(main())
