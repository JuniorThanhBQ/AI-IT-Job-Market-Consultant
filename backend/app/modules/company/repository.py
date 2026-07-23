from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlmodel import col

from app.modules.company.models import Company, CompanyBenefit
from app.utils.embeddings import generate_embedding


class CompanyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Company | None:
        statement = select(Company).where(col(Company.name) == name)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def get_by_id(self, company_id: int) -> Company | None:
        return await self.session.get(Company, company_id)

    async def save(self, company: Company) -> Company:
        if company.vector_context:
            company.embedding = generate_embedding(company.vector_context)

        existing = await self.get_by_name(company.name)
        if existing:
            existing.industry = company.industry
            existing.size = company.size
            existing.location = company.location
            existing.description = company.description
            existing.website = company.website
            existing.slogan = company.slogan
            existing.company_type = company.company_type
            existing.country = company.country
            existing.addresses = company.addresses
            existing.working_days = company.working_days
            existing.overtime_policy = company.overtime_policy
            existing.updated_date = company.updated_date
            existing.vector_context = company.vector_context
            existing.embedding = company.embedding

            statement = select(CompanyBenefit).where(
                col(CompanyBenefit.company_id) == existing.id
            )
            old_benefits_res = await self.session.execute(statement)
            old_benefits = old_benefits_res.scalars().all()

            for b in old_benefits:
                await self.session.delete(b)

            if company.benefits:
                for b in company.benefits:
                    new_benefit = CompanyBenefit(
                        name=b.name,
                        company_id=existing.id,
                        created_date=b.created_date,
                        updated_date=b.updated_date,
                    )
                    self.session.add(new_benefit)

            try:
                async with self.session.begin_nested():
                    self.session.add(existing)
                    await self.session.flush()
            except IntegrityError:
                pass
            return existing
        else:
            try:
                async with self.session.begin_nested():
                    self.session.add(company)
                    await self.session.flush()
                return company
            except IntegrityError:
                existing = await self.get_by_name(company.name)
                if existing:
                    return existing
                return company
