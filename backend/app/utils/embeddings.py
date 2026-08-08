import logging

from app.google_genai.client import GenAIClientManager
from app.google_genai.configs import GenAIConfig
from app.google_genai.embedding import EmbeddingService
from app.google_genai.models import GeminiModel

logger = logging.getLogger(__name__)

_config = GenAIConfig()
_client_manager = GenAIClientManager(_config)
_embedding_service = EmbeddingService(_client_manager)

DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"


def get_gemini_api_key() -> str:
    return _client_manager._get_api_key()


def _normalize_model_name(model_name: str) -> GeminiModel:
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
    model = _normalize_model_name(model_name)
    return await _embedding_service.generate_embedding_async(text, model=model)


def generate_embedding(
    text: str, model_name: str = DEFAULT_EMBEDDING_MODEL
) -> list[float]:
    model = _normalize_model_name(model_name)
    return _embedding_service.generate_embedding(text, model=model)
