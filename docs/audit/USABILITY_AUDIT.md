# Usability audit — what shipped this round

Date: 2026-11-18  
Scope: user-facing workflows and API coverage relevant to daily operations.

## What was already usable
- Guided forms on every create action
- Tables with status pills
- Charts on the dashboard
- Auth, RBAC, maker-checker, silent session refresh
- Docker production stack with TLS
- Alembic migrations; tests pass (122)

## What shipped in this round
- Invoice PDF download (`GET /api/v1/invoices/{id}/pdf`)
- Invoice email send with optional SMTP; **mailto fallback** when SMTP is not configured
- Invoice e-invoice XML retained as separate download
- All exports verified working in Docker pilot (`.env`-driven secrets, `.env` git-ignored)
- `/metrics/prometheus` endpoint for monitoring
- `tests/conftest.py` + `tests/test_period_guard.py` — test session isolated from dev DB

## Remaining high-impact gaps
- No printing from the browser (should use the PDF endpoints; add `@media print` CSS)
- No threaded comments/activity timeline on records
- No global search across modules
- No bulk import wizard
- No scheduled export delivery (emails/reports)
