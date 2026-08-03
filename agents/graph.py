from __future__ import annotations

import logging
from enum import Enum

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.registry import get_agent
from agents.state import AgentState

logger = logging.getLogger(__name__)


# ── Intent → Pipeline mapping ──────────────────────────────────
class Intent(str, Enum):
    """Supported orchestration intents.

    Each intent maps to an ordered sequence of agent names that form
    the execution pipeline.
    """

    MARKET_ANALYSIS = "MARKET_ANALYSIS"
    PERSONAL_STANDARD_EVALUATION = "PERSONAL_STANDARD_EVALUATION"
    JOB_RECOMMEND = "JOB_RECOMMEND"
    DEEP_ANALYSIS_EVALUATION = "DEEP_ANALYSIS_EVALUATION"


# The value is an ordered list of registered agent names.
INTENT_PIPELINES: dict[Intent, list[str]] = {
    Intent.MARKET_ANALYSIS: [
        "market_analysis",
    ],
    Intent.PERSONAL_STANDARD_EVALUATION: [
        "personalization",
    ],
    Intent.JOB_RECOMMEND: [
        "personalization",
        "recommendation",
    ],
    Intent.DEEP_ANALYSIS_EVALUATION: [
        "market_analysis",
        "personalization",
        "recommendation",
    ],
}


def build_graph(intent: Intent) -> CompiledStateGraph:
    """Construct and compile a LangGraph StateGraph for the given intent.

    The graph is a linear pipeline — each agent node feeds into the next.
    Agent instances are resolved from the global registry at build time.
    """
    pipeline = INTENT_PIPELINES[intent]
    if not pipeline:
        raise ValueError(f"No pipeline defined for intent: {intent}")

    builder = StateGraph(AgentState)

    for agent_name in pipeline:
        agent = get_agent(agent_name)
        # Each node calls the agent's `run()` method (BaseAgent.run)
        builder.add_node(agent_name, agent.run)

    # Wire edges: START → first → ... → last → END
    builder.add_edge(START, pipeline[0])
    for i in range(len(pipeline) - 1):
        builder.add_edge(pipeline[i], pipeline[i + 1])
    builder.add_edge(pipeline[-1], END)

    logger.info(
        "Built graph for intent '%s': %s",
        intent.value,
        " → ".join(pipeline),
    )
    return builder.compile()
