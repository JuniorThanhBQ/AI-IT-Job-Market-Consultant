import json
import logging
from typing import Any, cast

from app.core.db import engine
from app.core.enums import JobStatus
from app.modules.job.models import Job, JobSkill, Skills
from sqlalchemy import func, select
from sqlmodel import Session

logger = logging.getLogger(__name__)


def execute_top_skills_chart(
    limit: int = 15,
    seniority_filter: str | None = None,
) -> str:
    limit = max(1, min(50, limit))

    try:
        with Session(engine) as session:
            stmt = (
                select(
                    cast(Any, Skills.name),
                    cast(Any, Skills.category),
                    func.count(cast(Any, JobSkill.job_id)).label("job_count"),
                )
                .join(JobSkill, cast(Any, Skills.id) == cast(Any, JobSkill.skill_id))
                .join(Job, cast(Any, Job.id) == cast(Any, JobSkill.job_id))
                .where(cast(Any, Job.status) == JobStatus.OPEN)
            )

            if seniority_filter:
                stmt = stmt.where(cast(Any, Job.seniority) == seniority_filter)

            stmt = (
                stmt.group_by(cast(Any, Skills.name), cast(Any, Skills.category))
                .order_by(func.count(cast(Any, JobSkill.job_id)).desc())
                .limit(limit)
            )

            rows = session.exec(cast(Any, stmt)).all()

            chart_data = [
                {"label": name, "value": count, "category": category}
                for name, category, count in rows
            ]

            return json.dumps(chart_data, ensure_ascii=False)

    except Exception:
        logger.exception("Error querying top skills chart data")
        return json.dumps(
            {"error": "Error querying top skills chart data."},
            ensure_ascii=False,
        )
