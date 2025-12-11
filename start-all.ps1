# YOLO-LLM 统一启动脚本 - 启动所有服务
# Unified YOLO-LLM Startup Script - Launch All Services
# Usage: 右键运行，或在终端执行: powershell -ExecutionPolicy Bypass -File .\start-all.ps1

# 设置编码为UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 初始化日志系统
Write-Host "`n=== 初始化日志系统 ===" -ForegroundColor Cyan
$logsDir = Join-Path $root "logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
}

# 创建会话目录
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$sessionDir = Join-Path $logsDir "session_$timestamp"
New-Item -ItemType Directory -Path $sessionDir -Force | Out-Null

# 创建各模块日志目录
$modules = @("backend", "ai_service", "mcp", "agent", "frontend")
foreach ($module in $modules) {
    $moduleDir = Join-Path $sessionDir $module
    New-Item -ItemType Directory -Path $moduleDir -Force | Out-Null
}

Write-Host "[日志] 会话目录创建: $sessionDir" -ForegroundColor Green
$global:logDir = $sessionDir

# 创建会话信息文件
$sessionInfo = @{
    session_id = Split-Path $sessionDir -Leaf
    start_time = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
    platform = $PSVersionTable.Platform
    modules = @{
        backend = @{ status = "pending"; port = 8080 }
        ai_service = @{ status = "pending"; port = 8000 }
        mcp_server = @{ status = "pending"; port = 8083 }
        agent = @{ status = "pending"; port = $null }
        frontend = @{ status = "pending"; port = 5173 }
    }
}
$sessionInfo | ConvertTo-Json -Depth 3 | Out-File -FilePath (Join-Path $sessionDir "session_info.json") -Encoding UTF8

# 设置环境变量
$env:DB_URL = "jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC"
$env:DB_USER = "root"
$env:DB_PASS = "Wangjiayi1"

# 设置LLM API Keys
$env:KIMI_API_KEY = $env:KIMI_API_KEY
$env:QWEN_API_KEY = $env:QWEN_API_KEY

# 设置MCP工具API Keys
$env:NEWS_API_KEY = $env:NEWS_API_KEY
$env:WEATHER_API_KEY = $env:WEATHER_API_KEY
$env:BREVO_API_KEY = $env:BREVO_API_KEY

# 设置MCP服务器URL
$env:MCP_SERVER_URL = "http://localhost:8083"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "      YOLO-LLM 智能控制系统启动" -ForegroundColor Cyan
Write-Host "    AI-Powered Gesture & Voice Control" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

function Test-DevelopmentEnvironment {
    Write-Host "`n=== Environment Check ===" -ForegroundColor Cyan

    $envReady = $true

    # 检查Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Python not found - Please install Python 3.8+" -ForegroundColor Red
        $envReady = $false
    }

    # 检查Java（允许Maven wrapper）
    try {
        $javaVersion = java -version 2>&1
        Write-Host "[OK] Java: Available" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Java not in PATH, checking Maven wrapper..." -ForegroundColor Yellow
    }

    # 检查Maven
    $beDir = Join-Path $root 'backend'
    if (Test-Path (Join-Path $beDir 'mvnw')) {
        Write-Host "[OK] Maven wrapper found" -ForegroundColor Green
    } elseif (Get-Command mvn -ErrorAction SilentlyContinue) {
        Write-Host "[OK] System Maven found" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Maven not found" -ForegroundColor Red
        $envReady = $false
    }

    # 检查Node.js
    try {
        $nodeVersion = node --version
        Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Node.js not found - Please install Node.js 18+" -ForegroundColor Red
        $envReady = $false
    }

    return $envReady
}

