# On-Prem Server Deployment Guide

## Prerequisites

Supported Linux host, Docker Engine with Compose, DNS, TLS certificate files, restricted firewall and administrator access. Place certificate files under `deployment/server/certs` and create `.env.production` from the example.

## Deploy

1. Generate strong database and application secrets.
2. Run `deployment/server/scripts/preflight.sh` with environment loaded.
3. Run `make server-up`.
4. Confirm database, migration, API and proxy services are healthy.
5. Call `/api/v1/health/live` and `/api/v1/health/ready` through HTTPS.
6. Create company data through controlled setup, then run the bootstrap-admin script inside the API container.
7. Configure roles, sequences, posting profiles, policies and reports.

## Network

Expose only HTTPS through the reverse proxy. Database and API remain on the private Compose network. Restrict administrative shell and backup access.

## Production setting

Set `PEAOPS_ENVIRONMENT=production`, PostgreSQL URL, explicit HTTPS origins, a unique secret of at least 32 characters, and `PEAOPS_AUTO_CREATE_SCHEMA=false`.
