import logging
import time

from google.genai import types

from app.genai.client import GenAIClientManager
from app.genai.models import GeminiModel

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
                return EmbeddingResult(
                    response.embeddings[0].values,
                    token_used=token_used,
                    latency=latency,
                    log=f"Successfully generated embedding using model {model.value}.",
                )

            return EmbeddingResult(
                [0.0] * 768,
                token_used=0.0,
                latency=latency,
                log="Empty embeddings returned from GenAI SDK",
            )
        except Exception as e:
            latency = time.perf_counter() - start_time
            err_msg = f"Error calling Gemini Embedding API via ({model.value}): {e}"
            logger.exception(err_msg)
            return EmbeddingResult(
                [0.0] * 768,
                token_used=0.0,
                latency=latency,
                log=err_msg,
            )
