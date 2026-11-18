# Hosting PeaOps for clients — Windows & Linux

How to run PeaOps for one or more client companies, on either a Linux or a Windows VM, and how to keep it safe and operable. Everything here matches the production Docker stack shipped with the repository (`deployment/server/`).

## 1. Choose a tenancy model

| Model | Isolation | When to use | How |
|---|---|---|---|
| A. One VM per client | Strongest | Enterprise clients, strict data residency | Give each client their own VM + this compose stack |
| B. One instance, many companies | Shared DB, company-scoping | Small/medium clients OK with shared infra | Multi-company is built in (company_id everywhere). Seed each client company separately; users see only their company |
| C. One VM, isolated container stack per client | Strong, dense | Many small clients | Run N copies of `docker-compose.production.yml` with different ports/domains/DB volumes/secrets |
| D. SaaS (multi-tenant) | Cloud native | Larger scale | Roadmap v2.0 (`docs/ADVANCED_ROADMAP.md`) — Tenant model + provisioning endpoint already exist (`POST /api/v1/admin/tenants`) |

All models use the same codebase and DB migrations. For B, a client's users only ever see their `company_id`; every table is scoped by company_id, and the API enforces it.

## 2. Prerequisites (either OS)

- VM: 2 vCPU / 4 GB RAM / 40 GB disk (heavier for busy companies)
- A domain name (e.g. `erp.clientcorp.com`) pointing at the VM
- Ports 80/443 open; SSH restricted (or RDP/SSH on non-standard port)
- Docker + Docker Compose plugin
- For Linux: `curl`, `git`, `ufw` or cloud firewall

## 3. Linux VM quick start (recommended)

Tested on Ubuntu 22.04/24.04.

```bash
# 1. Update and install Docker
sudo apt-get update
sudo apt-get install -y git curl ufw docker.io docker-compose-v2
sudo systemctl enable --now docker

# 2. Firewall
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw --force enable

# 3. Get the code (or copy the folder)
git clone <your-peaops-repo-url> peaops && cd peaops/deployment/server

# 4. Configure and start (fills in secrets + certs automatically)
./install.sh            # Ubuntu installer (creates .env, certs, builds, seeds demo, starts stack)
# or manual: cp .env.example .env && edit .env, then docker compose -f docker-compose.production.yml up -d
```

The stack: Postgres 16 (internal) → `migrate` (Alembic upgrade head) → `api` (FastAPI/uvicorn) → `web` (nginx + SPA) → `proxy` (TLS termination, 80→443 redirect).

Verify:

```bash
docker compose -f docker-compose.production.yml ps
curl -k https://localhost/api/v1/health/ready   # {"status":"ready","database":"ok"}
```

### TLS certificates
- Demo/local: `./install.sh` generates a self-signed cert (browser warning expected).
- Production: point DNS at the VM, then:
  ```bash
  sudo apt-get install -y certbot
  sudo certbot certonly --standalone -d erp.clientcorp.com
  sudo cp /etc/letsencrypt/live/erp.clientcorp.com/{fullchain.pem,privkey.pem} deployment/server/certs/
  ```
  Renew: `sudo certbot renew --deploy-hook "docker restart server-proxy-1"`, or use a cron.

### Backups
`scripts/backup.sh` (pg_dump -Fc + sha256, 30-day retention). Schedule:

```bash
sudo crontab -e
# nightly 02:00
0 2 * * * cd /home/you/peaops/deployment/server && POSTGRES_PASSWORD=$(grep POSTGRES_PASSWORD .env | cut -d= -f2) ./scripts/backup.sh >> /var/log/peaops-backup.log 2>&1
```

Test restore monthly with `scripts/restore.sh`. Off-site copy: rsync/S3/B2 the `backups/` folder out of the VM.

### Upgrades
`docker compose pull`, `docker compose build`, `docker compose up -d` — migrations run automatically via the `migrate` service. Rollback: `docs/operations/UPGRADE_AND_ROLLBACK.md`.

## 4. Windows Server VM (2019/2022/2025)

Two paths:

### 4a. Docker Desktop / WSL2 (recommended)
Mirrors the Linux path closely:

