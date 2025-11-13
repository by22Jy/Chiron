# Stop YOLO-LLM dev servers by process/port (enhanced version)
# Usage: powershell -ExecutionPolicy Bypass -File .\stop-all.ps1

$ErrorActionPreference = 'SilentlyContinue'

Write-Host '========================================' -ForegroundColor Cyan
Write-Host "    Stop YOLO-LLM All Services" -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan

Write-Host "`nStopping development services..." -ForegroundColor Yellow

# 停止Agent Python进程 - 使用多种方法确保停止
Write-Host "Stopping Agent (Gesture Control)..." -ForegroundColor Blue
$agentStopped = $false

# 方法1: 通过命令行匹配
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

# 方法2: 通过窗口标题匹配
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

# 方法3: 直接查找Python进程
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
    Write-Host "+ Agent stopped" -ForegroundColor Green
} else {
    Write-Host "! No Agent processes found" -ForegroundColor Yellow
}

# 停止uvicorn进程 (AI服务)
$uvicornProcesses = Get-Process -Name uvicorn -ErrorAction SilentlyContinue
if ($uvicornProcesses) {
    Write-Host "Stopping AI Service (uvicorn)..." -ForegroundColor Blue
    $uvicornProcesses | Stop-Process -Force
    Write-Host "+ AI Service stopped" -ForegroundColor Green
}

# 停止Java进程 (Backend)
$javaProcesses = Get-Process -Name java -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -match 'spring-boot' -or $_.CommandLine -match 'spring-boot' }
if ($javaProcesses) {
    Write-Host "Stopping Backend Service (Spring Boot)..." -ForegroundColor Blue
    $javaProcesses | Stop-Process -Force
    Write-Host "+ Backend Service stopped" -ForegroundColor Green
}

# 停止Node进程 (Frontend)
$nodeProcesses = Get-Process -Name node -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -match 'vite|npm run dev' }
if ($nodeProcesses) {
    Write-Host "Stopping Frontend Service (Node.js)..." -ForegroundColor Blue
    $nodeProcesses | Stop-Process -Force
    Write-Host "+ Frontend Service stopped" -ForegroundColor Green
}

# 停止相关的PowerShell窗口 - 更精确的匹配
Write-Host "Stopping related PowerShell windows..." -ForegroundColor Blue
$psProcesses = Get-Process -Name powershell -ErrorAction SilentlyContinue |
    Where-Object {
        $_.MainWindowTitle -match 'mvn spring-boot:run|npm run dev|uvicorn|agent.*main\.py' -or
        $_.MainWindowTitle -match 'backend|ai\\|frontend\\|agent\\' -or
        $_.MainWindowTitle -eq 'Administrator: ' -and $_.CommandLine -match 'start-all\.ps1'
    }
if ($psProcesses) {
    Write-Host "Found PowerShell windows to close..." -ForegroundColor Blue
    $psProcesses | ForEach-Object {
        Write-Host "Closing: $($_.MainWindowTitle)" -ForegroundColor Blue
        # 先尝试优雅关闭
        $_.CloseMainWindow() | Out-Null
        Start-Sleep -Seconds 1
        # 如果还在运行就强制关闭
        if (!$_.HasExited) {
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }
    Write-Host "+ PowerShell windows closed" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "       所有服务已停止" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 额外检查端口占用
Write-Host "检查端口占用情况..." -ForegroundColor Yellow
$ports = @(8000, 8080, 5173)
foreach ($port in $ports) {
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("127.0.0.1", $port)
        if ($connection.Connected) {
            Write-Host "⚠️  端口 $port 仍被占用" -ForegroundColor Yellow
        }
        $connection.Close()
    } catch {
        Write-Host "✅ 端口 $port 已释放" -ForegroundColor Green
    }
}

Write-Host "`n停止完成！" -ForegroundColor Green