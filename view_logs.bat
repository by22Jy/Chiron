@echo off
setlocal enabledelayedexpansion

echo ========================================
echo       YOLO-LLM 日志查看工具
echo ========================================
echo.

:menu
echo 请选择操作:
echo 1. 查看最新日志 (所有模块)
echo 2. 查看指定模块日志
echo 3. 只查看错误信息
echo 4. 查看会话信息
echo 5. 列出所有会话
echo 6. 实时监控日志
echo 7. 退出
echo.
set /p choice="请输入选择 (1-7): "

if "%choice%"=="1" (
    echo.
    echo 📋 查看最新日志...
    python log_reader.py --lines 30
    goto menu
)
if "%choice%"=="2" (
    echo.
    echo 📋 可用模块:
    echo   - backend (后端服务)
    echo   - ai_service (AI服务)
    echo   - mcp (MCP服务器)
    echo   - agent (语音Agent)
    echo   - frontend (前端服务)
    echo.
    set /p module="请输入模块名称: "
    echo.
    echo 📋 查看 %module% 模块日志...
    python log_reader.py --module %module% --lines 50
    goto menu
)
if "%choice%"=="3" (
    echo.
    echo 🔍 查看错误信息...
    python log_reader.py --errors
    goto menu
)
if "%choice%"=="4" (
    echo.
    echo 📊 查看会话信息...
    python log_reader.py --info
    goto menu
)
if "%choice%"=="5" (
    echo.
    echo 📁 列出所有会话...
    python log_reader.py --list
    goto menu
)
if "%choice%"=="6" (
    echo.
    echo 👀 开始实时监控 (Ctrl+C 退出)...
    set /p module="请输入模块名称 (留空监控所有模块): "
    if "!module!"=="" (
        python log_reader.py --watch
    ) else (
        python log_reader.py --watch --module !module!
    )
    goto menu
)
if "%choice%"=="7" (
    echo 👋 退出
    goto end
)

echo ❌ 无效选择，请重新输入
goto menu

:end
pause