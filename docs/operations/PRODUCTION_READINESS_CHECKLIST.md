
# Production Readiness Checklist - v0.8

v0.8 is a **production foundation and controlled-pilot candidate**, not unrestricted GA. A deployment may advance only when accountable owners verify each applicable gate.

## Release and change control

- [ ] Tagged release built by CI from reviewed commit.
- [ ] Cumulative tests, frontend build and migration smoke test pass.
- [ ] Release notes, migrations, known limitations and rollback steps reviewed.
- [ ] Two-person review for security, accounting and migration changes.

## Infrastructure

- [ ] Dedicated supported Linux server with capacity and patch ownership.
- [ ] PostgreSQL storage, retention and monitoring configured.
- [ ] TLS certificate and DNS configured; HTTP redirects to HTTPS.
- [ ] Secrets are randomly generated and stored outside repository.
- [ ] Production runtime validation passes.

## Database

- [ ] Alembic upgrade tested on a copy of production-sized data.
- [ ] Backup completed and checksum verified before migration.
- [ ] Restore drill meets approved recovery objectives.
- [ ] Database roles and network access follow least privilege.

## Security

- [ ] First admin created through controlled bootstrap and password rotated securely.
- [ ] Roles and permissions approved by process owners.
- [ ] No shared accounts; lockout and security events tested.
- [ ] Dependency, CodeQL and secret scans reviewed.
- [ ] Threat model and open risks accepted by accountable owner.

## Business control

- [ ] Chart of accounts, periods, sequences and posting profiles approved.
- [ ] Opening balances and inventory reconcile to source systems.
- [ ] Quote-to-Cash and Procure-to-Pay UAT passes.
- [ ] Financial statements, ageing and stock value reconcile.

## Operations

- [ ] Health/readiness monitoring and alerting configured.
- [ ] Backup schedule, retention and off-server copy configured.
- [ ] Incident, support, escalation and maintenance ownership assigned.
- [ ] Log retention protects sensitive information.

## Remaining GA blockers

MFA/SSO, mature segregation-of-duties enforcement, automated restore drills, concurrency/load testing, complete API authorization coverage, browser E2E coverage, formal upgrade compatibility testing, SBOM/signing, and production support SLA remain required for Core GA unless an accountable risk owner explicitly accepts a narrower pilot scope.
