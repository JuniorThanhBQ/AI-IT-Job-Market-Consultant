import logging
from typing import cast, Any
from sqlalchemy import func, text
from sqlalchemy.orm import selectinload
from sqlmodel import select

from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.company.models import Company, CompanyEmbedding
from app.utils.embeddings import generate_embedding_async, DEFAULT_EMBEDDING_MODEL


logger = logging.getLogger(__name__)


class CompanyRepository:
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

    async def get_by_name(self, name: str) -> Company | None:
        if not name or not name.strip():
            return None
        cleaned = name.strip().lower()
        statement = (
            select(Company)
            .where(func.lower(func.trim(Company.name)) == cleaned)
            .options(selectinload(cast(Any, Company.embedding)))
        )
        result = await self.session.exec(statement)
        return result.first()

    async def save_or_update(
        self, company: Company, generate_embedding: bool = True
    ) -> Company:
        if not company.name:
            raise ValueError("Company name is required for repository operations.")

        company_name_clean = company.name.strip()
        lock_key = f"company:{company_name_clean.lower()}"
        await self._acquire_advisory_lock(lock_key)

        existing = await self.get_by_name(company_name_clean)

        needs_embedding = True
        if existing and existing.embedding:
            if existing.vector_context == company.vector_context:
                needs_embedding = False

        embedding_obj = None
        if generate_embedding and needs_embedding and company.vector_context:
            try:
                vector = await generate_embedding_async(
                    company.vector_context, model_name=DEFAULT_EMBEDDING_MODEL
                )
                embedding_obj = CompanyEmbedding(
                    embedding=vector,
                    embedding_model=DEFAULT_EMBEDDING_MODEL,
                    token_used=getattr(vector, "token_used", 0.0),
                    latency=getattr(vector, "latency", 0.0),
                    log=getattr(vector, "log", None),
                )
            except Exception as e:
                logger.error(
                    f"Failed to generate embedding for company '{company_name_clean}': {e}"
                )

        if existing:
            self._update_company_fields(existing, company)
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
                company.name = company_name_clean
                self.session.add(company)
                if embedding_obj:
                    company.embedding = embedding_obj
                await self.session.flush()
                return company
        except IntegrityError as orig_err:
            existing = await self.get_by_name(company_name_clean)
            if existing:
                self._update_company_fields(existing, company)
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
                raise RuntimeError(
                    f"[CompanyRepository] IntegrityError occurred during insert of company '{company_name_clean}', "
                    f"but get_by_name returned None! This indicates a database snapshot visibility issue (isolation level) "
                    f"or a name comparison mismatch (normalization/collation). Original error: {orig_err}"
                ) from orig_err

    @staticmethod
    def _update_company_fields(target: Company, source: Company) -> None:
        target.industry = source.industry or target.industry
        target.size = source.size or target.size
        target.website = source.website or target.website
        target.slogan = source.slogan or target.slogan
        target.company_type = source.company_type or target.company_type
        target.country = source.country or target.country
        target.working_days = source.working_days or target.working_days
        target.overtime_policy = source.overtime_policy or target.overtime_policy
        target.vector_context = source.vector_context or target.vector_context

        if source.description:
            if "is an active technology employer" not in source.description:
                target.description = source.description
            elif not target.description:
                target.description = source.description

        if source.location:
            if source.location.strip().lower() != "vietnam":
                target.location = source.location
            elif not target.location or target.location.strip().lower() == "vietnam":
                target.location = source.location

        if source.addresses:
            if not target.addresses:
                target.addresses = []
            existing_addresses = {a.strip().lower() for a in target.addresses if a}
            for addr in source.addresses:
                if addr and addr.strip().lower() not in existing_addresses:
                    target.addresses.append(addr.strip())
                    existing_addresses.add(addr.strip().lower())

        if source.benefits:
            if not target.benefits:
                target.benefits = []
            existing_benefits = {b.strip().lower() for b in target.benefits if b}
            for new_b in source.benefits:
                if new_b and new_b.strip().lower() not in existing_benefits:
                    target.benefits.append(new_b.strip())
                    existing_benefits.add(new_b.strip().lower())
