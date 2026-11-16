#!/usr/bin/env bash
set -e
python -m compileall backend/app backend/tests
printf 'PeaOps Python syntax check passed.\n'
