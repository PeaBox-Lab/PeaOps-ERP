#!/usr/bin/env bash
set -e
python -m compileall backend/app backend/tests
PYTHONPATH=backend python -m pytest backend/tests
printf 'PeaOps v0.6 validation passed.\n'
