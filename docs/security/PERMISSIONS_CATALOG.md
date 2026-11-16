# Permissions Catalog

Permission names use `domain:action`; `domain:*` grants a domain and `admin:*` grants all current permissions.

Recommended domains: `admin`, `finance`, `sales`, `procurement`, `inventory`, `integration`, `reports`, `audit`, `support`.

Initial administrative APIs enforce `admin:users` and `admin:roles`. The production-readiness checklist treats complete endpoint authorization coverage and segregation-of-duties testing as a GA blocker.

Suggested roles: Company Administrator, Finance Administrator, Accountant, AR Clerk, AP Clerk, Sales User, Credit Manager, Buyer, Requester, Warehouse User, Inventory Controller, Manager/Analyst, Auditor (read-only), Support Analyst, Integration Operator.
