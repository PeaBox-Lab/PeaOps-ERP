# Security Baseline

## Required before production use
- Replace development secret and use managed secrets.
- TLS everywhere outside localhost.
- Implement and test authentication, password hashing and MFA for cloud.
- Server-side RBAC with explicit Create/View/Edit/Delete/Approve/Post/Reverse/Export/Admin permissions.
- Segregation-of-duties checks for financial approval/posting.
- Rate limiting and security headers at the gateway.
- Tenant isolation tests before SaaS exposure.
- Encrypted backups and tested restore procedures.
- Dependency/SBOM and secret scanning in CI.
- Immutable or append-only audit retention suitable for the customer policy.

v0.1 is an engineering foundation, not a compliance-certified production release.
