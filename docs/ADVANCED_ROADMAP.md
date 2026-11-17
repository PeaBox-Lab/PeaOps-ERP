# PeaOps Advanced Roadmap (top-ERP-informed)

Comparison: SAP S/4HANA, Oracle Fusion Cloud ERP / NetSuite, Microsoft Dynamics 365 F&O / Business Central, Sage Intacct / X3, Infor CloudSuite, Epicor Kinetic, Acumatica, IFS Cloud, Odoo, SAP Business One, Unit4. HRIS excluded.

## Where PeaOps plays
- SMBs and mid-market (10–1,000 users); finance-first with operations
- On-prem Linux server first, then optional cloud SaaS
- Open-source (Apache-2.0), API-first, module marketplace

## Pillar 1 — Core financial excellence (NetSuite/Intacct-class)
- Multi-entity/consolidation, intercompany elimination, dimensional analysis, real-time close-to-report
- ASC 606/IFRS 15 revenue recognition, multi-currency revaluation, tax localization (GST, VAT, e-invoicing)
- Budgeting, forecasting, 13-week rolling cash flow, AP/AR automation, payment matching

## Pillar 2 — Supply chain & operations (Infor/Epicor-class)
- MRP/MRP-II, BOM/routings/work-order dispatch, shop-floor execution, capacity planning, APS scheduling
- WMS: bin/location, directed putaway/picking, wave picking, cycle counting, GS1 barcode/RFID
- Procure-to-pay unification: contracts, landed cost, 3-way match tolerances, supplier scorecards/returns, supplier collaboration

## Pillar 3 — Sales, CRM & commerce (Business Central/Acumatica-class)
- Quote→order→delivery→invoice unification, returns/RMA, pricing/discount engine, credit management, subscriptions, customer portal, e-commerce connectors (Shopify/Amazon), B2B buyer portal

## Pillar 4 — Project & service (Unit4/IFS-class)
- Project accounting (WIP, milestones, rev recognition), time/expense, service contracts, field service (mobile), asset EAM, maintenance scheduling

## Pillar 5 — Intelligence & AI (SAP Joule / D365 Copilot-class)
- Embedded analytics: real-time executive dashboards, KPI tracking, anomaly detection, what-if scenarios
- AI assistant: natural-language query over GL/sales/inventory, draft journal entries/orders, suggest reorder points, exception prediction for integration events, document capture (AP invoice OCR)
- Demand sensing, forecasting (time-series), cash-flow forecasting

## Pillar 6 — Platform & integration (Acumatica/NetSuite-class)
- REST + webhooks + event bus, GraphQL/read-model API, integration adapters (banking, e-invoice, payment gateways, Shopify/Amazon, EDI), low-code app builder, feature-flagged modules/marketplace, plugin SDK

## Pillar 7 — Security, governance & compliance
- MFA/SSO (OIDC/SAML), row-level and column-level security, SoD policy engine, approval workflows per entity/amount/threshold, immutable audit ledger, immutable backup + restore drills, SOC 2-aligned controls, GDPR DSR, data residency

## Pillar 8 — Cloud & multi-tenancy (v2.0)
- Multi-tenant SaaS: tenant provisioning, per-tenant isolation, tenant billing/metering, HA (multi-AZ), autoscaling, DR with RPO/RTO SLAs, zero-downtime upgrades

## Release arc
- v0.9 GA hardening → v1.0 Core GA (Local Server) → v1.1 Financial depth → v1.2 SCM/MRP/WMS → v1.3 Project/service → v1.4 AI & analytics → v1.5 Extensibility/marketplace → v2.0 Cloud GA SaaS → v2.1 AI copilots & anomaly ops → v2.5 global tier.
