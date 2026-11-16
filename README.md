# PeaOps v0.8.0 — Production Foundation

PeaOps is an open-source ERP foundation for Finance, Sales, Procurement, Inventory, Integration and Insight. v0.8 moves the project onto an **on-prem Server-first production line** by adding security, migrations, operations, recovery, GitHub governance and release controls.

> **Release classification:** controlled-pilot candidate / production foundation. It is not unrestricted production GA. Review the readiness checklist and known blockers before deployment.

## Production foundation added

- Individual users, strong password policy and PBKDF2-SHA256 hashing.
- Expiring signed access tokens, failed-login tracking and temporary lockout.
- Company-scoped roles, permissions and protected user/role administration.
- Security-event records and request/security response headers.
- Production runtime validation that rejects default secrets, SQLite and insecure browser origins.
- Alembic migration structure and PostgreSQL migration startup gate.
- Liveness/readiness endpoints and structured request logging foundation.
- Docker Compose production stack: PostgreSQL, migration job, API, web application and TLS reverse proxy.
- Checksummed database backup and restore scripts plus operational runbooks.
- Apache License 2.0 and GitHub-ready contribution, governance, security, issue, PR, CI, CodeQL, Dependabot and release files.
- Production operations, security, database-administration, deployment, incident, maintenance and publishing guides.
- Security/operations/open-source user stories and traceability.

## Existing cumulative modules

Foundation, Finance, Sales, Procurement, Inventory, Integration and Insight remain included with all earlier tests and documentation.

## Start here

- General users: `docs/USER_GUIDE.md`
- Server deployment: `docs/operations/SERVER_DEPLOYMENT_GUIDE.md`
- Production gate: `docs/operations/PRODUCTION_READINESS_CHECKLIST.md`
- Security: `SECURITY.md` and `docs/security/THREAT_MODEL.md`
- Open-source publishing: `docs/open-source/GITHUB_PUBLISHING_GUIDE.md`
- Contributors: `CONTRIBUTING.md`
- Product stories: `docs/product/USER_STORIES.md`

## Developer check

```bash
bash scripts/check.sh
```

## License

Apache License 2.0. See `LICENSE` and `NOTICE`.
