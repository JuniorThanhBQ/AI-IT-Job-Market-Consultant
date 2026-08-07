from sqladmin import ModelView

from app.modules.company.models import Company


class CompanyAdmin(ModelView, model=Company):
    name = "Company"
    name_plural = "Companies"
    column_list = ["id", "name", "industry", "location"]
    column_searchable_list = ["name"]
    icon = "fa-solid fa-building"
