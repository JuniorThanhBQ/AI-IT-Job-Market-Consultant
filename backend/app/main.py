# ruff: noqa: E402
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))

if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import sentry_sdk
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request

from app.admin import init_admin
from app.core.config import settings
from app.core.middlewares import (
    ExceptionHandlerMiddleware,
    ProcessTimeMiddleware,
    SecurityHeadersMiddleware,
    StructuredLoggingMiddleware,
)
from app.core.security import authenticate_admin
from app.db import base as _db_base  # noqa: F401
from app.modules.routers import api_router
from app.modules.user.models import User


def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

docs_url = None if settings.ENVIRONMENT == "production" else "/docs"
redoc_url = None if settings.ENVIRONMENT == "production" else "/redoc"
openapi_url = (
    None
    if settings.ENVIRONMENT == "production"
    else f"{settings.API_V1_STR}/openapi.json"
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=openapi_url,
    docs_url=docs_url,
    redoc_url=redoc_url,
    generate_unique_id_function=custom_generate_unique_id,
)

init_admin(app)

static_dir = os.path.join(current_dir, "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

templates_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)


if settings.ENVIRONMENT == "production":

    @app.get(f"{settings.API_V1_STR}/openapi.json", include_in_schema=False)
    def get_open_api_endpoint(_: User = Depends(authenticate_admin)):
        return get_openapi(title=app.title, version=app.version, routes=app.routes)

    @app.get("/docs", include_in_schema=False)
    def get_swagger_documentation(_: User = Depends(authenticate_admin)):
        return get_swagger_ui_html(
            openapi_url=f"{settings.API_V1_STR}/openapi.json",
            title=f"{app.title} - Swagger UI",
        )

    @app.get("/redoc", include_in_schema=False)
    def get_redoc_documentation(_: User = Depends(authenticate_admin)):
        return get_redoc_html(
            openapi_url=f"{settings.API_V1_STR}/openapi.json",
            title=f"{app.title} - ReDoc",
        )


@app.get("/", response_class=HTMLResponse, tags=["home"])
def home_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"frontend_host": settings.FRONTEND_HOST},
    )


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
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "http://localhost:3000", "http://localhost:8000"],
    )

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

if settings.ENVIRONMENT != "production":
    from typing import Any, cast

    from debug_toolbar.middleware import DebugToolbarMiddleware

    app.add_middleware(cast(Any, DebugToolbarMiddleware))

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}
