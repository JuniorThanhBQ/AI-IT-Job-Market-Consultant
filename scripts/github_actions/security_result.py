import json
import os
from pathlib import Path

NON_BLOCKING_CHECKS = {"security-packages"}

results = json.loads(os.environ["SCAN_RESULTS"])
failed = []
rows = ["| Scanner | Job | Scan |", "| --- | --- | --- |"]
for name, job in results.items():
    outcome = job.get("outputs", {}).get("scan-outcome", "missing")
    rows.append(f"| {name} | {job['result']} | {outcome} |")
    if (
        job["result"] != "success" or outcome != "success"
    ) and name not in NON_BLOCKING_CHECKS:
        failed.append(name)

Path(os.environ["GITHUB_STEP_SUMMARY"]).write_text("\n".join(rows) + "\n")
if failed:
    print("::error::Security checks failed: " + ", ".join(failed))

raise SystemExit(bool(failed))
