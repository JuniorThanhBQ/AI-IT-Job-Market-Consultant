import json
import logging
from typing import Any, cast

from google import genai
from google.genai import types

from agents.base import BaseAgent
from agents.subagents.market_analysis_agent.tools import (
    execute_market_consultant,
    execute_market_overview,
    execute_top_skills_chart,
)
from agents.supervisor.state import AgentState
from app.google_genai import GenAIClientManager, GenAIConfig
from app.google_genai.prompts.templates import get_prompt_template

logger = logging.getLogger(__name__)


TOOL_DECLARATIONS = [
    types.FunctionDeclaration(
        name="market_consultant",
        description=(
            "Phân tích thị trường IT dựa trên dữ liệu tuyển dụng thực tế (RAG). "
            "Dùng khi người dùng hỏi về xu hướng, công nghệ, vị trí, mức lương, "
            "hoặc cần phân tích chi tiết từ dữ liệu tuyển dụng."
        ),
        parameters=cast(
            Any,
            {
                "type": "OBJECT",
                "properties": {
                    "query": {
                        "type": "STRING",
                        "description": "Câu hỏi phân tích thị trường của người dùng",
                    },
                },
                "required": ["query"],
            },
        ),
    ),
    types.FunctionDeclaration(
        name="top_skills_chart",
        description=(
            "Truy vấn cơ sở dữ liệu để lấy danh sách kỹ năng IT được tuyển nhiều nhất. "
            "Trả về dữ liệu dạng JSON cho biểu đồ (Chart.js). "
            "Dùng khi người dùng hỏi về kỹ năng hot, top kỹ năng, công nghệ phổ biến."
        ),
        parameters=cast(
            Any,
            {
                "type": "OBJECT",
                "properties": {
                    "limit": {
                        "type": "INTEGER",
                        "description": "Số lượng kỹ năng cần lấy (mặc định: 15)",
                    },
                    "seniority_filter": {
                        "type": "STRING",
                        "description": (
                            "Lọc theo cấp bậc: Intern, Fresher, Junior, Mid, "
                            "Senior, Lead, Manager"
                        ),
                    },
                },
            },
        ),
    ),
    types.FunctionDeclaration(
        name="market_overview",
        description=(
            "Truy vấn cơ sở dữ liệu để lấy tổng quan thị trường: "
            "tổng việc làm, phân bổ theo cấp bậc, mô hình làm việc, "
            "thống kê lương, top domain, top công ty. "
            "Dùng khi người dùng hỏi tổng quan, thống kê chung."
        ),
        parameters=cast(
            Any,
            {
                "type": "OBJECT",
                "properties": {
                    "seniority_filter": {
                        "type": "STRING",
                        "description": "Lọc theo cấp bậc",
                    },
                    "working_model_filter": {
                        "type": "STRING",
                        "description": "Lọc theo mô hình: Remote, Hybrid, Onsite",
                    },
                },
            },
        ),
    ),
]


