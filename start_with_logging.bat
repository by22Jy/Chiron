@echo off
setlocal enabledelayedexpansion

echo ========================================
echo    YOLO-LLM 系统启动器 (带日志管理)
echo ========================================
echo.

REM 检查Python是否可用
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo ✅ Python环境检查通过
echo.

REM 启动带日志管理的系统
echo 🚀 启动系统...
python start_system_with_logging.py

if %errorlevel% neq 0 (
    echo ❌ 系统启动失败
    pause
    exit /b 1
)

echo.
echo ✅ 系统已关闭
pause