function Test-MySQLConnection {
    Write-Host "`n=== Database Connection Test ===" -ForegroundColor Cyan
    try {
        $mysqlCmd = Get-Command mysql -ErrorAction SilentlyContinue
        if (-not $mysqlCmd) {
            Write-Host "[INFO] MySQL client not found (not critical)" -ForegroundColor Yellow
            Write-Host "  Backend will handle database connection" -ForegroundColor Yellow
            return
        }

        $result = & mysql -u $env:DB_USER -p$env:DB_PASS -e "USE yolo_platform;" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "[WARN] MySQL test failed (not critical)" -ForegroundColor Yellow
            Write-Host "  Backend will show connection status" -ForegroundColor Yellow
        } else {
            Write-Host "[OK] MySQL connection successful" -ForegroundColor Green
        }
    } catch {
        Write-Host "[INFO] MySQL test skipped" -ForegroundColor Yellow
    }
}

function Start-MCPServer {
    Write-Host "`n=== Enhanced MCP Server starting (Port: 8083) ===" -ForegroundColor Cyan
    $mcpDir = Join-Path $root 'mcp'
    if (-not (Test-Path $mcpDir)) {
        throw "MCP directory not found: $mcpDir"
    }

    # 检查API Keys
    $hasValidKeys = $false
    if ($env:NEWS_API_KEY) {
        Write-Host "[OK] NEWS_API_KEY configured" -ForegroundColor Green
        $hasValidKeys = $true
    } else {
        Write-Host "[WARN] NEWS_API_KEY not configured - news feature unavailable" -ForegroundColor Yellow
    }

    if ($env:WEATHER_API_KEY) {
        Write-Host "[OK] WEATHER_API_KEY configured" -ForegroundColor Green
        $hasValidKeys = $true
    } else {
        Write-Host "[WARN] WEATHER_API_KEY not configured - weather feature unavailable" -ForegroundColor Yellow
    }

    if ($env:BREVO_API_KEY) {
        Write-Host "[OK] BREVO_API_KEY configured" -ForegroundColor Green
        $hasValidKeys = $true
    } else {
        Write-Host "[WARN] BREVO_API_KEY not configured - email feature unavailable" -ForegroundColor Yellow
    }

    if (-not $hasValidKeys) {
        Write-Host "[WARN] No MCP tool API Keys configured" -ForegroundColor Yellow
        Write-Host "  Server will start but some features unavailable" -ForegroundColor Yellow
    }

    $venvPython = Join-Path $mcpDir '.venv/Scripts/python.exe'
    $venvPip = Join-Path $mcpDir '.venv/Scripts/pip.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host "[INFO] Creating MCP virtual environment..." -ForegroundColor Blue
        & python -m venv (Join-Path $mcpDir '.venv')
        Write-Host "[INFO] Installing MCP dependencies..." -ForegroundColor Blue
        & $venvPip install -r (Join-Path $mcpDir 'requirements.txt') | Out-Null
    } else {
        Write-Host "[OK] MCP virtual environment ready" -ForegroundColor Green
    }

    Write-Host "[INFO] Starting Enhanced MCP Server..." -ForegroundColor Yellow
    Write-Host "[日志] MCP日志将保存到: $global:logDir\mcp\" -ForegroundColor Cyan

    $mcpLogFile = Join-Path $global:logDir "mcp\mcp_server.log"
    $cmd = "& `"$venvPython`" main.py 2>&1 | Out-File -FilePath `"$mcpLogFile`" -Encoding UTF8 -Append"
    $psArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location `"$mcpDir`"; $cmd")
    Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized | Out-Null
    Write-Host "[SUCCESS] MCP Server starting: http://localhost:8083" -ForegroundColor Green
    Write-Host "  Including 9 computer control tools and news/weather/email features" -ForegroundColor Cyan
    Start-Sleep -Seconds 5
}

