# 统一蓝色PowerShell启动脚本 - 所有窗口都是PowerShell蓝色
# Unified Blue PowerShell Startup Script - All Windows Use PowerShell Blue

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 设置环境变量
$env:DB_URL = "jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC"
$env:DB_USER = "root"
$env:DB_PASS = "Wangjiayi1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  YOLO-LLM Blue PowerShell Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

function Start-BluePowerShellService {
    param(
        [string]$ServiceName,
        [string]$Directory,
        [string]$Command,
        [string]$WindowStyle = "Minimized"
    )

    Write-Host "Starting $ServiceName..." -ForegroundColor Yellow

    # 构建完整的PowerShell命令
    $fullCommand = "cd '$Directory'; $Command"

    # 启动蓝色PowerShell窗口
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command",$fullCommand -WindowStyle $WindowStyle

    Write-Host "+ $ServiceName started successfully" -ForegroundColor Green
}

function Test-Environment {
    Write-Host "`n=== Environment Check ===" -ForegroundColor Cyan

    # 检查Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "+ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "! Python not found in PATH" -ForegroundColor Red
        return $false
    }

    # 检查Java (允许Maven wrapper)
    $javaFound = $false
    try {
        $javaVersion = java -version 2>&1
        Write-Host "+ Java found" -ForegroundColor Green
        $javaFound = $true
    } catch {
        Write-Host "! Java not in PATH, checking for Maven wrapper..." -ForegroundColor Yellow
    }

    # 检查Maven或Maven wrapper
    try {
        $beDir = Join-Path $root 'backend'
        if (Test-Path (Join-Path $beDir 'mvnw')) {
            Write-Host "+ Maven wrapper found" -ForegroundColor Green
        } elseif (Get-Command mvn -ErrorAction SilentlyContinue) {
            Write-Host "+ Maven found" -ForegroundColor Green
        } else {
            Write-Host "! Maven not found" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "! Maven not found" -ForegroundColor Red
        return $false
    }

    # 检查Node.js
    try {
        $nodeVersion = node --version
        Write-Host "+ Node.js: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "! Node.js not found in PATH" -ForegroundColor Red
        return $false
    }

    return $true
}

function Start-AIService {
    Write-Host "`n=== AI Service Setup ===" -ForegroundColor Cyan
    $aiDir = Join-Path $root 'ai'
    $venvPython = Join-Path $aiDir '.venv/Scripts/python.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host "Creating AI virtual environment..." -ForegroundColor Blue
        & python -m venv (Join-Path $aiDir '.venv')
        Write-Host "Installing AI requirements (first time only)..." -ForegroundColor Blue
        & (Join-Path $aiDir '.venv/Scripts/pip.exe') install -r (Join-Path $aiDir 'requirements.txt') | Out-Null
    } else {
        Write-Host "AI virtual environment ready" -ForegroundColor Green
    }

    $command = "& '$venvPython' -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload"
    Start-BluePowerShellService "AI Service" $aiDir $command "Minimized"
    Write-Host "✓ AI Service: http://localhost:8000" -ForegroundColor White
    Start-Sleep -Seconds 5
}

function Start-Backend {
    Write-Host "`n=== Backend Service Setup ===" -ForegroundColor Cyan
    $beDir = Join-Path $root 'backend'

    # API Key检查
    $hasValidKey = $false
    if ($env:DEEPSEEK_API_KEY -and $env:DEEPSEEK_API_KEY -ne "") {
        $hasValidKey = $true
        Write-Host "+ DeepSeek API Key detected" -ForegroundColor Green
    }
    elseif ($env:KIMI_API_KEY -and $env:KIMI_API_KEY -ne "your_kimi_api_key_here") {
        $hasValidKey = $true
        Write-Host "+ KIMI API Key detected" -ForegroundColor Green
    }
    elseif ($env:QWEN_API_KEY -and $env:QWEN_API_KEY -ne "your_qwen_api_key_here") {
        $hasValidKey = $true
        Write-Host "+ Qwen API Key detected" -ForegroundColor Green
    }
    elseif ($env:ANTHROPIC_AUTH_TOKEN -and $env:ANTHROPIC_AUTH_TOKEN -ne "change-me") {
        $hasValidKey = $true
        Write-Host "+ GLM API Key detected" -ForegroundColor Green
    }

    if (-not $hasValidKey) {
        Write-Host "! Warning: No valid LLM API Key set" -ForegroundColor Yellow
        Write-Host "  Get free API key at https://platform.deepseek.com" -ForegroundColor Yellow
    }

    # 优先使用Maven wrapper，否则使用系统Maven
    if (Test-Path (Join-Path $beDir 'mvnw')) {
        $command = ".\mvnw spring-boot:run"
        Write-Host "Using Maven wrapper" -ForegroundColor Green
    } else {
        $command = "mvn spring-boot:run"
        Write-Host "Using system Maven" -ForegroundColor Green
    }

    Start-BluePowerShellService "Backend Service" $beDir $command "Minimized"
    Write-Host "✓ Backend Service: http://localhost:8080" -ForegroundColor White
    Start-Sleep -Seconds 8
}

