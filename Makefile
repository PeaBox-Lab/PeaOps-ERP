.PHONY: check test migrate server-up server-down backup
check:
	bash scripts/check.sh
test:
	PYTHONPATH=backend python -m pytest backend/tests
migrate:
	cd backend && alembic -c alembic.ini upgrade head
server-up:
	docker compose --env-file deployment/server/.env.production -f deployment/server/docker-compose.production.yml up -d --build
server-down:
	docker compose --env-file deployment/server/.env.production -f deployment/server/docker-compose.production.yml down
backup:
	docker compose --env-file deployment/server/.env.production -f deployment/server/docker-compose.production.yml exec db /opt/peaops/scripts/backup.sh
