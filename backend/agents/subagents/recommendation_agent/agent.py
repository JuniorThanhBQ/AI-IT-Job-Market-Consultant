import json
import logging
from typing import Any

from google.genai import types

from agents.base import BaseAgent
from agents.supervisor.state import AgentState
from app.google_genai import GenAIClientManager, GenAIConfig
from app.google_genai.prompts import (
    RECOMMENDATION_SYSTEM_PROMPT,
    RECOMMENDATION_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class RecommendationAgent(BaseAgent):
    """Recommends top 5 matching jobs based on personalization assessment and goals.

    Input state keys:
    - user_profile: candidate goal, biography, CV data
    - personal_evaluation: output from PersonalizationAgent
    - rag_context: job context documents

    Output state keys:
    - recommendations: formatted Vietnamese recommendation report
    - final_result: same as recommendations
    """

    name = "recommendation"

    async def execute(self, state: AgentState) -> dict[str, Any]:
        user_profile = state.get("user_profile")
        personal_eval = state.get("personal_evaluation") or ""
        rag_context = state.get("rag_context", "")
        user_input = state.get("user_input", "")

        name = "Ứng viên"
        goal = "N/A"
        biography = "N/A"
        skills = ""

        if user_profile:
            name = (
                f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip()
                or "Ứng viên"
            )
            goal = user_profile.get("goal", "N/A")
            biography = user_profile.get("biography", "N/A")
            skills = ", ".join(user_profile.get("skills", []))

        user_prompt = RECOMMENDATION_USER_TEMPLATE.format(
            name=name,
            goal=goal,
            biography=biography,
            skills=skills,
            personal_evaluation=personal_eval,
            rag_context=rag_context,
            user_input=user_input,
        )

        try:
            config = GenAIConfig()
            manager = GenAIClientManager(config)
            client = manager.get_client()

            generation_config = types.GenerateContentConfig(
                system_instruction=RECOMMENDATION_SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.5,
            )

            response = None
            for m in config.flash_models:
                try:
                    response = await client.aio.models.generate_content(
                        model=m,
                        contents=user_prompt,
                        config=generation_config,
                    )
                    if response.text:
                        break
                except Exception as e:
                    logger.warning(
                        "Flash model %s failed in recommendation agent: %s",
                        m,
                        e,
                    )

            if not response or not response.text:
                raise ValueError("All Flash models failed for recommendation agent.")

            raw_json = response.text.strip()
            parsed = json.loads(raw_json)
        except Exception:
            logger.exception("Error calling Gemini Flash for recommendation agent")
            parsed = {"recommendations": []}

        formatted_report = self._format_vietnamese_report(parsed, personal_eval)
        tool_outputs = state.get("tool_outputs") or {}
        tool_outputs["job_recommendations"] = parsed

        return {
            "recommendations": formatted_report,
            "final_result": formatted_report,
            "tool_outputs": tool_outputs,
        }

    @staticmethod
    def _format_vietnamese_report(data: dict, personal_eval: str) -> str:
        lines = []

        if personal_eval:
            lines.append(personal_eval)
            lines.append("\n" + "=" * 50 + "\n")

        lines.append("### TOP 5 VIỆC LÀM PHÙ HỢP NHẤT VỚI BẠN")
        jobs = data.get("recommendations", [])
        if not jobs:
            lines.append(
                "Không tìm thấy công việc phù hợp trong danh mục lưu trữ hiện tại."
            )
            return "\n".join(lines)

        for idx, job in enumerate(jobs[:5], start=1):
            lines.append(
                f"**{idx}. {job.get('job_title', 'N/A')} tại {job.get('company_name', 'N/A')}**"
            )
            lines.append(f"- **Mức lương:** {job.get('salary', 'Thỏa thuận')}")
            lines.append(f"- **Độ phù hợp:** {job.get('match_score', 0)}/100")
            lines.append(f"- **Lý do phù hợp:** {job.get('why_fits', 'N/A')}")
            lines.append(
                f"- **Kỹ năng cần bổ sung cho vị trí này:** {job.get('skills_to_upgrade', 'Không yêu cầu gì thêm')}\n"
            )

        return "\n".join(lines)
