# Architecture

## Strategy

PeaOps is a modular monolith. Finance, Sales, Procurement, Inventory, Reporting, Workflow and Administration remain bounded modules sharing a controlled platform layer. This minimizes distributed-transaction risk while retaining future extraction boundaries.

## Stack

- React + TypeScript UI
- FastAPI / Python API
- SQLAlchemy ORM
- PostgreSQL for multi-user deployments
- SQLite for local evaluation/development
- REST under `/api/v1`

## Finance design

v0.2 separates pure accounting/finance rules from SQLAlchemy persistence. Journal balance, invoice arithmetic, allocation limits, ageing and numbering can be validated without a database. API routes enforce company, party and document-direction constraints before mutation.

## Core rules

- Company ID is explicit in business data.
- Posted accounting is immutable; corrections will use reversals.
- Debits equal credits before journal posting.
- Invoice totals are derived from line values.
- Allocations cannot exceed outstanding or unallocated balances.
- Authorization will be server-side when authentication/RBAC is introduced.
