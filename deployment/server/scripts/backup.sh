
#!/usr/bin/env sh
set -eu
: "${POSTGRES_DB:=peaops}"; : "${POSTGRES_USER:=peaops}"; : "${BACKUP_DIR:=/backups}"
mkdir -p "$BACKUP_DIR"
file="$BACKUP_DIR/peaops-$(date -u +%Y%m%dT%H%M%SZ).dump"
pg_dump -Fc -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f "$file"
sha256sum "$file" > "$file.sha256"
find "$BACKUP_DIR" -type f -name 'peaops-*.dump*' -mtime +30 -delete
printf '%s\n' "$file"
