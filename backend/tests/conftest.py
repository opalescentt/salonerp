"""Shared pytest fixtures.

Only app-level fixtures for now. DB fixtures (a real Postgres test database,
transaction-per-test rollback, factories) land with the booking-core work,
since that's the first place tests actually touch the database — see
CLAUDE.md's "Who writes what": DB test fixtures/factories are Claude's
plumbing, but they're scaffolded when there's a real schema to test against,
not before.
"""

import pytest
from fastapi.testclient import TestClient

from salonerp.main import create_app


@pytest.fixture
def client() -> TestClient:
    return TestClient(create_app())
