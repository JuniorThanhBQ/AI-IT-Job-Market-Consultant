import json
from typing import Any, cast

from langchain_core.tools import tool
from sqlmodel import Session, func, or_, select

from app.core.db import engine
from app.core.enums import JobStatus, SeniorityLevel
from app.modules.job.models import Job
from app.tools.get_15_top_skills import get_15_top_skills
from app.tools.hybrid_retrieval import get_hybrid_candidates
from app.utils.embeddings import generate_embedding_async


@tool
def get_top_skills_tool(query: str = "", limit: int = 15) -> str:
    """Look up the most in-demand skills in the current IT job market.
    Use this tool when the user asks about popular skills, trending technologies,
    or what skills are most requested by employers.

    Args:
        query: Optional keyword to filter skills by job title or description
               (e.g. "backend", "data engineer"). Leave empty for overall market.
        limit: Number of top skills to return. Default 15, max 15.

    Returns:
        JSON list of skills with name, category, job count, and market percentage.
    """
    limit = min(limit, 15)
    with Session(engine) as session:
        results = get_15_top_skills(session=session, query=query or None, limit=limit)
    return json.dumps(results, ensure_ascii=False)


@tool
async def search_jobs_tool(query: str, limit: int = 10) -> str:
    """Search for IT job listings matching a query using hybrid retrieval (semantic + keyword).
    Use this tool when the user asks about specific job openings, roles,
    or wants to see what positions are available.

    Args:
        query: Search query describing the type of jobs to find
               (e.g. "senior Python backend developer", "React frontend Ho Chi Minh").
        limit: Number of jobs to return. Default 10, max 15.

    Returns:
        JSON list of job listings with title, company, seniority, salary range,
        working model, skills, and URL.
    """
    limit = min(limit, 15)
    user_vector = await generate_embedding_async(query)
    with Session(engine) as session:
        candidates, _, _ = get_hybrid_candidates(
            session=session,
            user_query=query,
            user_vector=list(user_vector),
            limit=limit,
            safe=True,
        )
        results = []
        for job, company, score in candidates:
            skills_list = [s.name for s in job.skills] if job.skills else []
            results.append(
                {
                    "title": job.title,
                    "company": company.name if company else "N/A",
                    "seniority": str(job.seniority.value)
                    if job.seniority
                    else "Unknown",
                    "salary_range": f"{job.min_salary:,.0f} - {job.max_salary:,.0f}",
                    "currency": str(job.currency.value) if job.currency else "VND",
                    "working_model": str(job.working_model.value)
                    if job.working_model
                    else "N/A",
                    "skills": skills_list,
                    "url": job.url,
                    "relevance_score": round(float(max(0.0, 1.0 - score)), 4),
                }
            )
    return json.dumps(results, ensure_ascii=False)


@tool
def salary_benchmark_tool(query: str = "", seniority: str = "") -> str:
    """Get salary statistics for IT jobs in the current market.
    Use this tool when the user asks about salary ranges, compensation benchmarks,
    or how much specific roles pay.

    Args:
        query: Optional keyword to filter by job title or description
               (e.g. "Python developer", "DevOps").
        seniority: Optional seniority level filter. One of: Intern, Fresher,
                   Junior, Mid, Senior, Lead, Manager, Director, Executive.

    Returns:
        JSON with salary statistics including min, max, average salary,
        job count, and currency breakdown.
    """
    with Session(engine) as session:
        select_fn = cast(Any, select)
        stmt = select_fn(
            func.count(cast(Any, Job.id)),
            func.min(cast(Any, Job.min_salary)),
            func.max(cast(Any, Job.max_salary)),
            func.avg(cast(Any, Job.min_salary)),
            func.avg(cast(Any, Job.max_salary)),
            Job.currency,
        ).where(Job.status == JobStatus.OPEN)

        if query:
            stmt = stmt.where(
                or_(
                    cast(Any, Job.title).ilike(f"%{query}%"),
                    cast(Any, Job.job_description).ilike(f"%{query}%"),
                )
            )

        if seniority:
            try:
                level = SeniorityLevel(seniority.strip().capitalize())
                stmt = stmt.where(Job.seniority == level)
            except ValueError:
                pass

        stmt = stmt.group_by(Job.currency)
        rows = session.exec(stmt).all()

    results = []
    for row in rows:
        results.append(
            {
                "job_count": int(row[0]) if row[0] else 0,
                "min_salary": float(row[1]) if row[1] else 0.0,
                "max_salary": float(row[2]) if row[2] else 0.0,
                "avg_min_salary": round(float(row[3]), 2) if row[3] else 0.0,
                "avg_max_salary": round(float(row[4]), 2) if row[4] else 0.0,
                "currency": str(row[5]) if row[5] else "VND",
            }
        )
    return json.dumps(results, ensure_ascii=False)
