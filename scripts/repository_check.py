from pathlib import Path
required=[
'LICENSE','NOTICE','CONTRIBUTING.md','CODE_OF_CONDUCT.md','SECURITY.md','GOVERNANCE.md','SUPPORT.md','.gitignore','.dockerignore','Makefile',
'.github/workflows/ci.yml','.github/workflows/security.yml','.github/workflows/release.yml','.github/dependabot.yml',
'backend/alembic.ini','backend/alembic/env.py','backend/alembic/versions/20261116_0001_baseline.py',
'deployment/server/docker-compose.production.yml','deployment/server/scripts/backup.sh','deployment/server/scripts/restore.sh','deployment/server/scripts/preflight.sh',
'docs/operations/PRODUCTION_READINESS_CHECKLIST.md','docs/security/THREAT_MODEL.md','docs/open-source/GITHUB_PUBLISHING_GUIDE.md']
missing=[x for x in required if not Path(x).is_file() or Path(x).stat().st_size==0]
if missing:raise SystemExit(f'Missing repository files: {missing}')
for path in Path('.').rglob('*'):
    if path.is_file() and (path.name=='.env' or path.suffix in {'.pyc'} or '__pycache__' in path.parts):raise SystemExit(f'Forbidden generated/secret file: {path}')
readme=Path('README.md').read_text()
for phrase in ['v0.8.1','Apache License 2.0','controlled-pilot']:
    if phrase not in readme:raise SystemExit(f'README missing {phrase}')
compose=Path('deployment/server/docker-compose.production.yml').read_text()
for service in ['db:','migrate:','api:','web:','proxy:']:
    if service not in compose:raise SystemExit(f'Production compose missing {service}')
print('Repository production/open-source checks passed.')
