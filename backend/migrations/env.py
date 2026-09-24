"""Alembic environment.

Reads the DB URL from our own Settings (not alembic.ini) so there's one
source of truth for connection config, matching core/db.py.

migrations/versions/ is where the hand-written RLS policies and the
exclusion constraint go (see CLAUDE.md — autogenerate won't produce either).
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from salonerp.core.config import get_settings
from salonerp.core.db import Base

# Import each module's models here so Base.metadata knows about their tables
# and `alembic revision --autogenerate` can diff against them, e.g.:
#   from salonerp.modules.booking import models as booking_models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", get_settings().database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
