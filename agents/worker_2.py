from langchain_core.messages import AIMessage
from agents.base import AgentState


def worker_2_node(state: AgentState) -> dict:
    print("[worker_2] Executing task...")

    return {
        "messages": [
            AIMessage(
                name="worker_2",
                content="Task completed by worker_2: Extracted key trends and salary ranges.",
            )
        ]
    }
