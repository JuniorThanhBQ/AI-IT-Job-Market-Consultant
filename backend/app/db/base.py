from app.db.base_model import BaseModel
from app.modules.company.models import Company, CompanyBenefit
from app.modules.job.models import Job, JobSkill, Skills

CompanyBenefit.model_rebuild()
Company.model_rebuild()
JobSkill.model_rebuild()
Skills.model_rebuild()
Job.model_rebuild()

__all__ = ["BaseModel", "Company", "CompanyBenefit", "Job", "JobSkill", "Skills"]
