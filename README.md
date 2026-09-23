# Salon ERP

## Context

## Options considered
1. Option A — pros / cons
2. Option B — pros / cons
3. Option C — pros / cons

## Decisions

## Consequences


## Backlog

- [ ] 0001 — PostgreSQL as the primary database 
- [ ] 0002 — Modular monolith with service-layer module boundaries
- [ ] 0003 — Shared schema + Row-Level Security for tenant isolation
- [ ] 0004 — Exclusion constraint for double-booking prevention
- [ ] 0005 — Transactional outbox for events
- [ ] 0006 — Redis as cache only, never source of truth for availability
- [ ] 0007 — Store timestamps in UTC; tenant timezone on tenant row