class MarketAnalysisAgent(BaseAgent):
    name = "market_analysis"
    MAX_TOOL_ITERATIONS = 3

    async def execute(self, state: AgentState) -> dict[str, Any]:
        user_input = state["user_input"]
        rag_context = state.get("rag_context", "")
        action_type = state.get("action_type")
        intent = state.get("intent")

        if intent != "DEEP_ANALYSIS_EVALUATION":
            logger.info("Bypassing ReAct loop for intent: %s", intent)
            final_text = await execute_market_consultant(
                query=user_input, rag_context=rag_context
            )
            return {
                "market_analysis": final_text,
                "final_result": final_text,
                "tool_outputs": {},
            }

        user_message = self._build_user_message(user_input, action_type)

        try:
            final_text, tool_outputs = await self._react_loop(
                user_message=user_message,
                rag_context=rag_context,
            )
        except Exception:
            logger.exception("ReAct loop failed, falling back to direct RAG")
            final_text = await execute_market_consultant(
                query=user_input, rag_context=rag_context
            )
            tool_outputs = {}

        return {
            "market_analysis": final_text,
            "final_result": final_text,
            "tool_outputs": tool_outputs,
        }

    async def _react_loop(
        self,
        user_message: str,
        rag_context: str,
    ) -> tuple[str, dict[str, Any]]:
        config = GenAIConfig()
        manager = GenAIClientManager(config)
        client: genai.Client = manager.get_client()

        contents: list[Any] = [
            types.Content(role="user", parts=[types.Part(text=user_message)])
        ]

        generation_config = types.GenerateContentConfig(
            system_instruction=get_prompt_template("market_analysis_system"),
            tools=[types.Tool(function_declarations=TOOL_DECLARATIONS)],
            temperature=0.3,
        )

        tool_outputs: dict[str, Any] = {}

        for iteration in range(self.MAX_TOOL_ITERATIONS):
            logger.info(
                "ReAct iteration %d/%d",
                iteration + 1,
                self.MAX_TOOL_ITERATIONS,
            )

            response = await client.aio.models.generate_content(
                model=config.default_flash_model,
                contents=cast(Any, contents),
                config=generation_config,
            )

            if not response.candidates:
                raise ValueError("Gemini returned empty candidates list.")

            candidate = response.candidates[0]
            model_content = candidate.content
            if model_content is None:
                raise ValueError("Model candidate content is None.")

            model_parts = model_content.parts or []

            function_calls = [
                part.function_call for part in model_parts if part.function_call
            ]

            if not function_calls:
                text_parts = [part.text for part in model_parts if part.text]
                return "\n".join(text_parts), tool_outputs

            contents.append(model_content)

            function_response_parts = []
            for fc in function_calls:
                tool_name = fc.name
                if not tool_name:
                    continue
                logger.info("Calling tool: %s(%s)", tool_name, fc.args)

                result = await self._execute_tool(
                    tool_name=tool_name,
                    tool_args=fc.args or {},
                    rag_context=rag_context,
                )

                tool_outputs[tool_name] = result

                function_response_parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=tool_name,
                            response={"result": result},
                        )
                    )
                )

            contents.append(types.Content(role="user", parts=function_response_parts))

        logger.warning("Max ReAct iterations reached (%d)", self.MAX_TOOL_ITERATIONS)
        summary_parts = []
        for tool_name, output in tool_outputs.items():
            summary_parts.append(f"[{tool_name}]: {output}")
        return "\n\n".join(
            summary_parts
        ) if summary_parts else user_message, tool_outputs

    async def _execute_tool(
        self,
        tool_name: str,
        tool_args: dict[str, Any],
        rag_context: str,
    ) -> str:
        try:
            if tool_name == "market_consultant":
                return await execute_market_consultant(
                    query=tool_args.get("query", ""),
                    rag_context=rag_context,
                )
            elif tool_name == "top_skills_chart":
                return execute_top_skills_chart(
                    limit=tool_args.get("limit", 15),
                    seniority_filter=tool_args.get("seniority_filter"),
                )
            elif tool_name == "market_overview":
                return execute_market_overview(
                    seniority_filter=tool_args.get("seniority_filter"),
                    working_model_filter=tool_args.get("working_model_filter"),
                )
            else:
                return json.dumps(
                    {"error": f"Unknown tool: {tool_name}"},
                    ensure_ascii=False,
                )
        except Exception:
            logger.exception("Error executing tool '%s'", tool_name)
            return json.dumps(
                {"error": f"Error executing tool '{tool_name}'."},
                ensure_ascii=False,
            )

    @staticmethod
    def _build_user_message(user_input: str, action_type: str | None) -> str:
        message = user_input

        if action_type and action_type != "DEFAULT":
            hints = {
                "CHART": (
                    "\n\n[Gợi ý hệ thống: Người dùng cần dữ liệu biểu đồ. "
                    "Hãy sử dụng công cụ top_skills_chart.]"
                ),
                "SQL_TOP_SKILLS": (
                    "\n\n[Gợi ý hệ thống: Người dùng cần thống kê kỹ năng. "
                    "Hãy sử dụng công cụ top_skills_chart.]"
                ),
                "SALARY_BENCHMARK": (
                    "\n\n[Gợi ý hệ thống: Người dùng cần phân tích lương. "
                    "Hãy sử dụng market_overview để lấy salary_stats.]"
                ),
                "DEMAND_TREND": (
                    "\n\n[Gợi ý hệ thống: Người dùng cần xu hướng tuyển dụng. "
                    "Hãy sử dụng market_overview VÀ market_consultant.]"
                ),
            }
            hint = hints.get(action_type, "")
            message += hint

        return message
