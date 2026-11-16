# PeaOps v0.7.0

PeaOps v0.7 adds financial and operational Insight plus a complete role-based documentation and user-story package to the cumulative ERP foundation.

## Product modules

- Foundation and administration
- Finance and accounting
- Sales / Quote-to-Cash
- Procurement / Procure-to-Pay
- Inventory and warehouse control
- Cross-module integration and posting
- Insight, statements, KPIs, saved reports, exports and data quality

## Complete documentation included

- Master user guide and role navigation.
- Guides for executives/customers, system admins, technical admins, implementers, Finance, Sales, Procurement, Inventory, managers/analysts, auditors, support, developers and general users.
- Module documentation for every cumulative module.
- User-story catalog with acceptance criteria.
- Requirements/test/release/role traceability matrix.
- Features, cumulative version history, architecture, security, roadmap and changelog.
- Implementation playbook, data-migration guide, UAT/cutover guide.
- Troubleshooting, FAQ, glossary and API workflow examples.

## Quick start

1. Copy `.env.example` to `.env`.
2. Install dependencies: `pip install -r backend/requirements.txt`.
3. Run API: `cd backend && uvicorn app.main:app --reload`.
4. Open `http://localhost:8000/docs`.
5. Run UI: `cd frontend && npm install && npm run dev`.
6. Run checks: `bash scripts/check.sh`.
7. Start documentation at `docs/USER_GUIDE.md`.

## Important limitations

v0.7.0 is an engineering release, not production GA. Frontend metrics are illustrative design content until connected to live API state. Reporting lacks comparative periods, consolidation, budgets/forecasts and formal cash-flow classification. Authentication, mature RBAC/SoD, migrations, production concurrency, observability, backups, DR, full E2E coverage and installer packaging remain roadmap work.
