# PeaOps installer for Windows Server / Windows 10-11 VMs.
# Run elevated: powershell -ExecutionPolicy Bypass -File .\install.ps1
# Options: -SeedDemo  (creates demo company ACME + admin / Admin@123456 - change it!)
#          -SiteDomain erp.clientcorp.com
param(
  [switch]$SeedDemo,
  [string]$SiteDomain = "localhost"
)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here

Write-Host "==> Checking Docker Desktop"
$docker = "$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe"
if (-not (Get-Command docker -ErrorAction SilentlyContinue) -and -not (Test-Path $docker)) {
  Write-Host "==> Installing Docker Desktop via winget"
  winget install -e --id Docker.DockerDesktop --accept-source-agreements --accept-package-agreements
  Write-Host "==> Launch Docker Desktop once to finish setup, then re-run this script."
  Start-Process "shell:AppsFolder\Docker.DockerForWindows.Settings"
  exit 0
}
$env:Path = "$env:ProgramFiles\Docker\Docker\resources\bin;$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin;$env:Path"
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { $env:Path = "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin;$env:Path" }

Write-Host "==> Generating .env (if missing)"
if (-not (Test-Path .env)) {
  $pg = [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Max 256 }))
  $sk = [Convert]::ToBase64String((1..48 | ForEach-Object { Get-Random -Max 256 }))
  @(
    "POSTGRES_DB=peaops",
    "POSTGRES_USER=peaops",
    "POSTGRES_PASSWORD=$pg",
    "PEAOPS_SECRET_KEY=$sk",
    "PEAOPS_ALLOWED_ORIGINS=https://$SiteDomain",
    "PEAOPS_ACCESS_TOKEN_MINUTES=15"
  ) | Set-Content .env -Encoding UTF8
  Write-Host ".env created (secrets are git-ignored)."
}

Write-Host "==> Generating self-signed certs (if missing)"
if (-not (Test-Path certs\fullchain.pem)) {
  New-Item -ItemType Directory -Force certs | Out-Null
  python "$here\scripts\gen_self_signed_cert.py" $SiteDomain
  if ($LASTEXITCODE -ne 0) { throw "Failed to generate certs (need Python + cryptography installed)." }
  Write-Host "certs/ created (self-signed - replace with a real cert for production)."
}

Write-Host "==> Preflight"
sh scripts/preflight.sh

Write-Host "==> Building and starting the stack"
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d

if ($SeedDemo) {
  Write-Host "==> Seeding demo company + admin"
  docker compose -f docker-compose.production.yml cp scripts/seed_pilot_demo.py api:/tmp/seed_pilot_demo.py
  docker compose -f docker-compose.production.yml exec -T -e PYTHONPATH=/app api python /tmp/seed_pilot_demo.py
}

Write-Host ""
Write-Host "PeaOps is up at https://$SiteDomain/  (demo seed: company 1 / admin / Admin@123456 - change it!)"
Write-Host "Verify: curl -k https://localhost/api/v1/health/ready"
Write-Host "Logs:   docker compose -f docker-compose.production.yml logs -f"