from __future__ import annotations

import logging
from enum import StrEnum

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agents.supervisor.registry import get_agent
from agents.supervisor.state import AgentState

logger = logging.getLogger(__name__)


class Intent(StrEnum):
    MARKET_ANALYSIS = "MARKET_ANALYSIS"
    PERSONAL_STANDARD_EVALUATION = "PERSONAL_STANDARD_EVALUATION"
    JOB_RECOMMEND = "JOB_RECOMMEND"
    DEEP_ANALYSIS_EVALUATION = "DEEP_ANALYSIS_EVALUATION"


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
    pipeline = INTENT_PIPELINES[intent]
    if not pipeline:
        raise ValueError(f"No pipeline defined for intent: {intent}")

    builder = StateGraph(AgentState)

    for agent_name in pipeline:
        agent = get_agent(agent_name)
        builder.add_node(agent_name, agent.run)

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
