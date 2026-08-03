import uuid
from typing import Any

from agents.graph import Intent
from agents.supervisor.orchestrator import execute_agent_flow
from sqlmodel import Session

from app.core.enums import ActionType, ConsultantMode
from app.modules.company.models import Company
from app.modules.consultant import repository as consultant_repo
from app.modules.consultee_profile import repository as profile_repo
from app.modules.job.models import Job
from app.utils.embeddings import generate_embedding_async


class ConsultantService:
    def __init__(self, db: Session):
        self.db = db

    def _build_rag_context(self, top_documents: list[Any]) -> str:
        rag_context = ""
        for idx, doc in enumerate(top_documents, start=1):
            if len(doc) == 3:
                job, company, distance = doc
            else:
                job, company = doc
                distance = None

            rag_context += f"--- Document {idx} ---\n"
            if distance is not None:
                rag_context += f"  Match Distance (Cosine Similarity): {distance:.6f}\n"

            rag_context += "Company Details:\n"
            rag_context += f"  Name: {company.name}\n"
            rag_context += f"  Industry: {company.industry}\n"
            if company.size:
                rag_context += f"  Size: {company.size}\n"
            if company.location:
                rag_context += f"  Location: {company.location}\n"
            if company.website:
                rag_context += f"  Website: {company.website}\n"
            if company.company_type:
                company_type_val = getattr(
                    company.company_type, "value", str(company.company_type)
                )
                rag_context += f"  Type: {company_type_val}\n"
            if company.addresses:
                rag_context += f"  Addresses: {', '.join(company.addresses)}\n"
            if company.working_days:
                rag_context += f"  Working Days: {company.working_days}\n"
            if company.overtime_policy:
                rag_context += f"  Overtime Policy: {company.overtime_policy}\n"

            rag_context += "Job Details:\n"
            rag_context += f"  Title: {job.title}\n"
            seniority_val = getattr(job.seniority, "value", str(job.seniority))
            rag_context += f"  Seniority: {seniority_val}\n"

            currency_val = getattr(job.currency, "value", str(job.currency))
            rag_context += (
                f"  Salary: {job.min_salary} - {job.max_salary} {currency_val}\n"
            )
            rag_context += f"  Working Hours: {job.working_hours}\n"

            working_model_val = getattr(
                job.working_model, "value", str(job.working_model)
            )
            rag_context += f"  Working Model: {working_model_val}\n"

            if job.responsibilities:
                rag_context += "  Responsibilities:\n"
                for resp in job.responsibilities[:5]:
                    rag_context += f"    - {resp}\n"
            if job.required_qualifications:
                rag_context += "  Required Qualifications:\n"
                for req in job.required_qualifications[:5]:
                    rag_context += f"    - {req}\n"
            if job.nice_to_have:
                rag_context += "  Nice to Have:\n"
                for nth in job.nice_to_have[:10]:
                    rag_context += f"    - {nth}\n"
            if job.domains:
                rag_context += f"  Domains: {', '.join(job.domains)}\n"
            if job.skills:
                skill_names = [skill.name for skill in job.skills]
                rag_context += f"  Skills: {', '.join(skill_names)}\n"
            rag_context += f"  URL: {job.url}\n\n"
        return rag_context

    async def _rerank_candidates_via_api(
        self, query: str, candidates: list[tuple[Job, Company, float]], limit: int = 5
    ) -> list[tuple[Job, Company, float]]:
        """Rerank the candidates using Gemini API to minimize local CPU/memory footprint on small VPS."""
        if not candidates:
            return []

        # Format candidate documents list for LLM context
        docs_text = ""
        for idx, (job, company, _distance) in enumerate(candidates):
            docs_text += f"[Document Index: {idx}]\n"
            docs_text += f"Company: {company.name}\n"
            docs_text += f"Job Title: {job.title}\n"
            docs_text += f"Description: {job.vector_context[:300]}\n"
            if job.skills:
                skill_names = [skill.name for skill in job.skills]
                docs_text += f"Skills: {', '.join(skill_names)}\n"
            docs_text += "\n"

        from app.google_genai.prompts.templates import get_prompt_template

        prompt = get_prompt_template(
            "rerank_candidates", query=query, docs_text=docs_text
        )

        try:
            from google.genai import types

            from app.google_genai import (
                FlashModelService,
                GenAIClientManager,
                GenAIConfig,
            )

            config = GenAIConfig()
            config.default_flash_model = "gemini-3.5-flash-lite"
            client_manager = GenAIClientManager(config)
            flash_service = FlashModelService(client_manager)

            generation_config = types.GenerateContentConfig(temperature=0.0)
            response = await flash_service.generate_content_async(
                prompt, config=generation_config
            )

            clean_res = response.strip().replace("[", "").replace("]", "")

            # Parse comma-separated index values
            indices = [
                int(i.strip()) for i in clean_res.split(",") if i.strip().isdigit()
            ]

            # Reorder candidates based on LLM output
            reranked = []
            seen = set()
            for idx in indices:
                if 0 <= idx < len(candidates) and idx not in seen:
                    reranked.append(candidates[idx])
                    seen.add(idx)

            # Append any candidates that the LLM missed
            for idx, cand in enumerate(candidates):
                if idx not in seen:
                    reranked.append(cand)

            return reranked[:limit]
        except Exception:
            # Fallback to the original hybrid ranking if the API call or parsing fails
            return candidates[:limit]

    def _build_user_profile(self, user_id: uuid.UUID) -> dict | None:
        """Fetch user profile + CV and convert to a dict for agent consumption."""
        profile = profile_repo.get_profile_by_user_id(session=self.db, user_id=user_id)
        if not profile:
            return None

        profile_dict: dict[str, Any] = {
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "biography": profile.biography,
            "goal": profile.goal,
        }

        if profile.cv:
            cv = profile.cv
            profile_dict.update(
                {
                    "job_position": cv.job_position,
                    "summary": cv.summary,
                    "education": cv.education,
                    "skills": cv.skills or [],
                    "certifications": cv.certifications or [],
                    "projects": [
                        {
                            "name": p.name,
                            "role": p.role,
                            "tech_stacks": p.tech_stacks or [],
                            "description": p.description,
                        }
                        for p in (cv.projects or [])[:3]
                    ],
                }
            )

        return profile_dict

    async def process_chatbot_intent(
        self, user_id: uuid.UUID, intent: ConsultantMode, user_input: str
    ) -> dict:
        """User-facing chatbot flow with hybrid retrieval + LLM reranking and execution logging."""
        user_vector = await generate_embedding_async(user_input)

        # Stage 1: Fast Hybrid Search (vector + tsvector) fetching candidate pool
        candidates = consultant_repo.get_hybrid_candidates(
            session=self.db, user_query=user_input, user_vector=user_vector, limit=15
        )

        # Stage 2: Rerank candidate list using fast/cheap Gemini API
        top_documents = await self._rerank_candidates_via_api(
            query=user_input, candidates=candidates, limit=7
        )

        rag_context = self._build_rag_context(top_documents)

        # Stage 3: Build user profile for personalization intents
        user_profile = None
        if intent in (
            ConsultantMode.PERSONAL_STANDARD_EVALUATION,
            ConsultantMode.JOB_RECOMMEND,
            ConsultantMode.DEEP_ANALYSIS_EVALUATION,
        ):
            user_profile = self._build_user_profile(user_id)

        agent_intent = Intent(intent.value)
        final_state = await execute_agent_flow(
            intent=agent_intent,
            user_input=user_input,
            rag_context=rag_context,
            action_type="DEFAULT",
            user_profile=user_profile,
        )

        # Build log strings of ALL hybrid candidates for quality inspection
        request_log = f"User query: {user_input}\nIntent: {intent.value}"

        docs_log = []
        for idx, doc in enumerate(candidates, start=1):
            job, company, distance = doc
            similarity = 1.0 - distance
            docs_log.append(
                f"Candidate {idx}: Job ID: {job.id}, Title: {job.title}, Company: {company.name}, Distance: {distance:.6f}, Similarity: {similarity:.6f}"
            )

        # Mark which documents made it to final RAG
        final_ids = {doc[0].id for doc in top_documents}
        response_log = "All Hybrid Candidates & Retrieval Quality:\n"
        for entry, doc in zip(docs_log, candidates, strict=True):
            is_selected = " [SELECTED FOR RAG]" if doc[0].id in final_ids else ""
            response_log += f"{entry}{is_selected}\n"

        response_log += f"\nAgent Output:\n{final_state.get('final_result', '')}"

        # Create history entry
        consultant_repo.create_history(
            session=self.db,
            user_id=user_id,
            user_input=user_input,
            output=final_state.get("final_result", ""),
            consultant_mode=intent,
            request_log=request_log,
            response_log=response_log,
            input_embedding=user_vector,
        )

        return final_state

    async def process_agent_intent(
        self, user_id: uuid.UUID, intent: ConsultantMode, action_type: ActionType
    ) -> dict:
        """System/agent services flow with broader database context and execution logging."""
        top_documents = consultant_repo.get_latest_jobs(session=self.db, limit=20)

        rag_context = self._build_rag_context(top_documents)

        user_input = f"Thống kê phân tích thị trường cho hành động: {action_type.value}"
        agent_intent = Intent(intent.value)
        final_state = await execute_agent_flow(
            intent=agent_intent,
            user_input=user_input,
            rag_context=rag_context,
            action_type=action_type.value,
        )

        # Build log strings for logging history
        request_log = (
            f"System query for Action: {action_type.value}\nIntent: {intent.value}"
        )

        docs_log = []
        for idx, doc in enumerate(top_documents, start=1):
            job, company = doc
            docs_log.append(
                f"Doc {idx}: Job ID: {job.id}, Title: {job.title}, Company: {company.name}"
            )
        response_log = (
            "Top RAG Documents:\n"
            + "\n".join(docs_log)
            + f"\n\nAgent Output:\n{final_state.get('final_result', '')}"
        )

        # Create history entry
        consultant_repo.create_history(
            session=self.db,
            user_id=user_id,
            user_input=user_input,
            output=final_state.get("final_result", ""),
            consultant_mode=intent,
            request_log=request_log,
            response_log=response_log,
            input_embedding=None,
        )

        return final_state
