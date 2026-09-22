import argparse
import json
import sys
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.main import app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, default="api_v2.json")
    args = parser.parse_args()
    filename = args.name.strip() if args.name else "api.json"
    if not filename.endswith(".json"):
        filename = f"{filename}.json"

    output_dir = Path(__file__).resolve().parent.parent / "docs" / "apis"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    schema = app.openapi()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    main()
