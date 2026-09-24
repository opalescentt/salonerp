"""Application settings, loaded from environment variables / .env.

pydantic-settings gives us validation for free: if DATABASE_URL is missing
or malformed, the app fails fast at startup instead of at the first query.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    env: str = "local"

    # Postgres. The app connects as a non-owner, non-superuser role (see
    # CLAUDE.md — "Multi-tenancy") because owners/superusers bypass Row-Level
    # Security. That role gets created in the first migration, not here.
    database_url: str = "postgresql+psycopg://salonerp_app:changeme@localhost:5432/salonerp"

    redis_url: str = "redis://localhost:6379/0"

    jwt_secret: str = "changeme-dev-only"
    jwt_algorithm: str = "HS256"


@lru_cache
def get_settings() -> Settings:
    """Cached so Settings() — which reads the environment — only runs once."""
    return Settings()
