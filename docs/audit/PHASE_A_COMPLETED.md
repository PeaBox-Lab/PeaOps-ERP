# Phase A — completed

Date: 2026-11-18  
Scope: harden the SaaS deployment for a controlled pilot and prove it works end-to-end.

## Delivered

### 1. Period-close enforcement
- New module `backend/app/domain/period_guard.py`
- Applied at posting points:
  - Journal entry postings
  - Invoice postings
  - Payment creation
  - Inventory movements
  - Goods receipts
  - Stock transfers
  - Deliveries
- Closed periods now reject postings with HTTP 409 and a clear message.

### 2. Force-password-change on first login
- `User.must_change_password` added
- `POST /api/v1/auth/change-password`
- Admin-created users start with `must_change_password=True`
- Seeded demo admin is exempt so the demo remains usable

### 3. Tokens and session expiry
- Silent refresh flow
- Proactive refresh 30s before expiry
- Single-flight refresh to avoid token stampede
- Session falls back cleanly to sign-in on unrecoverable expiration

### 4. Health and migrations
- `alembic upgrade head` verified in both SQLite dev runs and Docker Postgres pilot
- Head is now `20261118_0003`

### 5. Test coverage
- `tests/test_period_guard.py` — period close reject, password-change flow, flag surfacing on login
- 122 total tests passing

## What is NOT in Phase A
- SSO / OIDC login (blocked by lack of identity provider in this environment)
- Redis-backed rate limiting (blocked by no Redis instance; rate limiter is in-process)
- Full browser Playwright E2E (not installed/validated here)
- Off-site backup restore drill (scripts present; restore not exercised in this session)
- Uptime alerting (docs and sample rules present; no Grafana/Prometheus host available)
