import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.utils.validators import SafeEmailStr, SafePasswordStr, SafeStr


class UserRegister(SQLModel):
    email: SafeEmailStr = Field(max_length=255)
    password: SafePasswordStr = Field(min_length=8, max_length=40)
    confirm_password: SafePasswordStr = Field(min_length=8, max_length=40)
    username: SafeStr | None = Field(default=None, max_length=255)


class PasswordReset(SQLModel):
    old_password: SafeStr = Field(min_length=8, max_length=40)
    new_password: SafePasswordStr = Field(min_length=8, max_length=40)
    confirm_new_password: SafePasswordStr = Field(min_length=8, max_length=40)


class VerificationConfirm(SQLModel):
    token: SafeStr


class VerificationRequest(SQLModel):
    email: SafeEmailStr


class UserPublic(SQLModel):
    id: uuid.UUID
    email: str
    is_verified: bool
    is_active: bool
    is_superuser: bool
    username: str | None = None
    last_login: datetime | None = None


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class MessageResponse(SQLModel):
    message: str
