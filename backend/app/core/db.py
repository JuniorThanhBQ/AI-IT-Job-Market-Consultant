from sqlmodel import Session, create_engine

from app.core.config import settings

engine = create_engine(
    str(settings.database.SQLALCHEMY_DATABASE_URI),
    pool_size=15,
    max_overflow=25,
    pool_recycle=1800,
    pool_pre_ping=True,
)


def init_db(session: Session) -> None:
    pass
