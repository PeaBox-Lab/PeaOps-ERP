# PeaOps Roadmap

| Release | Theme | Major outcomes |
|---|---|---|
| 0.1 | Foundation | Core organization, masters, GL, posting, trial balance, audit, UI shell |
| 0.2 | Finance | AR, AP, banking, fiscal periods, numbering, opening balances |
| 0.3 | Sales | Customers, quotations, orders, promises, pricing |
| 0.4 | Procurement | Requisitions, RFQ, PO, receipts, supplier evaluation |
| 0.5 | Inventory | Stock ledger, transfers, valuation, lots/serials, reorder controls |
| 0.6 | Integration | Quote-to-cash and procure-to-pay end-to-end posting |
| 0.7 | Insight | Financial statements, dashboards, saved views, exports |
| 0.8 | Workflow | Approval engine, delegation, escalation, notifications |
| 0.9 | Hardening | RBAC, SoD, import/export, backup/restore, audit and E2E gates |
| 1.0 | Core GA | Production hardening for Local + Local Server core ERP |
| 1.1 | Assets | Acquisition, depreciation, transfer, revaluation, disposal |
| 1.2 | Projects | Projects, budgets, time, cost, billing, profitability |
| 1.3 | CRM | Leads, pipeline, activities, conversion and forecasting |
| 1.4 | Manufacturing | BOM, routing, work centers, production orders |
| 1.5 | MRP | Net requirements, planned orders, capacity foundations |
| 1.6 | WMS | Bins, put-away, picking, packing, barcode/cycle count |
| 1.7 | Service | Cases, SLA, warranty, maintenance, field service |
| 1.8 | Ecosystem | Webhooks, integrations, extension SDK, public API |
| 1.9 | India | GST/TDS/e-invoice/e-way-bill integration after current-spec validation |
| 2.0 | Cloud GA | SaaS tenancy, provisioning, MFA, observability, autoscaling, DR |
| 2.x | Intelligence | OCR, anomaly detection, forecasting and approval-safe ERP agents |

## Release quality gates
- Accounting invariant tests must pass.
- Database migration tests must pass.
- Authorization tests must pass for every protected endpoint.
- UI routes/actions receive E2E coverage as implemented.
- No critical/high unresolved security defects for production releases.
- Backup/restore drill required for server/cloud GA.
