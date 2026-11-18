
# PeaOps v0.8.2 — Approval Binding

PeaOps v0.8.2 strengthens the Apache-2.0, GitHub-ready, on-prem Server-first ERP production foundation for controlled pilots.

## v0.8.2 highlights

- Central deny-by-default API permission policy.
- Exact maker-checker approval binding for journal post, credit override, manual inventory adjustment and role assignment.
- Refresh sessions with hashed tokens, expiry and logout revocation.
- Maker-checker approval records for high-risk actions.
- Selected role conflict/segregation validation.
- Optimistic version checks that reject stale approval decisions.
- Expanded pilot operations, session/access and SoD documentation.
- 116 cumulative pure-rule tests across ERP, reporting, security and hardening.

## Cumulative package

Finance, Sales, Procurement, Inventory, Integration, Insight, production server deployment, migrations, backup/restore, authentication/RBAC, GitHub governance, 15+ role guides, user stories and traceability remain included.

> **Classification:** controlled-pilot candidate, not Core GA. MFA/SSO, full domain authorization review, concurrency/load tests and browser/API E2E remain blockers.

Start with `docs/USER_GUIDE.md`, `docs/operations/PRODUCTION_READINESS_CHECKLIST.md`, `docs/operations/PILOT_OPERATIONS_GUIDE.md`, and `docs/RELEASE_NOTES_v0.8.2.md`.

Licensed under Apache License 2.0.

## Quick start — install on a VM

```bash
# Linux (Ubuntu 22.04/24.04)
sudo SITE_DOMAIN=erp.example.com SEED_DEMO=true deployment/server/install.sh

# Windows Server / Windows 10-11 (elevated PowerShell)
powershell -ExecutionPolicy Bypass -File deployment\server\install.ps1 -SiteDomain erp.example.com -SeedDemo
```

Open `https://<your-domain>/` — sign in with company `1` / `admin` / `Admin@123456` (change it!).
Verify with `curl -k https://localhost/api/v1/health/ready`.

## Documentation

- Getting started in the web UI: `docs/USER_GUIDE.md` ("Getting started (v0.8.2 web UI)")
- Task-oriented help: `docs/help/HELP_TOPICS.md`
- Hosting for clients (Linux & Windows VMs, tenancy, TLS, backups, client onboarding): `docs/operations/HOSTING_AND_CLIENT_ONBOARDING.md`
- Production stack: `docs/operations/SERVER_DEPLOYMENT_GUIDE.md`
- Roadmap: `docs/ROADMAP.md` · Feature catalog: `docs/FEATURE_CATALOG.md` · Advanced roadmap: `docs/ADVANCED_ROADMAP.md`
