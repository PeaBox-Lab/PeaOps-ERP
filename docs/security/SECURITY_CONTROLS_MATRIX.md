# Security Controls Matrix

| Risk | v0.8 control | Evidence | Remaining work |
|---|---|---|---|
| Weak passwords | Complexity and PBKDF2-SHA256 | Security rule tests | MFA, breached-password check |
| Brute force | Five-failure temporary lockout | Security events/user state | Distributed throttling |
| Token forgery | HMAC signature and expiry | Token tests | Rotation/revocation, asymmetric keys |
| Excess privilege | Roles and permissions | Role tables/admin endpoints | Full endpoint mapping, SoD |
| Insecure transport | TLS proxy/HSTS configuration | Server config | Certificate automation |
| Unsafe schema change | Alembic baseline and CI migration | Migration files/workflow | Compatibility rehearsal automation |
| Duplicate posting | Idempotency events | Integration tests | Concurrent PostgreSQL tests |
| Supply chain | Dependabot, CodeQL, dependency review | GitHub workflows | SBOM and signing |
| Data loss | Backup/checksum/restore scripts | Runbook/scripts | Automated off-site copy and restore drill |
