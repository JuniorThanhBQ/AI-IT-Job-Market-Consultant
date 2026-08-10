from datetime import UTC, datetime

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.modules.consultee_profile.models import ConsulteeProfile, CurriculumVitae
from app.modules.user.models import User


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(
    *,
    session: Session,
    email: str,
    password: str,
    username: str | None = None,
) -> User:
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        username=username,
        is_superuser=False,
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


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user or not db_user.hashed_password:
        return None
    is_valid, _ = verify_password(password, db_user.hashed_password)
    if not is_valid:
        return None
    return db_user
