# YOLO-LLM 服务停止脚本
Write-Host "========================================" -ForegroundColor Green
Write-Host "     YOLO-LLM 智能控制系统停止脚本" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 停止前端服务
Write-Host "停止前端服务 (端口 5173)..." -ForegroundColor Yellow
try {
    Get-Process node -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*5173*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ 前端服务已停止" -ForegroundColor Green
} catch {
    Write-Host "前端服务未运行" -ForegroundColor Gray
}

# 停止AI服务
Write-Host "停止AI服务 (端口 8000)..." -ForegroundColor Yellow
try {
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*8000*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ AI服务已停止" -ForegroundColor Green
} catch {
    Write-Host "AI服务未运行" -ForegroundColor Gray
}

# 停止后端服务
Write-Host "停止后端服务 (端口 8080)..." -ForegroundColor Yellow
try {
    Get-Process java -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*8080*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ 后端服务已停止" -ForegroundColor Green
} catch {
    Write-Host "后端服务未运行" -ForegroundColor Gray
}

# 停止MCP服务器
Write-Host "停止MCP服务器 (端口 8083)..." -ForegroundColor Yellow
try {
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*8083*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ MCP服务器已停止" -ForegroundColor Green
} catch {
    Write-Host "MCP服务器未运行" -ForegroundColor Gray
}

# 停止Agent相关进程
Write-Host "停止Agent相关进程..." -ForegroundColor Yellow
try {
    Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.CommandLine -like "*agent*"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "✅ Agent进程已停止" -ForegroundColor Green
} catch {
    Write-Host "Agent进程未运行" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "       所有服务已停止" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# 检查端口占用
Write-Host "检查端口占用情况..." -ForegroundColor Yellow
$ports = @(8000, 8080, 8083, 5173)

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

Write-Host ""
Write-Host "停止完成！" -ForegroundColor Green
Write-Host "提示: 如需重新启动服务，请运行 .\start-all.ps1" -ForegroundColor Cyan