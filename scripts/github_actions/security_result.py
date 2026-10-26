import json
import os
from pathlib import Path

results = json.loads(os.environ["SCAN_RESULTS"])
failed = []
rows = ["| Scanner | Job | Scan |", "| --- | --- | --- |"]
for name, job in results.items():
    outcome = job.get("outputs", {}).get("scan-outcome", "missing")
    rows.append(f"| {name} | {job['result']} | {outcome} |")
    if job["result"] != "success" or outcome != "success":
        failed.append(name)

Path(os.environ["GITHUB_STEP_SUMMARY"]).write_text("\n".join(rows) + "\n")
if failed:
    print("::error::Security checks failed: " + ", ".join(failed))

raise SystemExit(bool(failed))
