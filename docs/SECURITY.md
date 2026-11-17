
# Security Baseline - v0.8

Implemented foundations: individual users, password complexity and hashing, login lockout, signed expiring tokens, role/permission data model, protected user/role administration, company-scope checks, security events, security headers, TLS proxy configuration, production-secret checks, private disclosure policy, CodeQL and dependency workflows.

Required before unrestricted production: MFA/SSO, token revocation and secret rotation, permission enforcement across every endpoint, segregation-of-duties rules, rate limiting, comprehensive tenant-isolation tests, penetration testing, centralized audit/log retention, encrypted/off-site backups, automated restore tests, SBOM and signed releases.

Never store secrets, certificates, backups or customer data in the repository.
