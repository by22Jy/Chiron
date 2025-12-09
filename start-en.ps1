# YOLO-LLM Startup Script (English Version)
# Usage: powershell -ExecutionPolicy Bypass -File .\start-en.ps1

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# Set environment variables
$env:DB_URL = "jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC"
$env:DB_USER = "root"
$env:DB_PASS = "Wangjiayi1"
$env:MCP_SERVER_URL = "http://localhost:8083"

# API Keys
$env:NEWS_API_KEY = $env:NEWS_API_KEY
$env:WEATHER_API_KEY = $env:WEATHER_API_KEY
$env:BREVO_API_KEY = $env:BREVO_API_KEY
$env:KIMI_API_KEY = $env:KIMI_API_KEY
$env:QWEN_API_KEY = $env:QWEN_API_KEY

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       YOLO-LLM Startup Script" -ForegroundColor Cyan
Write-Host "    Enterprise AI Control Platform" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

function Test-Environment {
    Write-Host "`n=== Environment Check ===" -ForegroundColor Cyan

    $envReady = $true

    try {
        $pythonVersion = python --version 2>&1
        Write-Host "[OK] Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Python not found" -ForegroundColor Red
        $envReady = $false
    }

    try {
        $nodeVersion = node --version
        Write-Host "[OK] Node.js: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Node.js not found" -ForegroundColor Red
        $envReady = $false
    }

    try {
        $javaVersion = java -version 2>&1
        Write-Host "[OK] Java: Available" -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Java not in PATH" -ForegroundColor Yellow
    }

    return $envReady
}

function Start-MCPServer {
    Write-Host "`n=== Starting MCP Server (Port: 8083) ===" -ForegroundColor Cyan
    $mcpDir = Join-Path $root 'mcp'

    if (-not (Test-Path $mcpDir)) {
        throw "MCP directory not found: $mcpDir"
    }

    if ($env:NEWS_API_KEY) {
        Write-Host "[OK] NEWS_API_KEY configured" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] NEWS_API_KEY not configured" -ForegroundColor Yellow
    }

    if ($env:WEATHER_API_KEY) {
        Write-Host "[OK] WEATHER_API_KEY configured" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] WEATHER_API_KEY not configured" -ForegroundColor Yellow
    }

    if ($env:BREVO_API_KEY) {
        Write-Host "[OK] BREVO_API_KEY configured" -ForegroundColor Green
    } else {
        Write-Host "[WARNING] BREVO_API_KEY not configured" -ForegroundColor Yellow
    }

    $venvPython = Join-Path $mcpDir '.venv/Scripts/python.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host "[INFO] Creating MCP virtual environment..." -ForegroundColor Blue
        & python -m venv (Join-Path $mcpDir '.venv')
        & (Join-Path $mcpDir '.venv/Scripts/pip.exe') install -r (Join-Path $mcpDir 'requirements.txt') | Out-Null
    }

    Write-Host "[INFO] Starting Enhanced MCP Server..." -ForegroundColor Yellow
    $cmd = "`"$venvPython`" enhanced_mcp_server.py"
    $psArgs = @("-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd `"$mcpDir`"; $cmd")
    Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized | Out-Null
    Write-Host "[SUCCESS] MCP Server starting: http://localhost:8083" -ForegroundColor Green
    Start-Sleep -Seconds 5
}

