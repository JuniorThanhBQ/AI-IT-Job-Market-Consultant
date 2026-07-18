from langchain_core.messages import AIMessage
from agents.base import AgentState


def worker_1_node(state: AgentState) -> dict:
    print("[worker_1] Executing task...")

    return {
        "messages": [
            AIMessage(
                name="worker_1",
                content="Task completed by worker_1: Fetched software engineering jobs.",
            )
        ]
    }
