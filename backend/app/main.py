import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRoute
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request

from app.admin import init_admin
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
from app.modules.shared.bm25 import BM25Index

logging.basicConfig(level=logging.INFO)
logging.getLogger("app").setLevel(logging.INFO)


def custom_generate_unique_id(route: APIRoute) -> str:
    tag = route.tags[0] if route.tags else "default"
    return f"{tag}-{route.name}"


docs_url = None if settings.ENVIRONMENT == "production" else "/docs"
redoc_url = None if settings.ENVIRONMENT == "production" else "/redoc"
openapi_url = (
    None
    if settings.ENVIRONMENT == "production"
    else f"{settings.API_V2_STR}/openapi.json"
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    with Session(engine) as session:
        BM25Index.build(session)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0",
    debug=settings.ENVIRONMENT != "production",
    openapi_url=openapi_url,
    docs_url=docs_url,
    redoc_url=redoc_url,
    generate_unique_id_function=custom_generate_unique_id,
    lifespan=lifespan,
)

init_admin(app)

app_dir = Path(__file__).resolve().parent
static_dir = app_dir / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")
templates_dir = app_dir / "templates"
templates = Jinja2Templates(directory=templates_dir)

if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if settings.trusted_hosts_list:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts_list)
else:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost"])

app.add_middleware(StructuredLoggingMiddleware)
app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

app.include_router(api_router, prefix=settings.API_V2_STR)


@app.get("/health", include_in_schema=False)
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def home_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"frontend_host": settings.FRONTEND_HOST},
    )


@app.get("/favicon.ico", include_in_schema=False)
def favicon() -> RedirectResponse:
    return RedirectResponse(
        url="https://res.cloudinary.com/dfolk8pz2/image/upload/v1786037265/AIJ-removebg-preview_xk5pz1.png"
    )
