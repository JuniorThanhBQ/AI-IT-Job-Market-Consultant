from sqladmin import ModelView

from app.modules.user.models import User


class UserAdmin(ModelView, model=User):
    column_list = ["id", "email", "is_active", "is_superuser"]
    column_searchable_list = ["email"]
    form_excluded_columns = ["is_superuser", "last_login"]
    icon = "fa-solid fa-user"
