from sqladmin import ModelView

from app.modules.consultant.models import ConsultantHistory


class ConsultantHistoryAdmin(ModelView, model=ConsultantHistory):
    name = "Consultant History"
    name_plural = "Consultant Histories"
    column_list = ["id", "user_id", "consultant_mode", "latency"]
    icon = "fa-solid fa-history"
