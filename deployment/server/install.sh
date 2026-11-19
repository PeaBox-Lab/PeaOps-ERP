#!/usr/bin/env sh
# PeaOps VM installer (Ubuntu). Production-ready defaults.
# Usage:
#   sudo SITE_DOMAIN=erp.clientcorp.com ./install.sh
#   sudo SEED_DEMO=true SITE_DOMAIN=erp.clientcorp.com ./install.sh

set -eu

SITE_DOMAIN="${SITE_DOMAIN:-localhost}"
SEED_DEMO="${SEED_DEMO:-false}"
CDN_ORIGIN="${PEAOPS_ALLOWED_ORIGINS:-https://$SITE_DOMAIN}"
cd "$(dirname "$0")"

echo "==> [1/8] Docker"
if ! command -v docker >/dev/null 2>&1; then
  apt-get update
  apt-get install -y docker.io docker-compose-v2 curl openssl certbot
fi
systemctl enable --now docker || true

echo "==> [2/8] .env"
if [ ! -f .env ]; then
  POSTGRES_PASSWORD=$(openssl rand -base64 32)
  PEAOPS_SECRET_KEY=$(openssl rand -base64 48)
  cat > .env <<EOF
POSTGRES_DB=peaops
POSTGRES_USER=peaops
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
PEAOPS_SECRET_KEY=$PEAOPS_SECRET_KEY
PEAOPS_ALLOWED_ORIGINS=$CDN_ORIGIN
PEAOPS_ACCESS_TOKEN_MINUTES=15
HTTP_PORT=80
HTTPS_PORT=443
EOF
  echo "Written .env."
fi

echo "==> [3/8] TLS certs"
if [ "$SITE_DOMAIN" != "localhost" ] && [ ! -f certs/fullchain.pem ]; then
  echo "Domain is $SITE_DOMAIN; requesting Let's Encrypt cert"
  apt-get update && apt-get install -y certbot || true
  if command -v certbot >/dev/null 2>&1; then
    certbot certonly --standalone -d "$SITE_DOMAIN" --agree-tos --non-interactive --email admin@"$SITE_DOMAIN" || true
    cp "/etc/letsencrypt/live/$SITE_DOMAIN/{fullchain.pem,privkey.pem}" certs/ 2>/dev/null || true
  fi
fi

if [ ! -f certs/fullchain.pem ]; then
  mkdir -p certs
  openssl req -x509 -nodes -newkey rsa:2048 -days 825 \
    -subj "/CN=$SITE_DOMAIN" -addext "subjectAltName=DNS:$SITE_DOMAIN,IP:127.0.0.1" \
    -keyout certs/privkey.pem -out certs/fullchain.pem
  echo "Self-signed cert at certs/ (replace with real cert before going live)"
fi

echo "==> [4/8] Preflight"
sh scripts/preflight.sh

echo "==> [5/8] Build & start"
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d

echo "==> [6/8] Wait for API"
for i in $(seq 1 45); do
  code=$(curl -sk -o /dev/null -w '%{http_code}' https://localhost/api/v1/health/ready || true)
  [ "$code" = "200" ] && break
  sleep 3
done
code=$(curl -sk -o /dev/null -w '%{http_code}' https://localhost/api/v1/health/ready || true)
echo "Health endpoint returned $code"

if [ "$SEED_DEMO" = "true" ]; then
  echo "==> [7/8] Seed demo company + admin"
  docker compose -f docker-compose.production.yml cp scripts/seed_pilot_demo.py api:/tmp/seed_pilot_demo.py
  docker compose -f docker-compose.production.yml exec -T -e PYTHONPATH=/app api python /tmp/seed_pilot_demo.py
fi

echo "==> [8/8] Done"
echo "PeaOps is up at https://$SITE_DOMAIN/"
echo "Verify: curl -k https://localhost/api/v1/health/ready"
echo "Logs:   docker compose -f docker-compose.production.yml logs -f"
echo "Reset password: docker compose -f docker-compose.production.yml exec api scripts_bootstrap_admin.py"
