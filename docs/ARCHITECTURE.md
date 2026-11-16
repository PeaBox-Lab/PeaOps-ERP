# Architecture

## Strategy
PeaOps starts as a modular monolith. Finance, Sales, Procurement, Inventory, Reporting, Workflow and Administration are bounded modules sharing a controlled platform layer. This lowers distributed-transaction and operations complexity while maintaining clear extraction boundaries.

## Canonical stack
- UI: React + TypeScript
- API: FastAPI / Python
- ORM: SQLAlchemy
- Database: PostgreSQL in multi-user/prod deployments
- Local evaluation/development: SQLite
- API style: REST `/api/v1`
- E2E target: Playwright
- Packaging: containers for server/cloud; desktop packaging is a later milestone

## Deployment branches
1. Local: single workstation, local service/database.
2. Server: LAN clients connect to a private on-prem PeaOps server backed by PostgreSQL.
3. Cloud: HTTPS gateway -> PeaOps application -> PostgreSQL + object storage; tenant isolation, observability, backup and MFA mature before SaaS GA.

## Core rules
- Tenant/company ID is explicit in business data.
- Posted accounting is immutable; corrections use reversals.
- Debits must equal credits before journal posting.
- Authorization is enforced server-side, never only in UI.
- Localization modules extend global tax/accounting primitives.
