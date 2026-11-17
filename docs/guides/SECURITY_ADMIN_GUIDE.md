
# Security Administrator Guide

Create individual users, approved roles and least-privilege permissions. Review failed logins, lockouts, role assignments and security events. Protect the application secret and database credentials. Coordinate vulnerability handling, dependency alerts and periodic access reviews.

v0.8 supports password authentication and RBAC foundations. MFA/SSO, session revocation, full endpoint authorization and formal segregation-of-duties enforcement remain required for GA.

## v0.8.2
Role assignment is now a bound maker-checker action. Create an approval for the exact user and `role_assignment`, obtain a distinct checker decision, then pass the approval ID when assigning the role.
