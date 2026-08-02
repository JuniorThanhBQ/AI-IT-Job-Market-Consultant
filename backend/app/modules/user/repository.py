from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.modules.user.models import User, UserCreate, UserUpdate


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User(
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        username=user_create.username,
        is_superuser=user_create.is_superuser,
        is_active=user_create.is_active,
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> User:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        if password:
            hashed_password = get_password_hash(password)
            extra_data["hashed_password"] = hashed_password
        del user_data["password"]
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user or not db_user.hashed_password:
        return None
    is_valid, _ = verify_password(password, db_user.hashed_password)
    if not is_valid:
        return None
    return db_user
