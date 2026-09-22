# ADR-05: Selection of Hierarchical Multi-Agent System (HMAS) Architecture

## Status
Accepted

## Context
This decision is being evaluated in the context of data processing and workflow requirements. Collecting and parsing job recruitment data, parsing and personalizing user profiles, matching job data with user goals, and querying generative LLMs are sequential steps rather than parallel processes. The system must know exactly when to execute each task with centralized orchestration, rather than allowing autonomous agents to operate independently without coordinated control.

## Decision
Choose a Hierarchical Multi-Agent System (HMAS) architecture instead of just using the ReAct AI Agent model.

## Rationale
1. **Centralized Control and Coordination:** A hierarchical structure ensures a supervisor/coordinator agent can manage the execution order of sub-tasks, preventing race conditions or out-of-order analysis.
2. **Easier Debugging and Monitoring:** With a supervisor agent orchestrating sub-agents, it is simpler to trace execution paths, catch failure states, and audit LLM prompts.
3. **Reduced LLM Token Consumption:** Centralized routing prevents sub-agents from independently querying LLMs recursively, keeping API usage structured and minimizing token costs.
4. **Predictable Output Quality:** Hierarchical control enforces structured data schemas at each stage, yielding more reliable and accurate recommendations for the end user.

## Consequences
### Positive
* **Predictable Execution Workflows:** Tasks flow sequentially through structured steps, minimizing random agent behavior.
* **Modular Agent Roles:** Each sub-agent is dedicated to a specific task, making it easy to upgrade individual agent logic without affecting other agents.
* **Robust Error Handling:** If a sub-agent fails, the supervisor agent can catch the error and execute a fallback strategy rather than crashing the entire pipeline.

### Negative
* **Supervisor Bottleneck:** If the coordinator agent crashes or fails to route tasks correctly, the entire multi-agent pipeline is blocked.
* **Increased System Complexity:** Designing and maintaining parent-child communication protocols, state-sharing variables, and supervisor decision logic is more complex than running simple script-based tasks.
* **Latency Accumulation:** A sequential, coordinated flow of agent queries means the total response time is the sum of each step, which can feel slower than fully asynchronous, independent agent networks.

## Decision Date
26/07/2026
