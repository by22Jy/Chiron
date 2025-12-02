# PowerShell script to start AI (FastAPI), Backend (SpringBoot), Frontend (Vite+Vue) and Agent
# Usage: Right-click Run with PowerShell, or: powershell -ExecutionPolicy Bypass -File .\start-all.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 设置环境变量
$env:DB_URL = "jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC"
$env:DB_USER = "root"
$env:DB_PASS = "Wangjiayi1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    YOLO-LLM Project Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

function Test-MySQLConnection {
    Write-Host "`nChecking MySQL connection..." -ForegroundColor Yellow
    try {
        # 首先检查mysql命令是否存在
        $mysqlCmd = Get-Command mysql -ErrorAction SilentlyContinue
        if (-not $mysqlCmd) {
            Write-Host "! MySQL client not found in PATH" -ForegroundColor Yellow
            Write-Host "This is not critical - Backend will handle database connection" -ForegroundColor Yellow
            Write-Host "+ Skipping MySQL connection test" -ForegroundColor Green
            return
        }

        # 尝试连接MySQL
        $result = & mysql -u $env:DB_USER -p$env:DB_PASS -e "USE yolo_platform;" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "! MySQL connection test failed, but continuing anyway" -ForegroundColor Yellow
            Write-Host "Backend will handle database connection during startup" -ForegroundColor Yellow
            Write-Host "Common issues:" -ForegroundColor Yellow
            Write-Host "- MySQL service not running" -ForegroundColor Yellow
            Write-Host "- Database yolo_platform not created" -ForegroundColor Yellow
            Write-Host "- Incorrect username/password" -ForegroundColor Yellow
        } else {
            Write-Host "+ MySQL connection OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "! MySQL test failed, but continuing with startup" -ForegroundColor Yellow
        Write-Host "Backend will show database connection status during startup" -ForegroundColor Yellow
    }
}

function Start-AIService {
    Write-Host "`nStarting AI Service (Port: 8000)..." -ForegroundColor Yellow
    $aiDir = Join-Path $root 'ai'
    if (-not (Test-Path $aiDir)) { throw "AI directory not found: $aiDir" }
    $venvPython = Join-Path $aiDir '.venv/Scripts/python.exe'
    $venvPip    = Join-Path $aiDir '.venv/Scripts/pip.exe'
    $uvicornExe = Join-Path $aiDir '.venv/Scripts/uvicorn.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host 'Creating Python venv for AI...' -ForegroundColor Blue
        & python -m venv (Join-Path $aiDir '.venv')
        Write-Host 'Installing AI requirements (first time only)...' -ForegroundColor Blue
        & $venvPip install -r (Join-Path $aiDir 'requirements.txt') | Out-Null
    } else {
        Write-Host 'AI venv already exists, skipping requirements installation...' -ForegroundColor Green
        # 可选：检查是否需要更新依赖
        # & $venvPip install -r (Join-Path $aiDir 'requirements.txt') --quiet | Out-Null
    }

    $cmd = "`"$uvicornExe`" main:app --host 127.0.0.1 --port 8000 --reload"
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$aiDir`"; $cmd" -WindowStyle Minimized | Out-Null
    Write-Host '+ AI Service starting: http://127.0.0.1:8000' -ForegroundColor Green
    Start-Sleep -Seconds 5
}

