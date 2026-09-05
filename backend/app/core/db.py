import time
from typing import Any

from sqlalchemy import event
from sqlmodel import Session, create_engine

from app.core.config import settings
from app.core.middlewares import query_stats

engine = create_engine(
    str(settings.database.SQLALCHEMY_DATABASE_URI),
    pool_size=15,
    max_overflow=25,
    pool_recycle=1800,
    pool_pre_ping=True,
)


@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(
    _conn: Any,
    _cursor: Any,
    _statement: str,
    _parameters: Any,
    context: Any,
    _executemany: bool,
) -> None:
    if context is not None:
        context.query_start_time = time.perf_counter()


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(
    _conn: Any,
    _cursor: Any,
    _statement: str,
    _parameters: Any,
    context: Any,
    _executemany: bool,
) -> None:
    stats = query_stats.get()
    if (
        stats is not None
        and context is not None
        and hasattr(context, "query_start_time")
    ):
        duration_ms = (time.perf_counter() - context.query_start_time) * 1000
        stats["count"] += 1
        stats["time_ms"] += duration_ms


def init_db(session: Session) -> None:
    pass
