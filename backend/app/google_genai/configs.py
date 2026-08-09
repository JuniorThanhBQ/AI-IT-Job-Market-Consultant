from pydantic import BaseModel

from app.core.config import settings


class GenAIConfig(BaseModel):
    api_keys: list[str] | str = settings.GEMINI_API_KEY
    use_vertex: bool = False
    default_flash_model: str = "gemini-3.6-flash"
    default_pro_model: str = "gemini-2.5-pro"
    default_embedding_model: str = "gemini-embedding-001"
    flash_models: list[str] = [
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-2.5-flash",
    ]
    pro_models: list[str] = [
        "gemini-2.5-pro",
        "gemini-3-pro-preview",
        "gemini-3.1-pro-preview",
    ]
    request_timeout: float = 30.0
    max_retries: int = 3
