"""Concurrency test fixtures — see test_concurrent_booking.py's docstring,
and the guidance discussed in chat, for what this needs to do and why.

TODO(dev): build committed_tenant_staff_customer here.
"""

import uuid

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from salonerp.core.config import get_settings
from salonerp.modules.customers.models import Customer
from salonerp.modules.staff.models import Staff
from salonerp.modules.tenant.models import Tenant

# lock_timeout is a backstop: any lock wait over 5s becomes a retryable error
# (SQLSTATE 55P03) instead of waiting forever. (Unlike deadlock_timeout, it does
# not need superuser rights.)
concurrency_engine = create_engine(
    get_settings().database_url,
    pool_size=40,
    max_overflow=0,
    connect_args={"options": "-c lock_timeout=5000"},
)
ConcurrencySessionLocal = sessionmaker(bind=concurrency_engine)


@pytest.fixture
def committed_tenant_staff_customer():

    session = ConcurrencySessionLocal()
    # Unique per run: a run killed before teardown leaves its tenant behind, and
    # a fixed slug would make every later run fail on the unique constraint.
    tenant = Tenant(
        name="Test Tenant",
        slug=f"concurrency-test-{uuid.uuid4().hex[:8]}",
        timezone="UTC",
    )
    session.add(tenant)
    session.flush()

    staff = Staff(
        tenant_id=tenant.id,
        first_name="Test",
        last_name="Staff",
    )

    customer = Customer(tenant_id=tenant.id, name="Test Customer")

    session.add(staff)
    session.add(customer)
    session.commit()

    yield tenant, staff, customer

    session.close()

    cleanup = ConcurrencySessionLocal()
    cleanup.execute(text("DELETE FROM appointment WHERE tenant_id = :tid"), {"tid": tenant.id})
    cleanup.execute(text("DELETE FROM customer WHERE tenant_id = :tid"), {"tid": tenant.id})
    cleanup.execute(text("DELETE FROM staff WHERE tenant_id = :tid"), {"tid": tenant.id})
    cleanup.execute(text("DELETE FROM tenant WHERE id = :tid"), {"tid": tenant.id})
    cleanup.commit()
    cleanup.close()