function Start-Backend {
    Write-Host "`n=== Starting Backend Service (Port: 8080) ===" -ForegroundColor Cyan
    $beDir = Join-Path $root 'backend'

    if (-not (Test-Path $beDir)) {
        throw "Backend directory not found: $beDir"
    }

    if (Test-Path (Join-Path $beDir 'mvnw')) {
        $cmd = '.\mvnw spring-boot:run'
        Write-Host "[INFO] Using Maven wrapper" -ForegroundColor Green
    } else {
        $cmd = 'mvn spring-boot:run'
        Write-Host "[INFO] Using system Maven" -ForegroundColor Green
    }

    $psArgs = @("-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd `"$beDir`"; $cmd")
    Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized | Out-Null
    Write-Host "[SUCCESS] Backend starting: http://localhost:8080" -ForegroundColor Green
    Start-Sleep -Seconds 8
}

function Start-AIService {
    Write-Host "`n=== Starting AI Service (Port: 8000) ===" -ForegroundColor Cyan
    $aiDir = Join-Path $root 'ai'

    if (-not (Test-Path $aiDir)) {
        throw "AI directory not found: $aiDir"
    }

    $venvPython = Join-Path $aiDir '.venv/Scripts/python.exe'
    $uvicornExe = Join-Path $aiDir '.venv/Scripts/uvicorn.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host "[INFO] Creating AI virtual environment..." -ForegroundColor Blue
        & python -m venv (Join-Path $aiDir '.venv')
        & (Join-Path $aiDir '.venv/Scripts/pip.exe') install -r (Join-Path $aiDir 'requirements.txt') | Out-Null
    }

    Write-Host "[INFO] Starting AI FastAPI service..." -ForegroundColor Yellow
    $cmd = "`"$uvicornExe`" main:app --host 127.0.0.1 --port 8000 --reload"
    $psArgs = @("-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd `"$aiDir`"; $cmd")
    Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized | Out-Null
    Write-Host "[SUCCESS] AI Service starting: http://127.0.0.1:8000" -ForegroundColor Green
    Start-Sleep -Seconds 5
}

function Start-Frontend {
    Write-Host "`n=== Starting Frontend Service (Port: 5173) ===" -ForegroundColor Cyan
    $feDir = Join-Path $root 'frontend'

    if (-not (Test-Path $feDir)) {
        throw "Frontend directory not found: $feDir"
    }

    if (-not (Test-Path (Join-Path $feDir 'node_modules'))) {
        Write-Host "[INFO] Installing frontend dependencies..." -ForegroundColor Blue
        $psArgs = @("-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd `"$feDir`"; npm install; npm run dev")
        Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized | Out-Null
    } else {
        $psArgs = @("-NoProfile", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", "cd `"$feDir`"; npm run dev")
        Start-Process powershell -ArgumentList $psArgs -WindowStyle Minimized | Out-Null
    }

    Write-Host "[SUCCESS] Frontend starting: http://127.0.0.1:5173" -ForegroundColor Green
    Start-Sleep -Seconds 6
}

function Test-Services {
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
                Write-Host "[OK] $($service.Name): $($service.Url)" -ForegroundColor Green
            } else {
                Write-Host "[PENDING] $($service.Name): $($service.Url)" -ForegroundColor Yellow
                $allHealthy = $false
            }
        } catch {
            Write-Host "[PENDING] $($service.Name): $($service.Url)" -ForegroundColor Yellow
            $allHealthy = $false
        }
    }

    return $allHealthy
}

try {
    Write-Host "`nStarting YOLO-LLM system..." -ForegroundColor Cyan

    if (-not (Test-Environment)) {
        Write-Host "`n[ERROR] Environment check failed" -ForegroundColor Red
        Write-Host "Press any key to exit..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }

    # Start all services
    Start-MCPServer
    Start-Backend
    Start-AIService
    Start-Frontend

    # Wait and check
    Write-Host "`nWaiting for services to start..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    Test-Services

    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "        All Services Started!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Service URLs:" -ForegroundColor White
    Write-Host "- MCP Server:   http://localhost:8083" -ForegroundColor White
    Write-Host "- Frontend:     http://localhost:5173" -ForegroundColor White
    Write-Host "- Backend:      http://localhost:8080" -ForegroundColor White
    Write-Host "- AI Service:    http://localhost:8000" -ForegroundColor White
    Write-Host "- API Docs:      http://localhost:8000/docs" -ForegroundColor White
    Write-Host "- Health Check:  http://localhost:8083/health" -ForegroundColor White
    Write-Host ""
    Write-Host "Press any key to exit..." -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

} catch {
    Write-Host "`n[ERROR] Startup failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Press any key to exit..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}