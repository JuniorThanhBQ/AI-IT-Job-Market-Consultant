from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session, select

from app.core.db import engine
from app.core.security import verify_password
from app.modules.user.models import User

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