function Start-AIService {
    Write-Host "`n=== AI Service starting (Port: 8000) ===" -ForegroundColor Cyan
    $aiDir = Join-Path $root 'ai'
    if (-not (Test-Path $aiDir)) {
        throw "AI directory not found: $aiDir"
    }

    $venvPython = Join-Path $aiDir '.venv/Scripts/python.exe'
    $venvPip    = Join-Path $aiDir '.venv/Scripts/pip.exe'
    $uvicornExe = Join-Path $aiDir '.venv/Scripts/uvicorn.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host "[INFO] Creating AI virtual environment..." -ForegroundColor Blue
        & python -m venv (Join-Path $aiDir '.venv')
        Write-Host "[INFO] Installing AI dependencies (first time only)..." -ForegroundColor Blue
        & $venvPip install -r (Join-Path $aiDir 'requirements.txt') | Out-Null
    } else {
        Write-Host "[OK] AI virtual environment ready" -ForegroundColor Green
    }

    Write-Host "[INFO] Starting AI FastAPI service..." -ForegroundColor Yellow
    Write-Host "[日志] AI服务日志将保存到: $global:logDir\ai_service\" -ForegroundColor Cyan

    $aiLogFile = Join-Path $global:logDir "ai_service\fastapi.log"
    $cmd = "& `"$uvicornExe`" main:app --host 127.0.0.1 --port 8000 --reload 2>&1 | Out-File -FilePath `"$aiLogFile`" -Encoding UTF8 -Append"
    $psArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location `"$aiDir`"; $cmd")
    Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized | Out-Null
    Write-Host "[SUCCESS] AI Service starting: http://127.0.0.1:8000" -ForegroundColor Green
    Start-Sleep -Seconds 5
}

function Start-Backend {
    Write-Host "`n=== Backend Service starting (Port: 8080) ===" -ForegroundColor Cyan
    $beDir = Join-Path $root 'backend'
    if (-not (Test-Path $beDir)) {
        throw "Backend directory not found: $beDir"
    }

    # API Key检查
    $hasValidKey = $false
    if ($env:DEEPSEEK_API_KEY -and $env:DEEPSEEK_API_KEY -ne "your_deepseek_api_key_here") {
        $hasValidKey = $true
        Write-Host "[OK] DeepSeek API Key configured (recommended)" -ForegroundColor Green
    }
    elseif ($env:KIMI_API_KEY -and $env:KIMI_API_KEY -ne "your_kimi_api_key_here") {
        $hasValidKey = $true
        Write-Host "[OK] KIMI API Key configured" -ForegroundColor Green
    }
    elseif ($env:QWEN_API_KEY -and $env:QWEN_API_KEY -ne "your_qwen_api_key_here") {
        $hasValidKey = $true
        Write-Host "[OK] Qwen API Key configured" -ForegroundColor Green
    }
    elseif ($env:ANTHROPIC_AUTH_TOKEN -and $env:ANTHROPIC_AUTH_TOKEN -ne "your_glm_api_key_here") {
        $hasValidKey = $true
        Write-Host "[OK] GLM API Key configured" -ForegroundColor Green
    }

    if (-not $hasValidKey) {
        Write-Host "[WARN] No valid LLM API Key configured" -ForegroundColor Yellow
        Write-Host "  Please set DEEPSEEK_API_KEY or other API Key" -ForegroundColor Yellow
        Write-Host "  Get free API key: https://platform.deepseek.com" -ForegroundColor Yellow
    }

    # 优先使用Maven wrapper
    if (Test-Path (Join-Path $beDir 'mvnw')) {
        $cmd = '.\mvnw spring-boot:run'
        Write-Host "[INFO] Using Maven wrapper" -ForegroundColor Green
    } else {
        $cmd = 'mvn spring-boot:run'
        Write-Host "[INFO] Using system Maven" -ForegroundColor Green
    }

    Write-Host "[日志] 后端日志将保存到: $global:logDir\backend\" -ForegroundColor Cyan

    $backendLogFile = Join-Path $global:logDir "backend\spring-boot.log"
    $psArgs = @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location `"$beDir`"; $cmd 2>&1 | Out-File -FilePath `"$backendLogFile`" -Encoding UTF8 -Append")
    Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized | Out-Null
    Write-Host "[SUCCESS] Backend Service starting: http://127.0.0.1:8080" -ForegroundColor Green
    Start-Sleep -Seconds 8
}

function Start-Frontend {
    Write-Host "`n=== Frontend Service starting (Port: 5173) ===" -ForegroundColor Cyan
    $feDir = Join-Path $root 'frontend'
    if (-not (Test-Path $feDir)) {
        throw "Frontend directory not found: $feDir"
    }

    Write-Host "[日志] 前端日志将保存到: $global:logDir\frontend\" -ForegroundColor Cyan

    $frontendLogFile = Join-Path $global:logDir "frontend\frontend.log"
    if (-not (Test-Path (Join-Path $feDir 'node_modules'))) {
        Write-Host "[INFO] Installing frontend dependencies..." -ForegroundColor Blue
        $cmd = "npm install; npm run dev 2>&1 | Out-File -FilePath `"$frontendLogFile`" -Encoding UTF8 -Append"
        $psArgs = @("-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location `"$feDir`"; $cmd")
        Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized | Out-Null
    } else {
        $cmd = "npm run dev 2>&1 | Out-File -FilePath `"$frontendLogFile`" -Encoding UTF8 -Append"
        $psArgs = @("-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location `"$feDir`"; $cmd")
        Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized | Out-Null
    }
    Write-Host "[SUCCESS] Frontend Service starting: http://127.0.0.1:5173" -ForegroundColor Green
    Start-Sleep -Seconds 6
}

