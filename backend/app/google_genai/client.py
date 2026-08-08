import json
import secrets

from google import genai

from app.google_genai.configs import GenAIConfig


class GenAIClientManager:
    _instance = None
    _clients: dict[str, genai.Client] = {}
    _vertex_client: genai.Client | None = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

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
                except Exception as e:
                    raise ValueError(
                        f"GEMINI_API_KEY in .env is configured as a list, but has a syntax/JSON error: {e}. Raw value: {keys}"
                    )
            else:
                return keys
        if isinstance(keys, list):
            return secrets.choice(keys) if keys else ""
        return keys

    def get_client(self) -> genai.Client:
        if self.config.use_vertex:
            if self._vertex_client is None:
                self._vertex_client = genai.Client(vertexai=True)
            return self._vertex_client

        api_key = self._get_api_key()
        if api_key not in self._clients:
            self._clients[api_key] = genai.Client(api_key=api_key)
        return self._clients[api_key]
