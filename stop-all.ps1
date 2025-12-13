# Stop YOLO-LLM All Services (Enhanced Version)
# Usage: powershell -ExecutionPolicy Bypass -File .\stop-all.ps1

# Set encoding to UTF-8
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = 'SilentlyContinue'

Write-Host '========================================' -ForegroundColor Cyan
Write-Host "    Stop YOLO-LLM All Services" -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan

Write-Host "`nStopping YOLO-LLM services..." -ForegroundColor Yellow

# Stop Agent Python processes - use multiple methods to ensure complete stop
Write-Host "Stopping Agent Services..." -ForegroundColor Blue
$agentStopped = $false

# Method 1: Command line matching
$agentProcesses = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'agent.*main\.py' }
if ($agentProcesses) {
    Write-Host "Found Agent processes via command line..." -ForegroundColor Blue
    $agentProcesses | ForEach-Object {
        Write-Host "Stopping Agent PID: $($_.ProcessId)" -ForegroundColor Blue
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
    $agentStopped = $true
}

# Method 2: Window title matching
$psAgentWindows = Get-Process powershell -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -match 'agent|main\.py|python.*agent' -or $_.ProcessName -eq 'python' }
if ($psAgentWindows) {
    Write-Host "Found Agent via PowerShell windows..." -ForegroundColor Blue
    $psAgentWindows | ForEach-Object {
        Write-Host "Closing Agent window: $($_.MainWindowTitle)" -ForegroundColor Blue
        $_.CloseMainWindow() | Out-Null
        Start-Sleep -Seconds 1
        if (!$_.HasExited) {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
    $agentStopped = $true
}

# Method 3: Direct Python process search
$pythonAgentProcesses = Get-Process python -ErrorAction SilentlyContinue |
    Where-Object { $_.MainWindowTitle -match 'agent|YOLO-LLM|main\.py' }
if ($pythonAgentProcesses) {
    Write-Host "Found Python Agent processes..." -ForegroundColor Blue
    $pythonAgentProcesses | ForEach-Object {
        Write-Host "Stopping Python Agent PID: $($_.Id)" -ForegroundColor Blue
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    $agentStopped = $true
}

if ($agentStopped) {
    Write-Host "[OK] Agent services stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] No Agent processes found" -ForegroundColor Yellow
}

# Stop uvicorn processes (AI Service)
$aiStopped = $false
$uvicornProcesses = Get-Process -Name uvicorn -ErrorAction SilentlyContinue
if ($uvicornProcesses) {
    Write-Host "Stopping AI Service (FastAPI)..." -ForegroundColor Blue
    $uvicornProcesses | ForEach-Object {
        Write-Host "Stopping AI Service PID: $($_.Id)" -ForegroundColor Blue
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    $aiStopped = $true
}

# Also stop Python processes running AI service
$pythonAIProcesses = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'uvicorn.*main:app' }
if ($pythonAIProcesses) {
    Write-Host "Found AI Service via command line..." -ForegroundColor Blue
    $pythonAIProcesses | ForEach-Object {
        Write-Host "Stopping AI Service PID: $($_.ProcessId)" -ForegroundColor Blue
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
    $aiStopped = $true
}

if ($aiStopped) {
    Write-Host "[OK] AI Service stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] No AI Service processes found" -ForegroundColor Yellow
}

# Stop Java processes (Backend)
$backendStopped = $false
$javaProcesses = Get-Process -Name java -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match 'spring-boot' -or $_.CommandLine -match 'spring-boot' }
if ($javaProcesses) {
    Write-Host "Stopping Backend Service (Spring Boot)..." -ForegroundColor Blue
    $javaProcesses | ForEach-Object {
        Write-Host "Stopping Backend PID: $($_.Id)" -ForegroundColor Blue
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    $backendStopped = $true
}

# Also check Maven processes
$mavenProcesses = Get-Process -Name mvn -ErrorAction SilentlyContinue
if ($mavenProcesses) {
    Write-Host "Stopping Maven processes..." -ForegroundColor Blue
    $mavenProcesses | ForEach-Object {
        Write-Host "Stopping Maven PID: $($_.Id)" -ForegroundColor Blue
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    $backendStopped = $true
}

if ($backendStopped) {
    Write-Host "[OK] Backend Service stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] No Backend Service processes found" -ForegroundColor Yellow
}

# Stop Node processes (Frontend)
$frontendStopped = $false
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'vite|npm run dev' }
if ($nodeProcesses) {
    Write-Host "Stopping Frontend Service (Node.js)..." -ForegroundColor Blue
    $nodeProcesses | ForEach-Object {
        Write-Host "Stopping Frontend PID: $($_.Id)" -ForegroundColor Blue
        Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
    }
    $frontendStopped = $true
}

if ($frontendStopped) {
    Write-Host "[OK] Frontend Service stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] No Frontend Service processes found" -ForegroundColor Yellow
}

# Stop related PowerShell windows - more precise matching
Write-Host "Stopping related PowerShell windows..." -ForegroundColor Blue
$psProcesses = Get-Process -Name powershell -ErrorAction SilentlyContinue |
    Where-Object {
        $_.MainWindowTitle -match 'mvn spring-boot:run|npm run dev|uvicorn|agent.*main\.py|start-all\.ps1' -or
        $_.MainWindowTitle -match 'backend|ai\\|frontend\\|agent\\|YOLO-LLM' -or
        $_.MainWindowTitle -match 'Text Control|Gesture Detection'
    }
if ($psProcesses) {
    Write-Host "Found PowerShell windows to close..." -ForegroundColor Blue
    $psProcesses | ForEach-Object {
        Write-Host "Closing: $($_.MainWindowTitle)" -ForegroundColor Blue
        # Try graceful close first
        $_.CloseMainWindow() | Out-Null
        Start-Sleep -Seconds 1
        # Force close if still running
        if (!$_.HasExited) {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "[OK] PowerShell windows closed" -ForegroundColor Green
} else {
    Write-Host "[INFO] No related PowerShell windows found" -ForegroundColor Yellow
}

# Stop MCP Server Python processes
$mcpStopped = $false
$mcpProcesses = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.CommandLine -match 'mcp.*main\.py' }
if ($mcpProcesses) {
    Write-Host "Stopping MCP Server..." -ForegroundColor Blue
    $mcpProcesses | ForEach-Object {
        Write-Host "Stopping MCP Server PID: $($_.ProcessId)" -ForegroundColor Blue
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
    $mcpStopped = $true
}

if ($mcpStopped) {
    Write-Host "[OK] MCP Server stopped" -ForegroundColor Green
} else {
    Write-Host "[INFO] No MCP Server processes found" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "       All Services Stopped Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Additional port occupation check
Write-Host "Checking port occupation status..." -ForegroundColor Yellow
$ports = @(8000, 8080, 8083, 5173)
$allPortsFree = $true
foreach ($port in $ports) {
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("127.0.0.1", $port)
        if ($connection.Connected) {
            Write-Host "[WARN] Port $port still occupied" -ForegroundColor Yellow
            $allPortsFree = $false
        }
        $connection.Close()
    } catch {
        Write-Host "[OK] Port $port released" -ForegroundColor Green
    }
}

if ($allPortsFree) {
    Write-Host "`n[SUCCESS] All ports released successfully!" -ForegroundColor Green
} else {
    Write-Host "`n[INFO] Some ports may still be in use. You can manually check:" -ForegroundColor Yellow
    Write-Host "  - Port 8000: AI Service (FastAPI)" -ForegroundColor Gray
    Write-Host "  - Port 8080: Backend Service (Spring Boot)" -ForegroundColor Gray
    Write-Host "  - Port 8083: MCP Server" -ForegroundColor Gray
    Write-Host "  - Port 5173: Frontend Service (Vue.js)" -ForegroundColor Gray
}

Write-Host "`nStop operation completed!" -ForegroundColor Green
Write-Host "You can now restart services with: .\start-all.ps1" -ForegroundColor Cyan