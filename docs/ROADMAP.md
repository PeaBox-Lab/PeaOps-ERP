
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

## Future roadmap (detailed)

### Phase 0 — Deployment readiness (now)
- Ship `.env.example` for backend and production compose; document secret generation.
- Add startup self-check (already in `validate_runtime`) and expand to verify DB connectivity + migrations applied.
- Add rate limiting on `/auth/login` and `/auth/refresh`; lockout telemetry.
- Add structured JSON logging + request-id correlation; ship to stdout for container collection.
- Add `/health/live` and `/health/ready` (already present) to load balancer probes.

### Phase 1 — Pilot completion (v0.8.x)
- PostgreSQL concurrency/load tests (k6) covering invoice post, payment allocation, inventory adjustment.
- Full API E2E suite (pytest + httpx) for finance/sales/procurement/inventory flows.
- Browser E2E (Playwright) for login → dashboard → create invoice → payment.
- Automated backup + restore drill in CI; verify RTO/RPO.
- Observability: Prometheus metrics, Grafana dashboards, alerting on 5xx/lockouts.

### Phase 2 — GA hardening (v0.9)
- MFA (TOTP) and optional SSO (OIDC/SAML).
- Complete domain authorization review; permission on every endpoint.
- SoD matrix enforcement across all high-risk actions.
- Security scanning in CI (bandit, pip-audit, npm audit, container scan).
- Signed releases + SBOM + provenance.

### Phase 3 — Core GA (v1.0)
- Supported on-prem Server release with documented SLA.
- Installer/upgrade scripts; zero-downtime migrations.
- Performance baselines and capacity planning guide.

### Phase 4 — Business expansion (v1.x)
- Assets, Projects, CRM, Manufacturing/MRP, WMS, Service management modules.

### Phase 5 — Cloud GA (v2.0)
- Multi-tenant SaaS: tenant provisioning, isolation, billing, HA, autoscaling, DR.
