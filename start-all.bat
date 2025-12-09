@echo off
echo ===================================
echo    YOLO-LLM 项目启动脚本 (Windows)
echo ===================================

REM 设置环境变量 - 请根据实际情况修改
set DB_URL=jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC
set DB_USER=root
set DB_PASS=Wangjiayi1
REM 请设置你的 LLM API Key
set KIMI_API_KEY=your_kimi_api_key_here
REM 或者使用 Qwen
REM set QWEN_API_KEY=your_qwen_api_key_here

echo.
echo 检查MySQL连接...
mysql -u %DB_USER% -p%DB_PASS% -e "USE yolo_platform;" 2>nul
if %errorlevel% neq 0 (
    echo [错误] 无法连接到MySQL数据库，请确保：
    echo 1. MySQL服务已启动
    echo 2. 数据库 yolo_platform 已创建
    echo 3. 用户名密码正确
    pause
    exit /b 1
)
echo [成功] MySQL连接正常

echo.
echo 启动MCP服务器 (端口: 8082)...
cd /d "%~dp0mcp"
if not exist ".venv" (
    echo 创建Python虚拟环境...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt -q
start "YOLO-LLM MCP Server" cmd /c ".venv\Scripts\activate.bat && set NEWS_API_KEY=%NEWS_API_KEY% && set WEATHER_API_KEY=%WEATHER_API_KEY% && set BREVO_API_KEY=%BREVO_API_KEY% && python real_mcp_server.py"
timeout /t 5 /nobreak

echo.
echo 启动后端服务 (端口: 8080)...
cd /d "%~dp0backend"
start "YOLO-LLM Backend" cmd /c "set MCP_SERVER_URL=http://localhost:8082 && mvn spring-boot:run"
timeout /t 10 /nobreak

echo.
echo 启动AI服务 (端口: 8000)...
cd /d "%~dp0ai"
if not exist ".venv" (
    echo 创建Python虚拟环境...
    python -m venv .venv
)
call .venv\Scripts\activate.bat
pip install -r requirements.txt -q
start "YOLO-LLM AI Service" cmd /c ".venv\Scripts\activate.bat && uvicorn main:app --reload --host 127.0.0.1 --port 8000"
timeout /t 5 /nobreak

echo.
echo 启动前端服务 (端口: 5173)...
cd /d "%~dp0frontend"
if not exist "node_modules" (
    echo 安装前端依赖...
    npm install
)
start "YOLO-LLM Frontend" cmd /c "npm run dev"
timeout /t 5 /nobreak

echo.
echo 安装Agent依赖...
cd /d "%~dp0agent"
pip install -r requirements.txt -q

echo.
echo ===================================
echo       所有服务启动完成
echo ===================================
echo MCP服务器: http://localhost:8082
echo 后端API: http://localhost:8080
echo AI服务:  http://localhost:8000
echo 前端界面: http://localhost:5173
echo.
echo 可用功能:
echo - 新闻查询: POST http://localhost:8082/mcp/news
echo - 天气查询: POST http://localhost:8082/mcp/weather
echo - 邮件发送: POST http://localhost:8082/mcp/email
echo - 高级电脑控制: POST http://localhost:8082/mcp/computer_control
echo.
echo Agent启动选项：
echo.
echo 1. 手势+语音实时控制 (推荐)
echo   python main.py --realtime
echo.
echo 2. 纯语音控制 (避免依赖冲突)
echo   python voice_simple_final.py
echo.
echo 3. 手势分析测试
echo   python main.py --analyze-gesture
echo.
echo 4. 智能对话模式
echo   python main.py --chat
echo.
echo 是否自动启动语音控制? (y/n)
set /p choice=
if /i "%choice%"=="y" (
    echo.
    echo 启动语音控制Agent...
    cd /d "%~dp0agent"
    start "YOLO-LLM Voice Agent" cmd /c "python voice_simple_final.py"
    timeout /t 3 /nobreak
    echo [成功] 语音控制Agent已启动
) else (
    echo.
    echo Agent未自动启动，您可以手动选择上述任一模式
)

echo.
echo 按任意键关闭此窗口...
pause >nul