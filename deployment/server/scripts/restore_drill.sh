#!/usr/bin/env bash
# PeaOps restore drill — proves backups actually restore.
# Usage:  POSTGRES_USER=peaops POSTGRES_DB=peaops ./scripts/restore_drill.sh
set -euo pipefail
: "${POSTGRES_USER:=peaops}"
: "${POSTGRES_DB:=peaops}"
DUMP="/tmp/peaops-drill-$(date +%Y%m%d%H%M%S).dump"

echo "==> 1/5 Creating temp restore database"
docker exec server-db-1 psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE IF EXISTS peaops_restore_test"
docker exec server-db-1 psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE peaops_restore_test"

echo "==> 2/5 Dumping production database to $DUMP"
docker exec server-db-1 pg_dump -Fc -U "$POSTGRES_USER" -d "$POSTGRES_DB" > "$DUMP"
sha256sum "$DUMP"

echo "==> 3/5 Restoring into peaops_restore_test"
docker exec -i server-db-1 pg_restore -U "$POSTGRES_USER" -d peaops_restore_test --no-owner --no-privileges < "$DUMP"

echo "==> 4/5 Sanity checks"
docker exec server-db-1 psql -U "$POSTGRES_USER" -d peaops_restore_test -c "SELECT 'companies', count(*) FROM companies"
docker exec server-db-1 psql -U "$POSTGRES_USER" -d peaops_restore_test -c "SELECT 'items', count(*) FROM items"
docker exec server-db-1 psql -U "$POSTGRES_USER" -d peaops_restore_test -c "SELECT 'users', count(*) FROM users"
docker exec server-db-1 psql -U "$POSTGRES_USER" -d peaops_restore_test -c "SELECT 'invoices', count(*) FROM invoices"

echo "==> 5/5 Cleanup"
docker exec server-db-1 psql -U "$POSTGRES_USER" -d postgres -c "DROP DATABASE peaops_restore_test"
rm -f "$DUMP"
echo "RESTORE DRILL PASSED"