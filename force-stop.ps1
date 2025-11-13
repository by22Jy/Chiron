# Force Stop YOLO-LLM All Services - Emergency Script
# Usage: powershell -ExecutionPolicy Bypass -File .\force-stop.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$ErrorActionPreference = 'SilentlyContinue'

Write-Host '========================================' -ForegroundColor Red
Write-Host "  FORCE STOP YOLO-LLM ALL SERVICES" -ForegroundColor Red
Write-Host "========================================" -ForegroundColor Red
Write-Host ""
Write-Host "! This script will forcefully terminate all YOLO-LLM related processes" -ForegroundColor Yellow
Write-Host "! Use with caution - may close unrelated processes" -ForegroundColor Yellow
Write-Host ""

$confirmation = Read-Host "Are you sure you want to force stop all services? (y/N)"
if ($confirmation -notmatch '^[Yy]') {
    Write-Host "Operation cancelled." -ForegroundColor Green
    exit 0
}

Write-Host "`nForce stopping all YOLO-LLM processes..." -ForegroundColor Red

# 强制停止所有相关进程的进程名列表
$processNames = @(
    'python',     # Python processes (Agent, AI Service)
    'uvicorn',    # FastAPI uvicorn
    'java',       # Spring Boot Backend
    'node',       # Node.js Frontend
    'mvn',        # Maven
    'powershell'  # PowerShell windows (will be filtered)
)

foreach ($processName in $processNames) {
    $processes = Get-Process -Name $processName -ErrorAction SilentlyContinue

    if ($processes) {
        Write-Host "`nChecking $processName processes..." -ForegroundColor Blue

        foreach ($process in $processes) {
            $shouldStop = $false
            $reason = ""

            # 检查进程是否与YOLO-LLM相关
            if ($process.MainWindowTitle -match 'YOLO-LLM|agent|main\.py|uvicorn|spring-boot|npm.*dev|vite') {
                $shouldStop = $true
                $reason = "Window title matches"
            }
            elseif ($processName -eq 'python' -and $process.CommandLine -match 'agent.*main\.py|uvicorn.*main:app') {
                $shouldStop = $true
                $reason = "Command line matches"
            }
            elseif ($processName -eq 'powershell' -and $process.CommandLine -match 'start-all\.ps1|agent.*main\.py|backend|ai\\|frontend\\|agent\\') {
                $shouldStop = $true
                $reason = "PowerShell script matches"
            }
            elseif ($processName -eq 'uvicorn') {
                $shouldStop = $true
                $reason = "uvicorn process"
            }
            elseif ($processName -eq 'java' -and $process.CommandLine -match 'spring-boot') {
                $shouldStop = $true
                $reason = "Spring Boot process"
            }
            elseif ($processName -eq 'node' -and $process.CommandLine -match 'vite|npm.*dev') {
                $shouldStop = $true
                $reason = "Node.js dev process"
            }

            if ($shouldStop) {
                Write-Host "  Stopping $($processName) PID: $($process.Id) - $reason" -ForegroundColor Red
                try {
                    # 先尝试优雅关闭
                    $process.CloseMainWindow() | Out-Null
                    Start-Sleep -Milliseconds 500

                    if (!$process.HasExited) {
                        # 强制终止
                        Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                        Start-Sleep -Milliseconds 200
                    }

                    if ($process.HasExited) {
                        Write-Host "    + Stopped successfully" -ForegroundColor Green
                    } else {
                        Write-Host "    X Failed to stop" -ForegroundColor Red
                    }
                } catch {
                    Write-Host "    X Error stopping process: $($_.Exception.Message)" -ForegroundColor Red
                }
            }
        }
    }
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "       Force stop completed" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# 额外检查并清理顽固进程
Write-Host "`nChecking for stubborn processes..." -ForegroundColor Yellow

# 检查端口占用
$ports = @(8000, 8080, 5173)
$portsStillOccupied = @()

foreach ($port in $ports) {
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("127.0.0.1", $port)
        if ($connection.Connected) {
            $portsStillOccupied += $port
            Write-Host "Port $port is still occupied" -ForegroundColor Yellow
        }
        $connection.Close()
    } catch {
        Write-Host "Port $port is free" -ForegroundColor Green
    }
}

if ($portsStillOccupied.Count -gt 0) {
    Write-Host ""
    Write-Host "! Some ports are still occupied. You may need to:" -ForegroundColor Yellow
    Write-Host "  1. Restart your computer" -ForegroundColor Yellow
    Write-Host "  2. Manually kill processes using Task Manager" -ForegroundColor Yellow
    Write-Host "  3. Wait a few seconds for processes to fully terminate" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "+ All YOLO-LLM ports are now free" -ForegroundColor Green
}

Write-Host ""
Write-Host "Force stop operation completed." -ForegroundColor Green
Write-Host "You can now safely restart the services." -ForegroundColor Green