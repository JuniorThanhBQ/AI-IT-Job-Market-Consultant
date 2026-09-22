from datetime import UTC, datetime

from sqlmodel import Session, or_, select

from app.core.security import get_password_hash, verify_password
from app.modules.consultee_profile.models import ConsulteeProfile, CurriculumVitae
from app.modules.user.models import User


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def get_user_by_email_name(*, session: Session, email_name: str) -> User | None:
    statement = select(User).where(
        or_(
            User.username == email_name,
            User.email == email_name,
        )
    )
    return session.exec(statement).first()


def create_user(
    *,
    session: Session,
    email: str,
    password: str,
    username: str | None = None,
    is_superuser: bool = False,
) -> User:
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        username=username,
        is_superuser=is_superuser,
    )
    session.add(user)
    session.flush()
    profile = ConsulteeProfile(user_id=user.id)
    session.add(profile)
    session.flush()
    cv = CurriculumVitae(profile_id=profile.id)
    session.add(cv)
    session.commit()
    session.refresh(user)
    return user


def update_user(*, session: Session, db_user: User, user_data: dict) -> User:
    extra_data: dict = {}
    if "password" in user_data:
        password = user_data.pop("password")
        if password:
            extra_data["hashed_password"] = get_password_hash(password)
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def update_last_login(*, session: Session, user: User) -> None:
    user.last_login = datetime.now(UTC)
    session.add(user)
    session.commit()


def authenticate(*, session: Session, email_name: str, password: str) -> User | None:
    db_user = get_user_by_email_name(session=session, email_name=email_name)
    if not db_user or not db_user.hashed_password:
        return None

    is_valid, _ = verify_password(password, db_user.hashed_password)
    if not is_valid:
        return None

    return db_user


def update_password(*, session: Session, user: User, new_password: str) -> User:
    user.hashed_password = get_password_hash(new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
