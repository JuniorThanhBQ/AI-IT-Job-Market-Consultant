from datetime import UTC, datetime

from sqlmodel import Field, Session, SQLModel
from test_base import TestBase

from app.db.base_model import BaseModel


class ConcreteDummyModel(BaseModel, table=True):
    __tablename__ = "concrete_dummy_models"
    name: str = Field(index=True)


class TestBaseModelDB(TestBase):
    def test_base_model_timestamp_generation(self, db_session: Session):
        SQLModel.metadata.create_all(db_session.bind)

        dummy = ConcreteDummyModel(name="test_record")

        db_session.add(dummy)
        db_session.commit()
        db_session.refresh(dummy)

        assert dummy.id is not None
        assert isinstance(dummy.created_date, datetime)
        assert isinstance(dummy.updated_date, datetime)

        is_sqlite = db_session.bind.dialect.name == "sqlite"
        if not is_sqlite:
            assert dummy.created_date.tzinfo is not None
            assert dummy.updated_date.tzinfo is not None

        now = datetime.now(UTC)
        created_date = dummy.created_date
        if is_sqlite and created_date.tzinfo is None:
            now_naive = now.replace(tzinfo=None)
            assert abs((now_naive - created_date).total_seconds()) < 5
        else:
            assert abs((now - created_date).total_seconds()) < 5
