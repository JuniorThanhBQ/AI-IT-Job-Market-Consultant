import logging
from collections.abc import AsyncGenerator

from google.genai import types

from app.google_genai import FlashModelService, GenAIClientManager, GenAIConfig
from app.google_genai.prompts.templates import get_prompt_template

logger = logging.getLogger(__name__)


async def execute_market_consultant_stream(
    query: str,
    rag_context: str,
) -> AsyncGenerator[str]:
    if not rag_context or not rag_context.strip():
        yield (
            "Không có dữ liệu tuyển dụng để phân tích. "
            "Vui lòng thử câu hỏi khác hoặc kiểm tra lại hệ thống."
        )
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
        yield (
            "Xin lỗi, hiện tại không thể phân tích dữ liệu thị trường "
            "do lỗi kết nối với AI."
        )


async def execute_market_consultant(
    query: str,
    rag_context: str,
) -> str:
    if not rag_context or not rag_context.strip():
        return (
            "Không có dữ liệu tuyển dụng để phân tích. "
            "Vui lòng thử câu hỏi khác hoặc kiểm tra lại hệ thống."
        )

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
        return (
            "Xin lỗi, hiện tại không thể phân tích dữ liệu thị trường "
            "do lỗi kết nối với AI."
        )
