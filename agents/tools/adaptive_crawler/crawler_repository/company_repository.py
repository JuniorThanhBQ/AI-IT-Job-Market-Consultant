import logging
from sqlalchemy import func, text
from sqlmodel import select

from sqlalchemy.exc import IntegrityError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.company.models import Company
from app.utils.embeddings import generate_embedding_async


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
        if not name:
            return None
        cleaned = name.strip().lower()
        statement = select(Company).where(
            func.lower(func.trim(Company.name)) == cleaned
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
                company.embedding = existing.embedding
                company.embedding_model = existing.embedding_model
                company.embedding_version = existing.embedding_version
                needs_embedding = False

        if (
            generate_embedding
            and needs_embedding
            and company.vector_context
            and not company.embedding
        ):
            try:
                company.embedding = await generate_embedding_async(
                    company.vector_context, model_name="models/gemini-embedding-001"
                )
                company.embedding_model = "models/gemini-embedding-001"
                company.embedding_version = 1
            except Exception as e:
                logger.error(
                    f"Failed to generate embedding for company '{company_name_clean}': {e}"
                )

        if existing:
            self._update_company_fields(existing, company)
            self.session.add(existing)
            await self.session.flush()
            return existing

        try:
            async with self.session.begin_nested():
                company.name = company_name_clean
                self.session.add(company)
                await self.session.flush()
                return company
        except IntegrityError as orig_err:
            existing = await self.get_by_name(company_name_clean)
            if existing:
                self._update_company_fields(existing, company)
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
        target.location = source.location or target.location
        target.description = source.description or target.description
        target.website = source.website or target.website
        target.slogan = source.slogan or target.slogan
        target.company_type = source.company_type or target.company_type
        target.country = source.country or target.country
        target.addresses = source.addresses or target.addresses
        target.working_days = source.working_days or target.working_days
        target.overtime_policy = source.overtime_policy or target.overtime_policy
        target.vector_context = source.vector_context or target.vector_context
        if source.embedding:
            target.embedding = source.embedding
            target.embedding_model = source.embedding_model
            target.embedding_version = source.embedding_version
        if source.benefits:
            existing_names = {b.name.strip().lower() for b in target.benefits if b.name}
            from app.modules.company.models import CompanyBenefit

            for new_b in source.benefits:
                if new_b.name and new_b.name.strip().lower() not in existing_names:
                    target.benefits.append(
                        CompanyBenefit(name=new_b.name, company=target)
                    )
                    existing_names.add(new_b.name.strip().lower())
