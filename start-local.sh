#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
[ -f backend/.env ] || cp backend/.env.example backend/.env
[ -d frontend/node_modules ] || (cd frontend && npm install)
(cd backend && python -m uvicorn app.main:app --reload --port 8000) &
(cd frontend && npm run dev) &
wait