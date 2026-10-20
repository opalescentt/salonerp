"""Small helpers for building test rows quickly, with sensible defaults, so
integration tests aren't full of repeated tenant/staff/customer setup.

Each function inserts one row via `db.flush()` — this sends the INSERT to
Postgres and populates generated fields (like the UUID `id`) WITHOUT
committing, so it still rolls back cleanly at the end of the test via the
db_session fixture.

Not a real factory library (factory_boy, etc.) — just plain functions.
That's a reasonable upgrade later if test setup gets more repetitive.
"""

import uuid
from typing import Any

from sqlalchemy.orm import Session

from salonerp.modules.customers.models import Customer
from salonerp.modules.staff.models import Staff
from salonerp.modules.tenant.models import Tenant


def make_tenant(db: Session, **overrides: Any) -> Tenant:
    defaults = {
        "name": "Test Salon",
        "slug": f"test-salon-{uuid.uuid4().hex[:8]}",  # unique per call
        "timezone": "Asia/Manila",
    }
    tenant = Tenant(**{**defaults, **overrides})
    db.add(tenant)
    db.flush()
    return tenant


def make_staff(db: Session, tenant_id: uuid.UUID, **overrides: Any) -> Staff:
    defaults = {
        "tenant_id": tenant_id,
        "first_name": "Jane",
        "last_name": "Doe",
        "is_active": True,
    }
    staff = Staff(**{**defaults, **overrides})
    db.add(staff)
    db.flush()
    return staff


def make_customer(db: Session, tenant_id: uuid.UUID, **overrides: Any) -> Customer:
    defaults = {
        "tenant_id": tenant_id,
        "name": "Test Customer",
    }
    customer = Customer(**{**defaults, **overrides})
    db.add(customer)
    db.flush()
    return customer
