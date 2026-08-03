"""Market Overview Tool — SQL-based market statistics aggregation.

Queries the database to produce comprehensive market statistics:
total jobs, distribution by seniority/working model, salary stats,
top domains, and top hiring companies.
"""

import json
import logging
from typing import Any, cast

from sqlalchemy import func, select, text
from sqlmodel import Session

from app.core.db import engine
from app.core.enums import JobStatus
from app.modules.company.models import Company
from app.modules.job.models import Job

logger = logging.getLogger(__name__)


def execute_market_overview(
    seniority_filter: str | None = None,
    working_model_filter: str | None = None,
) -> str:
    """Query comprehensive market statistics from the job database.

    Args:
        seniority_filter: Optional seniority level filter.
        working_model_filter: Optional working model filter.

    Returns:
        JSON string with market overview data.
    """
    try:
        with Session(engine) as session:
            # ── Base filter ──────────────────────────────────────
            base_filter: list[Any] = [Job.status == JobStatus.OPEN]
            if seniority_filter:
                base_filter.append(Job.seniority == seniority_filter)
            if working_model_filter:
                base_filter.append(Job.working_model == working_model_filter)

            # 1. Total jobs
            total_stmt = select(func.count(cast(Any, Job.id))).where(*base_filter)
            total_jobs = session.exec(cast(Any, total_stmt)).one()

            # 2. Distribution by seniority
            seniority_stmt = (
                select(cast(Any, Job.seniority), func.count(cast(Any, Job.id)))
                .where(*base_filter)
                .group_by(cast(Any, Job.seniority))
                .order_by(func.count(cast(Any, Job.id)).desc())
            )
            seniority_rows = session.exec(cast(Any, seniority_stmt)).all()
            by_seniority = [
                {"seniority": str(s), "count": c} for s, c in seniority_rows
            ]

            # 3. Distribution by working model
            wm_stmt = (
                select(cast(Any, Job.working_model), func.count(cast(Any, Job.id)))
                .where(*base_filter)
                .group_by(cast(Any, Job.working_model))
                .order_by(func.count(cast(Any, Job.id)).desc())
            )
            wm_rows = session.exec(cast(Any, wm_stmt)).all()
            by_working_model = [
                {"working_model": str(wm), "count": c} for wm, c in wm_rows
            ]

            # 4. Salary statistics (grouped by currency)
            salary_stmt = (
                select(
                    cast(Any, Job.currency),
                    func.min(cast(Any, Job.min_salary)).label("min_sal"),
                    func.max(cast(Any, Job.max_salary)).label("max_sal"),
                    func.avg(
                        (cast(Any, Job.min_salary) + cast(Any, Job.max_salary)) / 2
                    ).label("avg_sal"),
                    func.count(cast(Any, Job.id)).label("job_count"),
                )
                .where(*base_filter)
                .group_by(cast(Any, Job.currency))
            )
            salary_rows = session.exec(cast(Any, salary_stmt)).all()
            salary_stats = [
                {
                    "currency": str(currency),
                    "min_salary": float(min_s),
                    "max_salary": float(max_s),
                    "avg_salary": round(float(avg_s), 2),
                    "job_count": cnt,
                }
                for currency, min_s, max_s, avg_s, cnt in salary_rows
            ]

            # 5. Top domains (from JSONB array)
            domain_stmt = text("""
                SELECT d.domain, COUNT(*) as cnt
                FROM jobs j,
                     jsonb_array_elements_text(j.domains) AS d(domain)
                WHERE j.status = :status
                GROUP BY d.domain
                ORDER BY cnt DESC
                LIMIT 10
            """)
            domain_rows = session.execute(
                domain_stmt, {"status": JobStatus.OPEN.value}
            ).fetchall()
            top_domains = [{"domain": row[0], "count": row[1]} for row in domain_rows]

            # 6. Top hiring companies
            company_stmt = (
                select(
                    cast(Any, Company.name),
                    func.count(cast(Any, Job.id)).label("job_count"),
                )
                .join(Company, cast(Any, Job.company_id) == cast(Any, Company.id))
                .where(*base_filter)
                .group_by(cast(Any, Company.name))
                .order_by(func.count(cast(Any, Job.id)).desc())
                .limit(10)
            )
            company_rows = session.exec(cast(Any, company_stmt)).all()
            top_companies = [
                {"company": name, "count": cnt} for name, cnt in company_rows
            ]

            result = {
                "total_jobs": total_jobs,
                "by_seniority": by_seniority,
                "by_working_model": by_working_model,
                "salary_stats": salary_stats,
                "top_domains": top_domains,
                "top_companies": top_companies,
            }

            return json.dumps(result, ensure_ascii=False)

    except Exception:
        logger.exception("Error querying market overview data")
        return json.dumps(
            {"error": "Không thể truy vấn dữ liệu tổng quan thị trường."},
            ensure_ascii=False,
        )
