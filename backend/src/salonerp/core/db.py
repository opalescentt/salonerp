"""SQLAlchemy engine/session wiring.

This is plumbing: creating engines, opening/closing sessions per request.
It deliberately does NOT set the tenant context (`set_config('app.tenant_id',
...)`) — that mechanism is the first piece of core domain logic in the
"Multi-tenancy" milestone (see CLAUDE.md), not scaffolding. Until that lands,
every session here talks to Postgres with no tenant filter applied.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from salonerp.core.config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Shared declarative base. Every module's models.py inherits from this."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: one session per request, always closed after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
