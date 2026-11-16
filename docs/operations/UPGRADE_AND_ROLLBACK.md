# Upgrade and Rollback Runbook

## Upgrade

Review release notes and migrations; test on a restored copy; announce maintenance; stop writes; take verified backup; deploy immutable release; run Alembic migration; validate readiness and critical business controls; reopen traffic; monitor.

## Rollback

Prefer forward correction. If rollback is authorized, stop writes, preserve failed-state evidence, restore the pre-upgrade database and prior application release together, validate, and communicate impact. Do not downgrade schema independently of data/application compatibility review.
