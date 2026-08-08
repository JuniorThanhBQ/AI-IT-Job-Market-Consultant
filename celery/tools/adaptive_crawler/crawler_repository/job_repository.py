import logging
from typing import cast, Any
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from sqlmodel import select
from app.core.enums import JobStatus
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.job.models import Job, Skills, JobEmbedding
from app.utils.embeddings import generate_embedding_async, DEFAULT_EMBEDDING_MODEL
from app.modules.company.models import Company
from .company_repository import CompanyRepository

logger = logging.getLogger(__name__)


class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _acquire_advisory_lock(self, lock_key: str) -> None:
        try:
            bind = self.session.get_bind()
            if bind and getattr(bind.dialect, "name", "") == "postgresql":
                await self.session.execute(
                    text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
                    {"key": lock_key},
                )
        except Exception as e:
            logger.debug(f"Advisory lock skipped or unavailable for '{lock_key}': {e}")

    async def get_by_url(self, url: str) -> Job | None:
        if not url:
            return None
        cleaned = url.strip()
        statement = (
            select(Job)
            .where(Job.url == cleaned)
            .options(selectinload(cast(Any, Job.embedding)))
        )
        result = await self.session.exec(statement)
        return result.first()

    async def get_by_content_hash(self, content_hash: str) -> Job | None:
        if not content_hash:
            return None
        statement = (
            select(Job)
            .where(Job.content_hash == content_hash)
            .options(selectinload(cast(Any, Job.embedding)))
        )
        result = await self.session.exec(statement)
        return result.first()

    async def get_open_jobs_batch(self, limit: int = 100, offset: int = 0) -> list[Job]:
        statement = (
            select(Job)
            .where(Job.status == JobStatus.OPEN)
            .options(
                selectinload(cast(Any, Job.embedding)),
                selectinload(cast(Any, Job.company)).selectinload(
                    cast(Any, Company.embedding)
                ),
            )
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.exec(statement)
        return list(result.all())

    async def save_or_update(self, job: Job, generate_embedding: bool = True) -> Job:
        if not job.url:
            raise ValueError("Job URL is required for repository operations.")

        job_url_clean = job.url.strip()
        lock_key = f"job:{job_url_clean.lower()}"
        await self._acquire_advisory_lock(lock_key)

        temp_company = job.company
        temp_skills = job.skills

        if temp_company and hasattr(temp_company, "jobs") and job in temp_company.jobs:
            temp_company.jobs.remove(job)

        if temp_skills:
            for skill in temp_skills:
                if hasattr(skill, "jobs") and job in skill.jobs:
                    skill.jobs.remove(job)

        job.company = None
        job.skills = []

        persisted_company = None
        if temp_company:
            company_repo = CompanyRepository(self.session)
            persisted_company = await company_repo.save_or_update(
                temp_company, generate_embedding=generate_embedding
            )

        persisted_skills = []
        if temp_skills:
            seen_skills = set()
            for skill in temp_skills:
                if not skill.name:
                    continue
                cleaned_skill_name = skill.name.strip()
                skill_name_lower = cleaned_skill_name.lower()
                if skill_name_lower in seen_skills:
                    continue
                seen_skills.add(skill_name_lower)
                skill.name = cleaned_skill_name
                try:
                    async with self.session.begin_nested():
                        self.session.add(skill)
                        await self.session.flush()
                    persisted_skills.append(skill)
                except IntegrityError:
                    stmt = select(Skills).where(
                        func.lower(func.trim(Skills.name)) == skill_name_lower
                    )
                    res = await self.session.exec(stmt)
                    existing_skill = res.first()
                    if existing_skill:
                        persisted_skills.append(existing_skill)

        existing = await self.get_by_url(job_url_clean)
        if not existing and job.content_hash:
            existing_by_hash = await self.get_by_content_hash(job.content_hash)
            if existing_by_hash:
                if (
                    existing_by_hash.source == job.source
                    and existing_by_hash.status == JobStatus.CLOSED
                ):
                    existing = existing_by_hash
                    job.status = job.status or JobStatus.OPEN
                else:
                    return existing_by_hash

        needs_embedding = True
        if existing and existing.embedding:
            if existing.vector_context == job.vector_context:
                needs_embedding = False

        embedding_obj = None
        if generate_embedding and needs_embedding and job.vector_context:
            try:
                vector = await generate_embedding_async(
                    job.vector_context, model_name=DEFAULT_EMBEDDING_MODEL
                )
                embedding_obj = JobEmbedding(
                    embedding=vector,
                    embedding_model=DEFAULT_EMBEDDING_MODEL,
                    token_used=getattr(vector, "token_used", 0.0),
                    latency=getattr(vector, "latency", 0.0),
                    log=getattr(vector, "log", None),
                )
            except Exception as e:
                logger.error(
                    f"Failed to generate embedding for job '{job_url_clean}': {e}"
                )

        if existing:
            if persisted_company:
                existing.company = persisted_company
                existing.company_id = persisted_company.id
            if persisted_skills:
                existing.skills = persisted_skills

            self._update_job_fields(existing, job)
            if embedding_obj:
                if existing.embedding:
                    existing.embedding.embedding = embedding_obj.embedding
                    existing.embedding.embedding_model = embedding_obj.embedding_model
                    existing.embedding.token_used = embedding_obj.token_used
                    existing.embedding.latency = embedding_obj.latency
                    existing.embedding.log = embedding_obj.log
                else:
                    existing.embedding = embedding_obj
            self.session.add(existing)
            await self.session.flush()
            return existing

        try:
            async with self.session.begin_nested():
                job.url = job_url_clean
                self.session.add(job)

                if persisted_company:
                    job.company = persisted_company
                    job.company_id = persisted_company.id

                if persisted_skills:
                    job.skills = persisted_skills

                if embedding_obj:
                    job.embedding = embedding_obj

                await self.session.flush()
                return job
        except IntegrityError:
            existing = await self.get_by_url(job_url_clean)
            if not existing and job.content_hash:
                existing_by_hash = await self.get_by_content_hash(job.content_hash)
                if existing_by_hash:
                    if (
                        existing_by_hash.source == job.source
                        and existing_by_hash.status == JobStatus.CLOSED
                    ):
                        existing = existing_by_hash
                        job.status = job.status or JobStatus.OPEN
                    else:
                        return existing_by_hash

            if existing:
                if persisted_company:
                    existing.company = persisted_company
                    existing.company_id = persisted_company.id
                if persisted_skills:
                    existing.skills = persisted_skills
                self._update_job_fields(existing, job)
                if embedding_obj:
                    if existing.embedding:
                        existing.embedding.embedding = embedding_obj.embedding
                        existing.embedding.embedding_model = (
                            embedding_obj.embedding_model
                        )
                        existing.embedding.token_used = embedding_obj.token_used
                        existing.embedding.latency = embedding_obj.latency
                        existing.embedding.log = embedding_obj.log
                    else:
                        existing.embedding = embedding_obj
                self.session.add(existing)
                await self.session.flush()
                return existing
            else:
                raise

    async def save(self, job: Job, generate_embedding: bool = True) -> Job:
        return await self.save_or_update(job, generate_embedding=generate_embedding)

    @staticmethod
    def _update_job_fields(target: Job, source: Job) -> None:
        target.url = source.url or target.url
        target.title = source.title or target.title
        target.job_description = source.job_description or target.job_description
        target.expired_date = source.expired_date or target.expired_date
        target.seniority = source.seniority or target.seniority
        target.min_salary = source.min_salary
        target.max_salary = source.max_salary
        target.currency = source.currency or target.currency
        target.working_hours = source.working_hours or target.working_hours
        target.working_model = source.working_model or target.working_model
        target.status = source.status or target.status
        target.content_hash = source.content_hash or target.content_hash
        target.responsibilities = source.responsibilities or target.responsibilities
        target.required_qualifications = (
            source.required_qualifications or target.required_qualifications
        )
        target.nice_to_have = source.nice_to_have or target.nice_to_have
        target.domains = source.domains or target.domains
        target.vector_context = source.vector_context or target.vector_context
        if source.source:
            target.source = source.source

        if source.company:
            target.company = source.company
            target.company_id = source.company.id

        if source.skills:
            target.skills = source.skills

    async def drop(self, job: Job) -> None:
        await self.session.delete(job)
        await self.session.flush()

    async def get_all_urls(self) -> list[str]:
        statement = select(Job.url)
        result = await self.session.exec(statement)
        return list(result.all())
