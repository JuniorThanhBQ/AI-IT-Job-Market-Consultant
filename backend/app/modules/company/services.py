from __future__ import annotations

from sqlmodel import Session

from app.core.enums import CompanyType
from app.modules.company import repository as company_repo
from app.modules.company.models import Company


class CompanyService:
    def __init__(self, db: Session):
        self.db = db

    def get_company(self, company_id: int) -> Company | None:
        return company_repo.get_company_by_id(session=self.db, company_id=company_id)

    def list_companies(
        self,
        name: str | None = None,
        industry: str | None = None,
        company_type: CompanyType | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Company]:
        return company_repo.list_companies(
            session=self.db,
            name=name,
            industry=industry,
            company_type=company_type,
            skip=skip,
            limit=limit,
        )
