
# GitHub Publishing Guide

The package is repository-ready but has not been published.

1. Create the GitHub repository with the desired owner and `main` branch.
2. Replace placeholder repository links in `.github/ISSUE_TEMPLATE/config.yml`.
3. Copy `.github/CODEOWNERS.example` to `.github/CODEOWNERS` and replace owners.
4. Enable Discussions, Issues, private vulnerability reporting, Dependabot alerts and branch protection.
5. Require CI and Security workflows, signed-off commits and pull-request review.
6. Add repository description, topics, homepage and social preview.
7. Push source without `.env`, secrets, backups, certificates or customer data.
8. Create the `v0.8.0` tag only after release validation.
9. Review generated release assets and notes before publishing.

Suggested topics: `erp`, `fastapi`, `react`, `postgresql`, `accounting`, `inventory`, `procurement`, `open-source`.
