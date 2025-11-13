# Simplified YOLO-LLM Startup Script (without MySQL dependency check)
# Usage: powershell -ExecutionPolicy Bypass -File .\start-simple.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 设置环境变量
$env:DB_URL = "jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC"
$env:DB_USER = "root"
$env:DB_PASS = "Wangjiayi1"
# 请设置你的 LLM API Key - 在这里修改
$env:KIMI_API_KEY = "your_kimi_api_key_here"
# 或者使用 Qwen
# $env:QWEN_API_KEY = "your_qwen_api_key_here"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    YOLO-LLM Simple Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

function Start-AIService {
    Write-Host "`nStarting AI Service (Port: 8000)..." -ForegroundColor Yellow
    $aiDir = Join-Path $root 'ai'
    if (-not (Test-Path $aiDir)) {
        Write-Host "X AI directory not found: $aiDir" -ForegroundColor Red
        return $false
    }

    $venvPython = Join-Path $aiDir '.venv/Scripts/python.exe'
    if (-not (Test-Path $venvPython)) {
        Write-Host 'Creating Python venv for AI...' -ForegroundColor Blue
        & python -m venv (Join-Path $aiDir '.venv')
    }

    Write-Host 'Installing AI requirements...' -ForegroundColor Blue
    $venvPip = Join-Path $aiDir '.venv/Scripts/pip.exe'
    & $venvPip install -r (Join-Path $aiDir 'requirements.txt') | Out-Null

    $uvicornExe = Join-Path $aiDir '.venv/Scripts/uvicorn.exe'
    $cmd = "`"$uvicornExe`" main:app --host 127.0.0.1 --port 8000 --reload"
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$aiDir`"; $cmd" -WindowStyle Minimized | Out-Null
    Write-Host '+ AI Service starting: http://127.0.0.1:8000' -ForegroundColor Green
    Start-Sleep -Seconds 5
    return $true
}

function Start-Backend {
    Write-Host "`nStarting Backend Service (Port: 8080)..." -ForegroundColor Yellow
    $beDir = Join-Path $root 'backend'
    if (-not (Test-Path $beDir)) {
        Write-Host "X Backend directory not found: $beDir" -ForegroundColor Red
        return $false
    }

    # 检查是否有API Key
    if (-not ($env:KIMI_API_KEY -or $env:QWEN_API_KEY) -or
        $env:KIMI_API_KEY -eq "your_kimi_api_key_here") {
        Write-Host "! Warning: No valid LLM API Key set" -ForegroundColor Yellow
        Write-Host "Please set KIMI_API_KEY or QWEN_API_KEY in the script" -ForegroundColor Yellow
    }

    $cmd = 'mvn spring-boot:run'
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$beDir`"; $cmd" -WindowStyle Minimized | Out-Null
    Write-Host '+ Backend Service starting: http://127.0.0.1:8080' -ForegroundColor Green
    Write-Host "! Backend will show database connection status" -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    return $true
}

function Start-Frontend {
    Write-Host "`nStarting Frontend Service (Port: 5173)..." -ForegroundColor Yellow
    $feDir = Join-Path $root 'frontend'
    if (-not (Test-Path $feDir)) {
        Write-Host "X Frontend directory not found: $feDir" -ForegroundColor Red
        return $false
    }

    if (-not (Test-Path (Join-Path $feDir 'node_modules'))) {
        Write-Host 'Installing frontend dependencies...' -ForegroundColor Blue
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$feDir`"; npm install; npm run dev" -WindowStyle Minimized | Out-Null
    } else {
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$feDir`"; npm run dev" -WindowStyle Minimized | Out-Null
    }
    Write-Host '+ Frontend Service starting: http://127.0.0.1:5173' -ForegroundColor Green
    Start-Sleep -Seconds 5
    return $true
}

function Start-Agent {
    Write-Host "`nStarting Agent (Gesture Control)..." -ForegroundColor Yellow
    $agentDir = Join-Path $root 'agent'
    if (-not (Test-Path $agentDir)) {
        Write-Host 'X Agent directory not found, skipping Agent startup' -ForegroundColor Red
        return $true # Agent is optional
    }

    $venvPython = Join-Path $agentDir '.venv/Scripts/python.exe'
    if (-not (Test-Path $venvPython)) {
        Write-Host 'Creating Python venv for Agent...' -ForegroundColor Blue
        & python -m venv (Join-Path $agentDir '.venv')
    }

    Write-Host 'Installing Agent requirements...' -ForegroundColor Blue
    $venvPip = Join-Path $agentDir '.venv/Scripts/pip.exe'
    & $venvPip install -r (Join-Path $agentDir 'requirements.txt') | Out-Null

    # 使用实时模式
    $cmd = "`"$venvPython`" main.py --realtime"
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$agentDir`"; $cmd" -WindowStyle Normal | Out-Null
    Write-Host '+ Agent real-time gesture detection started' -ForegroundColor Green
    return $true
}

try {
    Write-Host "`n=== Starting All Services ===" -ForegroundColor Cyan
    Write-Host "! Database connection will be checked by Backend during startup" -ForegroundColor Yellow

    # 按顺序启动服务
    $success = $true
    $success = (Start-AIService) -and $success
    $success = (Start-Backend) -and $success
    $success = (Start-Frontend) -and $success
    $success = (Start-Agent) -and $success

    if ($success) {
        Write-Host "`n========================================" -ForegroundColor Green
        Write-Host "       All Services Started!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Web Frontend: http://localhost:5173" -ForegroundColor White
        Write-Host "Backend API:  http://localhost:8080" -ForegroundColor White
        Write-Host "AI Service:   http://localhost:8000" -ForegroundColor White
        Write-Host "API Docs:     http://localhost:8000/docs" -ForegroundColor White
        Write-Host ""
        Write-Host "Tips:" -ForegroundColor Yellow
        Write-Host "- Check Backend console for database connection status" -ForegroundColor Yellow
        Write-Host "- Agent window shows real-time gesture detection" -ForegroundColor Yellow
        Write-Host "- Test gesture control in the web interface" -ForegroundColor Yellow
        Write-Host "- Use stop-all.ps1 to stop all services" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Database Setup (if needed):" -ForegroundColor Cyan
        Write-Host "1. Install MySQL and start service" -ForegroundColor Cyan
        Write-Host "2. Create database: CREATE DATABASE yolo_platform;" -ForegroundColor Cyan
        Write-Host "3. Restart Backend service" -ForegroundColor Cyan
        Write-Host ""
    } else {
        Write-Host "`n! Some services failed to start. Check the messages above." -ForegroundColor Yellow
    }

} catch {
    Write-Host "`nX Startup error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check the error message and retry" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}