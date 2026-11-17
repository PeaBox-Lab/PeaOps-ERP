
# Technical Administrator and DevOps Guide

## Runtime

Backend: FastAPI/Python. Frontend: React/TypeScript. Canonical multi-user database: PostgreSQL. SQLite is for local evaluation/development.

## Configuration

Use environment variables prefixed `PEAOPS_`. Replace development secrets. Run the API and frontend separately during development. The server deployment file supplies a PostgreSQL and API baseline.

## Operational responsibilities

- Manage secrets, TLS, database availability and storage.
- Establish backups and restore testing before production.
- Replace metadata `create_all` with migrations before controlled upgrades.
- Monitor API, database, integration events and resource usage.
- Run syntax and automated tests before release promotion.
- Preserve logs without exposing credentials or sensitive business data.

## Known production gaps

Authentication, mature RBAC, MFA, migrations, concurrency hardening, rate limiting, observability, backup/restore automation and disaster recovery are roadmap work.
