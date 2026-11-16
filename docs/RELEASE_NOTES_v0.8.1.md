# PeaOps v0.8.1 Pilot Hardening Release Notes

## Purpose

Reduce the highest-risk controlled-pilot gaps in v0.8.0 without claiming Core GA.

## Added

- Central route-permission policy protecting reads and writes by default.
- Refresh sessions with hashed refresh tokens, expiry and logout revocation.
- Approval records for journal posting, credit override, inventory adjustment, supplier-match override and role assignment.
- Maker-checker validation that prevents requesters approving their own high-risk actions.
- Incompatible role-permission checks for selected segregation conflicts.
- Optimistic version checks for approval decisions.
- New hardening tests for route policy, SoD, concurrency and refresh-token behavior.

## Pilot limitation

The centralized policy provides broad protection, but domain-specific permission granularity and complete API integration/E2E testing still require further v0.8.x hardening. MFA/SSO and production-scale concurrency testing remain GA blockers.
