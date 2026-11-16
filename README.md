# PeaOps v0.6.0

PeaOps v0.6 connects the Finance, Sales, Procurement and Inventory foundations into controlled Quote-to-Cash and Procure-to-Pay posting flows.

## v0.6 Integration scope

- Idempotent integration events that prevent duplicate business posting.
- Document links connecting orders, deliveries, receipts, invoices and journals.
- Sales delivery against confirmed orders with inventory issue and cost capture.
- Integrated AR invoice creation after posted delivery.
- Configurable sales posting profiles for AR, revenue, inventory and cost of goods sold.
- Supplier invoice creation only after purchase-order receipt.
- Three-way match across purchase order, received quantity and supplier invoice.
- Configurable quantity and price tolerances with explicit match exceptions.
- Configurable procurement posting profiles for inventory/expense and AP.
- Balanced GL journal creation when a complete posting profile is configured.
- Integration event monitor and trace APIs.
- Integration command-centre UI.
- All Finance, Sales, Procurement and Inventory capabilities retained.

## Quick start

1. Copy `.env.example` to `.env`.
2. Install dependencies: `pip install -r backend/requirements.txt`.
3. Run API: `cd backend && uvicorn app.main:app --reload`.
4. Open API documentation at `http://localhost:8000/docs`.
5. Run UI: `cd frontend && npm install && npm run dev`.
6. Run checks: `bash scripts/check.sh`.

## Important limitations

v0.6.0 remains an engineering release. Posting profiles must be configured for automatic GL journals; otherwise operational invoices are created without a journal. The API requires idempotency keys but production concurrency still needs database migrations, row locking and retry policies. Sales delivery currently invoices full order lines after delivery eligibility rather than milestone billing. Three-way match is line-based but does not yet support freight, landed cost, tax reconciliation or approval routing.

See `docs/INTEGRATION.md`, module guides, architecture, roadmap, user guide, security baseline and changelog.
