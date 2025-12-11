@echo off
chcp 65001 >nul
echo ===================================
echo  YOLO-LLM Project Startup Script (Windows) - With Logging
echo ===================================

REM Initialize Logging System
echo Initializing Logging System...
cd /d "%~dp0"
if not exist "logs" mkdir logs
python -c "import sys, os, datetime; from pathlib import Path; logs_dir = Path('logs'); logs_dir.mkdir(exist_ok=True); timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S'); session_dir = logs_dir / f'session_{timestamp}'; session_dir.mkdir(exist_ok=True); [ (session_dir / m).mkdir(exist_ok=True) for m in ['backend', 'ai_service', 'mcp', 'agent', 'frontend'] ]; print(session_dir)" > temp_session_dir.txt
set /p LOG_DIR=<temp_session_dir.txt
del temp_session_dir.txt
echo [LOG] Session created: %LOG_DIR%

REM Set environment variables - modify according to your actual situation
set DB_URL=jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true^&characterEncoding=utf8^&serverTimezone=UTC
set DB_USER=root
set DB_PASS=Wangjiayi1

REM LLM API Keys (set your actual API Key)
set KIMI_API_KEY=%KIMI_API_KEY%
set QWEN_API_KEY=%QWEN_API_KEY%

REM MCP Tools API Keys (set your actual API Key)
set NEWS_API_KEY=%NEWS_API_KEY%
set WEATHER_API_KEY=%WEATHER_API_KEY%
set BREVO_API_KEY=%BREVO_API_KEY%

REM Check necessary environment variables
if "%NEWS_API_KEY%"=="" (
    echo [WARNING] NEWS_API_KEY not set, news feature will be unavailable
)
if "%WEATHER_API_KEY%"=="" (
    echo [WARNING] WEATHER_API_KEY not set, weather feature will be unavailable
)
if "%BREVO_API_KEY%"=="" (
    echo [WARNING] BREVO_API_KEY not set, email feature will be unavailable
)

echo.
echo Checking MySQL connection...
mysql -u %DB_USER% -p%DB_PASS% -e "USE yolo_platform;" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Unable to connect to MySQL database, please ensure:
    echo 1. MySQL service is started
    echo 2. Database yolo_platform is created
    echo 3. Username and password are correct
    echo.
    echo Continue starting other services? Database features will be unavailable ^(y/n^)
    set /p continue=
    if /i not "%continue%"=="y" (
        echo Aborting startup.
        exit /b 1
    )
) else (
    echo [SUCCESS] MySQL connection is normal
)

echo.
echo Starting Enhanced MCP Server (Port: 8083)...
cd /d "%~dp0mcp"
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt -q

echo [LOG] MCP logs will be saved to: %LOG_DIR%\mcp\

REM Start MCP Server with logging
start "YOLO-LLM New Modular MCP Server" cmd /c ".venv\Scripts\activate.bat && set NEWS_API_KEY=%NEWS_API_KEY% && set WEATHER_API_KEY=%WEATHER_API_KEY% && set BREVO_API_KEY=%BREVO_API_KEY% && cd mcp && python main.py > \"%LOG_DIR%\mcp\mcp_server.log\" 2>&1"
timeout /t 8 /nobreak

echo.
echo Starting Backend Service (Port: 8080)...
cd /d "%~dp0backend"

echo [LOG] Backend logs will be saved to: %LOG_DIR%\backend\

REM Start Backend with logging
start "YOLO-LLM Backend" cmd /c "set KIMI_API_KEY=%KIMI_API_KEY% && set QWEN_API_KEY=%QWEN_API_KEY% && set MCP_SERVER_URL=http://localhost:8083 && mvn spring-boot:run > \"%LOG_DIR%\backend\spring-boot.log\" 2>&1"
timeout /t 12 /nobreak

echo.
echo Starting AI Service (Port: 8000)...
cd /d "%~dp0ai"
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt -q

echo [LOG] AI Service logs will be saved to: %LOG_DIR%\ai_service\

