#!/usr/bin/env sh
set -eu
for name in POSTGRES_PASSWORD PEAOPS_SECRET_KEY PEAOPS_ALLOWED_ORIGINS; do eval value="\${$name:-}"; [ -n "$value" ] || { echo "$name is required" >&2; exit 1; }; done
[ "${#PEAOPS_SECRET_KEY}" -ge 32 ] || { echo "PEAOPS_SECRET_KEY must be at least 32 characters" >&2; exit 1; }
case "$PEAOPS_ALLOWED_ORIGINS" in https://*) ;; *) echo "PEAOPS_ALLOWED_ORIGINS must use HTTPS" >&2; exit 1;; esac
command -v docker >/dev/null
printf 'PeaOps server preflight passed.\n'
