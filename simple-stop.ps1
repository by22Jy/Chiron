Write-Host "停止所有YOLO-LLM服务..." -ForegroundColor Green

# 强制停止所有相关进程
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue

Write-Host "所有服务已停止" -ForegroundColor Green
Write-Host "重新启动请运行: .\start-all.ps1" -ForegroundColor Cyan