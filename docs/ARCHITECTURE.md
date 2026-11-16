# Architecture

## Strategy

PeaOps remains a modular monolith. Finance and Sales are bounded domain areas sharing organization, party, item, audit and numbering foundations. This avoids premature service distribution while retaining extraction boundaries.

## Stack

- React + TypeScript UI
- FastAPI / Python API
- SQLAlchemy ORM
- PostgreSQL for multi-user deployments
- SQLite for local evaluation/development
- REST under `/api/v1`

## Rule isolation

Pure rule modules provide independently testable controls without requiring database access:

- `rules.py`: journals, invoice arithmetic, allocations, ageing and numbering.
- `sales_rules.py`: line pricing, discounts, taxes, quotation validity, delivery promises and credit exposure.

Persistence models call the same rule functions used by automated tests. API routes additionally enforce company ownership, party type, item ownership and lifecycle transitions.

## Integration boundaries

Sales-to-Finance integration currently stops at draft AR invoice creation. Inventory reservation, delivery, cost recognition, revenue posting and payment settlement remain explicit later milestones rather than hidden side effects.
