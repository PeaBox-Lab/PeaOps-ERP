# Backup and Restore Runbook

## Backup

The database container mounts backup storage and read-only scripts. `backup.sh` creates a PostgreSQL custom-format dump, a SHA-256 file and deletes local backup files older than 30 days. Change retention to match policy and copy backups to protected off-server storage.

## Restore drill

1. Select a verified backup and checksum.
2. Restore into an isolated test database using `restore.sh`.
3. Run migrations if the application version requires them.
4. Validate company counts, journal totals, AR/AP, inventory balances, integration events and reports.
5. Record duration, issues and achieved recovery point/time.

## Production recovery

Declare incident ownership, stop writes, preserve evidence, select the authorized recovery point, restore, validate, obtain business approval, reopen access and document data loss if any.
