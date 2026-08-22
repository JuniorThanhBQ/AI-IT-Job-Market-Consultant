import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from app.utils.validators import SafeEmailStr, SafeStr


class UserRegister(SQLModel):
    email: SafeEmailStr = Field(max_length=255)
    password: SafeStr = Field(min_length=8, max_length=40)
    username: SafeStr | None = Field(default=None, max_length=255)


class UserCreate(SQLModel):
    email: SafeEmailStr = Field(max_length=255)
    password: SafeStr = Field(min_length=8, max_length=40)
    username: SafeStr | None = Field(default=None, max_length=255)
    is_active: bool = True


class UserUpdate(SQLModel):
    email: SafeEmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    username: SafeStr | None = Field(default=None, max_length=255)
    password: SafeStr | None = Field(default=None, min_length=8, max_length=40)


class NewPassword(SQLModel):
    token: SafeStr
    new_password: SafeStr = Field(min_length=8, max_length=40)


class UserPublic(SQLModel):
    id: uuid.UUID
    email: str
    is_verified: bool
    is_active: bool
    is_superuser: bool
    username: str | None = None
    last_login: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class MessageResponse(SQLModel):
    message: str
