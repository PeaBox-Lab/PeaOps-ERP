# Help topics

Quick, task-oriented answers for the PeaOps web UI (v0.8.2). For reference detail, see `USER_GUIDE.md` and the module guides.

## Sign-in & access

**Q: I forgot my password.**
A: Passwords are not recoverable from the UI. Ask a system administrator to reset your account (Security events will show the reset), or use `backend/scripts_bootstrap_admin.py` on the server to recreate an admin.

**Q: I'm locked out after 5 failed attempts.**
A: Accounts auto-unlock after 15 minutes. An administrator can also restore access by editing `locked_until`.

**Q: What does "MFA (TOTP)" mean here?**
A: (Administration → MFA) Generate a secret, add it to your authenticator app as a TOTP entry, then verify the code. Once enabled, every sign-in requires the code.

**Q: I get "Missing permission" on an action.**
A: Your role lacks the required permission. Ask an admin to add the role/permission (e.g. `finance:invoice`) — wildcards: `finance:*`, `admin:*`.

**Q: "Company not found / wrong company".**
A: Your account is tied to a company (the Company ID on the sign-in form, default 1). Use the ID of the company your user belongs to.

## Using the app

**Q: A list is empty even though records exist.**
A: Lists show records for your company only. Click **Refresh**. If still empty, confirm you are signed into the right company.

**Q: Creating a document fails with "Number sequence not configured".**
A: An administrator must create a number sequence for that document type (Administration → Number sequences, e.g. `ar_invoice`).

**Q: "Customer not found for company" (or item/party).**
A: The selected Party/Item doesn't exist or belongs to another company. Create it first (Sales → Customers & vendors / Inventory item master).

**Q: Where do I see invoices/payments I can allocate?**
A: Finance → Invoices (View tab). Allocate: Finance → Payments & allocations → Action → Allocate payment to invoice, with the payment ID and amount.

**Q: How do I export data?**
A: `GET /api/v1/invoices/export.csv`, `/api/v1/invoices/export.xlsx`, `/api/v1/reports/export/trial-balance.csv`. All 100+ endpoints are interactive at `/docs`.

**Q: What's the difference between Post / Send / Confirm / Submit?**
A: Each is the legal next step in that document's lifecycle: invoices Post, quotes Send, sales orders Confirm, purchase requests Submit, RFQs Issue. Actions that need another user's approval require an Approval record first.

**Q: How do I approve something?**
A: Administration → Approvals → Action → Approve request (you must not be the requester; the action requires a distinct approver).

## Dashboard & reports

**Q: The Overview shows "Cannot reach the API".**
A: The dev proxy targets the local demo proxy on :8080 by default — ensure the Docker stack is up (`docker compose -f deployment/server/docker-compose.production.yml -f deployment/server/docker-compose.local.yml up -d demo`), or run the backend directly on :8000 and set the proxy target in `frontend/vite.config.ts`. After changing `vite.config.ts`, restart the dev server.

**Q: KPI tiles show zeros.**
A: They read live from the database — usually the seed data is empty (no invoices/movements yet). Create a document and refresh.

**Q: How are reports run?**
A: Reports → any report type (Income statement, KPIs, sales performance…) renders instantly. Reports → Run a report executes parameterised runs. Saved reports can be shared and scheduled (e.g. `0 9 1 * *`).

## Deployment & server

**Q: I installed but the site shows an nginx 502 / can't reach API.**
A: The API container is unhealthy. Check `docker compose -f deployment/server/docker-compose.production.yml logs api` and `docker compose ps`. Health: `curl -k https://localhost/api/v1/health/ready`.

**Q: The browser shows a certificate warning.**
A: Local demo uses a self-signed cert (expected). For internet use, install a real certificate (see HOSTING_AND_CLIENT_ONBOARDING.md) or trust the local CA.

**Q: Where is my data? Backups?**
A: Postgres volume `peaops_db` inside Docker. Backups: `deployment/server/scripts/backup.sh` (pg_dump + sha256, 30-day retention). Restore: `scripts/restore.sh`. Schedule backups before go-live.

**Q: How do I update PeaOps?**
A: See `deployment/server/scripts/upgrade.sh` and `docs/operations/UPGRADE_AND_ROLLBACK.md`.

**Q: Can I host this for multiple client companies?**
A: Yes — see `docs/operations/HOSTING_AND_CLIENT_ONBOARDING.md` for multi-company (single DB), per-client isolated stacks, and the SaaS roadmap.

## Troubleshooting quick map

| Symptom | Likely cause | Fix |
|---|---|---|
| 502 / blank page | web/api container down | `docker compose ps`, check health endpoints (`curl -k https://localhost/api/v1/health/ready`); UI dev server proxies /api to the local demo proxy on :8080 |
| Sign-in fails for password | wrong company/user/password | use company `1`, user `admin`; reset via bootstrap script |
| Everything is zero | empty seed DB | seed demo or enter real documents |
| 403 everywhere | missing permissions | ask admin for the role/permission |
| 409 on create | no number sequence / unbalanced / duplicate | add sequence; fix journal lines; check duplicates |
| Old UI after deploy | stale bundle/cache | hard refresh (Ctrl+F5), rebuild web image |
