# PeaOps Roadmap

| Release | Theme | Major outcomes | Status |
|---|---|---|---|
| 0.1 | Foundation | Organization, masters, GL, posting, trial balance, audit, UI shell | Complete |
| 0.2 | Finance | AR, AP, banking, fiscal periods, numbering, ageing | Current |
| 0.3 | Sales | Customers, quotations, orders, promises, pricing | Next |
| 0.4 | Procurement | Requisitions, RFQ, PO, receipts, supplier evaluation | Planned |
| 0.5 | Inventory | Stock ledger, transfers, valuation, lots/serials, reorder controls | Planned |
| 0.6 | Integration | Quote-to-cash and procure-to-pay end-to-end posting | Planned |
| 0.7 | Insight | Financial statements, dashboards, saved views, exports | Planned |
| 0.8 | Workflow | Approval, delegation, escalation, notifications | Planned |
| 0.9 | Hardening | RBAC, SoD, migrations, import/export, backup/restore, E2E gates | Planned |
| 1.0 | Core GA | Production hardening for Local and Local Server | Planned |

## Next release: v0.3 Sales

Planned progression: Lead/Opportunity foundation → Quotation → Sales Order → Delivery promise → Invoice handoff. It will add customer pricing, discounts, quotation conversion, order statuses, credit-limit checks and sales dashboards without prematurely implementing inventory fulfilment.

## Release quality gates

- Accounting and finance invariant tests pass.
- Source compiles without syntax errors.
- Database migration tests become mandatory when migrations are introduced.
- Authorization and E2E tests become mandatory as those capabilities are implemented.
