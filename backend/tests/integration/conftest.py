"""Integration test fixtures — real Postgres, one transaction per test.

We never talk to the database directly in these tests without going through
this fixture. `db_session` opens one connection, starts one transaction, and
hands you a session bound to it. After the test finishes (pass or fail), the
transaction is rolled back and the connection closed — so tests can insert
whatever rows they like and never have to clean up after themselves, and
running the suite twice in a row never leaves duplicate data behind.

Note: this reuses the same database from your .env (not a separate test
database). That's fine for local, solo development. Before this runs in CI
or a team touches it, a dedicated test database (e.g. `salonerp_test`) would
be worth setting up, so tests can never collide with real dev data.
"""

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from salonerp.core.config import get_settings

# Importing each module's models registers their tables on Base.metadata.
# Needed here so SQLAlchemy can resolve foreign keys (e.g. appointment ->
# staff, staff -> tenant) when the factories in factories.py build objects.
from salonerp.modules.booking import models as booking_models  # noqa: F401
from salonerp.modules.catalog import models as catalog_models  # noqa: F401
from salonerp.modules.customers import models as customers_models  # noqa: F401
from salonerp.modules.staff import models as staff_models  # noqa: F401
from salonerp.modules.tenant import models as tenant_models  # noqa: F401


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(get_settings().database_url)
    connection = engine.connect()
    transaction = connection.begin()
    # "create_savepoint" wraps each unit of work (e.g. each flush()) in its
    # own SAVEPOINT, instead of using our outer `transaction` directly. That
    # means a test that triggers an expected DB error (e.g. asserting an
    # IntegrityError with pytest.raises) only unwinds that inner savepoint —
    # our outer `transaction` stays alive and intact for teardown below.
    # Without this, SQLAlchemy's own error handling can end the outer
    # transaction early, making `transaction.rollback()` below a no-op with
    # a "transaction already deassociated from connection" warning.
    session = sessionmaker(bind=connection, join_transaction_mode="create_savepoint")()

    yield session

    session.close()
    transaction.rollback()  # undoes everything the test inserted
    connection.close()
