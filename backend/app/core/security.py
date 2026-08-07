from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pwdlib import PasswordHash
from pwdlib.hashers.argon2 import Argon2Hasher
from pwdlib.hashers.bcrypt import BcryptHasher
from sqlmodel import Session, select

from app.core.config import settings
from app.core.db import engine
from app.modules.user.models import User

password_hash = PasswordHash(
    (
        Argon2Hasher(),
        BcryptHasher(),
    )
)


ALGORITHM = "HS256"


def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(
    plain_password: str, hashed_password: str
) -> tuple[bool, str | None]:
    try:
        return password_hash.verify_and_update(plain_password, hashed_password)
    except Exception:
        return plain_password == hashed_password, None


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)


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
