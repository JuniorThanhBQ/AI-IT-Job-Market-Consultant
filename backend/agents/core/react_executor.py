import logging
import time
from typing import Any

from app.genai.configs import GenAIConfig
from app.genai.prompts.templates import MARKET_ANALYSIS_SYSTEM_PROMPT
from app.tools.market_analysis_tools import (
    get_top_skills_tool,
    salary_benchmark_tool,
    search_jobs_tool,
)
from app.utils.embeddings import get_gemini_api_key
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)

TOOLS = [get_top_skills_tool, search_jobs_tool, salary_benchmark_tool]


def build_react_agent():
    config = GenAIConfig()
    api_key = get_gemini_api_key()

    llm = ChatGoogleGenerativeAI(
        model=config.default_flash_model,
        google_api_key=api_key,
        max_output_tokens=4096,
    )

    return create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=SystemMessage(content=MARKET_ANALYSIS_SYSTEM_PROMPT),
    )


def extract_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                text_val = part.get("text", "")
                if text_val:
                    parts.append(text_val)
        return "".join(parts)
    return str(content) if content else ""


async def execute_agent_async(
    user_input: str,
    chat_history: str,
) -> dict[str, Any]:
    agent = build_react_agent()
    start_time = time.perf_counter()
    tool_calls: list[dict[str, str]] = []
    try:
        delimited_input = f"<user_query>{user_input}</user_query>"
        messages = []
        if chat_history and chat_history != "No previous conversation.":
            messages.append(
                HumanMessage(content=f"Previous conversation:\n{chat_history}")
            )

        messages.append(HumanMessage(content=delimited_input))
        result = await agent.ainvoke(
            {"messages": messages},
            config={"recursion_limit": 6},
        )
        output_messages = result.get("messages", [])
        output_text = ""

        for msg in reversed(output_messages):
            if isinstance(msg, AIMessage):
                candidate = extract_text(msg.content).strip()
                if candidate and not getattr(msg, "tool_calls", None):
                    output_text = candidate
                    break

        for msg in output_messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls.append(
                        {
                            "tool": tc.get("name", ""),
                            "input": str(tc.get("args", {})),
                        }
                    )

        if not output_text:
            config = GenAIConfig()
            api_key = get_gemini_api_key()
            fallback_llm = ChatGoogleGenerativeAI(
                model=config.default_flash_model,
                google_api_key=api_key,
                max_output_tokens=4096,
            )
            synth_messages = list(output_messages) + [
                HumanMessage(
                    content="Based on the data retrieved above, provide your final market analysis in clear, professional Markdown. Do not output raw JSON."
                )
            ]
            synth_resp = await fallback_llm.ainvoke(synth_messages)
            output_text = extract_text(getattr(synth_resp, "content", ""))

        latency = time.perf_counter() - start_time

        return {
            "final_result": output_text,
            "latency": round(latency, 3),
            "iterations": len(tool_calls),
            "tool_calls": [tc["tool"] for tc in tool_calls],
        }

    except Exception:
        logger.exception("Agent execution failed")
        error_text = "I apologize, but I encountered an issue processing your request. Please try again"
        return {
            "final_result": error_text,
            "latency": round(time.perf_counter() - start_time, 3),
            "iterations": 0,
            "tool_calls": [],
        }
