@echo off
echo ===================================
echo    YOLO-LLM 项目停止脚本 (Windows) - 更新版
echo ===================================

echo.
echo 正在停止YOLO-LLM所有服务...

REM 停止MCP服务器 (8083端口)
echo 停止增强版MCP服务器...
for /f "tokens=5" %%a in ('netstat -ano ^| find ":8083"') do (
    echo 停止进程 %%a (MCP服务器)
    taskkill /f /pid %%a >nul 2>&1
)

REM 停止后端服务 (8080端口)
echo 停止后端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| find ":8080"') do (
    echo 停止进程 %%a (后端服务)
    taskkill /f /pid %%a >nul 2>&1
)

REM 停止AI服务 (8000端口)
echo 停止AI服务...
for /f "tokens=5" %%a in ('netstat -ano ^| find ":8000"') do (
    echo 停止进程 %%a (AI服务)
    taskkill /f /pid %%a >nul 2>&1
)

REM 停止前端服务 (5173端口)
echo 停止前端服务...
for /f "tokens=5" %%a in ('netstat -ano ^| find ":5173"') do (
    echo 停止进程 %%a (前端服务)
    taskkill /f /pid %%a >nul 2>&1
)

REM 额外检查并停止可能遗留的Python进程
echo.
echo 检查并停止遗留的Python进程...

REM 停止MCP服务器Python进程
taskkill /f /im python.exe /fi "windowtitle eq YOLO-LLM*" >nul 2>&1

REM 停止特定的MCP服务器进程
wmic process where "commandline like '%enhanced_mcp_server.py%'" delete >nul 2>&1
wmic process where "commandline like '%real_mcp_server.py%'" delete >nul 2>&1
wmic process where "commandline like '%mcp_http_server.py%'" delete >nul 2>&1

REM 停止Spring Boot进程
wmic process where "commandline like '%spring-boot:run%'" delete >nul 2>&1

REM 停止uvicorn进程
wmic process where "commandline like '%uvicorn main:app%'" delete >nul 2>&1

REM 停止Agent进程
wmic process where "commandline like '%main.py --realtime%'" delete >nul 2>&1
wmic process where "commandline like '%voice_simple_final.py%'" delete >nul 2>&1
wmic process where "commandline like '%universal_computer_control.py%'" delete >nul 2>&1

REM 停止可能的Java进程（如果Spring Boot没有完全停止）
echo 检查Java进程...
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq java.exe" /fo csv ^| find "java.exe"') do (
    echo 检查Java进程 %%a...
    wmic process where "processid=%%a" get commandline /format:list | findstr "spring-boot" >nul
    if !errorlevel! equ 0 (
        echo 停止Spring Boot Java进程 %%a
        taskkill /f /pid %%a >nul 2>&1
    )
)

REM 停止可能的Node.js进程（npm dev）
echo 检查Node.js进程...
for /f "tokens=2" %%a in ('tasklist /fi "imagename eq node.exe" /fo csv ^| find "node.exe"') do (
    echo 检查Node.js进程 %%a...
    wmic process where "processid=%%a" get commandline /format:list | findstr "vite.*dev\|npm.*dev" >nul
    if !errorlevel! equ 0 (
        echo 停止Vite开发服务器进程 %%a
        taskkill /f /pid %%a >nul 2>&1
    )
)

echo.
echo ===================================
echo 服务停止完成
echo ===================================
echo.
echo 检查端口占用情况:
echo - MCP服务器 (8083):
netstat -ano | find ":8083" >nul && echo [占用] || echo [空闲]
echo - 后端API (8080):
netstat -ano | find ":8080" >nul && echo [占用] || echo [空闲]
echo - AI服务 (8000):
netstat -ano | find ":8000" >nul && echo [占用] || echo [空闲]
echo - 前端界面 (5173):
netstat -ano | find ":5173" >nul && echo [占用] || echo [空闲]
echo.
echo 如需重新启动，请运行: start-all.bat
echo.
pause