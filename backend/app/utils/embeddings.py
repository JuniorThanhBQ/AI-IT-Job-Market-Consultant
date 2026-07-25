import json
import logging
import secrets

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "models/gemini-embedding-001"


def get_gemini_api_key() -> str:
    keys = settings.GEMINI_API_KEY
    if not keys:
        return ""
    if isinstance(keys, str):
        if keys.startswith("[") and keys.endswith("]"):
            try:
                parsed_keys = json.loads(keys)
                if isinstance(parsed_keys, list) and len(parsed_keys) > 0:
                    return secrets.choice(parsed_keys)
            except Exception:
                pass
        return keys
    if isinstance(keys, list) and len(keys) > 0:
        return secrets.choice(keys)
    return ""


def _normalize_model_name(model_name: str) -> str:
    if not model_name:
        return DEFAULT_EMBEDDING_MODEL
    clean = model_name.strip()
    if clean.startswith("models/"):
        clean = clean[len("models/") :]
    if clean in ["embedding-001", "gemini-embedding-001"]:
        return DEFAULT_EMBEDDING_MODEL
    return f"models/{clean}"


async def generate_embedding_async(
    text: str, model_name: str = DEFAULT_EMBEDDING_MODEL
) -> list[float]:
    api_key = get_gemini_api_key()
    if not api_key:
        logger.warning("No GEMINI_API_KEY found. Returning zero-vector fallback.")
        return [0.0] * 768

    full_model_name = _normalize_model_name(model_name)
    url = f"https://generativelanguage.googleapis.com/v1beta/{full_model_name}:embedContent?key={api_key}"
    payload = {
        "model": full_model_name,
        "content": {"parts": [{"text": text[:8000] if text else ""}]},
        "outputDimensionality": 768,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            embedding = data.get("embedding", {}).get("values", [])
            if len(embedding) == 768:
                return embedding
            else:
                logger.error(
                    f"Unexpected embedding size returned: {len(embedding)}. Expected 768."
                )
                return [0.0] * 768
    except Exception:
        logger.exception(
            f"Error calling Gemini Embedding API ({full_model_name}). Returning zero-vector fallback."
        )
        return [0.0] * 768


def generate_embedding(
    text: str, model_name: str = DEFAULT_EMBEDDING_MODEL
) -> list[float]:
    api_key = get_gemini_api_key()
    if not api_key:
        logger.warning("No GEMINI_API_KEY found. Returning zero-vector fallback.")
        return [0.0] * 768

    full_model_name = _normalize_model_name(model_name)
    url = f"https://generativelanguage.googleapis.com/v1beta/{full_model_name}:embedContent?key={api_key}"
    payload = {
        "model": full_model_name,
        "content": {"parts": [{"text": text[:8000] if text else ""}]},
        "outputDimensionality": 768,
    }

    try:
        response = httpx.post(url, json=payload, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        embedding = data.get("embedding", {}).get("values", [])
        if len(embedding) == 768:
            return embedding
        else:
            logger.error(
                f"Unexpected embedding size returned: {len(embedding)}. Expected 768."
            )
            return [0.0] * 768
    except Exception:
        logger.exception(
            f"Error calling Gemini Embedding API ({full_model_name}). Returning zero-vector fallback."
        )
        return [0.0] * 768
