# PeaOps v0.8.2 Approval Binding Release Notes
## Purpose
Complete the next controlled-pilot hardening step by binding selected high-risk business commands to approved maker-checker records and fixing API runtime/import defects found during full source reconstruction.
## Added
- Exact approval-to-company, entity, entity ID and action binding.
- Mandatory approved record for journal posting.
- Mandatory approved record for credit-limit overrides.
- Mandatory approved record for manual inventory adjustments.
- Mandatory approved record for user-role assignment.
- Five approval-binding rule tests.
## Fixed
- API route module now imports `String` for integrated sales cost queries.
- Login route now explicitly imports `decode_access_token`.
- Saved-report parameter defaults use `Field(default_factory=dict)` to avoid mutable defaults.
## Compatibility
Journal posting now requires `approval_id` as a query parameter. Credit override and inventory adjustments require `approval_id` in the request when the high-risk path is used. User-role assignment requires `approval_id`.
## Classification
Controlled-pilot release, not Core GA. MFA/SSO, scalable rate limiting, PostgreSQL contention/load evidence, full API/browser E2E, automated off-site recovery drills, centralized observability and signed/SBOM releases remain GA work.
