from sqladmin import ModelView

from app.modules.job.models import Job, Skills


class JobAdmin(ModelView, model=Job):
    column_list = ["id", "title", "company_id", "status"]
    column_searchable_list = ["title"]
    icon = "fa-solid fa-briefcase"


class SkillsAdmin(ModelView, model=Skills):
    name = "Skill"
    name_plural = "Skills"
    column_list = ["id", "name", "category"]
    column_searchable_list = ["name"]
    icon = "fa-solid fa-tags"
