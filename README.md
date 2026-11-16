# PeaOps v0.3.0

PeaOps is an India-first, globally-ready ERP foundation for SME and mid-market organizations. v0.3 extends the verified Finance core with a controlled Sales / Quote-to-Cash foundation while retaining one modular product across Local, Local Server and Cloud deployment paths.

## v0.3 Sales scope

- Customer and item masters reused from the shared ERP core.
- Dated, currency-specific price lists with item prices.
- Sales quotations with validity dates, discounts, taxes and controlled send status.
- Quote-to-sales-order conversion that preserves commercial lines.
- Direct sales-order creation and promised-delivery dates.
- Order confirmation with customer credit-exposure checks.
- Explicit, audited credit overrides requiring a reason.
- Confirmed-order handoff to draft Accounts Receivable invoices.
- Sales command-centre UI for pipeline, orders, promises and credit holds.
- Existing Finance v0.2 capabilities retained: AR, AP, payments, allocations, ageing, fiscal periods, numbering, banking foundation, GL journals and trial balance.

## Quick start

1. Copy `.env.example` to `.env`.
2. Install dependencies: `pip install -r backend/requirements.txt`.
3. Run API: `cd backend && uvicorn app.main:app --reload`.
4. Open API documentation at `http://localhost:8000/docs`.
5. Run UI: `cd frontend && npm install && npm run dev`.
6. Run checks: `bash scripts/check.sh`.

## Important limitations

v0.3.0 is an engineering release. Delivery and inventory fulfilment are not yet implemented; order invoice handoff creates a draft AR invoice rather than posting inventory or GL entries. Authentication, RBAC, segregation of duties, migrations, approvals, production backup/restore and a desktop installer remain future milestones.

See `docs/SALES.md`, `docs/FINANCE.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/USER_GUIDE.md`, `docs/SECURITY.md` and `CHANGELOG.md`.
