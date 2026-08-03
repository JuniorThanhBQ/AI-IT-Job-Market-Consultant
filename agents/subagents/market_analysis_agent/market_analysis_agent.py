"""Backward-compatible module.

Preserves the old import path:
    from agents.subagents.market_analysis_agent.market_analysis_agent import (
        MarketAnalysisAgent, run_market_analysis,
    )

New code should import from the package directly:
    from agents.subagents.market_analysis_agent import MarketAnalysisAgent
"""

from agents.state import AgentState
from agents.subagents.market_analysis_agent.agent import MarketAnalysisAgent

__all__ = ["MarketAnalysisAgent", "run_market_analysis"]


async def run_market_analysis(
    user_input: str, rag_context: str, action_type: str | None = None
) -> str:
    """Thin wrapper preserving the old function-based call signature."""
    agent = MarketAnalysisAgent()
    state = AgentState(
        user_input=user_input,
        rag_context=rag_context,
        action_type=action_type,
        user_profile=None,
        market_analysis=None,
        personal_evaluation=None,
        recommendations=None,
        execution_order=[],
        final_result="",
        error=None,
        status="ok",
        tool_outputs=None,
    )
    result = await agent.execute(state)
    return result.get("market_analysis", "")
