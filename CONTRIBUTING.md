# Contributing to PeaOps

Thank you for helping build an open, reliable ERP platform.

## Before contributing

Read the architecture, developer guide, security policy, roadmap and user stories. Search open issues before creating a duplicate. Use discussions for design proposals and issues for actionable defects/features.

## Development workflow

1. Fork and create a focused branch.
2. Add or update user stories and acceptance criteria for behavioral changes.
3. Keep business invariants in pure rule modules where practical.
4. Add tests for success, boundaries and rejection paths.
5. Update role/module documentation and changelog.
6. Run `bash scripts/check.sh`.
7. Open a pull request using the template.

## Pull-request expectations

Small coherent scope; no secrets or customer data; migrations for schema changes; compatibility/migration notes; security impact; screenshots for UI changes; evidence of tests and documentation.

## Developer Certificate of Origin

By contributing, you certify that you have the right to submit the contribution under the Apache-2.0 license. Sign commits with `git commit -s`.
