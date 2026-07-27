import logging
from sqlalchemy import func, text
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from app.core.enums import JobStatus
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.job.models import Job, Skills
from app.utils.embeddings import generate_embedding_async
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
        statement = select(Job).where(Job.url == cleaned)
        result = await self.session.exec(statement)
        return result.first()

    async def get_open_jobs_batch(self, limit: int = 100, offset: int = 0) -> list[Job]:
        statement = (
            select(Job).where(Job.status == JobStatus.OPEN).offset(offset).limit(limit)
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
            for skill in temp_skills:
                if not skill.name:
                    continue
                cleaned_skill_name = skill.name.strip()
                skill.name = cleaned_skill_name
                try:
                    async with self.session.begin_nested():
                        self.session.add(skill)
                        await self.session.flush()
                    persisted_skills.append(skill)
                except IntegrityError:
                    stmt = select(Skills).where(
                        func.lower(func.trim(Skills.name)) == cleaned_skill_name.lower()
                    )
                    res = await self.session.exec(stmt)
                    existing_skill = res.first()
                    if existing_skill:
                        persisted_skills.append(existing_skill)

        existing = await self.get_by_url(job_url_clean)

        if existing:
            if persisted_company:
                existing.company = persisted_company
                existing.company_id = persisted_company.id
            if persisted_skills:
                existing.skills = persisted_skills

            needs_embedding = True
            if existing.embedding:
                if existing.vector_context == job.vector_context:
                    job.embedding = existing.embedding
                    job.embedding_model = existing.embedding_model
                    job.embedding_version = existing.embedding_version
                    needs_embedding = False

            if (
                generate_embedding
                and needs_embedding
                and job.vector_context
                and not job.embedding
            ):
                try:
                    job.embedding = await generate_embedding_async(
                        job.vector_context, model_name="models/gemini-embedding-001"
                    )
                    job.embedding_model = "models/gemini-embedding-001"
                    job.embedding_version = 1
                except Exception as e:
                    logger.error(
                        f"Failed to generate embedding for job '{job_url_clean}': {e}"
                    )

            self._update_job_fields(existing, job)
            self.session.add(existing)
            await self.session.flush()
            return existing

        embedding = None
        embedding_model = None
        embedding_version = None
        if generate_embedding and job.vector_context and not job.embedding:
            try:
                embedding = await generate_embedding_async(
                    job.vector_context, model_name="models/gemini-embedding-001"
                )
                embedding_model = "models/gemini-embedding-001"
                embedding_version = 1
            except Exception as e:
                logger.error(
                    f"Failed to generate embedding for job '{job_url_clean}': {e}"
                )

        try:
            async with self.session.begin_nested():
                job.url = job_url_clean
                self.session.add(job)

                if persisted_company:
                    job.company = persisted_company
                    job.company_id = persisted_company.id

                if persisted_skills:
                    job.skills = persisted_skills

                if embedding:
                    job.embedding = embedding
                    job.embedding_model = embedding_model
                    job.embedding_version = embedding_version

                await self.session.flush()
                return job
        except IntegrityError:
            existing = await self.get_by_url(job_url_clean)
            if existing:
                if persisted_company:
                    existing.company = persisted_company
                    existing.company_id = persisted_company.id
                if persisted_skills:
                    existing.skills = persisted_skills
                self._update_job_fields(existing, job)
                if embedding:
                    existing.embedding = embedding
                    existing.embedding_model = embedding_model
                    existing.embedding_version = embedding_version
                self.session.add(existing)
                await self.session.flush()
                return existing
            else:
                raise

    async def save(self, job: Job, generate_embedding: bool = True) -> Job:
        return await self.save_or_update(job, generate_embedding=generate_embedding)

    @staticmethod
    def _update_job_fields(target: Job, source: Job) -> None:
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
        target.source = source.source or target.source

        if source.embedding:
            target.embedding = source.embedding
            target.embedding_model = source.embedding_model
            target.embedding_version = source.embedding_version

        if source.company:
            target.company = source.company
            target.company_id = source.company.id

        if source.skills:
            target.skills = source.skills
