import os
from pathlib import Path
from typing import Any

from pydantic.fields import FieldInfo
from pydantic_settings import PydanticBaseSettingsSource


class FlatEnvSettingsSource(PydanticBaseSettingsSource):
    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        return None, field_name, False

    def __call__(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        env_files = self.settings_cls.model_config.get("env_file", [])
        if env_files is None:
            env_files = []
        elif isinstance(env_files, (str, Path)):
            env_files = [env_files]

        for env_file in env_files:
            for base_path in [Path("."), Path(__file__).resolve().parent.parent.parent]:
                path = base_path / env_file
                if path.is_file():
                    try:
                        for line in path.read_text(encoding="utf-8").splitlines():
                            line = line.strip()
                            if not line or line.startswith("#"):
                                continue
                            if "=" in line:
                                k, v = line.split("=", 1)
                                k = k.strip()
                                v = v.strip().strip("'\"")
                                data[k] = v
                    except Exception:
                        pass

        for k, v in os.environ.items():
            data[k] = v
        return data
