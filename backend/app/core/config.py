import logging
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, Literal, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    EmailStr,
    PostgresDsn,
    computed_field,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from app.utils.utils_configs import (
    FlatEnvSettingsSource,
    get_secret,
    parse_cors,
    parse_trusted_host,
)


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
    SITE_CRAWL_TIMEOUT_SECONDS: int = 6600
    CRAWLER_MAX_REQUESTS_PER_CRAWL: int = 1500
    CRAWLER_MAX_REQUEST_RETRIES: int = 2
    CRAWLER_REQUEST_HANDLER_TIMEOUT_SECONDS: int = 120
    CRAWLER_UPDATE_BATCH_SIZE: int = 50
    CRAWLER_UPDATE_MIN_DELAY_SECONDS: float = 0.5
    CRAWLER_UPDATE_MAX_DELAY_SECONDS: float = 1.5
    CRAWLER_MIN_DELAY_SECONDS: float = 2.5
    CRAWLER_MAX_DELAY_SECONDS: float = 5.0
    CRAWLER_BROWSER_TYPE: str = "chromium"
    CRAWLER_HEADLESS: bool = True
    ITVIEC_LINK: str = "https://itviec.com/it-jobs"
    TOPDEV_LINK: str = "https://topdev.vn/jobs/search?job_categories_ids=2%2C3%2C4%2C5%2C6%2C7%2C8%2C9%2C10%2C11%2C12%2C13%2C67"
    ITJOBS_LINK: str = (
        "https://www.itjobs.com.vn/vi/search?Text=&FunctionalLevelKey=&CityId="
    )
    VIETNAMWORKS_LINK: str = "https://www.vietnamworks.com/viec-lam?q=it&g=5&j=35.28.27.31.25.29.36.34.30.33.26.32.38&sorting=lasted"


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


NESTED_SETTINGS_MAP: dict[str, tuple[type[BaseModel], list[str]]] = {
    "database": (
        DatabaseSettings,
        [
            "POSTGRES_SERVER",
            "POSTGRES_PORT",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "POSTGRES_DB",
        ],
    ),
    "rabbitmq": (
        RabbitMQSettings,
        [
            "RABBITMQ_SERVER",
            "RABBITMQ_PORT",
            "RABBITMQ_USER",
            "RABBITMQ_PASSWORD",
            "CUSTOM_RABBITMQ_URL",
        ],
    ),
    "redis": (
        RedisSettings,
        ["REDIS_SERVER", "REDIS_PORT", "CUSTOM_REDIS_URL"],
    ),
    "crawler": (
        CrawlerSettings,
        [
            "CRAWLER_MAX_CONCURRENCY",
            "SITE_CRAWL_TIMEOUT_SECONDS",
            "CRAWLER_MAX_REQUESTS_PER_CRAWL",
            "CRAWLER_MAX_REQUEST_RETRIES",
            "CRAWLER_REQUEST_HANDLER_TIMEOUT_SECONDS",
            "CRAWLER_UPDATE_BATCH_SIZE",
            "CRAWLER_UPDATE_MIN_DELAY_SECONDS",
            "CRAWLER_UPDATE_MAX_DELAY_SECONDS",
            "CRAWLER_MIN_DELAY_SECONDS",
            "CRAWLER_MAX_DELAY_SECONDS",
            "CRAWLER_BROWSER_TYPE",
            "CRAWLER_HEADLESS",
            "ITVIEC_LINK",
            "TOPDEV_LINK",
            "ITJOBS_LINK",
            "VIETNAMWORKS_LINK",
        ],
    ),
    "smtp": (
        SMTPSettings,
        [
            "SMTP_TLS",
            "SMTP_SSL",
            "SMTP_PORT",
            "SMTP_HOST",
            "SMTP_USER",
            "SMTP_PASSWORD",
            "EMAILS_FROM_EMAIL",
            "EMAILS_FROM_NAME",
        ],
    ),
    "backup": (
        BackupSettings,
        [
            "BACKUP_RESTORE_ADMIN_PASSWORD",
            "RCLONE_REMOTE_PATH",
            "BACKUP_MAX_STACKS",
        ],
    ),
}


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
    ENVIRONMENT: Literal["local", "development", "staging", "production"] = "local"
    BACKEND_CORS_ORIGINS: Annotated[list[str], BeforeValidator(parse_cors)] = []
    BACKEND_TRUSTED_HOSTS: Annotated[list[str], BeforeValidator(parse_cors)] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
            self.FRONTEND_HOST
        ]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def trusted_hosts_list(self) -> list[str]:
        hosts = [parse_trusted_host(h) for h in self.BACKEND_TRUSTED_HOSTS]
        if self.FRONTEND_HOST:
            hosts.append(parse_trusted_host(self.FRONTEND_HOST))
        return list(dict.fromkeys(filter(None, hosts)))

    PROJECT_NAME: str = "AI IT Job Market Consultant"
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

    @staticmethod
    def build_nested_model(
        data: dict[str, Any],
        setting_cls: type[BaseModel],
        keys: list[str],
        existing: Any,
    ) -> BaseModel:
        extracted = {k: data[k] for k in keys if k in data}
        if isinstance(existing, dict):
            return setting_cls(**{**extracted, **existing})
        if existing:
            return existing
        return setting_cls(**extracted)

    @model_validator(mode="before")
    @classmethod
    def parse_nested_settings(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        for key, (setting_cls, keys) in NESTED_SETTINGS_MAP.items():
            data[key] = cls.build_nested_model(data, setting_cls, keys, data.get(key))

        return data

    def check_default_secret(self, var_name: str, value: str | None) -> None:
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
    def enforce_non_default_secrets(self) -> Self:
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

        self.check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self.check_default_secret("POSTGRES_PASSWORD", self.database.POSTGRES_PASSWORD)
        self.check_default_secret(
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
