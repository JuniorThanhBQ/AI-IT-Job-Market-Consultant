import time
from typing import Any, cast

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.modules.company.models import Company
from app.modules.job.models import Job, JobEmbedding
from app.tools.hybrid_retrieval.bm25 import BM25Index
from app.tools.hybrid_retrieval.rrf import reciprocal_rank_fusion
from app.utils.validators import vector_validator


def fetch_jobs_map(
    session: Session, job_ids: list[int]
) -> dict[int, tuple[Job, Company]]:
    if not job_ids:
        return {}

    stmt = (
        select(Job, Company)
        .join(Company)
        .options(selectinload(cast(Any, Job.skills)))
        .where(cast(Any, Job.id).in_(job_ids))
    )
    results = session.exec(stmt).all()
    return {job.id: (job, company) for job, company in results if job.id is not None}


def search_semantic_job_ids(
    session: Session, user_vector: list[float], limit: int
) -> tuple[list[int], dict[int, float]]:
    distance_expr = cast(Any, JobEmbedding.embedding).cosine_distance(user_vector)
    stmt = (
        select(JobEmbedding.job_id, distance_expr).order_by(distance_expr).limit(limit)
    )
    results = session.exec(stmt).all()
    job_ids = [row[0] for row in results]
    distances = {row[0]: float(row[1]) for row in results}
    return job_ids, distances


def search_lexical_job_ids(
    user_query: str, limit: int
) -> tuple[list[int], dict[int, float]]:
    results = BM25Index.search(user_query, top_n=limit)
    job_ids = [job_id for job_id, score in results]
    scores = {job_id: float(score) for job_id, score in results}
    return job_ids, scores


def semantic_search_candidates(
    *, session: Session, user_vector: list[float], limit: int = 15
) -> tuple[list[tuple[Job, Company, float]], float]:
    start_time = time.time()
    if not vector_validator(user_vector):
        return [], time.time() - start_time

    job_ids, distances = search_semantic_job_ids(session, user_vector, limit)
    job_map = fetch_jobs_map(session, job_ids)
    candidates: list[tuple[Job, Company, float]] = []
    for job_id in job_ids:
        if job_id in job_map:
            candidates.append(
                (job_map[job_id][0], job_map[job_id][1], distances[job_id])
            )
    return candidates, time.time() - start_time


def lexical_search_candidates(
    *, session: Session, user_query: str, limit: int = 15
) -> tuple[list[tuple[Job, Company, float]], float]:
    start_time = time.time()
    job_ids, scores = search_lexical_job_ids(user_query, limit)
    job_map = fetch_jobs_map(session, job_ids)
    candidates: list[tuple[Job, Company, float]] = []
    for job_id in job_ids:
        if job_id in job_map:
            candidates.append((job_map[job_id][0], job_map[job_id][1], scores[job_id]))
    return candidates, time.time() - start_time


def get_hybrid_candidates(
    *,
    session: Session,
    user_query: str,
    user_vector: list[float] | None = None,
    limit: int = 15,
    safe: bool = False,
) -> tuple[list[tuple[Job, Company, float]], float, float]:
    start_time = time.time()
    bm25_job_ids, bm25_scores = search_lexical_job_ids(user_query, limit * 2)
    if user_vector is None or not vector_validator(user_vector):
        if safe:
            job_map = fetch_jobs_map(session, bm25_job_ids[:limit])
            fallback_candidates: list[tuple[Job, Company, float]] = []
            for job_id in bm25_job_ids[:limit]:
                if job_id in job_map:
                    fallback_candidates.append(
                        (job_map[job_id][0], job_map[job_id][1], bm25_scores[job_id])
                    )
            retrieval_latency = time.time() - start_time
            return fallback_candidates, retrieval_latency, 0.0
        raise ValueError("Invalid user vector for hybrid search")

    vector_job_ids, distances = search_semantic_job_ids(session, user_vector, limit * 2)
    all_job_ids = list(set(vector_job_ids + bm25_job_ids))
    job_map = fetch_jobs_map(session, all_job_ids)
    job_candidate_map: dict[int, tuple[Job, Company, float]] = {}
    for job_id in all_job_ids:
        if job_id in job_map:
            job, company = job_map[job_id]
            distance = distances.get(job_id, 1.0)
            job_candidate_map[job_id] = (job, company, distance)

    retrieval_time = time.time()
    retrieval_latency = retrieval_time - start_time
    rrf_results = reciprocal_rank_fusion([vector_job_ids, bm25_job_ids], k=60)
    sorted_job_ids: list[int] = []
    for item in rrf_results:
        job_id = item[0]
        if job_id in job_candidate_map:
            sorted_job_ids.append(job_id)
            if len(sorted_job_ids) == limit:
                break

    rrf_latency = time.time() - retrieval_time
    candidates: list[tuple[Job, Company, float]] = []
    for job_id in sorted_job_ids:
        candidates.append(job_candidate_map[job_id])

    return candidates, retrieval_latency, rrf_latency
