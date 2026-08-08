import logging
import time

from google.genai import types

from app.google_genai.client import GenAIClientManager
from app.google_genai.models import GeminiModel

logger = logging.getLogger(__name__)


class EmbeddingResult(list):
    def __init__(self, values, token_used=0.0, latency=0.0, log=None):
        super().__init__(values)
        self.token_used = token_used
        self.latency = latency
        self.log = log


class EmbeddingService:
    def __init__(self, client_manager: GenAIClientManager):
        self.client_manager = client_manager

    async def generate_embedding_async(
        self, text: str, model: GeminiModel = GeminiModel.GEMINI_EMBEDDING_001
    ) -> list[float]:
        start_time = time.perf_counter()
        token_used = float(max(1, len(text) // 4)) if text else 0.0
        try:
            client = self.client_manager.get_client()
            if not client:
                logger.warning(
                    "No Gemini client generated. Returning zero-vector fallback."
                )
                return EmbeddingResult(
                    [0.0] * 768,
                    token_used=0.0,
                    latency=0.0,
                    log="No Gemini client generated",
                )

            clean_text = text[:8000] if text else ""
            response = await client.aio.models.embed_content(
                model=model.value,
                contents=clean_text,
                config=types.EmbedContentConfig(output_dimensionality=768),
            )
            latency = time.perf_counter() - start_time
            if (
                response
                and response.embeddings
                and response.embeddings[0].values is not None
            ):
                log_msg = f"Successfully generated embedding using model {model.value}."
                return EmbeddingResult(
                    response.embeddings[0].values,
                    token_used=token_used,
                    latency=latency,
                    log=log_msg,
                )

            logger.error("Empty embeddings returned from GenAI SDK.")
            return EmbeddingResult(
                [0.0] * 768,
                token_used=0.0,
                latency=latency,
                log="Empty embeddings returned from GenAI SDK",
            )
        except Exception as e:
            latency = time.perf_counter() - start_time
            err_msg = f"Error calling Gemini Embedding API via unified SDK ({model.value}): {e}"
            logger.exception(err_msg)
            return EmbeddingResult(
                [0.0] * 768,
                token_used=0.0,
                latency=latency,
                log=err_msg,
            )

    def generate_embedding(
        self, text: str, model: GeminiModel = GeminiModel.GEMINI_EMBEDDING_001
    ) -> list[float]:
        start_time = time.perf_counter()
        token_used = float(max(1, len(text) // 4)) if text else 0.0
        try:
            client = self.client_manager.get_client()
            if not client:
                logger.warning(
                    "No Gemini client generated. Returning zero-vector fallback."
                )
                return EmbeddingResult(
                    [0.0] * 768,
                    token_used=0.0,
                    latency=0.0,
                    log="No Gemini client generated",
                )

            clean_text = text[:8000] if text else ""
            response = client.models.embed_content(
                model=model.value,
                contents=clean_text,
                config=types.EmbedContentConfig(output_dimensionality=768),
            )
            latency = time.perf_counter() - start_time
            if (
                response
                and response.embeddings
                and response.embeddings[0].values is not None
            ):
                log_msg = f"Successfully generated embedding using model {model.value}."
                return EmbeddingResult(
                    response.embeddings[0].values,
                    token_used=token_used,
                    latency=latency,
                    log=log_msg,
                )

            logger.error("Empty embeddings returned from GenAI SDK.")
            return EmbeddingResult(
                [0.0] * 768,
                token_used=0.0,
                latency=latency,
                log="Empty embeddings returned from GenAI SDK",
            )
        except Exception as e:
            latency = time.perf_counter() - start_time
            err_msg = f"Error calling Gemini Embedding API via unified SDK ({model.value}): {e}"
            logger.exception(err_msg)
            return EmbeddingResult(
                [0.0] * 768,
                token_used=0.0,
                latency=latency,
                log=err_msg,
            )
