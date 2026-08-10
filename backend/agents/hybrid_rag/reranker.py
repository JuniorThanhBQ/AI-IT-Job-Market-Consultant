import logging

from google.genai import types

from app.google_genai import FlashModelService, GenAIClientManager, GenAIConfig
from app.google_genai.prompts.templates import get_prompt_template
from app.modules.company.models import Company
from app.modules.job.models import Job

logger = logging.getLogger(__name__)


async def rerank_candidates_via_api(
    query: str, candidates: list[tuple[Job, Company, float]], limit: int = 5
) -> list[tuple[Job, Company, float]]:
    if not candidates:
        return []

    try:
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

        prompt = get_prompt_template(
            "rerank_candidates", query=query, docs_text=docs_text
        )

        config = GenAIConfig()
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
    except Exception:
        logger.exception(
            "Gemini reranking failed, returning top candidates by vector distance"
        )
        return candidates[:limit]
