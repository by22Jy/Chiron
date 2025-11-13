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
echo 启动后端服务 (端口: 8080)...
cd /d "%~dp0backend"
start "YOLO-LLM Backend" cmd /c "mvn spring-boot:run"
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
echo ===================================
echo       所有服务启动完成
echo ===================================
echo 后端API: http://localhost:8080
echo AI服务:  http://localhost:8000
echo 前端界面: http://localhost:5173
echo.
echo Agent手动启动命令：
echo   cd agent
echo   pip install -r requirements.txt
echo   python main.py --realtime
echo.
echo 按任意键关闭此窗口...
pause >nul