@echo off
echo Starting YOLO-LLM Services (Direct PowerShell Launch)
echo =================================================

REM Force PowerShell execution for all services
start /min powershell -NoProfile -ExecutionPolicy Bypass -Command "& {$env:DB_USER='root'; $env:DB_PASS='Wangjiayi1'; cd /d %~dp0\ai; if (Test-Path .venv\Scripts\python.exe) { .venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload } else { python -m venv .venv; .venv\Scripts\pip.exe install -r requirements.txt; .venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload } }"

start /min powershell -NoProfile -ExecutionPolicy Bypass -Command "& {$env:DB_USER='root'; $env:DB_PASS='Wangjiayi1'; cd /d %~dp0\backend; mvn spring-boot:run }"

start /min powershell -NoProfile -ExecutionPolicy Bypass -Command "& { cd /d %~dp0\frontend; npm run dev }"

start powershell -NoProfile -ExecutionPolicy Bypass -Command "& {$env:DB_USER='root'; $env:DB_PASS='Wangjiayi1'; cd /d %~dp0\agent; if (Test-Path .venv\Scripts\python.exe) { .venv\Scripts\python.exe main.py --realtime } else { python -m venv .venv; .venv\Scripts\pip.exe install -r requirements.txt; .venv\Scripts\python.exe main.py --realtime } }"

echo.
echo All services started!
echo Frontend: http://localhost:5173
echo Backend:  http://localhost:8080
echo AI Service: http://localhost:8000
echo Agent: Real-time gesture detection
echo.
pause