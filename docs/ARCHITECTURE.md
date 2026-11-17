
# Architecture - v0.8

PeaOps is a modular monolith with bounded Finance, Sales, Procurement, Inventory, Integration, Insight and Security/Operations areas.

## Production server topology

TLS reverse proxy → React static web and FastAPI API → PostgreSQL. A one-shot migration job upgrades schema before API startup. Services run on a private container network; only proxy ports are exposed.

## Security architecture

Users belong to a company. Roles contain permission strings; users receive roles. Passwords use PBKDF2-SHA256 with per-password salt. Access tokens are HMAC signed, short lived and contain company/permission claims. Protected administration endpoints enforce permission and company scope. Security events capture authentication and administration outcomes.

## Data and transaction architecture

SQLAlchemy models persist business records. Alembic owns production schema evolution. Pure rule modules hold deterministic invariants. Integrated posting operations use database transactions, idempotency events and document links.

## Operational architecture

Liveness verifies process availability; readiness verifies database access. Reverse proxy applies TLS/HSTS. Backups use PostgreSQL custom format and SHA-256. CI runs tests, frontend build and migration smoke test.

## Pre-GA gaps

Complete authorization coverage, MFA/SSO, token revocation/rotation, SoD policy engine, concurrency controls, load/E2E testing, centralized observability, automated recovery and signed/SBOM releases.
