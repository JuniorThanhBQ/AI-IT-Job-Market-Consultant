import os
import tempfile

if not os.environ.get("HF_HOME"):
    try:
        home = os.path.expanduser("~")
        if not os.path.exists(home) or not os.access(home, os.W_OK):
            os.environ["HF_HOME"] = os.path.join(tempfile.gettempdir(), "huggingface")
    except Exception:
        os.environ["HF_HOME"] = os.path.join(tempfile.gettempdir(), "huggingface")

import asyncio
import logging
from functools import lru_cache

from sentence_transformers import CrossEncoder

from app.modules.company.models import Company
from app.modules.job.models import Job

logger = logging.getLogger(__name__)

_MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def _get_cross_encoder() -> CrossEncoder:
    logger.info("Loading cross-encoder model: %s", _MODEL_NAME)
    return CrossEncoder(_MODEL_NAME)


def _run_cross_encoder(
    query: str,
    candidates: list[tuple[Job, Company, float]],
    limit: int,
) -> list[tuple[Job, Company, float]]:
    cross_encoder = _get_cross_encoder()

    pairs = []
    for job, company, _distance in candidates:
        doc_text = (
            f"Company: {company.name}\n"
            f"Job Title: {job.title}\n"
            f"Description: {job.vector_context[:300]}\n"
        )
        if job.skills:
            skill_names = [skill.name for skill in job.skills]
            doc_text += f"Skills: {', '.join(skill_names)}\n"
        pairs.append((query, doc_text))

    scores: list[float] = cross_encoder.predict(pairs).tolist()

    scored = sorted(
        zip(scores, candidates, strict=False),
        key=lambda x: x[0],
        reverse=True,
    )
    return [cand for _score, cand in scored[:limit]]


async def _fallback_gemini_rerank(
    query: str,
    candidates: list[tuple[Job, Company, float]],
    limit: int,
) -> list[tuple[Job, Company, float]]:
    from google.genai import types

    from app.google_genai import FlashModelService, GenAIClientManager, GenAIConfig
    from app.google_genai.prompts.templates import get_prompt_template

    docs_text = ""
    for idx, (job, company, _distance) in enumerate(candidates):
        docs_text += f"[Document Index: {idx}]\n"
        docs_text += f"Company: {company.name}\n"
        docs_text += f"Job Title: {job.title}\n"
        docs_text += f"Description: {job.vector_context[:300]}\n"
        if job.skills:
            skill_names = [skill.name for skill in job.skills]
            docs_text += f"Skills: {', '.join(skill_names)}\n"
        docs_text += "\n"

    prompt = get_prompt_template("rerank_candidates", query=query, docs_text=docs_text)

    config = GenAIConfig()
    config.default_flash_model = "gemini-3.5-flash-lite"
    client_manager = GenAIClientManager(config)
    flash_service = FlashModelService(client_manager)

    generation_config = types.GenerateContentConfig(temperature=0.0)
    response = await flash_service.generate_content_async(
        prompt, config=generation_config
    )

    clean_res = response.strip().replace("[", "").replace("]", "")
    indices = [int(i.strip()) for i in clean_res.split(",") if i.strip().isdigit()]

    reranked = []
    seen: set[int] = set()
    for idx in indices:
        if 0 <= idx < len(candidates) and idx not in seen:
            reranked.append(candidates[idx])
            seen.add(idx)

    for idx, cand in enumerate(candidates):
        if idx not in seen:
            reranked.append(cand)

    return reranked[:limit]


async def rerank_candidates_via_api(
    query: str, candidates: list[tuple[Job, Company, float]], limit: int = 5
) -> list[tuple[Job, Company, float]]:
    if not candidates:
        return []

    try:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, _run_cross_encoder, query, candidates, limit
        )
    except Exception:
        logger.exception("Cross-encoder reranking failed, falling back to Gemini API")

    try:
        return await _fallback_gemini_rerank(query, candidates, limit)
    except Exception:
        logger.exception(
            "Gemini fallback reranking also failed, returning top-%d by vector distance",
            limit,
        )
        return candidates[:limit]
