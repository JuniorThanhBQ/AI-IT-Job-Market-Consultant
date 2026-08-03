"""Market Consultant Tool — RAG-based market analysis.

This tool uses the pre-retrieved RAG context (job postings) to answer
market analysis questions via Gemini Flash. It is the existing core
functionality, now wrapped as a callable tool for the agent.
"""

import logging

from google.genai import types

from agents.subagents.market_analysis_agent.prompts import (
    MARKET_CONSULTANT_CONTEXT_TEMPLATE,
)
from app.google_genai import FlashModelService, GenAIClientManager, GenAIConfig

logger = logging.getLogger(__name__)


async def execute_market_consultant(
    query: str,
    rag_context: str,
) -> str:
    """Analyze the IT job market using RAG context and Gemini Flash.

    Args:
        query: The user's market analysis question.
        rag_context: Pre-retrieved job posting documents from the RAG pipeline.

    Returns:
        Vietnamese text analysis based on the RAG context.
    """
    if not rag_context or not rag_context.strip():
        return (
            "Không có dữ liệu tuyển dụng để phân tích. "
            "Vui lòng thử câu hỏi khác hoặc kiểm tra lại hệ thống."
        )

    prompt = MARKET_CONSULTANT_CONTEXT_TEMPLATE.format(
        rag_context=rag_context,
        query=query,
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
