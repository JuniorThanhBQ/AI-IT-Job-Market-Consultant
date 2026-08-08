from app.db.base_model import BaseModel
from app.modules.company.models import Company, CompanyEmbedding
from app.modules.consultant.models import ConsultantHistory
from app.modules.consultee_profile.models import (
    ConsulteeProfile,
    CurriculumVitae,
    CurriculumVitaeProject,
)
from app.modules.job.models import Job, JobEmbedding, JobSkill, Skills
from app.modules.user.models import User

CompanyEmbedding.model_rebuild()
Company.model_rebuild()
JobSkill.model_rebuild()
Skills.model_rebuild()
JobEmbedding.model_rebuild()
Job.model_rebuild()
ConsultantHistory.model_rebuild()
User.model_rebuild()
ConsulteeProfile.model_rebuild()
CurriculumVitae.model_rebuild()
CurriculumVitaeProject.model_rebuild()

__all__ = [
    "BaseModel",
    "Company",
    "CompanyEmbedding",
    "Job",
    "JobEmbedding",
    "JobSkill",
    "Skills",
    "User",
    "ConsultantHistory",
    "ConsulteeProfile",
    "CurriculumVitae",
    "CurriculumVitaeProject",
]
