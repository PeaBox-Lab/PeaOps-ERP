# Threat Model - v0.8

## Protected assets

Credentials, tokens, financial data, customer/supplier data, inventory, audit/security events, backups, posting configuration and repository integrity.

## Trust boundaries

Browser to TLS proxy; proxy to API; API to PostgreSQL; administrators to server; CI to repository/release; backup storage and restore environment.

## Material threats and controls

- Credential compromise: strong password policy, hashing, short token lifetime, lockout, security events; MFA remains open.
- Authorization bypass: permission claims and protected admin APIs; full endpoint permission coverage remains open.
- Cross-company access: company IDs and admin-company checks; comprehensive tenant-isolation tests remain open.
- Duplicate posting: idempotency keys and unique events.
- Data tampering: transaction controls, audit/movement/event history, TLS and database access restrictions.
- Injection: ORM queries and schema validation; security testing remains required.
- Supply chain: Dependabot, dependency review and CodeQL; signing/SBOM remain open.
- Backup theft: operational guidance requires protected off-server storage; application encryption tooling remains open.
- Availability: health checks and restart policies; HA and DR automation remain open.
