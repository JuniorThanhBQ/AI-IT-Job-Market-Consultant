from typing import Any, cast

from sqlmodel import Session, func, or_, select

from app.core.enums import JobStatus
from app.modules.job.models import Job, JobSkill, Skills


def get_15_top_skills(
    *,
    session: Session,
    query: str | None = None,
    limit: int = 15,
) -> list[dict[str, Any]]:
    count_stmt = select(func.count(cast(Any, Job.id))).where(
        Job.status == JobStatus.OPEN
    )
    if query:
        count_stmt = count_stmt.where(
            or_(
                cast(Any, Job.title).ilike(f"%{query}%"),
                cast(Any, Job.job_description).ilike(f"%{query}%"),
            )
        )
    total_count_result = session.exec(count_stmt).one()
    total_jobs = int(total_count_result) if total_count_result is not None else 0

    stmt = (
        select(
            Skills.id,
            Skills.name,
            Skills.category,
            func.count(cast(Any, JobSkill.job_id)),
        )
        .join(JobSkill, cast(Any, Skills.id) == cast(Any, JobSkill.skill_id))
        .join(Job, cast(Any, Job.id) == cast(Any, JobSkill.job_id))
        .where(Job.status == JobStatus.OPEN)
    )
    if query:
        stmt = stmt.where(
            or_(
                cast(Any, Job.title).ilike(f"%{query}%"),
                cast(Any, Job.job_description).ilike(f"%{query}%"),
            )
        )
    stmt = (
        stmt.group_by(
            cast(Any, Skills.id),
            cast(Any, Skills.name),
            cast(Any, Skills.category),
        )
        .order_by(func.count(cast(Any, JobSkill.job_id)).desc())
        .limit(limit)
    )
    rows = session.exec(stmt).all()

    results: list[dict[str, Any]] = []
    for row in rows:
        skill_id = int(row[0]) if row[0] is not None else 0
        skill_name = str(row[1])
        skill_category = str(row[2])
        job_count = int(row[3])
        percentage = round((job_count / total_jobs) * 100, 2) if total_jobs > 0 else 0.0
        results.append(
            {
                "id": skill_id,
                "name": skill_name,
                "category": skill_category,
                "count": job_count,
                "percentage": percentage,
            }
        )
    return results
