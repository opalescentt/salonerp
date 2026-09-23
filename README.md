# SalonERP

Multi-tenant B2B SaaS ERP for salons, built as a portfolio + learning project.

This README documents the project for anyone (including future me) picking it up: what it does, the architecture, the tradeoffs made along the way, and results from load testing. It's kept up to date as the project progresses — see `CLAUDE.md` for the day-to-day working context and full decision list.

## Status

Early setup — no application code yet. See `CLAUDE.md` for current milestone and build order.

## Architecture (summary)

- **Backend:** FastAPI + Pydantic v2 + SQLAlchemy 2.0 + Alembic, PostgreSQL.
- **Multi-tenancy:** shared schema, Row-Level Security.
- **No double-booking:** Postgres exclusion constraint (`btree_gist`) on stylist/time-range overlap.
- **Modular monolith:** one package per module (booking, staff, catalog, ...), communicating only via service layers.
- **Events:** transactional outbox → Redis Streams/Kafka.
- **Frontend:** Next.js + TypeScript, thin client generated from the OpenAPI spec.

## Tradeoffs

_To be filled in as decisions are made — RLS vs schema-per-tenant, outbox vs dual-write, modular monolith vs microservices, exclusion constraint vs slot table/locking, what changes at 100x scale._

## Load testing

_To be filled in once k6 load tests are run (see build order step 3 in `CLAUDE.md`)._
