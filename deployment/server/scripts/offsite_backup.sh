#!/usr/bin/env sh
# Off-site PeaOps database backup + sha256 + push to S3-compatible storage.
# Usage:
#   S3_ENDPOINT=https://s3.ap-south-1.amazonaws.com \
#   S3_BUCKET=peaops-backups-client \
#   AWS_ACCESS_KEY_ID=... AWS_SECRET_ACCESS_KEY=... \
#   ./scripts/offsite_backup.sh
set -eu

: "${S3_ENDPOINT:?S3_ENDPOINT required}"

: "${S3_BUCKET:?S3_BUCKET required}"
: "${AWS_ACCESS_KEY_ID:?AWS_ACCESS_KEY_ID required}"
: "${AWS_SECRET_ACCESS_KEY:?AWS_SECRET_ACCESS_KEY required}"

DUMP="/backups/peaops-$(date -u +%Y%m%dT%H%M%SZ).dump"
SHA="${DUMP}.sha256"

echo "==> Dumping production database to $DUMP"
mkdir -p /backups
docker exec server-db-1 pg_dump -Fc -U peaops -d peaops -f "/tmp/$(basename "$DUMP")"
docker cp "server-db-1:/tmp/$(basename "$DUMP")" "$DUMP"
sha256sum "$DUMP" > "$SHA"

echo "==> Uploading to $S3_BUCKET"
if command -v aws >/dev/null 2>&1; then
  aws s3 cp "$DUMP" "s3://${S3_BUCKET}/backups/$(basename $DUMP)" --endpoint-url "$S3_ENDPOINT"
  aws s3 cp "$SHA"  "s3://${S3_BUCKET}/backups/$(basename $SHA)"  --endpoint-url "$S3_ENDPOINT"
else
  # fallback: rclone
  rclone copy "$DUMP" ":s3:${S3_BUCKET}/backups/" --s3-endpoint="$S3_ENDPOINT" --s3-access-key-id="$AWS_ACCESS_KEY_ID" --s3-secret-access-key="$AWS_SECRET_ACCESS_KEY"
  rclone copy "$SHA"  ":s3:${S3_BUCKET}/backups/" --s3-endpoint="$S3_ENDPOINT" --s3-access-key-id="$AWS_ACCESS_KEY_ID" --s3-secret-access-key="$AWS_SECRET_ACCESS_KEY"
fi

echo "==> Verifying remote object"
OBJECT="${S3_BUCKET}/backups/$(basename $DUMP)"
if command -v aws >/dev/null 2>&1; then
  aws s3 ls "s3://${OBJECT}" --endpoint-url "$S3_ENDPOINT" >/dev/null
else
  rclone lsf ":s3:${OBJECT}" --s3-endpoint="$S3_ENDPOINT" --s3-access-key-id="$AWS_ACCESS_KEY_ID" --s3-secret-access-key="$AWS_SECRET_ACCESS_KEY" >/dev/null
fi

echo "OFFSITE BACKUP PASSED: $DUMP"
