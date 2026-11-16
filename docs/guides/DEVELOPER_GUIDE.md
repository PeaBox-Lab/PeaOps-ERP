# Developer and Integration Engineer Guide

## Structure

`backend/app/domain` contains persistence models and pure rule modules. `backend/app/api` contains schemas and routes. `frontend/src` contains the current operator shell. Tests are grouped by accounting, finance, sales, procurement, inventory, integration and reporting rules.

## Contribution rules

- Keep business invariants in pure rule functions where practical.
- Preserve cumulative behavior and versioned documentation.
- Use database transactions for cross-module operations.
- Require idempotency for externally retried posting commands.
- Add tests for happy path, boundaries and rejected states.
- Do not silently create GL or stock effects from generic model hooks.

Run `bash scripts/check.sh` before packaging.
