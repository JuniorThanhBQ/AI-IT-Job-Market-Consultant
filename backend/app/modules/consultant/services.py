import json
import os
import uuid
from collections.abc import AsyncGenerator
from typing import Any, cast

from sqlmodel import Session, select

from agents.hybrid_rag.embeddings import build_user_profile
from agents.hybrid_rag.reranker import rerank_candidates_via_api
from agents.hybrid_rag.retriever import build_rag_context
from agents.subagents.market_analysis_agent.tools import (
    execute_market_consultant_stream,
)
from agents.supervisor.graph import Intent
from agents.supervisor.orchestrator import execute_agent_flow
from agents.tools.document_parser.main import parse_document
from app.core.enums import ActionType, ConsultantMode
from app.modules.consultant import repository as consultant_repo
from app.modules.consultant.models import ConsultantHistory
from app.modules.consultee_profile import repository as profile_repo
from app.utils.embeddings import generate_embedding_async

ALL_HYBRID_CANDIDATES_HEADER = "All Hybrid Candidates & Retrieval Quality:\n"
SELECTED_FOR_RAG_TAG = " [SELECTED FOR RAG]"


class ConsultantService:
    def __init__(self, db: Session):
        self.db = db

    def _save_chatbot_history(
        self,
        *,
        user_id: uuid.UUID,
        intent: ConsultantMode,
        user_input: str,
        user_vector: list[float],
        candidates: list[Any],
        top_documents: list[Any],
        final_text: str,
    ) -> None:
        request_log = f"User query: {user_input}\nIntent: {intent.value}"
        docs_log = []
        for idx, doc in enumerate(candidates, start=1):
            job, company, distance = doc
            similarity = 1.0 - distance
            docs_log.append(
                f"Candidate {idx}: Job ID: {job.id}, Title: {job.title}, Company: {company.name}, Distance: {distance:.6f}, Similarity: {similarity:.6f}"
            )

        final_ids = {doc[0].id for doc in top_documents}
        response_log = ALL_HYBRID_CANDIDATES_HEADER
        for entry, doc in zip(docs_log, candidates, strict=True):
            is_selected = SELECTED_FOR_RAG_TAG if doc[0].id in final_ids else ""
            response_log += f"{entry}{is_selected}\n"

        response_log += f"\nAgent Output:\n{final_text}"

        consultant_repo.create_history(
            session=self.db,
            user_id=user_id,
            user_input=user_input,
            output=final_text,
            consultant_mode=intent,
            request_log=request_log,
            response_log=response_log,
            input_embedding=user_vector,
        )

    async def _stream_market_analysis(
        self,
        *,
        user_id: uuid.UUID,
        intent: ConsultantMode,
        user_input: str,
        user_vector: list[float],
        candidates: list[Any],
        top_documents: list[Any],
        rag_context: str,
    ) -> AsyncGenerator[str]:
        final_text = ""
        async for chunk in execute_market_consultant_stream(
            query=user_input, rag_context=rag_context
        ):
            final_text += chunk
            yield json.dumps({"type": "chunk", "text": chunk}) + "\n"

        self._save_chatbot_history(
            user_id=user_id,
            intent=intent,
            user_input=user_input,
            user_vector=user_vector,
            candidates=candidates,
            top_documents=top_documents,
            final_text=final_text,
        )

        yield (
            json.dumps(
                {
                    "type": "metadata",
                    "intent": intent.value,
                    "execution_order": ["market_analysis"],
                    "tool_outputs": {},
                    "final_result": final_text,
                }
            )
            + "\n"
        )

    async def _stream_agent_flow(
        self,
        *,
        user_id: uuid.UUID,
        intent: ConsultantMode,
        user_input: str,
        user_vector: list[float],
        candidates: list[Any],
        top_documents: list[Any],
        rag_context: str,
        user_profile: Any,
    ) -> AsyncGenerator[str]:
        agent_intent = Intent(intent.value)
        final_state = await execute_agent_flow(
            intent=agent_intent,
            user_input=user_input,
            rag_context=rag_context,
            action_type="DEFAULT",
            user_profile=user_profile,
        )

        final_text = final_state.get("final_result", "")
        yield json.dumps({"type": "chunk", "text": final_text}) + "\n"

        self._save_chatbot_history(
            user_id=user_id,
            intent=intent,
            user_input=user_input,
            user_vector=user_vector,
            candidates=candidates,
            top_documents=top_documents,
            final_text=final_text,
        )

        yield (
            json.dumps(
                {
                    "type": "metadata",
                    "intent": intent.value,
                    "execution_order": final_state.get("execution_order", []),
                    "tool_outputs": final_state.get("tool_outputs"),
                    "final_result": final_text,
                }
            )
            + "\n"
        )

    async def process_chatbot_intent(
        self, user_id: uuid.UUID, intent: ConsultantMode, user_input: str
    ) -> dict:
        user_vector = await generate_embedding_async(user_input)
        candidates = consultant_repo.get_hybrid_candidates(
            session=self.db, user_query=user_input, user_vector=user_vector, limit=30
        )

        top_documents = await rerank_candidates_via_api(
            query=user_input, candidates=candidates, limit=4
        )

        rag_context = build_rag_context(top_documents)

        user_profile = None
        if intent in (
            ConsultantMode.PERSONAL_STANDARD_EVALUATION,
            ConsultantMode.JOB_RECOMMEND,
            ConsultantMode.DEEP_ANALYSIS_EVALUATION,
        ):
            user_profile = build_user_profile(self.db, user_id)

        agent_intent = Intent(intent.value)
        final_state = await execute_agent_flow(
            intent=agent_intent,
            user_input=user_input,
            rag_context=rag_context,
            action_type="DEFAULT",
            user_profile=user_profile,
        )

        final_text = final_state.get("final_result", "")
        self._save_chatbot_history(
            user_id=user_id,
            intent=intent,
            user_input=user_input,
            user_vector=user_vector,
            candidates=candidates,
            top_documents=top_documents,
            final_text=final_text,
        )

        return final_state

    async def stream_chatbot_intent(
        self, user_id: uuid.UUID, intent: ConsultantMode, user_input: str
    ) -> AsyncGenerator[str]:
        user_vector = await generate_embedding_async(user_input)
        candidates = consultant_repo.get_hybrid_candidates(
            session=self.db, user_query=user_input, user_vector=user_vector, limit=10
        )

        # top_documents = await rerank_candidates_via_api(
        #     query=user_input, candidates=candidates, limit=5
        # )

        rag_context = build_rag_context(candidates[:5])

        user_profile = None
        if intent in (
            ConsultantMode.PERSONAL_STANDARD_EVALUATION,
            ConsultantMode.JOB_RECOMMEND,
            ConsultantMode.DEEP_ANALYSIS_EVALUATION,
        ):
            user_profile = build_user_profile(self.db, user_id)

        if intent != ConsultantMode.DEEP_ANALYSIS_EVALUATION:
            generator = self._stream_market_analysis(
                user_id=user_id,
                intent=intent,
                user_input=user_input,
                user_vector=user_vector,
                candidates=candidates,
                top_documents=candidates[:5],
                rag_context=rag_context,
            )
        else:
            generator = self._stream_agent_flow(
                user_id=user_id,
                intent=intent,
                user_input=user_input,
                user_vector=user_vector,
                candidates=candidates,
                top_documents=candidates[:5],
                rag_context=rag_context,
                user_profile=user_profile,
            )

        async for chunk in generator:
            yield chunk

    async def process_agent_intent(
        self, user_id: uuid.UUID, intent: ConsultantMode, action_type: ActionType
    ) -> dict:
        top_documents = consultant_repo.get_latest_jobs(session=self.db, limit=20)
        rag_context = build_rag_context(top_documents)
        user_input = f"Thống kê phân tích thị trường cho hành động: {action_type.value}"
        agent_intent = Intent(intent.value)
        user_profile = None
        if intent in (
            ConsultantMode.PERSONAL_STANDARD_EVALUATION,
            ConsultantMode.JOB_RECOMMEND,
            ConsultantMode.DEEP_ANALYSIS_EVALUATION,
        ):
            profile = profile_repo.get_profile_by_user_id(
                session=self.db, user_id=user_id
            )
            if profile and profile.cv:
                exceed_page_limit = False
                structure_illogical = False
                bad_text_recognition = False
                if profile.cv.attachment:
                    file_path = os.path.join("uploads", profile.cv.attachment)
                    if os.path.exists(file_path):
                        parsed_res = parse_document(file_path, "cv")
                        exceed_page_limit = parsed_res["exceed_page_limit"]
                        structure_illogical = parsed_res["structure_illogical"]
                        bad_text_recognition = parsed_res["bad_text_recognition"]
                    else:
                        structure_illogical = not profile.cv.skills
                        bad_text_recognition = (
                            not profile.cv.summary or len(profile.cv.summary) < 10
                        )
                else:
                    structure_illogical = not profile.cv.skills
                    bad_text_recognition = (
                        not profile.cv.summary or len(profile.cv.summary) < 10
                    )
                profile_repo.update_cv(
                    session=self.db,
                    cv=profile.cv,
                    data={
                        "exceed_page_limit": exceed_page_limit,
                        "structure_illogical": structure_illogical,
                        "bad_text_recognition": bad_text_recognition,
                    },
                )
            user_profile = build_user_profile(self.db, user_id)
        final_state = await execute_agent_flow(
            intent=agent_intent,
            user_input=user_input,
            rag_context=rag_context,
            action_type=action_type.value,
            user_profile=user_profile,
        )
        if intent in (
            ConsultantMode.PERSONAL_STANDARD_EVALUATION,
            ConsultantMode.DEEP_ANALYSIS_EVALUATION,
        ):
            profile = profile_repo.get_profile_by_user_id(
                session=self.db, user_id=user_id
            )
            if profile and profile.cv:
                score = 60
                if (
                    final_state.get("tool_outputs")
                    and "personalization_analysis" in final_state["tool_outputs"]
                ):
                    score = int(
                        final_state["tool_outputs"]["personalization_analysis"].get(
                            "score", 60
                        )
                    )
                using_cv_mode = profile.cv.using_cv_mode
                has_attachment = bool(profile.cv.attachment)
                if not using_cv_mode or not has_attachment:
                    score = min(score, 80)
                profile_repo.update_cv(
                    session=self.db, cv=profile.cv, data={"score": score}
                )
                if "personalization_analysis" in final_state["tool_outputs"]:
                    final_state["tool_outputs"]["personalization_analysis"]["score"] = (
                        score
                    )

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

    def get_history(self, user_id: uuid.UUID) -> list[ConsultantHistory]:
        stmt = (
            select(ConsultantHistory)
            .where(ConsultantHistory.user_id == user_id)
            .where(ConsultantHistory.user_input != "deleted")
            .where(ConsultantHistory.user_input != "")
            .where(ConsultantHistory.output != "deleted")
            .where(ConsultantHistory.output != "")
            .order_by(cast(Any, ConsultantHistory.id))
        )
        return list(self.db.exec(stmt).all())

    def clear_history(self, user_id: uuid.UUID) -> int:
        stmt = select(ConsultantHistory).where(ConsultantHistory.user_id == user_id)
        histories = self.db.exec(stmt).all()
        for h in histories:
            h.user_input = "deleted"
            h.output = "deleted"
            self.db.add(h)
        self.db.commit()
        return len(histories)
