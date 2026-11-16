# Security Baseline
## Required before production use
- Replace development secrets and use managed secret storage.
- TLS outside localhost.
- Authentication, password hashing and MFA for cloud.
- Server-side RBAC and segregation-of-duties checks.
- Tenant-isolation tests before SaaS exposure.
- Rate limits, security headers, dependency scanning and secret scanning.
- Database migrations, encrypted backups and tested restores.
- Append-only audit retention aligned with customer policy.
v0.2 is an engineering foundation, not a compliance-certified production release.
