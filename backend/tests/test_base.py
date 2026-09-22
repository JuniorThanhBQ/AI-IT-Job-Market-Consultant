from app.main import app
from fastapi import FastAPI
from sqlmodel import Session


class TestBase:
    def test_app(self) -> None:
        assert app is not None
        assert isinstance(app, FastAPI)

    def test_session(self, db_session: Session) -> None:
        assert db_session is not None
        assert isinstance(db_session, Session)
