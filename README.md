# PeaOps v0.2.0

PeaOps is an India-first, globally-ready ERP foundation for SME and mid-market organizations. It retains one modular core across Local Desktop, Local Server and Cloud deployment paths.

## v0.2 Finance scope

- Existing general-ledger foundation: chart of accounts, balanced journals, posting and trial balance.
- Customer and supplier masters with GSTIN-ready fields and customer credit-limit foundation.
- Accounts Receivable and Accounts Payable invoice models and REST endpoints.
- Draft-to-open invoice posting with line, tax and total recalculation.
- Receipts and supplier payments with controlled partial allocation.
- Overpayment and cross-party allocation protection.
- Outstanding balances and AR/AP ageing buckets: Current, 1–30, 31–60, 61–90 and 90+.
- Fiscal-period, document-numbering and bank-account foundations.
- Audit events for company, party, invoice, payment and allocation actions.
- Finance command-centre UI with receivables, payables, banking and period-control views.

## Quick start

1. Copy `.env.example` to `.env`.
2. Install dependencies: `pip install -r backend/requirements.txt`.
3. Run API: `cd backend && uvicorn app.main:app --reload`.
4. Open API docs at `http://localhost:8000/docs`.
5. Run UI: `cd frontend && npm install && npm run dev`.
6. Run checks: `bash scripts/check.sh`.

## Important limitations

v0.2.0 is an engineering release, not a production-ready accounting system. It does not yet include database migrations, authentication, full RBAC/segregation of duties, approval workflows, automatic GL posting from subledgers, inventory fulfilment, bank reconciliation, financial statements, backup/restore tooling or a desktop installer.

See `docs/ARCHITECTURE.md`, `docs/FINANCE.md`, `docs/ROADMAP.md`, `docs/USER_GUIDE.md`, `docs/SECURITY.md` and `CHANGELOG.md`.
