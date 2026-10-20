"""Proves the `no_double_bookings` exclusion constraint (see
alembic/versions/0fd54b735936_..._no_double_booking_.py) actually rejects a
double-booking, not just that it exists.

TODO(dev): implement test_overlapping_appointment_for_same_staff_is_rejected.

Steps:
1. Use the factories (make_tenant, make_staff, make_customer) to set up one
   tenant, one staff member, and two customers.
2. Build and add() one Appointment for that staff member, e.g. 2:00-3:00 PM
   (use timezone-aware datetimes — see how `started_at`/`end_at` are typed
   in salonerp.modules.booking.models.Appointment). db.flush() it.
3. Build and add() a SECOND Appointment for the SAME staff member, with an
   overlapping time range (e.g. 2:30-3:30 PM), for the other customer.
4. Assert that flushing/committing the second one raises
   sqlalchemy.exc.IntegrityError. (This is what we saw psql itself raise
   when we tested this by hand: "conflicting key value violates exclusion
   constraint 'no_double_bookings'".)

A good second test to add once this one passes: two NON-overlapping
appointments for the same staff member should succeed with no error —
proving the constraint doesn't over-block valid bookings.
"""

import datetime as dt

import pytest
from sqlalchemy.exc import IntegrityError

from salonerp.modules.booking.models import Appointment

from .factories import make_customer, make_staff, make_tenant


def test_overlapping_appointment_for_same_staff_is_rejected(db_session):

    tenant = make_tenant(db_session)
    staff = make_staff(db_session, tenant_id=tenant.id)
    customer1 = make_customer(db_session, tenant_id=tenant.id, name="Test Customer 1")
    customer2 = make_customer(db_session, tenant_id=tenant.id, name="Test Customer 2")

    appointment1 = Appointment(
        tenant_id=tenant.id,
        customer_id=customer1.id,
        staff_id=staff.id,
        started_at=dt.datetime(2026, 3, 27, 14, 0, tzinfo=dt.UTC),
        end_at=dt.datetime(2026, 3, 27, 15, 0, tzinfo=dt.UTC),
        status="confirmed",
    )

    appointment2 = Appointment(
        tenant_id=tenant.id,
        customer_id=customer2.id,
        staff_id=staff.id,
        started_at=dt.datetime(2026, 3, 27, 14, 30, tzinfo=dt.UTC),
        end_at=dt.datetime(2026, 3, 27, 15, 0, tzinfo=dt.UTC),
        status="confirmed",
    )

    db_session.add(appointment1)
    db_session.flush()

    with pytest.raises(IntegrityError):
        db_session.add(appointment2)
        db_session.flush()


def test_back_to_back_appointment_for_same_staff_is_accepted(db_session):

    tenant = make_tenant(db_session)
    staff = make_staff(db_session, tenant_id=tenant.id)
    customer1 = make_customer(db_session, tenant_id=tenant.id, name="Test Customer 1")
    customer2 = make_customer(db_session, tenant_id=tenant.id, name="Test Customer 2")

    appointment1 = Appointment(
        tenant_id=tenant.id,
        customer_id=customer1.id,
        staff_id=staff.id,
        started_at=dt.datetime(2026, 3, 27, 14, 0, tzinfo=dt.UTC),
        end_at=dt.datetime(2026, 3, 27, 15, 0, tzinfo=dt.UTC),
        status="confirmed",
    )

    appointment2 = Appointment(
        tenant_id=tenant.id,
        customer_id=customer2.id,
        staff_id=staff.id,
        started_at=dt.datetime(2026, 3, 27, 15, 0, tzinfo=dt.UTC),
        end_at=dt.datetime(2026, 3, 27, 15, 30, tzinfo=dt.UTC),
        status="confirmed",
    )

    db_session.add(appointment1)
    db_session.flush()

    db_session.add(appointment2)
    db_session.flush()
