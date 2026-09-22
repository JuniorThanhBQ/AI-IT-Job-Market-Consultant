import logging
import os
from pathlib import Path

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session, select

import app.db.base  # noqa: F401
from app.core.db import engine
from app.core.security import verify_password
from app.modules.user.models import User
from app.modules.user.repository import create_user, get_user_by_email
from app.utils.utils_configs import parse_env_file

logger = logging.getLogger(__name__)

security_basic = HTTPBasic()


def authenticate_admin(
    credentials: HTTPBasicCredentials = Depends(security_basic),
) -> User:
    with Session(engine) as session:
        statement = select(User).where(User.email == credentials.username)
        user = session.exec(statement).first()
        if (
            user
            and user.hashed_password
            and verify_password(credentials.password, user.hashed_password)
            and user.is_superuser
            and user.is_active
        ):
            return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Basic"},
    )


def create_admin_account() -> None:
    env_data: dict[str, str] = {}
    search_roots = [Path("."), Path(__file__).resolve().parent.parent.parent]
    for base_path in search_roots:
        env_data.update(parse_env_file(base_path / ".env"))

    env_data.update(os.environ)
    first_superuser = env_data.get("FIRST_SUPERUSER")
    first_superuser_password = env_data.get("FIRST_SUPERUSER_PASSWORD")
    secret_key = env_data.get("SECRET_KEY") or env_data.get("secret_key")

    if not first_superuser or not first_superuser_password or not secret_key:
        logger.error("Invalid environment key for admin")
        return

    with Session(engine) as session:
        existing_user = get_user_by_email(session=session, email=first_superuser)
        if existing_user:
            logger.warning(f"Admin account '{first_superuser}' already exists.")
            return

        admin_password = f"{secret_key}_{first_superuser_password}"
        create_user(
            session=session,
            email=first_superuser,
            password=admin_password,
            username="admin",
            is_superuser=True,
        )
