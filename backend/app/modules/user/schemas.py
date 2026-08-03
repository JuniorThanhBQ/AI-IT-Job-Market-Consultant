import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

# ──────────────────────────────────────────────
# Request Schemas
# ──────────────────────────────────────────────


class UserRegister(SQLModel):
    """Public registration request."""

    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    username: str | None = Field(default=None, max_length=255)


class UserCreate(SQLModel):
    """Admin-only user creation. is_superuser always forced to False via API."""

    email: str = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    username: str | None = Field(default=None, max_length=255)
    is_active: bool = True


class UserUpdate(SQLModel):
    """Admin-only user update."""

    email: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    username: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    """Self-service user update (email and username only)."""

    username: str | None = Field(default=None, max_length=255)
    email: str | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    """Change password (requires current password)."""

    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class ForgotPassword(SQLModel):
    """Request a password reset token."""

    email: str = Field(max_length=255)


class NewPassword(SQLModel):
    """Reset password using a token."""

    token: str
    new_password: str = Field(min_length=8, max_length=40)


class VerifyAccount(SQLModel):
    """Account verification request (temp mock)."""

    token: str


# ──────────────────────────────────────────────
# Response Schemas
# ──────────────────────────────────────────────


class UserPublic(SQLModel):
    """Public user representation."""

    id: uuid.UUID
    email: str
    is_verified: bool
    is_active: bool
    is_superuser: bool
    username: str | None = None
    last_login: datetime | None = None


class UsersPublic(SQLModel):
    """Paginated list of public users."""

    data: list[UserPublic]
    count: int


class Token(SQLModel):
    """JWT access token response."""

    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """JWT token payload."""

    sub: str | None = None


class MessageResponse(SQLModel):
    """Generic message response."""

    message: str
