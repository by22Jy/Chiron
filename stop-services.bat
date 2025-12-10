@echo off
echo Stopping all YOLO-LLM services...

echo.
echo Stopping MCP Server (8083)...
for /f "tokens=2" %%i in ('tasklist /fi "imagename eq python.exe" /fo table /nh ^| findstr "python.exe"') do taskkill /PID %%i /F 2>nul

echo.
echo Stopping AI Service (8000)...
for /f "tokens=2" %%i in ('netstat -ano ^| findstr ":8000"') do taskkill /PID %%i /F 2>nul

echo.
echo Stopping Backend Service (8080)...
for /f "tokens=2" %%i in ('netstat -ano ^| findstr ":8080"') do taskkill /PID %%i /F 2>nul

echo.
echo Stopping Frontend Service (5173)...
for /f "tokens=2" %%i in ('netstat -ano ^| findstr ":5173"') do taskkill /PID %%i /F 2>nul

echo.
echo Stopping Agent services...
taskkill /f /im python.exe /t 2>nul
taskkill /f /im node.exe /t 2>nul
taskkill /f /im java.exe /t 2>nul

echo.
echo All services stopped!
pause