from sqladmin import ModelView

from app.modules.consultee_profile.models import (
    ConsulteeProfile,
    CurriculumVitae,
    CurriculumVitaeProject,
)


class ConsulteeProfileAdmin(ModelView, model=ConsulteeProfile):
    column_list = ["id", "first_name", "last_name", "user_id"]
    column_searchable_list = ["first_name", "last_name"]
    icon = "fa-solid fa-id-card"


class CurriculumVitaeAdmin(ModelView, model=CurriculumVitae):
    column_list = ["id", "profile_id", "job_position", "score"]
    icon = "fa-solid fa-file-invoice"


class CurriculumVitaeProjectAdmin(ModelView, model=CurriculumVitaeProject):
    column_list = ["id", "cv_id", "name", "role"]
    icon = "fa-solid fa-project-diagram"
