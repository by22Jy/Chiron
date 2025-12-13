@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    Stop YOLO-LLM All Services
echo ========================================
echo.

echo Stopping YOLO-LLM services...
echo.

REM Stop Python processes
echo [INFO] Stopping Python processes...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im pythonw.exe >nul 2>&1

REM Stop Node.js processes
echo [INFO] Stopping Node.js processes...
taskkill /f /im node.exe >nul 2>&1

REM Stop Java processes
echo [INFO] Stopping Java processes...
taskkill /f /im java.exe >nul 2>&1

REM Stop Maven processes
echo [INFO] Stopping Maven processes...
taskkill /f /im mvn.exe >nul 2>&1

REM Kill processes on specific ports
echo [INFO] Checking for processes on ports 8000, 8080, 8083, 5173...
netstat -ano | findstr ":8000" >nul
if %errorlevel% equ 0 (
    echo Found processes on port 8000, stopping them...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do (
        echo Stopping process on port 8000 (PID: %%a)
        taskkill /f /pid %%a >nul 2>&1
    )
)

netstat -ano | findstr ":8080" >nul
if %errorlevel% equ 0 (
    echo Found processes on port 8080, stopping them...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080"') do (
        echo Stopping process on port 8080 (PID: %%a)
        taskkill /f /pid %%a >nul 2>&1
    )
)

netstat -ano | findstr ":8083" >nul
if %errorlevel% equ 0 (
    echo Found processes on port 8083, stopping them...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8083"') do (
        echo Stopping process on port 8083 (PID: %%a)
        taskkill /f /pid %%a >nul 2>&1
    )
)

netstat -ano | findstr ":5173" >nul
if %errorlevel% equ 0 (
    echo Found processes on port 5173, stopping them...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":5173"') do (
        echo Stopping process on port 5173 (PID: %%a)
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo.
echo ========================================
echo    All Services Stopped!
echo ========================================
echo.

echo Service cleanup completed!
echo You can restart services with: start-all.bat
echo.
pause