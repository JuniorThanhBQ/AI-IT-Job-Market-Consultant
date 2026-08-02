import logging
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import (
    AnyUrl,
    BaseModel,
    BeforeValidator,
    EmailStr,
    HttpUrl,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from app.utils.utils_configs import FlatEnvSettingsSource


def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


def get_secret(name: str, default: str = "") -> str:
    for path in (
        Path(f"/run/secrets/{name.lower()}"),
        Path(f"/run/secrets/{name.upper()}"),
    ):
        if path.is_file():
            return path.read_text().strip()
    return default


class DatabaseSettings(BaseModel):
    POSTGRES_SERVER: str = "db"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "app"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        password = self.POSTGRES_PASSWORD or get_secret("postgres_password")
        user = self.POSTGRES_USER or get_secret("postgres_user", "postgres")
        db = self.POSTGRES_DB or get_secret("postgres_db", "app")
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=user,
            password=password,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=db,
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def ASYNC_SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        password = self.POSTGRES_PASSWORD or get_secret("postgres_password")
        user = self.POSTGRES_USER or get_secret("postgres_user", "postgres")
        db = self.POSTGRES_DB or get_secret("postgres_db", "app")
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=user,
            password=password,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=db,
        )


class RabbitMQSettings(BaseModel):
    RABBITMQ_SERVER: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    CUSTOM_RABBITMQ_URL: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def RABBITMQ_URL(self) -> str:
        if self.CUSTOM_RABBITMQ_URL:
            return self.CUSTOM_RABBITMQ_URL
        password = self.RABBITMQ_PASSWORD or get_secret("rabbitmq_password", "guest")
        user = self.RABBITMQ_USER or get_secret("rabbitmq_user", "guest")
        return f"amqp://{user}:{password}@{self.RABBITMQ_SERVER}:{self.RABBITMQ_PORT}//"


class RedisSettings(BaseModel):
    REDIS_SERVER: str = "redis"
    REDIS_PORT: int = 6379
    CUSTOM_REDIS_URL: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def REDIS_URL(self) -> str:
        if self.CUSTOM_REDIS_URL:
            return self.CUSTOM_REDIS_URL
        return f"redis://{self.REDIS_SERVER}:{self.REDIS_PORT}/0"


class CrawlerSettings(BaseModel):
    CRAWLER_MAX_CONCURRENCY: int = 1
    SITE_CRAWL_TIMEOUT_SECONDS: int = 300
    CRAWLER_MAX_REQUESTS_PER_CRAWL: int = 1500
    CRAWLER_MAX_REQUEST_RETRIES: int = 2
    CRAWLER_REQUEST_HANDLER_TIMEOUT_SECONDS: int = 120
    CRAWLER_MIN_DELAY_SECONDS: float = 2.5
    CRAWLER_MAX_DELAY_SECONDS: float = 5.0
    CRAWLER_BROWSER_TYPE: str = "chromium"
    CRAWLER_HEADLESS: bool = True


class SMTPSettings(BaseModel):
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    SMTP_PORT: int = 587
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def emails_enabled(self) -> bool:
        return bool(self.SMTP_HOST and self.EMAILS_FROM_EMAIL)


