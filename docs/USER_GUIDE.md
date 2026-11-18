
# PeaOps Complete User Guide - v0.8.2

## Getting started (v0.8.2 web UI)

### 1. Sign in
Open the server URL in your browser (e.g. `https://your-host/` or `http://localhost:8080`).
Sign in with your **Company ID**, **username** and **password**. If your account has MFA
(TOTP) enabled, enter the 6-digit code from your authenticator app. Demo pilot credentials
(see Pilot seeding) are company `1`, user `admin`, password `Admin@123456` — change these before real use.

### 2. Navigate
After sign-in you land on the **Overview** dashboard (live readiness, request counters, your permissions).
Use the sidebar for modules: Overview, and each business module (Finance, Sales, Procurement, Inventory,
CRM, Manufacturing, Projects, Maintenance & Assets, Consolidation & Treasury, Reports, Administration, Platform).

### 3. View and create records
Every module page has three tabs:

- **View** — list of records for your company (live from the API). Table columns show all fields.
- **Create** — a guided form for that document type. Dropdowns load customers, suppliers, bank accounts,
  BOMs, assets, POs etc. from the system. Repeating line items (quotes, orders, requests) use the
  on-line editor with add/remove rows.
- **Action** — one-click or parameterised actions on a record, e.g. Post invoice, Send quote, Allocate payment,
  Convert quote→order, Post monthly depreciation, Approve, Verify MFA.

Most create actions in the Finance module also have live validation (e.g. journal entries must balance).

### 4. Typical daily flows
- **Sales:** create customer → create quote → send → convert quote to order → confirm order → deliver → invoice.
- **Procurement:** create purchase request → submit → RFQ → compare quotes → PO → receive goods → integrated supplier invoice.
- **Finance:** create invoice → post → receive payment → allocate payment to the invoice.
- **Inventory:** set reorder policies → record movements → watch reorder alerts → transfer stock.
- **Reports:** open Reports module → pick KPI / statement / performance → save the report → schedule it.

### 5. Approvals and maker-checker
High-risk actions (journal post, credit override, manual inventory adjustment, role assignment) need an approved
maker-checker record. Create a request in **Administration → Approvals**, and a different user approves it.

### 6. Exports
Invoice CSV: `/api/v1/invoices/export.csv` · Invoice Excel: `/api/v1/invoices/export.xlsx` ·
Trial balance CSV: `/api/v1/reports/export/trial-balance.csv`. Use the browser download URL with your session, or
explore all endpoints in **API Explorer** (`/docs`).



This is the navigation guide for everyone involved in selecting, implementing, administering, operating, supporting, auditing or using PeaOps.

## Choose your role

| Role | Start here | Primary responsibilities |
|---|---|---|
| Business sponsor / customer executive | `guides/EXECUTIVE_AND_CUSTOMER_GUIDE.md` | Outcomes, governance, KPIs, rollout decisions |
| System administrator | `guides/SYSTEM_ADMIN_GUIDE.md` | Companies, masters, periods, numbering, controls |
| Technical administrator / DevOps | `guides/TECHNICAL_ADMIN_GUIDE.md` | Configuration, deployment and operations |
| Security administrator | `guides/SECURITY_ADMIN_GUIDE.md` | Users, roles, security events and access review |
| Database administrator | `guides/DATABASE_ADMIN_GUIDE.md` | PostgreSQL, migrations, backup and recovery |
| Implementation consultant | `guides/IMPLEMENTATION_GUIDE.md` | Discovery, design, migration, testing, cutover |
| Finance user / controller | `guides/FINANCE_USER_GUIDE.md` | GL, AR, AP, payments, ageing, statements |
| Sales user / sales operations | `guides/SALES_USER_GUIDE.md` | Pricing, quotes, orders, delivery, invoicing |
| Procurement user / buyer | `guides/PROCUREMENT_USER_GUIDE.md` | Requests, RFQs, comparison, POs, receipts |
| Inventory / warehouse user | `guides/INVENTORY_USER_GUIDE.md` | Movements, transfers, reservations, tracking |
| Manager / analyst | `guides/MANAGER_AND_ANALYST_GUIDE.md` | KPIs, statements, saved reports, exports |
| Auditor / compliance reviewer | `guides/AUDITOR_GUIDE.md` | Evidence, traceability, exceptions, controls |
| Support / service desk | `guides/SUPPORT_GUIDE.md` | Triage, diagnostics, safe recovery, escalation |
| Developer / integration engineer | `guides/DEVELOPER_GUIDE.md` | Code structure, API, testing, extension boundaries |
| General end user | `guides/END_USER_QUICKSTART.md` | Navigation, records, statuses, common actions |

## Product-wide lifecycle

1. Configure organization, accounts, parties, items and warehouses.
2. Configure periods, numbering, inventory policy and posting profiles.
3. Operate Sales, Procurement, Inventory and Finance documents.
4. Use Integration commands for cross-module posting.
5. Monitor exceptions and data quality.
6. Review Insight reports, save views and export evidence.

## Common status principle

Documents progress through explicit statuses. Do not edit posted financial or inventory history to correct it. Use controlled follow-on or reversal processes as they are introduced. In v0.7, inspect the API response and audit/integration events before retrying a failed action.

## Documentation map

- Module guides: `FINANCE.md`, `SALES.md`, `PROCUREMENT.md`, `INVENTORY.md`, `INTEGRATION.md`, `INSIGHT.md`
- Product: `product/FEATURES.md`, `product/VERSION_HISTORY.md`, `product/USER_STORIES.md`, `product/TRACEABILITY_MATRIX.md`
- Implementation: `implementation/IMPLEMENTATION_PLAYBOOK.md`, `implementation/DATA_MIGRATION_GUIDE.md`, `implementation/UAT_AND_CUTOVER.md`
- Operations/help: `help/TROUBLESHOOTING.md`, `help/FAQ.md`, `help/GLOSSARY.md`, `help/API_WORKFLOW_EXAMPLES.md`

## Production and open-source administration

- Controlled pilot deployment: `operations/SERVER_DEPLOYMENT_GUIDE.md`
- Production gate: `operations/PRODUCTION_READINESS_CHECKLIST.md`
- Security administrator: `guides/SECURITY_ADMIN_GUIDE.md`
- Database administrator: `guides/DATABASE_ADMIN_GUIDE.md`
- GitHub maintainer: `open-source/GITHUB_PUBLISHING_GUIDE.md`
- Backup/recovery and incidents: `operations/BACKUP_AND_RESTORE.md`, `operations/INCIDENT_RESPONSE.md`

## Pilot hardening additions

- Session/access controls: `security/SESSION_AND_ACCESS_CONTROL.md`
- Segregation of duties: `security/SEGREGATION_OF_DUTIES.md`
- Pilot operations: `operations/PILOT_OPERATIONS_GUIDE.md`

## v0.8.2 approval binding
High-risk journal posting, credit override, manual inventory adjustment and role assignment now require an exact approved maker-checker record. See `security/APPROVAL_BINDING.md`.