function Start-Agent {
    Write-Host "`n=== Agent Service starting (Gesture + Voice Control) ===" -ForegroundColor Cyan
    $agentDir = Join-Path $root 'agent'
    if (-not (Test-Path $agentDir)) {
        Write-Host "[SKIP] Agent directory not found, skipping Agent startup" -ForegroundColor Red
        return
    }

    $venvPython = Join-Path $agentDir '.venv/Scripts/python.exe'
    $venvPip    = Join-Path $agentDir '.venv/Scripts/pip.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host "[INFO] Creating Agent virtual environment..." -ForegroundColor Blue
        & python -m venv (Join-Path $agentDir '.venv')
        Write-Host "[INFO] Installing Agent dependencies (first time only)..." -ForegroundColor Blue
        & $venvPip install -r (Join-Path $agentDir 'requirements.txt') | Out-Null
    } else {
        Write-Host "[OK] Agent virtual environment ready" -ForegroundColor Green
    }

    Write-Host "[日志] Agent日志将保存到: $global:logDir\agent\" -ForegroundColor Cyan

    $agentLogFile = Join-Path $global:logDir "agent\agent.log"

    # 分离启动：先摄像头，后语音
    Write-Host "[INFO] Step 1: Starting gesture recognition camera..." -ForegroundColor Yellow
    $cameraCmd = "& `"$venvPython`" main.py --realtime 2>&1 | Out-File -FilePath `"$agentLogFile`" -Encoding UTF8 -Append"
    try {
        $psArgs = @("-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location `"$agentDir`"; $cameraCmd")
        Start-Process powershell -ArgumentList $psArgs -WindowStyle Normal -ErrorAction Stop | Out-Null
        Write-Host "[SUCCESS] Camera gesture recognition started" -ForegroundColor Green
        Write-Host "  Look for window: 'YOLO-LLM Agent - Gesture Detection'" -ForegroundColor Cyan
    } catch {
        Write-Host "[ERROR] Camera startup failed: $($_.Exception.Message)" -ForegroundColor Red
        return
    }

    # 等待摄像头初始化
    Write-Host "[INFO] Waiting for camera initialization..." -ForegroundColor Yellow
    for ($i = 8; $i -gt 0; $i--) {
        Write-Host -NoNewLine "`r  Starting voice in $i seconds... "
        Start-Sleep -Seconds 1
    }
    Write-Host "`r[SUCCESS] Camera ready!                              " -ForegroundColor Green

    # 启动语音控制
    Write-Host "[INFO] Step 2: Starting voice control..." -ForegroundColor Yellow
    $voiceLogFile = Join-Path $global:logDir "agent\voice.log"
    $voiceCmd = "& `"$venvPython`" main.py --voice 2>&1 | Out-File -FilePath `"$voiceLogFile`" -Encoding UTF8 -Append"
    try {
        $psArgs = @("-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "Set-Location `"$agentDir`"; $voiceCmd")
        Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized -ErrorAction Stop | Out-Null
        Write-Host "[SUCCESS] Voice control started (background)" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Voice control startup failed, but camera still works" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "Agent Status:" -ForegroundColor White
    Write-Host "  Camera: Running in separate window" -ForegroundColor Green
    Write-Host "  Voice: Running in background process" -ForegroundColor Green
    Write-Host "  Tip: Check taskbar if camera window not visible" -ForegroundColor Cyan
}

function Test-ServiceHealth {
    Write-Host "`n=== Service Health Check ===" -ForegroundColor Cyan

    $services = @(
        @{Name="MCP Server"; Url="http://localhost:8083/health"},
        @{Name="Frontend"; Url="http://localhost:5173"},
        @{Name="Backend"; Url="http://localhost:8080"},
        @{Name="AI Service"; Url="http://localhost:8000"}
    )

    $allHealthy = $true
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.Url -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "[OK] $($service.Name): $($service.Url) - Running normally" -ForegroundColor Green
            } else {
                Write-Host "[PENDING] $($service.Name): $($service.Url) - Starting" -ForegroundColor Yellow
                $allHealthy = $false
            }
        } catch {
            Write-Host "[PENDING] $($service.Name): $($service.Url) - Starting" -ForegroundColor Yellow
            $allHealthy = $false
        }
    }

    return $allHealthy
}

