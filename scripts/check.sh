#!/usr/bin/env bash
set -e
python -m compileall backend/app backend/tests backend/alembic
PYTHONPATH=backend python -m pytest backend/tests
find backend -type d -name __pycache__ -prune -exec rm -rf {} +
find backend -type f -name '*.pyc' -delete
rm -rf .pytest_cache
python scripts/repository_check.py
printf 'PeaOps v0.8.1 validation passed.\n'
