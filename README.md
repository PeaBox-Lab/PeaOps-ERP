# PeaOps v0.1.0

PeaOps is an India-first, globally-ready ERP foundation for SME/mid-market organizations. It uses one shared product core with Local Desktop, Local Server, and Cloud deployment branches.

## v0.1 scope
- Authentication foundation and RBAC model
- Companies, branches, fiscal periods, currencies, departments and cost centers
- Customers, suppliers, items, units, tax codes and warehouses
- Finance foundation: chart of accounts, journals, balanced journal entries, posting and trial balance
- Audit events
- React/TypeScript operator shell
- FastAPI REST API
- PostgreSQL canonical database; SQLite supported for developer/local evaluation
- Docker deployment skeletons for local/server/cloud

## Quick start (developer)
1. Copy `.env.example` to `.env`.
2. Install Python dependencies: `pip install -r backend/requirements.txt`
3. Run API: `cd backend && uvicorn app.main:app --reload`
4. API docs: `http://localhost:8000/docs`
5. Frontend: `cd frontend && npm install && npm run dev`

## Product principles
- Modular monolith first; service extraction only when scale justifies it.
- Posted accounting documents are immutable; correction is through reversal.
- Every financial journal must balance debit = credit.
- Tenant/company boundaries are represented from the beginning.
- India localization is an extension, not hard-coded into the global core.
- Configuration over source-code customization.

See `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/USER_GUIDE.md`, `docs/SECURITY.md`, and `CHANGELOG.md`.
