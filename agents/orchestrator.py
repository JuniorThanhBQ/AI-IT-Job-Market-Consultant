from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage

from agents.base import AgentState
from agents.worker_1 import worker_1_node
from agents.worker_2 import worker_2_node
from agents.worker_3 import worker_3_node
from agents.supervisor import supervisor_node, supervisor_router


class AgentOrchestrator:
    def __init__(self):
        builder = StateGraph(AgentState)

        builder.add_node("supervisor", supervisor_node)
        builder.add_node("worker_1", worker_1_node)
        builder.add_node("worker_2", worker_2_node)
        builder.add_node("worker_3", worker_3_node)

        builder.add_edge(START, "supervisor")

        builder.add_conditional_edges(
            "supervisor",
            supervisor_router,
            {
                "worker_1": "worker_1",
                "worker_2": "worker_2",
                "worker_3": "worker_3",
                "__end__": END,
            },
        )

        builder.add_edge("worker_1", "supervisor")
        builder.add_edge("worker_2", "supervisor")
        builder.add_edge("worker_3", "supervisor")

        self.graph = builder.compile()

    def process(self, user_query: str) -> dict:
        initial_state = {
            "messages": [HumanMessage(content=user_query)],
            "context": {},
            "errors": [],
        }

        print(f"Starting LangGraph orchestration for: '{user_query}'\n")

        result = self.graph.invoke(initial_state)
        return result


def main():
    orchestrator = AgentOrchestrator()
    result = orchestrator.process(
        "Tell me about software engineering trends in Vietnam."
    )

    print("\n--- Final Messages ---")
    for msg in result["messages"]:
        name_str = f" ({msg.name})" if hasattr(msg, "name") and msg.name else ""
        print(f"{msg.type.upper()}{name_str}: {msg.content}")


if __name__ == "__main__":
    main()
