
# Requirements and Traceability Matrix

| Epic | Stories | Primary module/API | Pure rule tests | Role guides |
|---|---|---|---|---|
| Platform administration | US-ADM-001–005 | companies, periods, sequences, posting profiles, saved reports | finance/reporting | System Admin, Technical Admin |
| Finance | US-FIN-001–006 | journals, invoices, payments, ageing, statements | accounting, finance, reporting | Finance, Auditor |
| Sales | US-SAL-001–006 | price lists, quotes, orders, delivery, integrated invoice | sales, integration | Sales, Finance |
| Procurement | US-PRO-001–006 | requests, RFQs, supplier quotes, POs, receipts, match | procurement, integration | Procurement, Finance |
| Inventory | US-INV-001–006 | movements, balances, transfer, reorder | inventory | Inventory, Manager |
| Integration | US-INT-001–003 | events, trace, posting profiles | integration | Developer, Support, Auditor |
| Insight | US-RPT-001–005 | statements, KPIs, performance, saved reports, quality | reporting | Manager, Finance, Admin |

## Release mapping

- v0.1: platform/GL foundation.
- v0.2: Finance stories.
- v0.3: Sales stories through order and invoice handoff.
- v0.4: Procurement stories through receipt.
- v0.5: Inventory stories.
- v0.6: Integrated delivery, matching, trace and GL posting.
- v0.7: Insight, saved reports, exports, data quality and complete documentation.

## Validation boundary

Pure-rule tests demonstrate deterministic business invariants. They do not replace database integration, API contract, authorization, concurrency, performance, security or browser E2E testing required before GA.
| Security | US-SEC-001–003 | authentication, users, roles, runtime validation | security/runtime tests | Security Admin, System Admin |
| Operations | US-OPS-001–003 | Alembic, health probes, backup/restore | migration/config validation | Technical Admin, DBA |
| Open source | US-OSS-001–002 | license, community files, CI/release workflows | repository completeness checks | Developer, Maintainer |
| Pilot access hardening | US-SEC-004–005 | sessions, route policy, logout/refresh | hardening/security tests | Security Admin, Developer |
| Segregation/concurrency | US-SOD-001–002, US-CON-001 | approvals, role validation, version checks | hardening tests | Controller, Security Admin, Auditor |
| Approval binding | US-SOD-003, US-SAL-007, US-INV-007, US-SEC-006 | journal post, credit override, inventory adjustment, role assignment | hardening tests | Finance, Sales, Inventory, Security Admin, Auditor |
