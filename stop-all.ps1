# Stop common dev servers by process name/port (best-effort)
# Usage: powershell -ExecutionPolicy Bypass -File .\stop-all.ps1

$ErrorActionPreference = 'SilentlyContinue'

Write-Host 'Stopping dev processes (uvicorn, java, node)...'
Get-Process -Name uvicorn -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name java -ErrorAction SilentlyContinue | Stop-Process -Force
Get-Process -Name node -ErrorAction SilentlyContinue | Stop-Process -Force

# Stop agent python processes (match commandline)
Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'agent\\main.py' } |
    ForEach-Object { Stop-Process -Id $_.ProcessId -Force }

# Optionally kill powershell windows running the dev servers
Get-Process -Name powershell -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match 'mvn spring-boot:run|npm run dev|uvicorn' } | Stop-Process -Force

Write-Host 'Done.'


