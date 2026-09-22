import json
import secrets

from google import genai

from app.genai.configs import GenAIConfig


class GenAIClientManager:
    instance = None
    clients: dict[str, genai.Client] = {}
    vertex_client: genai.Client | None = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, config: GenAIConfig):
        if not hasattr(self, "config"):
            self.config = config

    def _get_api_key(self) -> str:
        keys = self.config.api_keys
        if not keys:
            return ""
        if isinstance(keys, str):
            stripped = keys.strip()
            if stripped.startswith("[") and stripped.endswith("]"):
                try:
                    keys = json.loads(stripped)
                except Exception:
                    raise ValueError(
                        "GEMINI_API_KEY in .env is configured as a list, but has a syntax/JSON error."
                    )
            else:
                return keys
        if isinstance(keys, list):
            return secrets.choice(keys) if keys else ""
        return keys

    def get_client(self) -> genai.Client:
        if self.config.use_vertex:
            if self.vertex_client is None:
                self.vertex_client = genai.Client(vertexai=True)
            return self.vertex_client

        api_key = self._get_api_key()
        if api_key not in self.clients:
            self.clients[api_key] = genai.Client(api_key=api_key)
        return self.clients[api_key]
