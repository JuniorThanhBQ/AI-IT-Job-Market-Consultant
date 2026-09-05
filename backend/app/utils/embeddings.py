import logging

from app.google_genai.client import GenAIClientManager
from app.google_genai.configs import GenAIConfig
from app.google_genai.embedding import EmbeddingService
from app.google_genai.models import GeminiModel

logger = logging.getLogger(__name__)

config = GenAIConfig()
client_manager = GenAIClientManager(config)
embedding_service = EmbeddingService(client_manager)

DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"
embedding_cache: dict[tuple[str, str], list[float]] = {}


def get_gemini_api_key() -> str:
    return client_manager._get_api_key()


def normalize_model_name(model_name: str) -> GeminiModel:
    if not model_name:
        return GeminiModel.GEMINI_EMBEDDING_001

    clean = model_name.strip()
    if clean.endswith("gemini-embedding-2"):
        return GeminiModel.GEMINI_EMBEDDING_2
    if clean.endswith("gemini-embedding-001") or clean.endswith("embedding-001"):
        return GeminiModel.GEMINI_EMBEDDING_001

    try:
        return GeminiModel(clean)
    except ValueError:
        return GeminiModel.GEMINI_EMBEDDING_001


async def generate_embedding_async(
    text: str, model_name: str = DEFAULT_EMBEDDING_MODEL
) -> list[float]:
    cache_key = (text, model_name)
    if cache_key in embedding_cache:
        return embedding_cache[cache_key]

    model = normalize_model_name(model_name)
    val = await embedding_service.generate_embedding_async(text, model=model)
    if len(embedding_cache) >= 1024:
        embedding_cache.pop(next(iter(embedding_cache)))

    embedding_cache[cache_key] = val
    return val
