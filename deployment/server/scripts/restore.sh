
#!/usr/bin/env sh
set -eu
if [ "$#" -ne 1 ]; then echo "Usage: restore.sh /backups/peaops-TIMESTAMP.dump" >&2; exit 2; fi
: "${POSTGRES_DB:=peaops}"; : "${POSTGRES_USER:=peaops}"
file="$1"; test -f "$file"; test -f "$file.sha256"; sha256sum -c "$file.sha256"
pg_restore --clean --if-exists --no-owner -U "$POSTGRES_USER" -d "$POSTGRES_DB" "$file"
