import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict):
    user_input: str
    rag_context: str
    action_type: str | None
    user_profile: dict | None
    intent: str | None
    market_analysis: str | None
    personal_evaluation: str | None
    recommendations: str | None
    execution_order: Annotated[list[str], operator.add]
    final_result: str
    tool_outputs: dict | None
    error: str | None
    status: str


def create_initial_state(
    *,
    user_input: str,
    rag_context: str,
    action_type: str | None = None,
    user_profile: dict | None = None,
    intent: str | None = None,
) -> AgentState:
    return AgentState(
        user_input=user_input,
        rag_context=rag_context,
        action_type=action_type,
        user_profile=user_profile,
        intent=intent,
        market_analysis=None,
        personal_evaluation=None,
        recommendations=None,
        execution_order=[],
        final_result="",
        tool_outputs=None,
        error=None,
        status="ok",
    )
