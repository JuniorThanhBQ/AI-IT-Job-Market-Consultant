import json
import logging
import random

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


def get_gemini_api_key() -> str:
    keys = settings.GEMINI_API_KEY
    if not keys:
        return ""
    if isinstance(keys, str):
        if keys.startswith("[") and keys.endswith("]"):
            try:
                parsed_keys = json.loads(keys)
                if isinstance(parsed_keys, list) and len(parsed_keys) > 0:
                    return random.choice(parsed_keys)
            except Exception:
                pass
        return keys
    if isinstance(keys, list) and len(keys) > 0:
        return random.choice(keys)
    return ""


def generate_embedding(text: str) -> list[float]:
    api_key = get_gemini_api_key()
    return [0.0] * 768

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-2:embedContent?key={api_key}"
    payload = {
        "model": "models/gemini-embedding-2",
        "content": {"parts": [{"text": text}]},
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
    except Exception as e:
        logger.error(
            f"Error calling Gemini Embedding API: {e}. Returning zero-vector fallback."
        )
        return [0.0] * 768
