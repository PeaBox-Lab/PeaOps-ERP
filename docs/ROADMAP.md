
# PeaOps Roadmap

| Release | Theme | Major outcomes | Status |
|---|---|---|---|
| 0.1–0.7 | ERP foundation | Finance, Sales, Procurement, Inventory, Integration, Insight | Complete |
| 0.8 | Production foundation | Auth/RBAC, migrations, server operations, GitHub/open source | Current |
| 0.8.1 | Pilot hardening | Route policy, revocable sessions, SoD and concurrency foundations | Current |
| 0.8.x | Pilot completion | Approval binding, E2E, performance and recovery drills | Next |
| 0.9 | GA hardening | MFA/SSO, SoD, E2E/load/security, observability, signed releases | Planned |
| 1.0 | Core GA | Supported Local Server core ERP release | Planned |
| 1.x | Business expansion | Assets, Projects, CRM, Manufacturing, MRP, WMS, Service | Planned |
| 2.0 | Cloud GA | SaaS tenancy, provisioning, HA, autoscaling and DR | Planned |

## Immediate production-line backlog

1. Apply permission dependencies to every business endpoint.
2. Add MFA/SSO and token revocation/rotation.
3. Add maker-checker/SoD workflow.
4. Build PostgreSQL concurrency and load tests.
5. Build full API and browser E2E suites.
6. Automate off-site backups and restore drills.
7. Add metrics, tracing, alerts and log aggregation.
8. Generate SBOM, provenance and signed artifacts.

## v0.8.2 outcome
Approval binding is now implemented for journal posting, credit overrides, inventory adjustments and role assignments. Next pilot-completion work focuses on PostgreSQL concurrency/load evidence, full API/browser E2E, rate limiting, automated recovery drills and observability before the v0.9 GA-hardening line.
