import asyncio
import logging
import re
from datetime import datetime
from typing import Any, cast

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlmodel import col

from app.modules.company.models import Company
from app.modules.job.models import Job, Skills
from app.utils.embeddings import generate_embedding

logger = logging.getLogger(__name__)


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, job: Job) -> Job:
        if (
            not job.title
            or job.title.strip().lower() in ["unknown title", "no title", ""]
            or not job.job_description
            or job.job_description.strip().lower()
            in ["no description provided", "not provided", ""]
        ):
            logger.warning(
                f"Quality gate rejected job from {job.source} (URL: {job.url}) "
                f"due to missing title or job_description."
            )
            return job

        original_skills: list[Skills] = list(job.skills) if job.skills else []
        job.skills = []

        existing_company = None
        if job.company:
            company = job.company
            job.company = None

            company_upsert = (
                pg_insert(Company)
                .values(
                    name=company.name.strip() if company.name else "Unknown Company",
                    industry=company.industry,
                    size=company.size,
                    location=company.location,
                    description=company.description,
                    website=company.website,
                    slogan=company.slogan,
                    company_type=company.company_type,
                    country=company.country,
                    addresses=company.addresses,
                    working_days=company.working_days,
                    overtime_policy=company.overtime_policy,
                    vector_context=company.vector_context,
                    embedding=company.embedding,
                )
                .on_conflict_do_update(
                    index_elements=["name"],
                    set_={
                        "industry": company.industry,
                        "size": company.size,
                        "location": company.location,
                        "description": company.description,
                        "website": company.website,
                        "slogan": company.slogan,
                        "company_type": company.company_type,
                        "country": company.country,
                        "addresses": company.addresses,
                        "working_days": company.working_days,
                        "overtime_policy": company.overtime_policy,
                        "vector_context": company.vector_context,
                        "embedding": company.embedding,
                    },
                )
                .returning(cast(Any, Company.id))
            )
            company_res = await self.session.execute(company_upsert)
            cid = company_res.scalar_one_or_none()
            if cid:
                job.company_id = cid
            else:
                with self.session.no_autoflush:
                    company_stmt = select(Company).where(
                        col(Company.name)
                        == (company.name.strip() if company.name else "")
                    )
                    company_stmt_res = await self.session.execute(company_stmt)
                    existing_company = company_stmt_res.scalars().first()

                if existing_company:
                    job.company_id = existing_company.id
                else:
                    logger.warning(
                        f"Post-upsert re-fetch for company '{company.name}' returned empty (URL: {job.url})"
                    )

        if job.company_id is None and job.vector_context:
            match = re.search(r"Company:\s*([^.]+)\.", job.vector_context)
            if match:
                extracted_cname = match.group(1).strip()
                if extracted_cname:
                    with self.session.no_autoflush:
                        company_stmt = select(Company).where(
                            func.lower(Company.name) == extracted_cname.lower()
                        )
                        company_stmt_res = await self.session.execute(company_stmt)
                        found_company = company_stmt_res.scalars().first()

                    if found_company:
                        job.company_id = found_company.id
                    else:
                        auto_company_upsert = (
                            pg_insert(Company)
                            .values(
                                name=extracted_cname,
                                industry="Information Technology",
                                size="Unknown",
                                location="Vietnam",
                                description=f"{extracted_cname} is an active employer in the IT market.",
                                website="",
                                vector_context=f"Company Name: {extracted_cname}. Industry: Information Technology.",
                            )
                            .on_conflict_do_update(
                                index_elements=["name"],
                                set_={"updated_date": datetime.utcnow()},
                            )
                            .returning(cast(Any, Company.id))
                        )
                        auto_res = await self.session.execute(auto_company_upsert)
                        auto_cid = auto_res.scalar_one_or_none()
                        if auto_cid:
                            job.company_id = auto_cid

        resolved_skills: list[Skills] = []
        for skill in original_skills:
            skill_upsert = (
                pg_insert(Skills)
                .values(name=skill.name, category=skill.category)
                .on_conflict_do_update(
                    index_elements=["name"],
                    set_={"category": skill.category},
                )
                .returning(cast(Any, Skills.id))
            )
            skill_res = await self.session.execute(skill_upsert)
            sid = skill_res.scalar_one_or_none()
            existing_skill = None
            if sid:
                existing_skill = await self.session.get(Skills, sid)

            if not existing_skill:
                with self.session.no_autoflush:
                    skill_stmt = select(Skills).where(col(Skills.name) == skill.name)
                    skill_stmt_res = await self.session.execute(skill_stmt)
                    existing_skill = skill_stmt_res.scalars().first()

            if existing_skill:
                resolved_skills.append(existing_skill)
            else:
                logger.warning(
                    f"Post-upsert re-fetch for skill '{skill.name}' returned empty (URL: {job.url})"
                )

        with self.session.no_autoflush:
            statement_url = (
                select(Job)
                .where(col(Job.url) == job.url)
                .options(
                    selectinload(cast(Any, Job.skills)),
                    selectinload(cast(Any, Job.company)),
                )
            )
            result_url = await self.session.execute(statement_url)
            existing_job = result_url.scalars().first()

            if not existing_job and job.content_hash:
                statement_hash = (
                    select(Job)
                    .where(col(Job.content_hash) == job.content_hash)
                    .options(
                        selectinload(cast(Any, Job.skills)),
                        selectinload(cast(Any, Job.company)),
                    )
                )
                result_hash = await self.session.execute(statement_hash)
                existing_job = result_hash.scalars().first()

        if (
            existing_job
            and existing_job.embedding
            and existing_job.vector_context == job.vector_context
        ):
            job.embedding = existing_job.embedding
        elif job.vector_context:
            job.embedding = await asyncio.to_thread(
                generate_embedding, job.vector_context
            )

        if existing_job:
            existing_job.title = job.title
            existing_job.job_description = job.job_description
            existing_job.expired_date = job.expired_date
            existing_job.updated_date = job.updated_date
            existing_job.seniority = job.seniority
            existing_job.min_salary = job.min_salary
            existing_job.max_salary = job.max_salary
            existing_job.currency = job.currency
            existing_job.working_hours = job.working_hours
            existing_job.working_model = job.working_model
            existing_job.status = job.status
            existing_job.content_hash = job.content_hash
            existing_job.responsibilities = job.responsibilities
            existing_job.required_qualifications = job.required_qualifications
            existing_job.nice_to_have = job.nice_to_have
            existing_job.domains = job.domains
            existing_job.vector_context = job.vector_context
            existing_job.embedding = job.embedding
            existing_job.source = job.source
            existing_job.url = url if (url := job.url) else existing_job.url
            if job.company_id is not None:
                existing_job.company_id = job.company_id
            elif existing_job.company_id is None:
                target_context = existing_job.vector_context or job.vector_context
                if target_context:
                    match = re.search(r"Company:\s*([^.]+)\.", target_context)
                    if match:
                        extracted_cname = match.group(1).strip()
                        if extracted_cname:
                            with self.session.no_autoflush:
                                company_stmt = select(Company).where(
                                    func.lower(Company.name) == extracted_cname.lower()
                                )
                                company_stmt_res = await self.session.execute(
                                    company_stmt
                                )
                                found_company = company_stmt_res.scalars().first()

                            if found_company:
                                existing_job.company_id = found_company.id
                            else:
                                auto_company_upsert = (
                                    pg_insert(Company)
                                    .values(
                                        name=extracted_cname,
                                        industry="Information Technology",
                                        size="Unknown",
                                        location="Vietnam",
                                        description=f"{extracted_cname} is an active employer in the IT market.",
                                        website="",
                                        vector_context=f"Company Name: {extracted_cname}. Industry: Information Technology.",
                                    )
                                    .on_conflict_do_update(
                                        index_elements=["name"],
                                        set_={"updated_date": datetime.utcnow()},
                                    )
                                    .returning(cast(Any, Company.id))
                                )
                                auto_res = await self.session.execute(
                                    auto_company_upsert
                                )
                                auto_cid = auto_res.scalar_one_or_none()
                                if auto_cid:
                                    existing_job.company_id = auto_cid

            existing_job.skills = resolved_skills
            try:
                async with self.session.begin_nested():
                    self.session.add(existing_job)
                    await self.session.flush()
                return existing_job
            except IntegrityError as err:
                logger.warning(
                    f"IntegrityError updating existing job (URL: {job.url}): {err}. Retrying lookup."
                )
                with self.session.no_autoflush:
                    result_retry = await self.session.execute(statement_url)
                    retried_job = result_retry.scalars().first()
                    if not retried_job and job.content_hash:
                        statement_hash = (
                            select(Job)
                            .where(col(Job.content_hash) == job.content_hash)
                            .options(
                                selectinload(cast(Any, Job.skills)),
                                selectinload(cast(Any, Job.company)),
                            )
                        )
                        res_hash = await self.session.execute(statement_hash)
                        retried_job = res_hash.scalars().first()
                if retried_job:
                    return retried_job
                logger.error(
                    f"Existing job update failed after IntegrityError retry for URL: {job.url}"
                )
                raise
        else:
            try:
                async with self.session.begin_nested():
                    self.session.add(job)
                    await self.session.flush()

                    job.skills = resolved_skills
                    await self.session.flush()

                return job
            except IntegrityError as err:
                logger.warning(
                    f"IntegrityError inserting new job (URL: {job.url}): {err}. Retrying lookup."
                )
                try:
                    self.session.expunge(job)
                except Exception:
                    pass
                with self.session.no_autoflush:
                    result_retry = await self.session.execute(statement_url)
                    retried_job = result_retry.scalars().first()
                    if not retried_job and job.content_hash:
                        statement_hash = (
                            select(Job)
                            .where(col(Job.content_hash) == job.content_hash)
                            .options(
                                selectinload(cast(Any, Job.skills)),
                                selectinload(cast(Any, Job.company)),
                            )
                        )
                        res_hash = await self.session.execute(statement_hash)
                        retried_job = res_hash.scalars().first()
                if retried_job:
                    return retried_job
                logger.error(
                    f"New job insert failed after IntegrityError retry for URL: {job.url}"
                )
                raise
