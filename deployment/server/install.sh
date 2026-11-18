#!/usr/bin/env sh
# PeaOps Ubuntu VM installer: installs Docker, configures .env + TLS certs,
# builds and starts the production stack, optionally seeds the demo company.
# Usage:
#   sudo SITE_DOMAIN=erp.clientcorp.com ./install.sh
#   sudo SEED_DEMO=true ./install.sh            # demo company + admin (change creds!)
set -eu

SITE_DOMAIN="${SITE_DOMAIN:-localhost}"
SEED_DEMO="${SEED_DEMO:-false}"
cd "$(dirname "$0")"

echo "==> Installing Docker (if missing)"
if ! command -v docker >/dev/null 2>&1; then
  apt-get update
  apt-get install -y docker.io docker-compose-v2 curl openssl
fi
systemctl enable --now docker || true

echo "==> Generating .env (if missing)"
if [ ! -f .env ]; then
  POSTGRES_PASSWORD=$(openssl rand -base64 32)
  PEAOPS_SECRET_KEY=$(openssl rand -base64 48)
  ORIGIN="${PEAOPS_ALLOWED_ORIGINS:-https://$SITE_DOMAIN}"
  cat > .env <<EOF
POSTGRES_DB=peaops
POSTGRES_USER=peaops
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
PEAOPS_SECRET_KEY=$PEAOPS_SECRET_KEY
PEAOPS_ALLOWED_ORIGINS=$ORIGIN
PEAOPS_ACCESS_TOKEN_MINUTES=15
EOF
  echo "Written .env (secrets are git-ignored)."
fi

echo "==> Generating self-signed TLS certs (if missing)"
if [ ! -f certs/fullchain.pem ]; then
  mkdir -p certs
  openssl req -x509 -nodes -newkey rsa:2048 -days 825 \
    -subj "/CN=$SITE_DOMAIN" -addext "subjectAltName=DNS:$SITE_DOMAIN,IP:127.0.0.1" \
    -keyout certs/privkey.pem -out certs/fullchain.pem
  echo "Written certs/ (self-signed — replace with Let's Encrypt for production)."
fi

echo "==> Preflight"
sh scripts/preflight.sh

echo "==> Building and starting the stack"
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d

echo "==> Waiting for the API to become healthy"
for i in $(seq 1 45); do
  code=$(curl -sk -o /dev/null -w '%{http_code}' https://localhost/api/v1/health/ready || true)
  [ "$code" = "200" ] && break
  sleep 3
done

if [ "$SEED_DEMO" = "true" ]; then
  echo "==> Seeding demo company + admin (change the password after first login)"
  docker compose -f docker-compose.production.yml cp scripts/seed_pilot_demo.py api:/tmp/seed_pilot_demo.py
  docker compose -f docker-compose.production.yml exec -T -e PYTHONPATH=/app api python /tmp/seed_pilot_demo.py
fi

echo ""
echo "PeaOps is up at https://$SITE_DOMAIN/"
echo "Checks: curl -k https://localhost/api/v1/health/ready"
echo "Logs:   docker compose -f docker-compose.production.yml logs -f"
echo "Backups:  $(pwd)/scripts/backup.sh   (schedule with cron: 0 2 * * *)"