class BackupSettings(BaseModel):
    BACKUP_RESTORE_ADMIN_PASSWORD: str = ""
    RCLONE_REMOTE_PATH: str = "gdrive:backups"
    BACKUP_MAX_STACKS: int = 30


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_ignore_empty=True,
        extra="allow",
        secrets_dir="/run/secrets" if Path("/run/secrets").is_dir() else None,
    )
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    FRONTEND_HOST: str = "http://localhost:5173"
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    BACKEND_TRUSTED_HOSTS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def trusted_hosts_list(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_TRUSTED_HOSTS] + [
            self.FRONTEND_HOST
        ]

    PROJECT_NAME: str = "AI IT Job Market Consultant"
    SENTRY_DSN: HttpUrl | None = None
    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 50
    GEMINI_API_KEY: list[str] | str = []

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEST_USER: EmailStr = "test@example.com"
    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = ""

    database: DatabaseSettings = None  # type: ignore
    rabbitmq: RabbitMQSettings = None  # type: ignore
    redis: RedisSettings = None  # type: ignore
    crawler: CrawlerSettings = None  # type: ignore
    smtp: SMTPSettings = None  # type: ignore
    backup: BackupSettings = None  # type: ignore

    @model_validator(mode="before")
    @classmethod
    def _parse_nested_settings(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        def extract(keys: list[str]) -> dict[str, Any]:
            return {k: data[k] for k in keys if k in data}

        db_keys = [
            "POSTGRES_SERVER",
            "POSTGRES_PORT",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
        ]
        rabbitmq_keys = [
            "RABBITMQ_SERVER",
            "RABBITMQ_PORT",
            "RABBITMQ_USER",
            "RABBITMQ_PASSWORD",
            "CUSTOM_RABBITMQ_URL",
        ]
        redis_keys = ["REDIS_SERVER", "REDIS_PORT", "CUSTOM_REDIS_URL"]
        crawler_keys = [
            "CRAWLER_MAX_CONCURRENCY",
            "SITE_CRAWL_TIMEOUT_SECONDS",
            "CRAWLER_MAX_REQUESTS_PER_CRAWL",
            "CRAWLER_MAX_REQUEST_RETRIES",
            "CRAWLER_REQUEST_HANDLER_TIMEOUT_SECONDS",
            "CRAWLER_MIN_DELAY_SECONDS",
            "CRAWLER_MAX_DELAY_SECONDS",
            "CRAWLER_BROWSER_TYPE",
            "CRAWLER_HEADLESS",
        ]
        smtp_keys = [
            "SMTP_TLS",
            "SMTP_SSL",
            "SMTP_PORT",
            "SMTP_HOST",
            "SMTP_USER",
            "SMTP_PASSWORD",
            "EMAILS_FROM_EMAIL",
            "EMAILS_FROM_NAME",
        ]
        backup_keys = [
            "BACKUP_RESTORE_ADMIN_PASSWORD",
            "RCLONE_REMOTE_PATH",
            "BACKUP_MAX_STACKS",
        ]

        db_data = extract(db_keys)
        rmq_data = extract(rabbitmq_keys)
        red_data = extract(redis_keys)
        crw_data = extract(crawler_keys)
        smp_data = extract(smtp_keys)
        bkp_data = extract(backup_keys)

        if "database" not in data or not data["database"]:
            data["database"] = DatabaseSettings(**db_data)
        elif isinstance(data["database"], dict):
            data["database"] = DatabaseSettings(**{**db_data, **data["database"]})

        if "rabbitmq" not in data or not data["rabbitmq"]:
            data["rabbitmq"] = RabbitMQSettings(**rmq_data)
        elif isinstance(data["rabbitmq"], dict):
            data["rabbitmq"] = RabbitMQSettings(**{**rmq_data, **data["rabbitmq"]})

        if "redis" not in data or not data["redis"]:
            data["redis"] = RedisSettings(**red_data)
        elif isinstance(data["redis"], dict):
            data["redis"] = RedisSettings(**{**red_data, **data["redis"]})

        if "crawler" not in data or not data["crawler"]:
            data["crawler"] = CrawlerSettings(**crw_data)
        elif isinstance(data["crawler"], dict):
            data["crawler"] = CrawlerSettings(**{**crw_data, **data["crawler"]})

        if "smtp" not in data or not data["smtp"]:
            data["smtp"] = SMTPSettings(**smp_data)
        elif isinstance(data["smtp"], dict):
            data["smtp"] = SMTPSettings(**{**smp_data, **data["smtp"]})

        if "backup" not in data or not data["backup"]:
            data["backup"] = BackupSettings(**bkp_data)
        elif isinstance(data["backup"], dict):
            data["backup"] = BackupSettings(**{**bkp_data, **data["backup"]})

        return data

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                logging.warning(message)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        if not self.SECRET_KEY:
            self.SECRET_KEY = get_secret("secret_key")
        if not self.SECRET_KEY:
            raise ValueError(
                "SECRET_KEY is required and must be set via environment or secrets."
            )

        if not self.database.POSTGRES_PASSWORD:
            self.database.POSTGRES_PASSWORD = get_secret(
                "postgres_password", "changethis"
            )
        if not self.FIRST_SUPERUSER_PASSWORD:
            self.FIRST_SUPERUSER_PASSWORD = get_secret(
                "first_superuser_password", "changethis"
            )

        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.database.POSTGRES_PASSWORD)
        self._check_default_secret(
            "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
        )

        if not self.smtp.EMAILS_FROM_NAME:
            self.smtp.EMAILS_FROM_NAME = self.PROJECT_NAME

        return self

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            FlatEnvSettingsSource(settings_cls),
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
