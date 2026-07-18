from typing import Literal
from langchain_core.messages import AIMessage
from agents.base import AgentState


def supervisor_node(state: AgentState) -> dict:
    print("[supervisor] Coordinating tasks...")
    return {
        "messages": [
            AIMessage(
                name="supervisor",
                content="Supervisor: Coordinating next worker delegation.",
            )
        ]
    }


def supervisor_router(
    state: AgentState,
) -> Literal["worker_1", "worker_2", "worker_3", "__end__"]:
    executed = set()
    for msg in state["messages"]:
        if isinstance(msg, AIMessage) and msg.name:
            executed.add(msg.name)

    if "worker_1" not in executed:
        return "worker_1"
    elif "worker_2" not in executed:
        return "worker_2"
    elif "worker_3" not in executed:
        return "worker_3"
    else:
        return "__end__"