REM Start AI Service with logging
start "YOLO-LLM AI Service" cmd /c ".venv\Scripts\activate.bat && uvicorn main:app --reload --host 127.0.0.1 --port 8000 > \"%LOG_DIR%\ai_service\fastapi.log\" 2>&1"
timeout /t 8 /nobreak

echo.
echo Starting Frontend Service (Port: 5173)...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install
)

echo [LOG] Frontend logs will be saved to: %LOG_DIR%\frontend\

REM Start Frontend with logging
start "YOLO-LLM Frontend" cmd /c "npm run dev > \"%LOG_DIR%\frontend\frontend.log\" 2>&1"
timeout /t 8 /nobreak

echo.
echo Installing Agent dependencies...
cd /d "%~dp0agent"
pip install -r requirements.txt -q

echo.
echo ===================================
echo       All Services Started Successfully
echo ===================================
echo.
echo Service URLs:
echo - Enhanced MCP Server: http://localhost:8083
echo - Backend API:         http://localhost:8080
echo - AI Service:          http://localhost:8000
echo - Frontend Web UI:     http://localhost:5173
echo.
echo Available MCP Tools:
echo - News Query:   POST http://localhost:8083/mcp/news
echo - Weather Query: POST http://localhost:8083/mcp/weather
echo - Email Send:   POST http://localhost:8083/mcp/email
echo - Computer Control: POST http://localhost:8083/mcp/computer_control
echo - Mouse Control:     POST http://localhost:8083/mcp/mouse_control
echo - Keyboard Control:  POST http://localhost:8083/mcp/keyboard_control
echo - Screen Control:    POST http://localhost:8083/mcp/screen_control
echo - File Operations:   POST http://localhost:8083/mcp/file_control
echo - Process Management: POST http://localhost:8083/mcp/process_control
echo - System Operations: POST http://localhost:8083/mcp/system_control
echo - Computer Stats:    POST http://localhost:8083/mcp/computer_stats
echo.
echo Agent Startup Options:
echo.
echo 1. Gesture + Voice Real-time Control (Recommended)
echo    python main.py --realtime
echo.
echo 2. Voice Only Control (Avoid dependency conflicts)
echo    python voice_simple_final.py
echo.
echo 3. Gesture Analysis Test
echo    python main.py --analyze-gesture
echo.
echo 4. Intelligent Chat Mode
echo    python main.py --chat
echo.
echo 5. Computer Control Test
echo    python ..\universal_computer_control.py
echo.
echo Auto start Voice Control Agent? (y/n)
set /p choice=
if /i "%choice%"=="y" (
    echo.
    echo Starting Voice Control Agent...
    cd /d "%~dp0agent"

    REM Get log directory
    for /f "delims=" %%i in ('python -c "from log_manager import LogManager; lm = LogManager(); print(lm.session_dir)"') do set LOG_DIR=%%i
    echo [LOG] Agent logs will be saved to: %LOG_DIR%\agent\

    REM Ensure log directory exists
    if not exist "%LOG_DIR%\agent" mkdir "%LOG_DIR%\agent"

    REM Start Agent with logging
    start "YOLO-LLM Voice Agent" cmd /c "python voice_simple_final.py > \"%LOG_DIR%\agent\agent.log\" 2>&1"
    timeout /t 3 /nobreak
    echo [SUCCESS] Voice Control Agent started
) else (
    echo.
    echo Agent not auto-started, you can manually choose any of the above modes
)

echo.
echo ===================================
echo Usage Instructions:
echo 1. Visit http://localhost:5173 to use Web Interface
echo 2. Stop all services by running: stop-all.bat
echo 3. Check service status at: http://localhost:8083/health
echo.
echo LOG MANAGEMENT:
echo - All logs are automatically saved to: %LOG_DIR%
echo - Quick view logs: view_logs.bat
echo - View errors: python log_reader.py -e
echo - Monitor logs: python log_reader.py --watch
echo ===================================

echo.
echo Press any key to close this window...
pause >nul