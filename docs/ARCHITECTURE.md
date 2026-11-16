# Architecture

## Strategy

PeaOps remains a modular monolith. Finance, Sales and Procurement are bounded domain areas sharing organization, party, item, warehouse, audit and numbering foundations. This avoids premature service distribution while retaining future extraction boundaries.

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
- `sales_rules.py`: selling prices, discounts, taxes, validity, delivery promises and credit exposure.
- `procurement_rules.py`: purchase pricing, sourcing dates, quote recommendation and receipt quantity controls.

Persistence models call these rule functions. API routes additionally enforce company ownership, supplier/customer type, item ownership, source-document status and lifecycle transitions.

## Integration boundaries

Procurement currently stops at quantity-controlled goods receipt. Stock-ledger movement, valuation, AP three-way match and GL posting remain explicit v0.5-v0.6 integration work rather than hidden side effects.
