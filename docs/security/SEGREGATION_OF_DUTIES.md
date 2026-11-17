
# Segregation of Duties - v0.8.1

## Implemented foundations

Role creation rejects selected incompatible permissions. High-risk approval records require a distinct requester and approver. Approval decisions include an expected version so stale concurrent decisions are rejected.

## High-risk actions represented

Journal posting, credit override, inventory adjustment, supplier-match override and role assignment.

## Required organizational design

Define makers, checkers, administrators, auditors and emergency access. Review role assignments periodically. Do not use `admin:*` for daily transaction processing.

## Remaining work

Approval records are a control foundation; business endpoints are not yet universally blocked pending approval. v0.8.x must bind each high-risk command to an approved record and add full SoD scenario tests before GA.
