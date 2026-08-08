import uuid

from fastapi import FastAPI
from sqladmin import Admin
from sqladmin.authentication import AuthenticationBackend
from sqlmodel import Session, select
from starlette.requests import Request

from app.core.config import settings
from app.core.db import engine
from app.core.security import verify_password
from app.modules.company.admin import CompanyAdmin
from app.modules.consultant.admin import ConsultantHistoryAdmin
from app.modules.consultee_profile.admin import (
    ConsulteeProfileAdmin,
    CurriculumVitaeAdmin,
    CurriculumVitaeProjectAdmin,
)
from app.modules.job.admin import JobAdmin, SkillsAdmin
from app.modules.user.admin import UserAdmin
from app.modules.user.models import User


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
        if not isinstance(email, str) or not isinstance(password, str):
            return False
        with Session(engine) as session:
            statement = select(User).where(User.email == email)
            user = session.exec(statement).first()
            if (
                user
                and user.hashed_password
                and verify_password(password, user.hashed_password)
                and user.is_superuser
                and user.is_active
            ):
                request.session.update({"token": str(user.id)})
                return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        try:
            user_uuid = uuid.UUID(token)
        except ValueError:
            return False
        with Session(engine) as session:
            user = session.get(User, user_uuid)
            if user and user.is_superuser and user.is_active:
                return True
        return False


authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)


def init_admin(app: FastAPI) -> Admin:
    admin = Admin(app, engine, authentication_backend=authentication_backend)
    admin.add_view(UserAdmin)
    admin.add_view(JobAdmin)
    admin.add_view(SkillsAdmin)
    admin.add_view(CompanyAdmin)
    admin.add_view(ConsultantHistoryAdmin)
    admin.add_view(ConsulteeProfileAdmin)
    admin.add_view(CurriculumVitaeAdmin)
    admin.add_view(CurriculumVitaeProjectAdmin)
    return admin