function Start-Backend {
    Write-Host "`nStarting Backend Service (Port: 8080)..." -ForegroundColor Yellow
    $beDir = Join-Path $root 'backend'
    if (-not (Test-Path $beDir)) { throw "Backend directory not found: $beDir" }

    # 检查是否有API Key
    $hasValidKey = $false
    if ($env:DEEPSEEK_API_KEY -and $env:DEEPSEEK_API_KEY -ne "your_deepseek_api_key_here") {
        $hasValidKey = $true
        Write-Host "+ DeepSeek API Key detected (Recommended)" -ForegroundColor Green
    }
    elseif ($env:KIMI_API_KEY -and $env:KIMI_API_KEY -ne "your_kimi_api_key_here") {
        $hasValidKey = $true
        Write-Host "+ KIMI API Key detected" -ForegroundColor Green
    }
    elseif ($env:QWEN_API_KEY -and $env:QWEN_API_KEY -ne "your_qwen_api_key_here") {
        $hasValidKey = $true
        Write-Host "+ Qwen API Key detected" -ForegroundColor Green
    }
    elseif ($env:ANTHROPIC_AUTH_TOKEN -and $env:ANTHROPIC_AUTH_TOKEN -ne "your_glm_api_key_here") {
        $hasValidKey = $true
        Write-Host "+ GLM API Key detected" -ForegroundColor Green
    }

    if (-not $hasValidKey) {
        Write-Host "! Warning: No valid LLM API Key set" -ForegroundColor Yellow
        Write-Host "Please set DEEPSEEK_API_KEY or other API Key in the script" -ForegroundColor Yellow
        Write-Host "Recommended: Get free API key at https://platform.deepseek.com" -ForegroundColor Yellow
    }

    $cmd = 'mvn spring-boot:run'
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$beDir`"; $cmd" -WindowStyle Minimized | Out-Null
    Write-Host '+ Backend Service starting: http://127.0.0.1:8080' -ForegroundColor Green
    Start-Sleep -Seconds 10
}

function Start-Frontend {
    Write-Host "`nStarting Frontend Service (Port: 5173)..." -ForegroundColor Yellow
    $feDir = Join-Path $root 'frontend'
    if (-not (Test-Path $feDir)) { throw "Frontend directory not found: $feDir" }
    if (-not (Test-Path (Join-Path $feDir 'node_modules'))) {
        Write-Host 'Installing frontend dependencies...' -ForegroundColor Blue
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$feDir`"; npm install; npm run dev" -WindowStyle Minimized | Out-Null
    } else {
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$feDir`"; npm run dev" -WindowStyle Minimized | Out-Null
    }
    Write-Host '+ Frontend Service starting: http://127.0.0.1:5173' -ForegroundColor Green
    Start-Sleep -Seconds 5
}

function Start-Agent {
    Write-Host "`nStarting Agent (Gesture Control)..." -ForegroundColor Yellow
    $agentDir = Join-Path $root 'agent'
    if (-not (Test-Path $agentDir)) {
        Write-Host 'X Agent directory not found, skipping Agent startup' -ForegroundColor Red
        return
    }
    $venvPython = Join-Path $agentDir '.venv/Scripts/python.exe'
    $venvPip    = Join-Path $agentDir '.venv/Scripts/pip.exe'
    if (-not (Test-Path $venvPython)) {
        Write-Host 'Creating Python venv for Agent...' -ForegroundColor Blue
        & python -m venv (Join-Path $agentDir '.venv')
        Write-Host 'Installing Agent requirements (first time only)...' -ForegroundColor Blue
        & $venvPip install -r (Join-Path $agentDir 'requirements.txt') | Out-Null
    } else {
        Write-Host 'Agent venv already exists, skipping requirements installation...' -ForegroundColor Green
    }

    # 使用实时模式而不是watch模式，更适合演示
    $cmd = "`"$venvPython`" main.py --realtime"
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$agentDir`"; $cmd" -WindowStyle Normal | Out-Null
    Write-Host '+ Agent real-time gesture detection started' -ForegroundColor Green
}

try {
    Write-Host "`n=== Starting All Services ===" -ForegroundColor Cyan

    # 检查MySQL连接
    Test-MySQLConnection

    # 按顺序启动服务
    Start-AIService
    Start-Backend
    Start-Frontend
    Start-Agent

    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "       All Services Started!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Web Frontend: http://localhost:5173" -ForegroundColor White
    Write-Host "Backend API:  http://localhost:8080" -ForegroundColor White
    Write-Host "AI Service:   http://localhost:8000" -ForegroundColor White
    Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "Tips:" -ForegroundColor Yellow
    Write-Host "- Agent window shows real-time gesture detection" -ForegroundColor Yellow
    Write-Host "- Test gesture control in the web interface" -ForegroundColor Yellow
    Write-Host "- Use stop-all.ps1 to stop all services" -ForegroundColor Yellow
    Write-Host ""

} catch {
    Write-Host "`nX Startup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check the error message and retry" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}