"""Proves the `no_double_bookings` exclusion constraint holds under REAL
concurrent load — not just sequential inserts one after another (see
tests/integration/test_no_double_booking.py for that, sequential version).

This fires many simultaneous attempts to book the exact same staff member
for the exact same time slot, from separate threads (each with its own
database connection), and asserts exactly one of them succeeds.

TODO(dev): implement test_only_one_concurrent_booking_succeeds.

Steps:
1. Use the `committed_tenant_staff_customer` fixture (see conftest.py) to
   get a REAL, committed tenant/staff/customer every thread can see.

2. Write a helper function, e.g. `attempt_booking(tenant_id, staff_id,
   customer_id) -> bool`:
   - Opens its OWN new session: `session = SessionLocal()` (import from
     `salonerp.core.db`). Do NOT share one session across threads — each
     attempt needs its own independent connection to genuinely race the
     others, same reasoning as why the fixture itself uses SessionLocal().
   - Builds one Appointment for the given tenant/staff/customer, using the
     SAME start/end time on every call (e.g. always 2:00-3:00 PM) — they
     all have to collide on purpose for this to test anything.
   - Tries `session.add(appt)` then `session.commit()` (real commit, not
     flush — you want Postgres's final word, not just a mid-transaction
     check).
   - Catches `IntegrityError` if it's raised: return False.
   - If commit succeeds with no error: return True.
   - Always `session.close()` when done, whichever branch you took (a
     `try`/`finally`, or `try`/`except`/`else` block, is a good fit here).

3. Use `concurrent.futures.ThreadPoolExecutor` to run `attempt_booking(...)`
   many times (try 30) at once, rather than one after another. Shape:

       from concurrent.futures import ThreadPoolExecutor

       with ThreadPoolExecutor(max_workers=30) as executor:
           futures = [executor.submit(attempt_booking, ...) for _ in range(30)]
           results = [f.result() for f in futures]

   `executor.submit(fn, *args)` schedules `fn(*args)` to run on a thread
   and immediately returns a `Future` (a placeholder for "the result, once
   it's done"). `.result()` blocks until that particular one finishes and
   gives you its return value. Building the whole `futures` list first,
   THEN calling `.result()` on each, is what makes them actually run
   concurrently — if you called `.submit(...).result()` one at a time in
   one line, you'd be back to sequential, one full attempt finishing
   before the next even starts.

4. Assert `results.count(True) == 1` and `results.count(False) == len(results) - 1`
   — exactly one booking won the race, every other attempt was correctly
   rejected by the exclusion constraint, even though they were all firing
   at the database at the same time.

A good second test to add once this passes: run the same thing but with
attempts for DIFFERENT, non-overlapping time slots (or different staff
members) — should all succeed, proving concurrency alone isn't what's
being rejected, only genuine conflicts are.
"""

import datetime as dt
import random
import time
from concurrent.futures import ThreadPoolExecutor

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, OperationalError

from salonerp.modules.booking.models import Appointment

from .conftest import ConcurrencySessionLocal

# Postgres error codes (SQLSTATE) worth retrying: the insert never got a verdict,
# so trying again is safe. Checked by code rather than message text.
#   40P01 = deadlock_detected, 55P03 = lock_not_available (our lock_timeout fired)
RETRYABLE_SQLSTATES = {"40P01", "55P03"}

MAX_ATTEMPTS = 10

# Booking procedure: take a per-staff advisory lock BEFORE inserting. Bookings for
# the same staff member then queue up one at a time instead of all racing through the
# exclusion-constraint check at once (which made them deadlock in long chains: tuning
# deadlock_timeout / retries / jitter only lowered the failure rate, never removed it).
# The first one commits; each later one gets a clean exclusion-constraint rejection.
# The constraint is still the safety net that guarantees correctness; the lock is the
# traffic control. pg_advisory_xact_lock releases itself at commit/rollback.
ACQUIRE_STAFF_LOCK = text("SELECT pg_advisory_xact_lock(hashtextextended(:key, 0))")


def attempt_booking(tenant_id, staff_id, customer_id):

    session = ConcurrencySessionLocal()

    for attempt in range(MAX_ATTEMPTS):
        try:
            session.execute(ACQUIRE_STAFF_LOCK, {"key": f"booking:{tenant_id}:{staff_id}"})

            appointment = Appointment(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=staff_id,
                started_at=dt.datetime(2026, 3, 27, 15, 0, tzinfo=dt.UTC),
                end_at=dt.datetime(2026, 3, 27, 15, 30, tzinfo=dt.UTC),
                status="confirmed",
            )

            session.add(appointment)
            session.commit()
            return True

        except IntegrityError:
            return False

        except OperationalError as e:
            if (
                getattr(e.orig, "sqlstate", None) in RETRYABLE_SQLSTATES
                and attempt < MAX_ATTEMPTS - 1
            ):
                time.sleep(random.uniform(0, min(0.01 * 2**attempt, 0.2)))
                continue
            raise

        finally:
            session.close()


@pytest.mark.repeat(10)
def test_only_one_concurrent_booking_succeeds(committed_tenant_staff_customer):

    tenant, staff, customer = committed_tenant_staff_customer

    with ThreadPoolExecutor(max_workers=30) as executor:
        futures = [
            executor.submit(attempt_booking, tenant.id, staff.id, customer.id) for _ in range(30)
        ]
        results = [f.result() for f in futures]

        assert results.count(True) == 1
