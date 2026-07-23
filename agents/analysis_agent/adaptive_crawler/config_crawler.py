import os
from app.core.config import settings

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_uri = str(settings.SQLALCHEMY_DATABASE_URI)
    if "postgresql+psycopg" in db_uri:
        DATABASE_URL = db_uri.replace("postgresql+psycopg", "postgresql+asyncpg")
    else:
        DATABASE_URL = db_uri.replace("postgresql://", "postgresql+asyncpg://")

MAX_REQUESTS_PER_CRAWL = 300
MAX_REQUEST_RETRIES = 2
MAX_CONCURRENCY = int(os.getenv("CRAWLER_MAX_CONCURRENCY", 1))
REQUEST_HANDLER_TIMEOUT_SECONDS = 120
MIN_DELAY_SECONDS = 2.5
MAX_DELAY_SECONDS = 5.0

BROWSER_TYPE = "chromium"
HEADLESS = True
