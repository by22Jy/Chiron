# 强制PowerShell启动脚本
param(
    [switch]$Force = $false
)

# 强制使用PowerShell
if (-not $PSVersionTable.PSVersion) {
    Write-Host "This script must be run in PowerShell!" -ForegroundColor Red
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    YOLO-LLM PowerShell Startup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$env:DB_URL = "jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC"
$env:DB_USER = "root"
$env:DB_PASS = "Wangjiayi1"

# 检查API Key
$hasValidKey = $false
if ($env:DEEPSEEK_API_KEY -and $env:DEEPSEEK_API_KEY -ne "your_deepseek_api_key_here") {
    $hasValidKey = $true
    Write-Host "+ DeepSeek API Key detected" -ForegroundColor Green
}

Write-Host "`n=== Starting Services ===" -ForegroundColor Cyan

# 1. AI Service
Write-Host "Starting AI Service..." -ForegroundColor Yellow
$aiScript = {
    param($RootPath)
    $aiDir = "$RootPath\ai"
    $venvPython = "$aiDir\.venv\Scripts\python.exe"

    if (Test-Path $venvPython) {
        Write-Host "AI venv found, starting FastAPI..." -ForegroundColor Green
        Set-Location $aiDir
        & $venvPython -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
    } else {
        Write-Host "Creating AI venv and installing dependencies..." -ForegroundColor Blue
        python -m venv .venv
        .venv\Scripts\pip.exe install -r requirements.txt
        Write-Host "Starting FastAPI..." -ForegroundColor Green
        Set-Location $aiDir
        & $venvPython -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
    }
}

# 2. Backend Service
Write-Host "Starting Backend Service..." -ForegroundColor Yellow
$backendScript = {
    param($RootPath)
    $beDir = "$RootPath\backend"
    Set-Location $beDir
    & mvn spring-boot:run
}

# 3. Frontend Service
Write-Host "Starting Frontend Service..." -ForegroundColor Yellow
$frontendScript = {
    param($RootPath)
    $feDir = "$RootPath\frontend"
    Set-Location $feDir
    & npm run dev
}

# 4. Agent Service
Write-Host "Starting Agent Service..." -ForegroundColor Yellow
$agentScript = {
    param($RootPath)
    $agentDir = "$RootPath\agent"
    $venvPython = "$agentDir\.venv\Scripts\python.exe"

    if (Test-Path $venvPython) {
        Write-Host "Agent venv found, starting gesture detection..." -ForegroundColor Green
        Set-Location $agentDir
        & $venvPython main.py --realtime
    } else {
        Write-Host "Creating Agent venv and installing dependencies..." -ForegroundColor Blue
        python -m venv .venv
        .venv\Scripts\pip.exe install -r requirements.txt
        Write-Host "Starting gesture detection..." -ForegroundColor Green
        Set-Location $agentDir
        & $venvPython main.py --realtime
    }
}

# 启动所有服务
Write-Host "Launching services in separate PowerShell windows..." -ForegroundColor Cyan

Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","& { `$aiScript } '$root' }" -WindowStyle Minimized
Write-Host "✓ AI Service: http://localhost:8000" -ForegroundColor Green

Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","& { `$backendScript} '$root' }" -WindowStyle Minimized
Write-Host "✓ Backend Service: http://localhost:8080" -ForegroundColor Green

Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","& { `$frontendScript} '$root' }" -WindowStyle Minimized
Write-Host "✓ Frontend Service: http://localhost:5173" -ForegroundColor Green

Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","& { `$agentScript} '$root' }" -WindowStyle Normal
Write-Host "✓ Agent Service: Gesture Detection (Normal Window)" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "       All Services Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "All services are running in PowerShell windows" -ForegroundColor White
Write-Host "Check the Agent window for real-time gesture detection" -ForegroundColor White
Write-Host ""

# 等待几秒钟后检查服务状态
Start-Sleep -Seconds 8
Write-Host "Checking service status..." -ForegroundColor Cyan

$services = @(
    @{Name="Frontend"; Url="http://localhost:5173"},
    @{Name="Backend"; Url="http://localhost:8080"},
    @{Name="AI Service"; Url="http://localhost:8000"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-WebRequest -Uri $service.Url -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ $($service.Name): RUNNING" -ForegroundColor Green
        } else {
            Write-Host "⚠ $($service.Name): STARTING" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠ $($service.Name): STARTING" -ForegroundColor Yellow
    }
}