import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class UserRegister(SQLModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    username: str | None = Field(default=None, max_length=255)


class UserCreate(SQLModel):
    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    username: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class UserUpdate(SQLModel):
    email: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    username: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


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
