import pytest

from app.core.config import Settings


class TestSettings:
    def test_computed_database_uris(self):
        settings = Settings(
            POSTGRES_SERVER="localhost",
            POSTGRES_PORT=5432,
            POSTGRES_USER="test_user",
            POSTGRES_PASSWORD="test_password",
            POSTGRES_DB="test_db",
        )

        assert (
            str(settings.SQLALCHEMY_DATABASE_URI)
            == "postgresql+psycopg://test_user:test_password@localhost:5432/test_db"
        )
        assert (
            str(settings.ASYNC_SQLALCHEMY_DATABASE_URI)
            == "postgresql+asyncpg://test_user:test_password@localhost:5432/test_db"
        )

    def test_computed_rabbitmq_url_custom(self):
        settings = Settings(CUSTOM_RABBITMQ_URL="amqp://custom:5672/")
        assert settings.RABBITMQ_URL == "amqp://custom:5672/"

    def test_enforce_non_default_secrets_local_warning(self, caplog):
        settings = Settings(
            ENVIRONMENT="local",
            SECRET_KEY="changethis",
            POSTGRES_PASSWORD="changethis",  # gitleaks:allow
        )

        assert settings.SECRET_KEY == "changethis"
        assert "for security, please change it" in caplog.text

    def test_enforce_non_default_secrets_production_error(self):
        with pytest.raises(ValueError, match="for security, please change it"):
            Settings(ENVIRONMENT="production", SECRET_KEY="changethis")
