from agents.subagents.market_analysis_agent.agent import MarketAnalysisAgent
from agents.supervisor.state import AgentState

__all__ = ["MarketAnalysisAgent", "run_market_analysis"]


async def run_market_analysis(
    user_input: str, rag_context: str, action_type: str | None = None
) -> str:
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
