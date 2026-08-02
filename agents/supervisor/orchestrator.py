import operator
from enum import Enum
from typing import cast, TypedDict, Annotated
from langgraph.graph import StateGraph, START, END

from ..subagents.market_analysis_agent.market_analysis_agent import run_market_analysis


class Intent(str, Enum):
    MARKET_ANALYSIS = "MARKET_ANALYSIS"
    PERSONAL_STANDARD_EVALUATION = "PERSONAL_STANDARD_EVALUATION"
    JOB_RECOMMEND = "JOB_RECOMMEND"
    DEEP_ANALYSIS_EVALUATION = "DEEP_ANALYSIS_EVALUATION"


class AgentState(TypedDict):
    user_input: str
    rag_context: str
    execution_order: Annotated[list[str], operator.add]
    final_result: str


async def market_node(state: AgentState):
    analysis_result = await run_market_analysis(
        state["user_input"], state["rag_context"]
    )
    return {
        "execution_order": ["market_analysis_agent"],
        "final_result": analysis_result,
    }


async def personal_node(state: AgentState):
    return {
        "execution_order": ["personalization_agent"],
        "final_result": state.get("final_result", ""),
    }


async def recommend_node(state: AgentState):
    return {
        "execution_order": ["recommendation_agent"],
        "final_result": state.get("final_result", ""),
    }


ROUTES = {
    Intent.MARKET_ANALYSIS: [("market_analysis", market_node)],
    Intent.PERSONAL_STANDARD_EVALUATION: [("personalization", personal_node)],
    Intent.JOB_RECOMMEND: [
        ("personalization", personal_node),
        ("recommendation", recommend_node),
    ],
    Intent.DEEP_ANALYSIS_EVALUATION: [
        ("market_analysis", market_node),
        ("personalization", personal_node),
        ("recommendation", recommend_node),
    ],
}


async def execute_agent_flow(intent: Intent, user_input: str, rag_context: str) -> dict:
    pipeline = ROUTES[intent]

    builder = StateGraph(AgentState)

    for name, node_func in pipeline:
        builder.add_node(name, node_func)

    builder.add_edge(START, pipeline[0][0])

    for i in range(len(pipeline) - 1):
        builder.add_edge(pipeline[i][0], pipeline[i + 1][0])

    builder.add_edge(pipeline[-1][0], END)

    graph = builder.compile()

    initial_state = cast(
        AgentState,
        {
            "user_input": user_input,
            "rag_context": rag_context,
            "execution_order": [],
            "final_result": "",
        },
    )

    result = await graph.ainvoke(initial_state)
    return result
