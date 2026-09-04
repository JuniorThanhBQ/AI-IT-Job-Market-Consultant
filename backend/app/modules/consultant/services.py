import json
import time
import uuid
from collections.abc import AsyncGenerator
from typing import Any, cast

from agents.hybrid_rag.retriever import build_rag_context
from agents.subagents.market_analysis_agent.tools import (
    execute_market_consultant_stream,
)
from agents.supervisor.graph import Intent
from agents.supervisor.orchestrator import execute_agent_flow
from sqlmodel import Session, select

from app.core.enums import ConsultantMode
from app.modules.consultant import repository as consultant_repo
from app.modules.consultant.models import ConsultantHistory
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
        token_used: float = 0.0,
        latency: float = 0.0,
        embedding_latency: float = 0.0,
        retrieval_latency: float = 0.0,
        rrf_latency: float = 0.0,
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
        latencies_header = (
            f"Embedding Latency: {embedding_latency:.4f}s\n"
            f"Retrieval Latency: {retrieval_latency:.4f}s\n"
            f"RRF Latency: {rrf_latency:.4f}s\n\n"
        )
        response_log = latencies_header + ALL_HYBRID_CANDIDATES_HEADER
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
            token_used=token_used,
            latency=latency,
        )

    async def stream_market_analysis(
        self,
        *,
        user_id: uuid.UUID,
        intent: ConsultantMode,
        user_input: str,
        user_vector: list[float],
        candidates: list[Any],
        top_documents: list[Any],
        rag_context: str,
        start_time: float,
        embedding_latency: float,
        retrieval_latency: float,
        rrf_latency: float,
    ) -> AsyncGenerator[str]:
        final_text = ""
        async for chunk in execute_market_consultant_stream(
            query=user_input, rag_context=rag_context
        ):
            final_text += chunk
            yield json.dumps({"type": "chunk", "text": chunk}) + "\n"

        latency = time.time() - start_time
        token_used = getattr(user_vector, "token_used", 0.0)

        self._save_chatbot_history(
            user_id=user_id,
            intent=intent,
            user_input=user_input,
            user_vector=user_vector,
            candidates=candidates,
            top_documents=top_documents,
            final_text=final_text,
            token_used=token_used,
            latency=latency,
            embedding_latency=embedding_latency,
            retrieval_latency=retrieval_latency,
            rrf_latency=rrf_latency,
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

    async def stream_agent_flow(
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
        start_time: float,
        embedding_latency: float,
        retrieval_latency: float,
        rrf_latency: float,
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

        latency = time.time() - start_time
        token_used = getattr(user_vector, "token_used", 0.0)

        self._save_chatbot_history(
            user_id=user_id,
            intent=intent,
            user_input=user_input,
            user_vector=user_vector,
            candidates=candidates,
            top_documents=top_documents,
            final_text=final_text,
            token_used=token_used,
            latency=latency,
            embedding_latency=embedding_latency,
            retrieval_latency=retrieval_latency,
            rrf_latency=rrf_latency,
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

    async def stream_chatbot_intent(
        self, user_id: uuid.UUID, intent: ConsultantMode, user_input: str
    ) -> AsyncGenerator[str]:
        start_time = time.time()
        user_vector = await generate_embedding_async(user_input)
        embedding_latency = time.time() - start_time
        candidates, retrieval_latency, rrf_latency = (
            consultant_repo.get_hybrid_candidates(
                session=self.db,
                user_query=user_input,
                user_vector=user_vector,
                limit=15,
            )
        )

        rag_context = build_rag_context(candidates[:3])

        generator = self.stream_market_analysis(
            user_id=user_id,
            intent=intent,
            user_input=user_input,
            user_vector=user_vector,
            candidates=candidates,
            top_documents=candidates[:5],
            rag_context=rag_context,
            start_time=start_time,
            embedding_latency=embedding_latency,
            retrieval_latency=retrieval_latency,
            rrf_latency=rrf_latency,
        )

        async for chunk in generator:
            yield chunk

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
