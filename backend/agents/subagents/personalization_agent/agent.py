import json
import logging
import re
from typing import Any

from google.genai import types

from agents.base import BaseAgent
from agents.supervisor.state import AgentState
from app.google_genai import GenAIClientManager, GenAIConfig
from app.google_genai.prompts import (
    PERSONALIZATION_SYSTEM_PROMPT,
    PERSONALIZATION_USER_TEMPLATE,
)

logger = logging.getLogger(__name__)


class PersonalizationAgent(BaseAgent):
    """Evaluates a candidate's IT skills, experience, and projects.

    Enforces scoring logic:
    - If CV attachment is not uploaded/used, final score is capped at 80.
    - If final score is < 70, outputs Resume Improvement recommendations.
    - Scans jobs in context to count frequency of target technologies (Docker,
      Kubernetes, AWS, etc.) for accurate market alignment reporting.
    """

    name = "personalization"

    async def execute(self, state: AgentState) -> dict[str, Any]:
        user_profile = state.get("user_profile")
        rag_context = state.get("rag_context", "")
        user_input = state.get("user_input", "")

        if not user_profile:
            evaluation = "Không tìm thấy hồ sơ cá nhân của ứng viên để đánh giá."
            return {
                "personal_evaluation": evaluation,
                "final_result": evaluation,
            }

        frequencies = self._count_skill_frequencies(rag_context)
        frequencies_str = "\n".join(
            f"- {skill}: {count} công việc" for skill, count in frequencies.items()
        )

        name = (
            f"{user_profile.get('first_name', '')} {user_profile.get('last_name', '')}".strip()
            or "Ứng viên"
        )
        projects = []
        for p in user_profile.get("projects", []):
            tech = (
                ", ".join(p.get("tech_stacks", []))
                if p.get("tech_stacks")
                else "Không có"
            )
            projects.append(
                f"- Project Name: {p.get('name', 'N/A')}\n"
                f"  Role: {p.get('role', 'N/A')}\n"
                f"  Description: {p.get('description', 'N/A')}\n"
                f"  Technology: {tech}"
            )
        projects_str = "\n\n".join(projects) if projects else "Không có dự án nào."

        user_prompt = PERSONALIZATION_USER_TEMPLATE.format(
            name=name,
            job_position=user_profile.get("job_position", "N/A"),
            goal=user_profile.get("goal", "N/A"),
            summary=user_profile.get("summary", "N/A"),
            education=user_profile.get("education", "N/A"),
            skills=", ".join(user_profile.get("skills", [])),
            certifications=", ".join(user_profile.get("certifications", [])),
            projects=projects_str,
            skill_frequencies=frequencies_str,
            rag_context=rag_context,
            user_input=user_input,
        )

        try:
            config = GenAIConfig()
            manager = GenAIClientManager(config)
            client = manager.get_client()

            generation_config = types.GenerateContentConfig(
                system_instruction=PERSONALIZATION_SYSTEM_PROMPT,
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
                        "Flash model %s failed in personalization evaluation: %s",
                        m,
                        e,
                    )

            if not response or not response.text:
                raise ValueError(
                    "All Flash models failed for personalization evaluation."
                )

            raw_json = response.text.strip()
            parsed = json.loads(raw_json)
        except Exception:
            logger.exception(
                "Error calling Gemini Flash for personalization evaluation"
            )

            parsed = {
                "score": 60,
                "must_have": [],
                "nice_to_improve": [],
                "need_to_import": [],
                "resume_improvement": "Lỗi kết nối với AI khi đánh giá hồ sơ.",
            }

        score = int(parsed.get("score", 60))
        using_cv_mode = user_profile.get("using_cv_mode", False)
        has_attachment = bool(user_profile.get("attachment"))

        if not using_cv_mode or not has_attachment:
            logger.info(
                "CV file attachment not used. Capping score to 80 (was %d).", score
            )
            score = min(score, 80)
            parsed["score"] = score

        if score < 70:
            if (
                not parsed.get("resume_improvement")
                or parsed["resume_improvement"] == "null"
            ):
                parsed["resume_improvement"] = (
                    "Hồ sơ của bạn hiện có điểm dưới 70. "
                    "Hãy bổ sung thêm các dự án thực tế sử dụng các công nghệ nhà tuyển dụng yêu cầu "
                    "và cập nhật tóm tắt chuyên môn để phản ánh đúng thế mạnh của bạn."
                )
        else:
            parsed["resume_improvement"] = None

        formatted_evaluation = self._format_vietnamese_report(parsed)

        tool_outputs = state.get("tool_outputs") or {}
        tool_outputs["personalization_analysis"] = parsed

        return {
            "personal_evaluation": formatted_evaluation,
            "final_result": formatted_evaluation,
            "tool_outputs": tool_outputs,
        }

    @staticmethod
    def _count_skill_frequencies(rag_context: str) -> dict[str, int]:
        """Count mentions of target skills in RAG context case-insensitively."""
        target_skills = [
            "Docker",
            "Kubernetes",
            "AWS",
            "Python",
            "FastAPI",
            "Java",
            "React",
            "Node.js",
            "Go",
            "SQL",
        ]
        counts = dict.fromkeys(target_skills, 0)

        docs = rag_context.split("--- Document ")
        for doc in docs:
            if not doc.strip():
                continue
            for skill in target_skills:
                if re.search(rf"\b{re.escape(skill)}\b", doc, re.IGNORECASE):
                    counts[skill] += 1

        return dict(sorted(counts.items(), key=lambda item: item[1], reverse=True))

    @staticmethod
    def _format_vietnamese_report(data: dict) -> str:
        lines = [
            "### BÁO CÁO ĐÁNH GIÁ NĂNG LỰC & ĐỘ PHÙ HỢP CÁ NHÂN",
            f"**Điểm tương thích:** {data.get('score', 0)}/100\n",
            "#### 1. Kỹ năng bắt buộc đã đáp ứng (Must have):",
        ]
        for skill in data.get("must_have", []):
            lines.append(f"  - {skill}")
        if not data.get("must_have"):
            lines.append("  - Không phát hiện kỹ năng bắt buộc phù hợp.")

        lines.append("\n#### 2. Kỹ năng cần cải thiện (Nice to improve):")
        for skill in data.get("nice_to_improve", []):
            lines.append(f"  - {skill}")
        if not data.get("nice_to_improve"):
            lines.append("  - Hồ sơ kỹ năng hiện tại của bạn tương đối ổn định.")

        lines.append("\n#### 3. Kỹ năng cần bổ sung (Need to import):")
        for skill in data.get("need_to_import", []):
            lines.append(f"  - {skill}")
        if not data.get("need_to_import"):
            lines.append("  - Không có thêm yêu cầu bắt buộc nào khác.")

        improvement = data.get("resume_improvement")
        if improvement:
            lines.append("\n#### ⚠️ Gợi ý cải thiện CV (Resume Improvement):")
            lines.append(f"{improvement}")

        return "\n".join(lines)
