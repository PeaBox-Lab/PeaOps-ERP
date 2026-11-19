# PeaOps v0.8.2 — Code audit (2026-11-18)

Scope: backend (FastAPI/SQLAlchemy/security), frontend (React SPA), deployment (Docker/nginx/CI), data model, tests. Automated: bandit (0 issues at medium+ severity), npm audit (0), pytest (119 passing).

## Strengths
- Deny-by-default central policy middleware; route-level `require_permission` on mutations; explicit company-scoping everywhere
- PBKDF2 password hashing (310k iterations) with per-user salt; compare_digest; lockout after 5 failures; MFA (TOTP) support with encrypted-at-rest secret storage (nullable column, only stored when enabled)
- Signed JWT access tokens (HS256), refresh tokens stored **hashed** (SHA-256) with 7-day expiry and per-session revocation
- Maker-checker approvals with distinct-actor enforcement and optimistic version checks
- Alembic migrations; production runtime validation (HTTPS origins, Postgres, 32+ char secret); health/readiness probes; container runs as non-root `peaops`
- Money handled as Decimal(18,2); journal balance validation; idempotency keys on integration flows

## Issues found & fixed this pass

| # | Issue | Severity | Fix |
|---|---|---|---|
| 1 | **Frontend never refreshed access tokens** — after 15 min every call failed with "Token expired" | High (UX-breaking) | `api.ts`: proactive refresh 30s before expiry + retry-once-on-401 with single-flight refresh; unrecoverable → sign-out redirect. Verified live: forced-expired session reloads with KPIs intact |
| 2 | Web container healthcheck failure (`wget localhost/health` → refused) — nginx only listened on IPv4 while `localhost` resolves to ::1 | High (deploy-blocking) | `listen [::]:80/[::]:443` added to frontend + proxy nginx configs |
| 3 | Build context pulled `node_modules` / dev DBs into images | Medium | `.dockerignore` for frontend and backend |
| 4 | Test/tool deps (pytest, httpx) shipped in the production image | Medium (attack surface) | Split `requirements.txt` (runtime) and `requirements-dev.txt`; CI installs dev reqs |
| 5 | Legacy duplicate `/health` endpoint (unversioned, overlapping live/ready) | Low | Removed |
| 6 | Postgres connections could die on idle without pre-ping | Medium | `pool_pre_ping=True`, `pool_recycle=1800` |
| 7 | Frontend dead code: unused exports/types/state, unreachable JSON-editor fallback, stale "116 tests" copy | Low | Dead code removed; table status cells now use colored pills |
| 8 | `.gitignore` gaps for generated local artifacts | Low | Already covered — `.env`, `*.db`, `certs/`, `node_modules`, `dist/`, `backups/` |

## Open findings / deferred (prioritized)

| # | Finding | Severity | Recommendation |
|---|---|---|---|
| A | Refresh tokens not rotated on use; 7-day lifetime | Medium | Rotate refresh token on every refresh; revoke previous |
| B | Rate limiter is in-memory, per-process | Medium | Move to Redis for multi-replica; at minimum per-worker sticky LB |
| C | CORS `allow_methods=["*"]`, `allow_headers=["*"]` | Low | Restrict to `["GET","POST","PATCH","DELETE"]` and `["Authorization","Content-Type"]` |
| D | `/docs` and `/openapi.json` public in production | Low | `openapi_url=None` when `PEAOPS_ENVIRONMENT=production`, or gate behind admin permission |
| E | CSP not set; `Permissions-Policy` present, HSTS only on 443 | Low | Set `Content-Security-Policy` (see app.security.policy) |
| F | No automated E2E/browser tests in CI | Medium | Playwright suite: login → invoice → pay → KPI |
| G | SQLite dev vs Postgres prod parity (e.g. `ILIKE`, FOR UPDATE) | Low | Dev on Postgres in Docker; keep SQLite only for unit tests |
| H | DB files/backups unencrypted at rest; self-signed TLS for demos | Medium | LUKS/host encryption; Let's Encrypt + `certbot renew --deploy-hook "docker restart server-proxy-1"` |
| I | Single uvicorn worker | Low | `--workers $(nproc)` or gunicorn behind the Docker proxy; tune `db` pool |
| J | Error messages from endpoints can echo internal details in some 5xx paths | Low | Global exception handler mapping to generic 500 + request-id |
| K | Demo seed ships weak admin password | Low | `SEED_DEMO` only for local pilots; enforce password change on first login |
| L | No refresh-token revocation UI | Low | Settings → Sessions: list and revoke active sessions |

## Performance notes
- Indexes exist on all FK/constraint columns; UniqueConstraints per company keep lookups O(log n).
- Money never leaves Python as float — str(Decimal) everywhere.
- N+1 risk on list endpoints that iterate relationships — acceptable at pilot scale; add `selectinload` systematically as usage grows.
- Postgres `pg_stat_statements` recommended on the client VM.

## Deployment health (as delivered)
`docker-compose.production.yml` verified live: db healthy → migrate exit 0 → api healthy → web healthy → proxy on 80/443 serves SPA + `/api` with HTTP→HTTPS redirect, HSTS and TLS 1.2+.
