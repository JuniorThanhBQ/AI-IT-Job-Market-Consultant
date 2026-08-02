from sqladmin import ModelView

from app.modules.job.models import Job
from app.modules.user.models import User


class UserAdmin(ModelView, model=User):
    column_list = ["id", "email", "is_active", "is_superuser"]
    column_searchable_list = ["email"]
    icon = "fa-solid fa-user"


class JobAdmin(ModelView, model=Job):
    column_list = ["id", "title", "company_id", "status"]
    column_searchable_list = ["title"]
    icon = "fa-solid fa-briefcase"
