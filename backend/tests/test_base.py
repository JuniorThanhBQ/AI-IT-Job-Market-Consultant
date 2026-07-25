from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import Session

from app.main import app


class TestBase:
    def test_app(self) -> None:
        assert app is not None
        assert isinstance(app, FastAPI)

    def test_session(self, db_session: Session) -> None:
        assert db_session is not None
        assert isinstance(db_session, Session)

    def test_client(self, client: TestClient) -> None:
        assert client is not None
        assert isinstance(client, TestClient)
