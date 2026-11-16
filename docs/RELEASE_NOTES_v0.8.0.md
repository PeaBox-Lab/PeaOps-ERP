# PeaOps v0.8.0 Release Notes

## Purpose

Move PeaOps from feature-foundation development into a controlled on-prem production-readiness line and make the repository suitable for open-source publication.

## Highlights

Authentication/RBAC foundations; production configuration checks; migrations; health checks; PostgreSQL server stack; TLS proxy; web container; backup/restore; CI and security workflows; Apache-2.0 licensing; community governance; production/security runbooks; expanded role guides and user stories.

## Upgrade impact

Production deployments must set PostgreSQL, a unique 32+ character application secret, explicit HTTPS origins and `PEAOPS_AUTO_CREATE_SCHEMA=false`. Run Alembic before the API. Existing development SQLite environments may retain auto schema creation.

## Known limitations

Full endpoint authorization, MFA/SSO, formal SoD, concurrent posting tests, complete browser/API E2E tests, automated off-site backup, HA/DR, SBOM/signing and support SLA are not complete. Use v0.8 for controlled pilots only after documented risk acceptance and readiness verification.