```powershell
# 1. Install Docker Desktop (WSL2 backend required)
winget install -e --id Docker.DockerDesktop
# reboot, sign in to Docker Desktop once

# 2. Firewall (elevated PowerShell)
New-NetFirewallRule -DisplayName "PeaOps HTTPS" -Direction Inbound -LocalPort 443 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "PeaOps HTTP"  -Direction Inbound -LocalPort 80  -Protocol TCP -Action Allow

# 3. Get the code
git clone <your-peaops-repo-url> C:\peaops; cd C:\peaops\deployment\server

# 4. Install & start
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

`install.ps1` generates secrets (`.env`), a self-signed cert, builds the images and starts the stack — identical to Linux. For HTTPS without the warning, use `win-acme` (`wacs.exe`) to obtain a Let's Encrypt cert, copy `fullchain.pem`/`privkey.pem` into `deployment/server/certs/`, restart `server-proxy-1`.

### 4b. Native Windows (no Docker)
More manual but no Docker needed:

```powershell
# 1. Prereqs
winget install -e --id PostgreSQL.PostgreSQL.16   # accept defaults, note the superuser password
winget install -e --id Python.Python.3.12
winget install -e --id Nginx.Nginx                # or use IIS as reverse proxy
# Node.js 20+ for the frontend build: winget install -e --id OpenJS.NodeJS.LTS

# 2. Backend
python -m venv C:\peaops\venv
C:\peaops\venv\Scripts\Activate.ps1
pip install -r C:\peaops\backend\requirements.txt
setx PEAOPS_ENVIRONMENT production /M
setx PEAOPS_DATABASE_URL "postgresql+psycopg://postgres:secret@localhost:5432/peaops" /M
setx PEAOPS_SECRET_KEY "<64+ random chars>" /M
setx PEAOPS_ALLOWED_ORIGINS "https://erp.clientcorp.com" /M
alembic -c C:\peaops\backend\alembic.ini upgrade head
python C:\peaops\backend\scripts_bootstrap_admin.py
uvicorn app.main:app --host 0.0.0.0 --port 8000 --loop uvloop

# 3. Frontend: build once and serve via IIS/nginx proxying /api to :8000
cd C:\peaops\frontend; npm install; npm run build
# IIS: serve dist\ as website on 443 with URL Rewrite → http://localhost:8000 for /api
```

Wrap uvicorn and the DB as services with NSSM or `pm2-service-studio` so they survive reboots. Honestly: 4a is less painful — prefer it.

## 5. Onboarding a client (one instance, model B)

1. **Create the company**: `POST /api/v1/companies` `{"code":"ACME","name":"Acme Pvt Ltd","base_currency":"INR"}` with an admin token, or SQL/Alembic for a fresh DB.
2. **Bootstrap the first admin**: `python backend/scripts_bootstrap_admin.py` — prompts for company code/username/password; grants `company_admin`.
3. **Create roles & users**: `POST /admin/users`, `POST /admin/roles`, `POST /admin/users/{id}/roles` (role assignment needs an approved maker-checker record in production).
4. **Seed master data**: accounts (COA), parties, items, warehouses, fiscal period, number sequences (ar_invoice, sales_order, etc.).
5. **Hand over**: give the client the URL, their company ID, the admin credentials (force change on first use), `docs/help/HELP_TOPICS.md`, and `docs/USER_GUIDE.md`.
6. **Verify**: login, create a quote, send it, convert to order, post an invoice, receive a payment — each must succeed.

Per-client isolated stacks (model C): copy `deployment/server` per client, edit `.env` (different `POSTGRES_DB`/ports), run one compose project each: `docker compose -p client-a -f docker-compose.production.yml up -d`.

## 6. Production checklist for client go-live

- [ ] Real TLS certificate installed (not the self-signed demo cert)
- [ ] `PEAOPS_SECRET_KEY` ≥ 32 random chars; `POSTGRES_PASSWORD` rotated from example
- [ ] `PEAOPS_ALLOWED_ORIGINS` = client's exact HTTPS origin
- [ ] Backup cron verified + restore drill done
- [ ] Admin password changed by client; MFA enabled for admins
- [ ] Demo company/data removed if a clean client build
- [ ] Monitoring: `/api/v1/health/ready` + `/metrics/prometheus` scraped (Uptime Kuma, Prometheus+Grafana)
- [ ] Update path agreed: who applies upgrades, how often
- [ ] Logs: container logs rotated (`docker compose logs` / journald)

## 7. Security & compliance notes

- Apache-2.0: you may self-host for clients without publishing your UX customizations.
- Data residency: model A/B keeps data on the client's VM; model C on your infra; model D is cloud.
- Audit: every mutation is captured (`audit_events`, `security_events`, approval records).
- Hardening: firewall closed to only 80/443/SSH, DB never exposed, strong password policy (12+ chars, symbol), optional MFA for everyone.
- Do not put secrets in the repo — `.env` and `certs/` are git-ignored.

## 8. Troubleshooting

See `docs/help/HELP_TOPICS.md#deployment--server`, or check `docker compose ps` / `logs`. The single most common fix is `docker compose restart api` after configuration changes.
