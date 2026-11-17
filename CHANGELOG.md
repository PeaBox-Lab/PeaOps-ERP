
# Changelog

## 0.8.1 - 2026-11-16
### Added
- Central deny-by-default route authorization policy.
- Revocable refresh sessions and logout.
- Maker-checker approval records and selected SoD conflicts.
- Optimistic approval version checks.
- Pilot operations, session/access and SoD guides.
- 16 pilot-hardening tests.
### Changed
- Product/API/frontend version advanced to 0.8.1.
- Controlled-pilot access posture strengthened.


## 0.8.0 - 2026-11-16
### Added
- User, role, permission, user-role and security-event models.
- Password policy, PBKDF2 hashing, signed expiring access tokens and lockout.
- Protected administration APIs and production runtime validation.
- Alembic migration baseline and production migration job.
- Liveness/readiness endpoints and request/security headers.
- On-prem production Docker stack with PostgreSQL, web, API and TLS proxy.
- Backup, checksum, restore, preflight and bootstrap-admin tooling.
- Apache-2.0 license, notice and complete GitHub community/governance files.
- CI, migration smoke test, CodeQL, dependency review, Dependabot and release workflows.
- Production, security, database, incident, maintenance, upgrade and publishing guides.
- Security, operations and open-source user stories.
### Changed
- Product/API/frontend version advanced to 0.8.0.
- Production schema ownership moves from automatic creation to Alembic.
- Release classified as controlled-pilot candidate, not GA.

## 0.7.0 - 2026-11-16
### Added
- Insight, statements, KPIs, reports, exports, data quality and complete documentation suite.
## 0.6.0 - 2026-11-16
### Added
- Idempotent integration, trace, delivery, matching and GL posting.
## 0.5.0 - 2026-11-16
### Added
- Inventory ledger, balances, valuation, transfers and reorder.
## 0.4.0 - 2026-11-16
### Added
- Procurement request-to-receipt.
## 0.3.0 - 2026-11-16
### Added
- Sales quote-to-order and credit controls.
## 0.2.0 - 2026-11-16
### Added
- Finance AR/AP and ageing.
## 0.1.0 - 2026-11-16
### Added
- ERP foundation and GL.
## 0.8.2 - 2026-11-17
### Added
- Exact approval binding for four high-risk business/admin actions.
- Approval-binding security guide and four cumulative user stories.
- Five approval-binding rule tests.
### Fixed
- Missing API imports used by authentication and integrated sales posting.
- Mutable report-parameter defaults.
### Changed
- Product/API/frontend version advanced to 0.8.2.
