import uuid
from typing import Any, cast

from sqlmodel import Session, select, text

from app.core.enums import ConsultantMode
from app.modules.company.models import Company
from app.modules.consultant.models import ConsultantHistory
from app.modules.job.models import Job, JobEmbedding


def get_relevant_jobs_by_vector(
    *, session: Session, user_vector: list[float], limit: int = 5
) -> list[tuple[Job, Company, float]]:
    """Query jobs, companies and their cosine distance sorted by similarity."""
    distance_expr = cast(Any, JobEmbedding.embedding).cosine_distance(user_vector)
    stmt = (
        select(Job, Company, distance_expr)
        .join(Company)
        .join(JobEmbedding)
        .order_by(distance_expr)
        .limit(limit)
    )
    result = session.exec(stmt)
    return result.all()  # type: ignore[return-value]


def get_hybrid_candidates(
    *, session: Session, user_query: str, user_vector: list[float], limit: int = 15
) -> list[tuple[Job, Company, float]]:
    """Retrieve top candidates using Vector search + Lexical full-text search merged via RRF."""
    # 1. Vector Search Query
    distance_expr = cast(Any, JobEmbedding.embedding).cosine_distance(user_vector)
    stmt_vector = (
        select(Job, Company, distance_expr)
        .join(Company)
        .join(JobEmbedding)
        .order_by(distance_expr)
        .limit(limit * 2)
    )
    vector_results = session.exec(stmt_vector).all()

    # 2. Lexical Search Query
    from sqlalchemy import func

    tsquery = func.plainto_tsquery("english", user_query)
    tsvector = func.to_tsvector("english", Job.vector_context)

    stmt_lexical = (
        select(Job, Company, func.ts_rank(tsvector, tsquery).label("lexical_score"))
        .join(Company)
        .where(tsvector.op("@@")(tsquery))
        .order_by(text("lexical_score DESC"))
        .limit(limit * 2)
    )
    try:
        lexical_results = session.exec(stmt_lexical).all()
    except Exception:
        # Fallback to simple ILIKE search if full-text search query fails or isn't indexed
        stmt_fallback = (
            select(Job, Company, text("1.0"))
            .join(Company)
            .where(cast(Any, Job.vector_context).ilike(f"%{user_query}%"))
            .limit(limit * 2)
        )
        lexical_results = session.exec(stmt_fallback).all()

    # 3. Reciprocal Rank Fusion (RRF)
    doc_map = {}

    vector_rank = {}
    for rank, (job, company, dist) in enumerate(vector_results, start=1):
        doc_map[job.id] = (job, company, dist)
        vector_rank[job.id] = rank

    lexical_rank = {}
    for rank, (job, company, _score) in enumerate(lexical_results, start=1):
        if job.id not in doc_map:
            doc_map[job.id] = (job, company, 1.0)
        lexical_rank[job.id] = rank

    k = 60
    rrf_scores = {}
    for job_id in doc_map:
        v_score = 1.0 / (k + vector_rank[job_id]) if job_id in vector_rank else 0.0
        l_score = 1.0 / (k + lexical_rank[job_id]) if job_id in lexical_rank else 0.0
        rrf_scores[job_id] = v_score + l_score

    sorted_job_ids = sorted(
        rrf_scores.keys(), key=lambda j_id: rrf_scores[j_id], reverse=True
    )[:limit]

    return [doc_map[j_id] for j_id in sorted_job_ids]


def get_latest_jobs(*, session: Session, limit: int = 20) -> list[tuple[Job, Company]]:
    """Query recent jobs and companies for aggregation or statistics."""
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
) -> ConsultantHistory:
    """Create a ConsultantHistory log entry."""
    history = ConsultantHistory(
        user_id=user_id,
        user_input=user_input,
        output=output,
        consultant_mode=consultant_mode,
        request_log=request_log,
        response_log=response_log,
        input_embedding=input_embedding,
    )
    session.add(history)
    session.commit()
    session.refresh(history)
    return history
