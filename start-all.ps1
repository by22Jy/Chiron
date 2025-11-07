# PowerShell script to start AI (FastAPI), Backend (SpringBoot), and Frontend (Vite+Vue)
# Usage: Right-click Run with PowerShell, or: powershell -ExecutionPolicy Bypass -File .\start-all.ps1

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

function Start-AIService {
    $aiDir = Join-Path $root 'ai'
    if (-not (Test-Path $aiDir)) { throw "AI directory not found: $aiDir" }
    $venvPython = Join-Path $aiDir '.venv/Scripts/python.exe'
    $venvPip    = Join-Path $aiDir '.venv/Scripts/pip.exe'
    $uvicornExe = Join-Path $aiDir '.venv/Scripts/uvicorn.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host 'Creating Python venv for AI...'
        & python -m venv (Join-Path $aiDir '.venv')
    }
    Write-Host 'Installing AI requirements (if needed)...'
    & $venvPip install -r (Join-Path $aiDir 'requirements.txt') | Out-Null

    $cmd = "`"$uvicornExe`" main:app --host 127.0.0.1 --port 8000 --reload"
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$aiDir`"; $cmd" -WindowStyle Minimized | Out-Null
    Write-Host 'AI service starting on http://127.0.0.1:8000'
}

function Start-Backend {
    $beDir = Join-Path $root 'backend'
    if (-not (Test-Path $beDir)) { throw "Backend directory not found: $beDir" }
    $cmd = 'mvn spring-boot:run'
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$beDir`"; $cmd" -WindowStyle Minimized | Out-Null
    Write-Host 'Backend starting on http://127.0.0.1:8080'
}

function Start-Frontend {
    $feDir = Join-Path $root 'frontend'
    if (-not (Test-Path $feDir)) { throw "Frontend directory not found: $feDir" }
    if (-not (Test-Path (Join-Path $feDir 'node_modules'))) {
        Write-Host 'Installing frontend dependencies (npm install)...'
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$feDir`"; npm install; npm run dev" -WindowStyle Minimized | Out-Null
    } else {
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-Command","cd `"$feDir`"; npm run dev" -WindowStyle Minimized | Out-Null
    }
    Write-Host 'Frontend starting on http://127.0.0.1:5173'
}

Write-Host '=== Starting services ==='
Start-AIService
Start-Backend
Start-Frontend
Write-Host 'All services launched in separate PowerShell windows.'


