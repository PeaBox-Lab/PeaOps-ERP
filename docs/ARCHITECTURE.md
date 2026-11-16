# Architecture

## Strategy

PeaOps remains a modular monolith. Finance, Sales, Procurement and Inventory are bounded domain areas sharing organization, party, item, warehouse, audit and numbering foundations.

## Stack

- React + TypeScript UI
- FastAPI / Python API
- SQLAlchemy ORM
- PostgreSQL for multi-user deployments
- SQLite for local evaluation/development
- REST under `/api/v1`

## Rule isolation

- `rules.py`: journals, invoices, allocations, ageing and numbering.
- `sales_rules.py`: selling prices, validity, promises and credit exposure.
- `procurement_rules.py`: purchase pricing, sourcing dates, quote comparison and receipt quantities.
- `inventory_rules.py`: signed movements, negative-stock control, weighted-average valuation, transfers, tracking and reorder logic.

## Inventory consistency

Inventory movements are append-only business records. Balance updates and movement creation occur in one database transaction. Transfers validate every line before applying source and destination changes. Production hardening still requires row locking, idempotency keys, migrations and concurrency tests.

## Integration boundaries

v0.5 exposes inventory operations but does not yet make Procurement receipts or Sales delivery automatically post stock. v0.6 will connect those document lifecycles to inventory and accounting.
