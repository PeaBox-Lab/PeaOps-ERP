@echo off
setlocal
cd /d "%~dp0"
if not exist backend\.env copy backend\.env.example backend\.env
if not exist frontend\node_modules call npm --prefix frontend install
start "PeaOps API" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"
start "PeaOps Web" cmd /k "cd frontend && npm run dev"
echo PeaOps starting: API http://localhost:8000  Web http://localhost:5173
endlocal