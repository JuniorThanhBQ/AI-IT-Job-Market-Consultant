from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.core.deps import get_db
from app.main import app


@pytest.fixture(name="db_session")
def fixture_db_session() -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    engine.dispose()


@pytest.fixture(name="client")
def fixture_client(db_session: Session) -> Generator[TestClient]:
    def get_db_override() -> Generator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = get_db_override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