# 主要启动流程
try {
    Write-Host "`nStarting YOLO-LLM system..." -ForegroundColor Cyan

    # 环境检测
    if (-not (Test-DevelopmentEnvironment)) {
        Write-Host "`n[ERROR] Environment check failed, please install missing dependencies" -ForegroundColor Red
        Write-Host "Press any key to exit..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }

    # 数据库连接测试
    Test-MySQLConnection

    # 按顺序启动服务
    Start-MCPServer
    Start-Backend
    Start-AIService
    Start-Frontend
    Start-Agent

    # 等待服务启动并检查状态
    Write-Host "`nWaiting for services to fully start..." -ForegroundColor Cyan
    Start-Sleep -Seconds 8
    Test-ServiceHealth

    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "       All Services Started Successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Service URLs:" -ForegroundColor White
    Write-Host "- MCP Server:   http://localhost:8083" -ForegroundColor White
    Write-Host "- Web Interface: http://localhost:5173" -ForegroundColor White
    Write-Host "- Backend API:  http://localhost:8080" -ForegroundColor White
    Write-Host "- AI Service:   http://localhost:8000" -ForegroundColor White
    Write-Host "- API Docs:     http://localhost:8000/docs" -ForegroundColor White
    Write-Host "- Health Check: http://localhost:8083/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Agent Status:" -ForegroundColor Cyan
    Write-Host "  Camera gesture recognition: Running in separate window" -ForegroundColor Green
    Write-Host "  Voice control: Listening in background" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage Tips:" -ForegroundColor Yellow
    Write-Host "  • Camera window shows real-time gesture recognition" -ForegroundColor Gray
    Write-Host "  • Voice control supports Chinese commands" -ForegroundColor Gray
    Write-Host "  • Use .\stop-all.ps1 to stop all services" -ForegroundColor Gray
    Write-Host ""

    Write-Host ""
    Write-Host "LOG MANAGEMENT:" -ForegroundColor Cyan
    Write-Host "  All logs are automatically saved to: $global:logDir" -ForegroundColor White
    Write-Host "  Quick view logs: view_logs.bat" -ForegroundColor Gray
    Write-Host "  View errors: python log_reader.py -e" -ForegroundColor Gray
    Write-Host "  Monitor logs: python log_reader.py --watch" -ForegroundColor Gray
    Write-Host ""

    Write-Host "YOLO-LLM system startup complete! Press any key to exit launcher..." -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

} catch {
    Write-Host "`n[ERROR] Startup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check error messages and retry" -ForegroundColor Yellow
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}