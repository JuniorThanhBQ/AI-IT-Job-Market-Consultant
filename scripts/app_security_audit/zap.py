import json
import os
import subprocess
from urllib.parse import urlsplit

LEVELS = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3}


def run(root, image, config, target):
    url = urlsplit(target)
    if url.scheme not in ("http", "https") or not url.hostname:
        raise ValueError("ZAP target must be an HTTP(S) URL")

    threshold = LEVELS[config["fail-on"]]
    folder = root / "docs" / "testing" / "zap"
    folder.mkdir(parents=True, exist_ok=True)
    if os.name != "nt":
        folder.chmod(0o777)

    report = folder / "report.json"
    report.unlink(missing_ok=True)
    code = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--add-host",
            "host.docker.internal:host-gateway",
            "-v",
            f"{folder}:/zap/wrk:rw",
            image,
            "zap-baseline.py",
            "-t",
            target,
            "-I",
            "-J",
            report.name,
            "-r",
            "report.html",
        ],
        check=False,
    ).returncode
    if code not in (0, 1, 2):
        return code

    data = json.loads(report.read_text("utf-8"))
    if not data.get("site"):
        raise ValueError("ZAP report contains no scanned sites")

    alerts = [alert for site in data["site"] for alert in site.get("alerts", [])]
    return int(any(int(alert["riskcode"]) >= threshold for alert in alerts))
