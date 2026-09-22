import contextvars
import json
import logging
import time
import uuid
from datetime import UTC, datetime

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

query_stats: contextvars.ContextVar[dict[str, float | int] | None] = (
    contextvars.ContextVar("query_stats", default=None)
)


class StructuredLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        stats: dict[str, float | int] = {"count": 0, "time_ms": 0.0}
        token = query_stats.set(stats)
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        finally:
            latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
            current_stats = query_stats.get() or {"count": 0, "time_ms": 0.0}
            query_stats.reset(token)

        log_data = {
            "timestamp": datetime.now(UTC).isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "query_count": int(current_stats["count"]),
            "query_time_ms": round(float(current_stats["time_ms"]), 2),
            "request_id": request_id,
        }

        if response.status_code >= 400:
            logger.error(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))

        response.headers["X-Request-ID"] = request_id
        return response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time
        stats = query_stats.get() or {"count": 0, "time_ms": 0.0}
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Query-Count"] = str(stats["count"])
        response.headers["X-Query-Time-Ms"] = f"{stats['time_ms']:.2f}"
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Strict-Transport-Security"] = (
            "max-age=63072000; includeSubDomains"
        )
        response.headers["Permissions-Policy"] = (
            "geolocation=(),midi=(),sync-xhr=(),microphone=(),camera=(),"
            "magnetometer=(),gyroscope=(),fullscreen=(self),payment=()"
        )
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        path = request.url.path

        is_admin_or_docs = path.startswith(("/docs", "/redoc", "/admin"))
        script_src = (
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.google.com https://www.gstatic.com https://z.clarity.ms https://*.clarity.ms https://*.googlesyndication.com; "
            if is_admin_or_docs
            else "script-src 'self' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://www.google.com https://www.gstatic.com https://z.clarity.ms https://*.clarity.ms https://*.googlesyndication.com; "
        )

        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            f"{script_src}"
            "base-uri 'self'; "
            "frame-ancestors 'none'; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com https://cdnjs.cloudflare.com; "
            "img-src 'self' data: https://res.cloudinary.com https://lh3.googleusercontent.com https://*.tiktokcdn-us.com https://fastapi.tiangolo.com; "
            "font-src 'self' data: https://fonts.gstatic.com; "
            "object-src 'none'; "
            "form-action 'self'; "
            "frame-src 'self' https://www.google.com https://www.gstatic.com; "
            "connect-src 'self' https://*.clarity.ms https://z.clarity.ms https://cdn.jsdelivr.net; "
            "upgrade-insecure-requests"
        )
        return response


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            logger.exception(f"Unhandled exception: {e}")
            return JSONResponse(
                status_code=500,
                content={"message": "An internal server error occurred."},
            )
