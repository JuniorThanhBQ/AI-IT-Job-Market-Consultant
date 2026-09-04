import logging
from collections.abc import AsyncGenerator

from app.google_genai import FlashModelService, GenAIClientManager, GenAIConfig
from app.google_genai.prompts.templates import get_prompt_template
from google.genai import types

logger = logging.getLogger(__name__)


async def execute_market_consultant_stream(
    query: str,
    rag_context: str,
) -> AsyncGenerator[str]:
    if not rag_context or not rag_context.strip():
        yield ("No data")
        return

    prompt = get_prompt_template(
        "market_analysis_agent",
        rag_context=rag_context,
        user_input=query,
    )

    try:
        config = GenAIConfig()
        client_manager = GenAIClientManager(config)
        flash_service = FlashModelService(client_manager)

        generation_config = types.GenerateContentConfig(temperature=0.3)
        async for chunk in flash_service.generate_stream_async(
            prompt, config=generation_config
        ):
            yield chunk
    except Exception:
        logger.exception("Error calling GenAI Flash for market consultant stream")
        yield ("Unable to connect to Gemini Flash")


async def execute_market_consultant(
    query: str,
    rag_context: str,
) -> str:
    if not rag_context or not rag_context.strip():
        return "No data"

    prompt = get_prompt_template(
        "market_analysis_agent",
        rag_context=rag_context,
        user_input=query,
    )

    try:
        config = GenAIConfig()
        client_manager = GenAIClientManager(config)
        flash_service = FlashModelService(client_manager)

        generation_config = types.GenerateContentConfig(temperature=0.3)
        result_text = await flash_service.generate_content_async(
            prompt, config=generation_config
        )
        return result_text.strip()
    except Exception:
        logger.exception("Error calling GenAI Flash for market consultant tool")
        return "Error connection"
