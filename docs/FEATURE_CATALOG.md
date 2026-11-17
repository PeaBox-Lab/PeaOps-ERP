# PeaOps ERP — Feature Catalog (Foundation + Essential)

Compiled by comparing the top 10 non-HRIS ERP platforms (SAP S/4HANA, Oracle ERP Cloud, Microsoft Dynamics 365 F&O, NetSuite, Odoo, Epicor Kinetic, Infor CloudSuite, IFS Cloud, Acumatica, Sage X3). Organized as Foundation (must-have to run) and Essential (needed for SMB/mid-market competitiveness).

## Legend
- ✅ Already in PeaOps
- 🟡 Partial
- ❌ Missing

## 1. Foundation (core platform)
- Multi-company / multi-branch / multi-currency ✅
- Users, roles, permissions (RBAC) ✅
- Authentication (JWT, refresh, lockout) ✅ (MFA ❌)
- Audit trail / security events ✅
- Number sequences / document numbering ✅
- Fiscal periods ✅
- Posting profiles / GL mapping ✅
- Health checks / readiness ✅
- Backups & restore scripts ✅
- Migrations (Alembic) ✅
- Notifications framework ❌
- Document attachments / file storage ❌
- Search / global lookup ❌
- Workflow / approval engine 🟡 (maker-checker only)
- Localization / i18n / multi-language ❌
- Tax engine (GST/VAT) 🟡 (rates only)
- Reporting engine / saved reports ✅ 🟡

## 2. Finance & Accounting (essential)
- Chart of accounts, journals, GL ✅
- AR invoices, payments, allocations ✅
- AP invoices, payments ✅
- Bank accounts, reconciliation ❌
- Fixed assets & depreciation ❌
- Budgeting & forecasting ❌
- Cash flow / treasury ❌
- Multi-currency revaluation ❌
- Tax returns / e-invoicing ❌
- Consolidation / intercompany ❌
- Cost accounting / cost centers ❌

## 3. Sales & CRM (essential)
- Customers/parties ✅
- Quotes, orders, deliveries ✅
- Invoicing from orders 🟡
- Price lists ✅
- Discounts & promotions ❌
- Credit management / limits ✅ (basic)
- Sales returns / RMA ❌
- CRM: leads, opportunities, pipeline ❌
- Customer portal ❌

## 4. Procurement (essential)
- Purchase requests, RFQ, supplier quotes, PO, GR ✅
- Supplier management ✅ (as parties)
- Three-way match ✅
- Supplier returns / debit notes ❌
- Contract management ❌
- Landed costs ❌

## 5. Inventory & Warehouse (essential)
- Items, warehouses, balances, movements ✅
- Stock transfers ✅
- Reorder points / policies ✅
- Lot/serial tracking 🟡
- Cycle counting ❌
- Bin locations / WMS ❌
- Barcode/RFID support ❌
- Inventory valuation methods (FIFO/LIFO/avg) 🟡 (avg only)

## 6. Manufacturing / MRP (expansion)
- BOM, routings, work orders ❌
- MRP planning ❌
- Capacity planning ❌
- Quality control ❌

## 7. Projects & Service (expansion)
- Projects, tasks, timesheets ❌
- Service orders, contracts ❌
- Field service ❌

## 8. Assets & Maintenance (expansion)
- Asset register, depreciation ✅ (planned)
- Preventive maintenance ❌

## 9. Integration & Platform (essential)
- REST API ✅
- Webhooks / integration events ✅
- Idempotency ✅
- E-invoicing / tax authority integration ❌
- Payment gateway integration ❌
- Email/SMS gateway ❌
- EDI ❌
- SSO/MFA ❌

## 10. Analytics & Reporting (essential)
- Saved reports ✅
- Dashboards / KPIs 🟡
- Export (CSV/PDF/Excel) ❌
- Scheduled reports ❌
- Data quality findings ✅

## Roadmap (feature-driven)
- v0.9: MFA/SSO, bank reconciliation, fixed assets, notifications, attachments, tax engine, exports.
- v1.0: CRM-lite, sales returns, landed costs, cycle counting, advanced inventory valuation, dashboards.
- v1.1: Manufacturing/MRP, projects, service.
- v1.2: Assets/maintenance, consolidation, treasury.
- v2.0: Cloud multi-tenant SaaS.

## Immediate build start
1. Notification framework (email + in-app) — foundation for approvals & alerts.
2. Bank reconciliation module.
3. Fixed assets register + depreciation.
4. Document attachments (file storage).
5. Export to CSV/Excel/PDF.