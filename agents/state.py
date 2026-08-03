import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict):
    """Canonical shared state for the multi-agent LangGraph pipeline.

    Each agent writes to its own dedicated output slot to avoid
    overwriting results from upstream agents in sequential flows.
    """

    # ── Inputs ──────────────────────────────────────────────────
    user_input: str
    rag_context: str
    action_type: str | None
    user_profile: dict | None

    # ── Per-agent output slots ──────────────────────────────────
    market_analysis: str | None
    personal_evaluation: str | None
    recommendations: str | None

    # ── Orchestration ───────────────────────────────────────────
    execution_order: Annotated[list[str], operator.add]
    final_result: str

    # ── Tool outputs ────────────────────────────────────────────
    tool_outputs: dict | None

    # ── Observability ───────────────────────────────────────────
    error: str | None
    status: str  # "ok" | "partial" | "failed"


def create_initial_state(
    *,
    user_input: str,
    rag_context: str,
    action_type: str | None = None,
    user_profile: dict | None = None,
) -> AgentState:
    """Build a fully initialized AgentState with safe defaults."""
    return AgentState(
        user_input=user_input,
        rag_context=rag_context,
        action_type=action_type,
        user_profile=user_profile,
        market_analysis=None,
        personal_evaluation=None,
        recommendations=None,
        execution_order=[],
        final_result="",
        tool_outputs=None,
        error=None,
        status="ok",
    )
