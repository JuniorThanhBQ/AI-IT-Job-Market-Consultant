import logging
from typing import Any

from agents.subagents.market_analysis_agent import MarketAnalysisAgent
from agents.supervisor.graph import Intent, build_graph
from agents.supervisor.registry import register_agent
from agents.supervisor.state import create_initial_state

register_agent(MarketAnalysisAgent())

logger = logging.getLogger(__name__)


async def execute_agent_flow(
    intent: Intent,
    user_input: str,
    rag_context: str,
    action_type: str | None = None,
    user_profile: dict | None = None,
) -> dict[str, Any]:
    graph = build_graph(intent)

    initial_state = create_initial_state(
        user_input=user_input,
        rag_context=rag_context,
        action_type=action_type,
        user_profile=user_profile,
        intent=intent.value,
    )

    logger.info(
        "Executing agent flow: intent=%s, action_type=%s",
        intent.value,
        action_type,
    )

    result = await graph.ainvoke(initial_state)
    return result
