from langchain_core.messages import AIMessage
from agents.base import AgentState


def worker_3_node(state: AgentState) -> dict:
    print("[worker_3] Executing task...")

    return {
        "messages": [
            AIMessage(
                name="worker_3",
                content="Task completed by worker_3: Compiled final recommendations for the candidate.",
            )
        ]
    }
