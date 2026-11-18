
# Changelog

## Unreleased — VM-ready, guided UI, hosting playbook
### Added
- Guided, schema-driven forms for every create action in the web UI (typed fields, live totals, line-item editors, remote dropdowns) — invoice, payment, journal, party, lead, opportunity, plus all procurement, inventory, projects, manufacturing, maintenance, consolidation, treasury, reports, admin and platform endpoints.
- Dashboard charts (capital profile, top customers, AR donut) and live KPI tiles.
- Prometheus metrics endpoint (`/metrics/prometheus`) alongside JSON `/metrics`.
- End-to-end API flow test (login → invoice → allocation) running in CI on an isolated database; test-session isolation via `tests/conftest.py`.
- `deploy/install.sh` / `deploy/install.ps1`: one-command VM installers (Docker, .env generation, self-signed or real TLS certs, build, start, optional demo seed, preflight).
- `deployment/server/scripts/seed_pilot_demo.py` and `gen_self_signed_cert.py` shared helpers.
- Client-hosting guide `docs/operations/HOSTING_AND_CLIENT_ONBOARDING.md` (Linux & Windows VMs, tenancy models, TLS, backups, client onboarding).
- Help-topics guide `docs/help/HELP_TOPICS.md` and a UI walkthrough section in `docs/USER_GUIDE.md`.
- `.dockerignore` for backend/frontend builds.
### Fixed
- Web container health check failing behind IPv6 (`[::]:80/443` listens added) — proxy now starts.
- Frontend build used absolute `http://localhost:8000` API URLs; now same-origin with dev/preview proxies.
- Post-create lists now refresh automatically; guided forms preselect the first available option; invoice form no longer wipes line items on save.
- Number sequence coverage for all document types in the pilot seed.

## 0.8.1 - 2026-11-16
### Added
- Central deny-by-default route authorization policy.
- Revocable refresh sessions and logout.
- Maker-checker approval records and selected SoD conflicts.
- Optimistic approval version checks.
- Pilot operations, session/access and SoD guides.
- 16 pilot-hardening tests.
### Changed
- Product/API/frontend version advanced to 0.8.1.
- Controlled-pilot access posture strengthened.


## 0.8.0 - 2026-11-16
### Added
- User, role, permission, user-role and security-event models.
- Password policy, PBKDF2 hashing, signed expiring access tokens and lockout.
- Protected administration APIs and production runtime validation.
- Alembic migration baseline and production migration job.
- Liveness/readiness endpoints and request/security headers.
- On-prem production Docker stack with PostgreSQL, web, API and TLS proxy.
- Backup, checksum, restore, preflight and bootstrap-admin tooling.
- Apache-2.0 license, notice and complete GitHub community/governance files.
- CI, migration smoke test, CodeQL, dependency review, Dependabot and release workflows.
- Production, security, database, incident, maintenance, upgrade and publishing guides.
- Security, operations and open-source user stories.
### Changed
- Product/API/frontend version advanced to 0.8.0.
- Production schema ownership moves from automatic creation to Alembic.
- Release classified as controlled-pilot candidate, not GA.

## 0.7.0 - 2026-11-16
### Added
- Insight, statements, KPIs, reports, exports, data quality and complete documentation suite.
## 0.6.0 - 2026-11-16
### Added
- Idempotent integration, trace, delivery, matching and GL posting.
## 0.5.0 - 2026-11-16
### Added
- Inventory ledger, balances, valuation, transfers and reorder.
## 0.4.0 - 2026-11-16
### Added
- Procurement request-to-receipt.
## 0.3.0 - 2026-11-16
### Added
- Sales quote-to-order and credit controls.
## 0.2.0 - 2026-11-16
### Added
- Finance AR/AP and ageing.
## 0.1.0 - 2026-11-16
### Added
- ERP foundation and GL.
## 0.8.2 - 2026-11-17
### Added
- Exact approval binding for four high-risk business/admin actions.
- Approval-binding security guide and four cumulative user stories.
- Five approval-binding rule tests.
### Fixed
- Missing API imports used by authentication and integrated sales posting.
- Mutable report-parameter defaults.
### Changed
- Product/API/frontend version advanced to 0.8.2.
