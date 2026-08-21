from sqlmodel import Session
from celery_app import app


class TestBase:
    def test_app(self) -> None:
        assert app is not None
        assert type(app).__name__ == "Celery"

    def test_session(self, db_session: Session) -> None:
        assert db_session is not None
        assert isinstance(db_session, Session)

    def test_tasks_registered(self) -> None:
        expected_tasks = {
            "celery_app.run_crawler_task",
            "celery_app.run_crawl4ai_task",
            "celery_app.run_jobs_update_task",
            "celery_app.run_database_backup_task",
        }
        for task_name in expected_tasks:
            assert task_name in app.tasks
