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
$dockerCandidates = @(
  "$env:ProgramFiles\Docker\Docker\resources\bin\docker.exe",
  "$env:LOCALAPPDATA\Programs\DockerDesktop\resources\bin\docker.exe"
)
$docker = $dockerCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
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

Write-Host "==> Selecting proxy ports"
$envLines = Get-Content .env
$needHTTP = -not ($envLines -match '^HTTP_PORT=')
$needHTTPS = -not ($envLines -match '^HTTPS_PORT=')
if ($needHTTP -and $needHTTPS) {
  # Port 80 is usually taken by Windows/WSL on dev boxes; use 8080/8443 locally
  Add-Content .env "HTTP_PORT=8080"
  Add-Content .env "HTTPS_PORT=8443"
}
$envLines = Get-Content .env
$httpPort = ($envLines -match '^HTTP_PORT=' | Select-Object -First 1) -replace '^HTTP_PORT=', ''
$httpsPort = ($envLines -match '^HTTPS_PORT=' | Select-Object -First 1) -replace '^HTTPS_PORT=', ''
Write-Host "Proxy ports: HTTP=$httpPort  HTTPS=$httpsPort"

Write-Host "==> Generating self-signed certs (if missing)"
if (-not (Test-Path certs\fullchain.pem)) {
  New-Item -ItemType Directory -Force certs | Out-Null
  python "$here\scripts\gen_self_signed_cert.py" $SiteDomain
  if ($LASTEXITCODE -ne 0) { throw "Failed to generate certs (need Python + cryptography installed)." }
  Write-Host "certs/ created (self-signed - replace with a real cert for production)."
}

Write-Host "==> Preflight"
$envContent = Get-Content .env -Raw
foreach ($name in @("POSTGRES_PASSWORD","PEAOPS_SECRET_KEY","PEAOPS_ALLOWED_ORIGINS")) {
  if ($envContent -notmatch "(?m)^$name=\S") { throw "$name is required in .env" }
}
if ($envContent -notmatch '(?m)^PEAOPS_SECRET_KEY=.{32,}') { throw "PEAOPS_SECRET_KEY must be at least 32 characters" }
if ($envContent -notmatch '(?m)^PEAOPS_ALLOWED_ORIGINS=https://') { throw "PEAOPS_ALLOWED_ORIGINS must start with https://" }
if (-not (Get-Command docker -ErrorAction SilentlyContinue) -and -not (Test-Path $docker)) { throw "docker CLI not found" }
Write-Host "PeaOps server preflight passed."

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