# ruff: noqa: E402
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.routing import APIRoute
from sqladmin import Admin
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.admin import JobAdmin, UserAdmin
from app.core.config import settings
from app.core.db import engine
from app.core.middlewares import (
    ExceptionHandlerMiddleware,
    ProcessTimeMiddleware,
    SecurityHeadersMiddleware,
    StructuredLoggingMiddleware,
)
from app.db import base as _db_base  # noqa: F401
from app.modules.routers import api_router


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

admin = Admin(app, engine)
admin.add_view(UserAdmin)
admin.add_view(JobAdmin)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(StructuredLoggingMiddleware)

app.add_middleware(ExceptionHandlerMiddleware)

if settings.trusted_hosts_list:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
else:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
