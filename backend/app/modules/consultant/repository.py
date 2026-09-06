import time
import uuid
from typing import Any, cast

from sqlalchemy.orm import selectinload
from sqlmodel import Session, or_, select

from app.core.enums import ConsultantMode
from app.modules.company.models import Company
from app.modules.consultant.models import ConsultantHistory
from app.modules.job.models import Job, JobEmbedding
from app.modules.shared.bm25 import BM25Index
from app.modules.shared.rrf import reciprocal_rank_fusion


def get_hybrid_candidates(
    *, session: Session, user_query: str, user_vector: list[float], limit: int = 15
) -> tuple[list[tuple[Job, Company, float]], float, float]:
    t_start = time.time()
    distance_expr = cast(Any, JobEmbedding.embedding).cosine_distance(user_vector)
    stmt_embedding = (
        select(JobEmbedding.job_id, distance_expr)
        .order_by(distance_expr)
        .limit(limit * 2)
    )
    embedding_results = session.exec(stmt_embedding).all()
    bm25_results = BM25Index.search(user_query, top_n=limit * 2)
    bm25_job_ids = [job_id for job_id, _score in bm25_results]
    vector_job_ids = [row[0] for row in embedding_results]
    all_job_ids = list(set(vector_job_ids + bm25_job_ids))

    doc_map = {}
    if all_job_ids:
        stmt_jobs = (
            select(Job, Company)
            .join(Company)
            .options(selectinload(cast(Any, Job.skills)))
            .where(cast(Any, Job.id).in_(all_job_ids))
        )
        job_results = session.exec(stmt_jobs).all()
        job_lookup = {job.id: (job, company) for job, company in job_results}
        distances = {row[0]: float(row[1]) for row in embedding_results}
        for job_id in all_job_ids:
            if job_id in job_lookup:
                job, company = job_lookup[job_id]
                dist = distances.get(job_id, 1.0)
                doc_map[job_id] = (job, company, dist)

    t_retrieval = time.time()
    retrieval_latency = t_retrieval - t_start
    rrf_results = reciprocal_rank_fusion([vector_job_ids, bm25_job_ids], k=60)
    sorted_job_ids = [job_id for job_id, _score in rrf_results if job_id in doc_map][
        :limit
    ]

    rrf_latency = time.time() - t_retrieval
    candidates = [doc_map[j_id] for j_id in sorted_job_ids]

    return candidates, retrieval_latency, rrf_latency


def get_latest_jobs(*, session: Session, limit: int = 20) -> list[tuple[Job, Company]]:
    stmt = (
        select(Job, Company)
        .join(Company)
        .order_by(cast(Any, Job.id).desc())
        .limit(limit)
    )
    result = session.exec(stmt)
    return result.all()  # type: ignore[return-value]


def create_history(
    *,
    session: Session,
    user_id: uuid.UUID,
    user_input: str,
    output: str,
    consultant_mode: ConsultantMode,
    request_log: str,
    response_log: str,
    input_embedding: list[float] | None = None,
    token_used: float = 0.0,
    latency: float = 0.0,
) -> ConsultantHistory:
    history = ConsultantHistory(
        user_id=user_id,
        user_input=user_input,
        output=output,
        consultant_mode=consultant_mode,
        request_log=request_log,
        response_log=response_log,
        input_embedding=input_embedding,
        token_used=token_used,
        latency=latency,
    )
    session.add(history)
    session.commit()
    session.refresh(history)
    return history


def get_history_by_user_id(
    *, session: Session, user_id: uuid.UUID
) -> list[ConsultantHistory]:
    stmt = (
        select(ConsultantHistory)
        .where(ConsultantHistory.user_id == user_id)
        .where(ConsultantHistory.user_input != "")
        .where(ConsultantHistory.output != "")
        .order_by(cast(Any, ConsultantHistory.id))
    )
    return list(session.exec(stmt).all())


def clear_history_by_user_id(*, session: Session, user_id: uuid.UUID) -> int:
    stmt = (
        select(ConsultantHistory)
        .where(ConsultantHistory.user_id == user_id)
        .where(
            or_(
                ConsultantHistory.user_input != "",
                ConsultantHistory.output != "",
            )
        )
    )
    histories = list(session.exec(stmt).all())
    for h in histories:
        h.user_input = ""
        h.output = ""
        session.add(h)
    session.commit()
    return len(histories)
