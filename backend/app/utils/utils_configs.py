import json
import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from pydantic.fields import FieldInfo
from pydantic_settings import PydanticBaseSettingsSource

logger = logging.getLogger(__name__)


def normalize_env_files(env_files: Any) -> list[str | Path]:
    if not env_files:
        return []
    if isinstance(env_files, (str, Path)):
        return [env_files]
    return list(env_files)


def parse_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    results: dict[str, str] = {}
    try:
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                results[k.strip()] = v.strip().strip("'\"")
    except Exception:
        logger.warning(f"Could not read env file: {path}")
    return results


class FlatEnvSettingsSource(PydanticBaseSettingsSource):
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        env_files = normalize_env_files(
            self.settings_cls.model_config.get("env_file", [])
        )
        search_roots = [Path("."), Path(__file__).resolve().parent.parent.parent]

        for env_file in env_files:
            for base_path in search_roots:
                data.update(parse_env_file(base_path / env_file))

        data.update(os.environ)
        return data


def parse_cors(v: Any) -> list[str]:
    if isinstance(v, str):
        v = v.strip()
        if v.startswith("[") and v.endswith("]"):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(i).strip() for i in parsed if str(i).strip()]
            except Exception:
                pass
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list):
        return [str(i).strip() for i in v if str(i).strip()]
    return []


def parse_trusted_host(v: str) -> str:
    cleaned = v.strip()
    if cleaned.startswith(("http://", "https://")):
        parsed = urlparse(cleaned)
        return parsed.hostname or parsed.netloc or cleaned
    return (
        cleaned.split(":")[0]
        if ":" in cleaned and not cleaned.startswith("*")
        else cleaned
    )


def get_secret(name: str, default: str = "") -> str:
    for path in (
        Path(f"/run/secrets/{name.lower()}"),
        Path(f"/run/secrets/{name.upper()}"),
    ):
        if path.is_file():
            return path.read_text().strip()
    return default
