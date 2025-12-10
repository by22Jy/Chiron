[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
Write-Host "Stopping all YOLO-LLM services..." -ForegroundColor Green

# Force stop all related processes
Stop-Process -Name "python" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "java" -Force -ErrorAction SilentlyContinue
Stop-Process -Name "node" -Force -ErrorAction SilentlyContinue

Write-Host "All services stopped" -ForegroundColor Green
Write-Host "To restart services, run: .\start-all.ps1" -ForegroundColor Cyan