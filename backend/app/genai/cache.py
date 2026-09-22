import logging
from typing import Any

from google.genai import types

from app.genai.client import GenAIClientManager

logger = logging.getLogger(__name__)


class ContextCacheService:
    def __init__(self, client_manager: GenAIClientManager):
        self.client_manager = client_manager

    def create_cache(
        self,
        model: str,
        contents: list[Any],
        ttl_seconds: int = 900,
        display_name: str | None = None,
    ) -> str:
        try:
            client = self.client_manager.get_client()
            cache = client.caches.create(
                model=model,
                config=types.CreateCachedContentConfig(
                    contents=contents,
                    ttl=f"{ttl_seconds}s",
                    display_name=display_name,
                ),
            )
            if cache.name is None:
                raise ValueError("Created context cache has no name returned.")
            return cache.name
        except Exception:
            logger.exception("Error creating context cache.")
            raise

    def get_cache(self, cache_name: str) -> Any:
        try:
            client = self.client_manager.get_client()
            return client.caches.get(name=cache_name)
        except Exception:
            logger.exception(
                f"Error retrieving context cache details for: {cache_name}"
            )
            raise

    def list_caches(self) -> Any:
        try:
            client = self.client_manager.get_client()
            return client.caches.list()
        except Exception:
            logger.exception("Error listing context caches.")
            raise

    def delete_cache(self, cache_name: str) -> None:
        try:
            client = self.client_manager.get_client()
            client.caches.delete(name=cache_name)
        except Exception:
            logger.exception(f"Error deleting context cache: {cache_name}")
            raise
