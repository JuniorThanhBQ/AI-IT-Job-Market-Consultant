import logging
from collections.abc import AsyncGenerator, Generator

from google.genai import types

from app.google_genai.client import GenAIClientManager

logger = logging.getLogger(__name__)


class BaseModelService:
    def __init__(
        self, client_manager: GenAIClientManager, model: str, model_name_log: str
    ):
        self.client_manager = client_manager
        self.model = model
        self.model_name_log = model_name_log

    async def generate_content_async(
        self, prompt: str, config: types.GenerateContentConfig | None = None
    ) -> str:
        try:
            client = self.client_manager.get_client()
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception:
            logger.exception(
                f"Error during async {self.model_name_log} model content generation."
            )
            raise

    def generate_content(
        self, prompt: str, config: types.GenerateContentConfig | None = None
    ) -> str:
        try:
            client = self.client_manager.get_client()
            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )
            return response.text or ""
        except Exception:
            logger.exception(
                f"Error during {self.model_name_log} model content generation."
            )
            raise

    async def generate_stream_async(
        self, prompt: str, config: types.GenerateContentConfig | None = None
    ) -> AsyncGenerator[str]:
        try:
            client = self.client_manager.get_client()
            response_stream = await client.aio.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config,
            )
            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception:
            logger.exception(
                f"Error during async streaming {self.model_name_log} model content generation."
            )
            raise

    def generate_stream(
        self, prompt: str, config: types.GenerateContentConfig | None = None
    ) -> Generator[str]:
        try:
            client = self.client_manager.get_client()
            response_stream = client.models.generate_content_stream(
                model=self.model,
                contents=prompt,
                config=config,
            )
            for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
        except Exception:
            logger.exception(
                f"Error during streaming {self.model_name_log} model content generation."
            )
            raise
