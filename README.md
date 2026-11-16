# PeaOps v0.4.0

PeaOps is an India-first, globally-ready ERP foundation for SME and mid-market organizations. v0.4 extends the Finance and Sales core with a Procurement / Source-to-Receive foundation while retaining one modular product across Local, Local Server and Cloud deployment paths.

## v0.4 Procurement scope

- Purchase requests with requester, department, justification and required date.
- Request submission and controlled lifecycle status.
- Requests for quotation with response deadlines and optional request linkage.
- Supplier quotation capture with line pricing, discounts, taxes, validity and promised dates.
- Supplier comparison ranked by total cost, then promised date.
- Supplier-quote conversion to purchase orders.
- Direct purchase-order creation and controlled confirmation.
- Partial and final goods receipts with over-receipt prevention.
- Optional warehouse reference on receipts.
- Procurement command-centre UI for sourcing, savings, commitments and receipt attention.
- Finance v0.2 and Sales v0.3 capabilities retained.

## Quick start

1. Copy `.env.example` to `.env`.
2. Install dependencies: `pip install -r backend/requirements.txt`.
3. Run API: `cd backend && uvicorn app.main:app --reload`.
4. Open API documentation at `http://localhost:8000/docs`.
5. Run UI: `cd frontend && npm install && npm run dev`.
6. Run checks: `bash scripts/check.sh`.

## Important limitations

v0.4.0 is an engineering release. Goods receipts track purchase-order quantities but do not yet update an inventory stock ledger or valuation. Supplier invoices are not automatically matched to purchase orders and receipts, and no AP or GL posting is generated from procurement documents. Authentication, RBAC, approvals, migrations, backup/restore and installer packaging remain future milestones.

See `docs/PROCUREMENT.md`, `docs/SALES.md`, `docs/FINANCE.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/USER_GUIDE.md`, `docs/SECURITY.md` and `CHANGELOG.md`.
