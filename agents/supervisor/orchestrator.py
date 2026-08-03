"""Supervisor orchestrator — entry point for multi-agent execution.

This module is the only public interface for running agent pipelines.
It builds a LangGraph graph based on the requested intent and invokes it.
"""

import logging
from typing import Any

from agents.graph import Intent, build_graph
from agents.state import create_initial_state

# ── Register all agents on import ──────────────────────────────
# Side-effect imports: each module registers its agent instance.
from agents.registry import register_agent
from agents.subagents.market_analysis_agent import MarketAnalysisAgent
from agents.subagents.personalization_agent import PersonalizationAgent
from agents.subagents.recommendation_agent import RecommendationAgent

register_agent(MarketAnalysisAgent())
register_agent(PersonalizationAgent())
register_agent(RecommendationAgent())

logger = logging.getLogger(__name__)


async def execute_agent_flow(
    intent: Intent,
    user_input: str,
    rag_context: str,
    action_type: str | None = None,
    user_profile: dict | None = None,
) -> dict[str, Any]:
    """Build and run the agent pipeline for the given intent.

    Args:
        intent: Which pipeline to execute (determines agent sequence).
        user_input: The user's query text.
        rag_context: Pre-built RAG context string (retrieved documents).
        action_type: Optional action modifier (e.g. CHART, SQL_TOP_SKILLS).
        user_profile: Optional user profile dict for personalization.

    Returns:
        The final ``AgentState`` dict after all agents have executed.
    """
    graph = build_graph(intent)

    initial_state = create_initial_state(
        user_input=user_input,
        rag_context=rag_context,
        action_type=action_type,
        user_profile=user_profile,
    )

    logger.info(
        "Executing agent flow: intent=%s, action_type=%s",
        intent.value,
        action_type,
    )

    result = await graph.ainvoke(initial_state)
    return result
