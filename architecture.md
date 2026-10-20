# API Architecture & Schemas

This document specifies the request/response contracts for SalonERP endpoints. Updated as we build.

---

## Booking Module — Create Appointment

### Request: `POST /bookings`

```json
{
  "customer_id": "uuid",
  "staff_id": "uuid",
  "started_at": "2026-10-20T14:00:00Z",
  "items": [
    {"service_id": "uuid"},
    {"service_id": "uuid"}
  ]
}
```

**Fields:**
- `customer_id`: UUID of the customer (guest or account holder).
- `staff_id`: UUID of the staff member.
- `started_at`: ISO 8601 timestamp with a timezone. The appointment starts at this moment.
- `items`: Ordered list of `{service_id}` objects. List order determines `sequence` in `appointment_item`.

**Validation (request layer, Pydantic):**
- All fields required.
- `items` must be non-empty.
- `started_at` must include a timezone and must not be in the past (rough check; availability is a later feature).

**Not in the request (server-supplied):** `tenant_id`, `end_at`, `status`, and each item's `duration_minutes` and `sequence`.

---

### Response: `201 Created`

```json
{
  "id": "uuid",
  "tenant_id": "uuid",
  "customer_id": "uuid",
  "staff_id": "uuid",
  "started_at": "2026-10-20T14:00:00Z",
  "end_at": "2026-10-20T15:10:00Z",
  "status": "scheduled",
  "items": [
    {
      "id": "uuid",
      "service_id": "uuid",
      "duration_minutes": 30,
      "sequence": 0
    },
    {
      "id": "uuid",
      "service_id": "uuid",
      "duration_minutes": 15,
      "sequence": 1
    }
  ],
  "created_at": "2026-10-20T12:00:00Z"
}
```

**Fields:**
- `id`: UUID of the appointment.
- `started_at`: As provided in the request.
- `end_at`: **Computed** as: `started_at + sum(service durations) + last_service.buffer_minutes`.
- `status`: Always `"scheduled"` on creation.
- `items`: List of appointment_item rows, in sequence order.
- `created_at`: Server-generated timestamp.

---

### Error: `409 Conflict` (Slot Taken)

```json
{
  "detail": "Staff member is already booked during this time."
}
```

**Triggers when:**
- Insertion violates the exclusion constraint (the appointment's time range overlaps with an existing, non-cancelled appointment for the same staff member).

---

### Error: `422 Unprocessable Entity` (Validation)

**Examples:**
- `service_ids` is empty.
- `customer_id` or `staff_id` doesn't exist.
- Service doesn't exist, or doesn't belong to this tenant.
- `started_at` is in the past or malformed.

---

## Data Model Notes

### Appointment

```python
class Appointment(Base):
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    staff_id: UUID
    started_at: DateTime(tz)  # UTC
    end_at: DateTime(tz)      # UTC
    status: str               # "scheduled" (default), others set via separate endpoint
    created_at: DateTime(tz)  # server-generated
```

### AppointmentItem

```python
class AppointmentItem(Base):
    id: UUID
    tenant_id: UUID
    appointment_id: UUID
    service_id: UUID
    duration_minutes: int     # snapshot of service.duration_minutes at booking time
    sequence: int             # order within the appointment (0, 1, 2, ...)
```

### Service (relevant fields)

```python
class Service(Base):
    id: UUID
    name: str
    duration_minutes: int
    buffer_minutes: int       # "cooldown" after this service (added to end_at)
    price: Decimal
    staff_id: UUID (optional) # NULL = salon-wide; set = staff-specific price
```

---

## Flow: Create Appointment

1. **Receive request** → validate schema.
2. **Fetch services** → get `duration_minutes` and `buffer_minutes` for each service.
3. **Compute `end_at`** = `started_at + sum(durations) + buffer_of_last_service`.
4. **Lock (advisory)** → `pg_advisory_xact_lock(hash('booking:<tenant>:<staff>'))`.
5. **Insert** → `appointment` row + `appointment_item` rows (one per service).
6. **Catch IntegrityError** → exclusion constraint violation → return 409.
7. **Return 201** → appointment + items.

---

## Constraints & Guarantees

- **Exclusion constraint** (Postgres): no overlapping appointments for the same staff, same tenant (ignoring cancelled appointments).
- **Advisory lock** (application): serializes concurrent bookings for the same staff member; the lock commits with the transaction.
- **Exactly one winner** (proven by concurrency test): among N concurrent requests for the same staff/slot, exactly one succeeds.
- **Back-to-back allowed**: appointment A ending at 3:00 PM + appointment B starting at 3:00 PM both succeed (range is `[start, end)` — start-inclusive, end-exclusive).

---

## Open for Later

- Availability checking (hours + time_off − existing appointments).
- Service-to-staff resolution (salon-wide vs. staff-specific pricing).
- Multi-tenant isolation (RLS, milestone 2).
- Price snapshot on `appointment_item` (defer if not needed).
