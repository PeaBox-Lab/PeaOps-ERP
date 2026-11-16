# PeaOps v0.5.0

PeaOps is an India-first, globally-ready ERP foundation for SME and mid-market organizations. v0.5 adds an Inventory / Stock-Control foundation to the existing Finance, Sales and Procurement modules.

## v0.5 Inventory scope

- Immutable stock-movement ledger for openings, receipts, issues, adjustments and transfers.
- Warehouse/item balances with on-hand, reserved and available quantities.
- Negative-stock prevention with an explicit per-item/warehouse policy override.
- Weighted-average cost and inventory-value foundation.
- Balanced inter-warehouse transfers with source and destination movements.
- Inventory reservation controls that cannot exceed available stock.
- Lot and serial tracking foundations, including one-unit serial movements.
- Reorder points, reorder quantities and available-stock-driven alerts.
- Inventory ledger, balances and reorder REST endpoints.
- Inventory command-centre UI for value, availability, warehouse balances and movement history.
- Finance v0.2, Sales v0.3 and Procurement v0.4 capabilities retained.

## Quick start

1. Copy `.env.example` to `.env`.
2. Install dependencies: `pip install -r backend/requirements.txt`.
3. Run API: `cd backend && uvicorn app.main:app --reload`.
4. Open API documentation at `http://localhost:8000/docs`.
5. Run UI: `cd frontend && npm install && npm run dev`.
6. Run checks: `bash scripts/check.sh`.

## Important limitations

v0.5.0 is an engineering release. Procurement goods receipts and Sales delivery are not yet automatically connected to stock movements. Valuation is a weighted-average foundation rather than a closed-period costing engine. Lot/serial fields are validated but do not yet include expiry, genealogy, recall, barcode or allocation workflows. Authentication, RBAC, approvals, migrations, backup/restore and installer packaging remain future milestones.

See `docs/INVENTORY.md`, `docs/PROCUREMENT.md`, `docs/SALES.md`, `docs/FINANCE.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/USER_GUIDE.md`, `docs/SECURITY.md` and `CHANGELOG.md`.
