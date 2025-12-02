# Unified Startup Script - 统一启动脚本
# 所有服务都在PowerShell窗口中启动

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 设置环境变量
$env:DB_URL = "jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC"
$env:DB_USER = "root"
$env:DB_PASS = "Wangjiayi1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    YOLO-LLM Unified Startup Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

function Test-MySQLConnection {
    Write-Host "`nChecking MySQL connection..." -ForegroundColor Yellow
    try {
        $mysqlCmd = Get-Command mysql -ErrorAction SilentlyContinue
        if (-not $mysqlCmd) {
            Write-Host "! MySQL client not found in PATH" -ForegroundColor Yellow
            Write-Host "+ Skipping MySQL connection test" -ForegroundColor Green
            return
        }

        $result = & mysql -u $env:DB_USER -p$env:DB_PASS -e "USE yolo_platform;" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "! MySQL connection test failed, but continuing anyway" -ForegroundColor Yellow
        } else {
            Write-Host "+ MySQL connection OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "! MySQL test failed, but continuing with startup" -ForegroundColor Yellow
    }
}

function Start-AIService {
    Write-Host "`nStarting AI Service (Port: 8000)..." -ForegroundColor Yellow
    $aiDir = Join-Path $root 'ai'
    $venvPython = Join-Path $aiDir '.venv/Scripts/python.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host 'Creating Python venv for AI...' -ForegroundColor Blue
        & python -m venv (Join-Path $aiDir '.venv')
        Write-Host 'Installing AI requirements (first time only)...' -ForegroundColor Blue
        & (Join-Path $aiDir '.venv/Scripts/pip.exe') install -r (Join-Path $aiDir 'requirements.txt') | Out-Null
    } else {
        Write-Host 'AI venv already exists, skipping requirements installation...' -ForegroundColor Green
    }

    $cmd = "& `"$venvPython`" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$aiDir`"; $cmd" -WindowStyle Minimized
    Write-Host '+ AI Service starting: http://127.0.0.1:8000' -ForegroundColor Green
    Start-Sleep -Seconds 5
}

function Start-Backend {
    Write-Host "`nStarting Backend Service (Port: 8080)..." -ForegroundColor Yellow
    $beDir = Join-Path $root 'backend'

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
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$beDir`"; $cmd" -WindowStyle Minimized
    Write-Host '+ Backend Service starting: http://127.0.0.1:8080' -ForegroundColor Green
    Start-Sleep -Seconds 10
}

function Start-Frontend {
    Write-Host "`nStarting Frontend Service (Port: 5173)..." -ForegroundColor Yellow
    $feDir = Join-Path $root 'frontend'

    if (-not (Test-Path (Join-Path $feDir 'node_modules'))) {
        Write-Host 'Installing frontend dependencies...' -ForegroundColor Blue
        $installCmd = "npm install"
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$feDir`"; $installCmd; npm run dev" -WindowStyle Minimized
    } else {
        $cmd = "npm run dev"
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$feDir`"; $cmd" -WindowStyle Minimized
    }
    Write-Host '+ Frontend Service starting: http://127.0.0.1:5173' -ForegroundColor Green
    Start-Sleep -Seconds 8
}

function Start-Agent {
    Write-Host "`nStarting Agent (Gesture Control)..." -ForegroundColor Yellow
    $agentDir = Join-Path $root 'agent'
    if (-not (Test-Path $agentDir)) {
        Write-Host 'X Agent directory not found, skipping Agent startup' -ForegroundColor Red
        return
    }

    $venvPython = Join-Path $agentDir '.venv/Scripts/python.exe'
    if (-not (Test-Path $venvPython)) {
        Write-Host 'Creating Python venv for Agent...' -ForegroundColor Blue
        & python -m venv (Join-Path $agentDir '.venv')
        Write-Host 'Installing Agent requirements (first time only)...' -ForegroundColor Blue
        & (Join-Path $agentDir '.venv/Scripts/pip.exe') install -r (Join-Path $agentDir 'requirements.txt') | Out-Null
    } else {
        Write-Host 'Agent venv already exists, skipping requirements installation...' -ForegroundColor Green
    }

    $cmd = "& `"$venvPython`" main.py --realtime"
    # Agent窗口设为Normal大小，方便查看实时手势检测
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$agentDir`"; $cmd" -WindowStyle Normal
    Write-Host '+ Agent real-time gesture detection started' -ForegroundColor Green
}

try {
    Write-Host "`n=== Starting All Services (Unified PowerShell) ===" -ForegroundColor Cyan

    # 检查MySQL连接
    Test-MySQLConnection

    # 按顺序启动服务
    Write-Host "`nStarting services sequentially..." -ForegroundColor Cyan

    Start-AIService
    Start-Backend
    Start-Frontend
    Start-Agent

    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "       All Services Started!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Web Frontend:  http://localhost:5173" -ForegroundColor White
    Write-Host "Backend API:   http://localhost:8080" -ForegroundColor White
    Write-Host "AI Service:     http://localhost:8000" -ForegroundColor White
    Write-Host "API Docs:       http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "Services:" -ForegroundColor Yellow
    Write-Host "- All services running in PowerShell windows" -ForegroundColor Yellow
    Write-Host "- Agent window shows real-time gesture detection" -ForegroundColor Yellow
    Write-Host "- Use stop-all.ps1 to stop all services" -ForegroundColor Yellow
    Write-Host ""

    # 显示服务状态检查
    Write-Host "Checking service status in 10 seconds..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10

    $services = @(
        @{Name="Frontend"; Url="http://localhost:5173"},
        @{Name="Backend"; Url="http://localhost:8080"},
        @{Name="AI Service"; Url="http://localhost:8000"}
    )

    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.Url -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✓ $($service.Name): $($service.Url) - RUNNING" -ForegroundColor Green
            } else {
                Write-Host "✗ $($service.Name): $($service.Url) - STARTING" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "✗ $($service.Name): $($service.Url) - STARTING" -ForegroundColor Yellow
        }
    }

} catch {
    Write-Host "`nX Startup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check the error message and retry" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}