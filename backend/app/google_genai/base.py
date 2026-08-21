import logging
from collections.abc import AsyncGenerator, Generator

from google.genai import types

from app.google_genai.client import GenAIClientManager

logger = logging.getLogger(__name__)


class BaseModelService:
    def __init__(
        self,
        client_manager: GenAIClientManager,
        model: str | list[str],
        model_name_log: str,
    ):
        self.client_manager = client_manager
        self.models: list[str] = [model] if isinstance(model, str) else list(model)
        self.model = self.models[0] if self.models else ""
        self.model_name_log = model_name_log

    async def generate_content_async(
        self, prompt: str, config: types.GenerateContentConfig | None = None
    ) -> str:
        last_error: Exception | None = None
        for m in self.models:
            try:
                local_config = (
                    config.model_copy() if config else types.GenerateContentConfig()
                )
                if "gemini-3" in m:
                    local_config.thinking_config = types.ThinkingConfig(
                        thinking_level=types.ThinkingLevel.MINIMAL
                    )
                else:
                    local_config.thinking_config = types.ThinkingConfig(
                        thinking_budget=768
                    )

                client = self.client_manager.get_client()
                response = await client.aio.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=local_config,
                )
                return response.text or ""
            except Exception as e:
                last_error = e
                logger.warning(
                    "Model '%s' failed in async %s generation: %s. Rotating to next model if available.",
                    m,
                    self.model_name_log,
                    e,
                )
        logger.exception(
            "All candidate models failed during async %s generation.",
            self.model_name_log,
        )
        if last_error:
            raise last_error
        raise RuntimeError("No candidate models configured.")

    def generate_content(
        self, prompt: str, config: types.GenerateContentConfig | None = None
    ) -> str:
        last_error: Exception | None = None
        for m in self.models:
            try:
                local_config = (
                    config.model_copy() if config else types.GenerateContentConfig()
                )
                if "gemini-3" in m:
                    local_config.thinking_config = types.ThinkingConfig(
                        thinking_level=types.ThinkingLevel.MINIMAL
                    )
                else:
                    local_config.thinking_config = types.ThinkingConfig(
                        thinking_budget=768
                    )

                client = self.client_manager.get_client()
                response = client.models.generate_content(
                    model=m,
                    contents=prompt,
                    config=local_config,
                )
                return response.text or ""
            except Exception as e:
                last_error = e
                logger.warning(
                    "Model '%s' failed in %s generation: %s. Rotating to next model if available.",
                    m,
                    self.model_name_log,
                    e,
                )
        logger.exception(
            "All candidate models failed during %s generation.",
            self.model_name_log,
        )
        if last_error:
            raise last_error
        raise RuntimeError("No candidate models configured.")

    async def generate_stream_async(
        self, prompt: str, config: types.GenerateContentConfig | None = None
    ) -> AsyncGenerator[str]:
        last_error: Exception | None = None
        for m in self.models:
            try:
                local_config = (
                    config.model_copy() if config else types.GenerateContentConfig()
                )
                if "gemini-3" in m:
                    local_config.thinking_config = types.ThinkingConfig(
                        thinking_level=types.ThinkingLevel.MINIMAL
                    )
                else:
                    local_config.thinking_config = types.ThinkingConfig(
                        thinking_budget=768
                    )

                client = self.client_manager.get_client()
                response_stream = await client.aio.models.generate_content_stream(
                    model=m,
                    contents=prompt,
                    config=local_config,
                )
                async for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                last_error = e
                logger.warning(
                    "Model '%s' failed in async streaming %s generation: %s. Rotating to next model if available.",
                    m,
                    self.model_name_log,
                    e,
                )
        logger.exception(
            "All candidate models failed during async streaming %s generation.",
            self.model_name_log,
        )
        if last_error:
            raise last_error
        raise RuntimeError("No candidate models configured.")

    def generate_stream(
        self, prompt: str, config: types.GenerateContentConfig | None = None
    ) -> Generator[str]:
        last_error: Exception | None = None
        for m in self.models:
            try:
                local_config = (
                    config.model_copy() if config else types.GenerateContentConfig()
                )
                if "gemini-3" in m:
                    local_config.thinking_config = types.ThinkingConfig(
                        thinking_level=types.ThinkingLevel.MINIMAL
                    )
                else:
                    local_config.thinking_config = types.ThinkingConfig(
                        thinking_budget=768
                    )

                client = self.client_manager.get_client()
                response_stream = client.models.generate_content_stream(
                    model=m,
                    contents=prompt,
                    config=local_config,
                )
                for chunk in response_stream:
                    if chunk.text:
                        yield chunk.text
                return
            except Exception as e:
                last_error = e
                logger.warning(
                    "Model '%s' failed in streaming %s generation: %s. Rotating to next model if available.",
                    m,
                    self.model_name_log,
                    e,
                )
        logger.exception(
            "All candidate models failed during streaming %s generation.",
            self.model_name_log,
        )
        if last_error:
            raise last_error
        raise RuntimeError("No candidate models configured.")