function Start-Frontend {
    Write-Host "`n=== Frontend Service Setup ===" -ForegroundColor Cyan
    $feDir = Join-Path $root 'frontend'

    if (-not (Test-Path (Join-Path $feDir 'node_modules'))) {
        Write-Host "Installing frontend dependencies..." -ForegroundColor Blue
        # 先安装依赖，然后启动
        $command = "npm install; npm run dev"
        Start-BluePowerShellService "Frontend Service" $feDir $command "Minimized"
    } else {
        $command = "npm run dev"
        Start-BluePowerShellService "Frontend Service" $feDir $command "Minimized"
    }
    Write-Host "✓ Frontend Service: http://localhost:5173" -ForegroundColor White
    Start-Sleep -Seconds 6
}

function Start-Agent {
    Write-Host "`n=== Agent Service Setup ===" -ForegroundColor Cyan
    $agentDir = Join-Path $root 'agent'

    if (-not (Test-Path $agentDir)) {
        Write-Host "X Agent directory not found, skipping" -ForegroundColor Red
        return
    }

    $venvPython = Join-Path $agentDir '.venv/Scripts/python.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host "Creating Agent virtual environment..." -ForegroundColor Blue
        & python -m venv (Join-Path $agentDir '.venv')
        Write-Host "Installing Agent requirements (first time only)..." -ForegroundColor Blue
        & (Join-Path $agentDir '.venv/Scripts/pip.exe') install -r (Join-Path $agentDir 'requirements.txt') | Out-Null
    } else {
        Write-Host "Agent virtual environment ready" -ForegroundColor Green
    }

    $command = "& '$venvPython' main.py --realtime"
    Start-BluePowerShellService "Agent Service" $agentDir $command "Normal"
    Write-Host "✓ Agent Service: Gesture Detection (Normal Window)" -ForegroundColor White
}

# 主要启动流程
try {
    Write-Host "`n=== Starting YOLO-LLM Services ===" -ForegroundColor Cyan

    # 环境检查
    if (-not (Test-Environment)) {
        Write-Host "`nX Environment check failed. Please install missing dependencies." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }

    Write-Host "`n=== Starting All Services in Blue PowerShell Windows ===" -ForegroundColor Cyan

    # 按顺序启动服务
    Start-AIService
    Start-Backend
    Start-Frontend
    Start-Agent

    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "       All Services Started!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "🎯 All services running in BLUE PowerShell windows" -ForegroundColor White
    Write-Host ""
    Write-Host "📱 Web Interface:    http://localhost:5173" -ForegroundColor Cyan
    Write-Host "🔧 Backend API:      http://localhost:8080" -ForegroundColor Cyan
    Write-Host "🤖 AI Service:       http://localhost:8000" -ForegroundColor Cyan
    Write-Host "📚 API Docs:         http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "💡 Agent window shows real-time gesture detection" -ForegroundColor Yellow
    Write-Host "🛑 Use stop-all.ps1 to stop all services" -ForegroundColor Yellow
    Write-Host ""

    # 等待服务启动并检查状态
    Write-Host "Checking service health in 8 seconds..." -ForegroundColor Cyan
    Start-Sleep -Seconds 8

    $services = @(
        @{Name="Frontend"; Url="http://localhost:5173"},
        @{Name="Backend"; Url="http://localhost:8080"},
        @{Name="AI Service"; Url="http://localhost:8000"}
    )

    Write-Host "`n=== Service Health Check ===" -ForegroundColor Cyan
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.Url -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $($service.Name): $($service.Url) - RUNNING" -ForegroundColor Green
            } else {
                Write-Host "⏳ $($service.Name): $($service.Url) - STARTING" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⏳ $($service.Name): $($service.Url) - STARTING" -ForegroundColor Yellow
        }
    }

    Write-Host "`n🎉 YOLO-LLM startup complete!" -ForegroundColor Green

} catch {
    Write-Host "`n❌ Startup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Please check the error message above and retry" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
}