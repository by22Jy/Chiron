# YOLO-LLM 统一启动脚本 - 启动所有服务
# Unified YOLO-LLM Startup Script - Launch All Services
# Usage: 右键运行，或在终端执行: powershell -ExecutionPolicy Bypass -File .\start-all.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# 设置环境变量
$env:DB_URL = "jdbc:mysql://127.0.0.1:3306/yolo_platform?useUnicode=true&characterEncoding=utf8&serverTimezone=UTC"
$env:DB_USER = "root"
$env:DB_PASS = "Wangjiayi1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "      YOLO-LLM 智能控制系统启动" -ForegroundColor Cyan
Write-Host "    AI-Powered Gesture & Voice Control" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

function Test-DevelopmentEnvironment {
    Write-Host "`n=== 环境检测 ===" -ForegroundColor Cyan

    $envReady = $true

    # 检查Python
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "+ Python: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "! Python not found - Please install Python 3.8+" -ForegroundColor Red
        $envReady = $false
    }

    # 检查Java（允许Maven wrapper）
    try {
        $javaVersion = java -version 2>&1
        Write-Host "+ Java: Available" -ForegroundColor Green
    } catch {
        Write-Host "! Java not in PATH, checking Maven wrapper..." -ForegroundColor Yellow
    }

    # 检查Maven
    $beDir = Join-Path $root 'backend'
    if (Test-Path (Join-Path $beDir 'mvnw')) {
        Write-Host "+ Maven wrapper found" -ForegroundColor Green
    } elseif (Get-Command mvn -ErrorAction SilentlyContinue) {
        Write-Host "+ System Maven found" -ForegroundColor Green
    } else {
        Write-Host "! Maven not found" -ForegroundColor Red
        $envReady = $false
    }

    # 检查Node.js
    try {
        $nodeVersion = node --version
        Write-Host "+ Node.js: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "! Node.js not found - Please install Node.js 18+" -ForegroundColor Red
        $envReady = $false
    }

    return $envReady
}

function Test-MySQLConnection {
    Write-Host "`n=== 数据库连接测试 ===" -ForegroundColor Cyan
    try {
        $mysqlCmd = Get-Command mysql -ErrorAction SilentlyContinue
        if (-not $mysqlCmd) {
            Write-Host "- MySQL client not found (not critical)" -ForegroundColor Yellow
            Write-Host "  Backend will handle database connection" -ForegroundColor Yellow
            return
        }

        $result = & mysql -u $env:DB_USER -p$env:DB_PASS -e "USE yolo_platform;" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "! MySQL test failed (not critical)" -ForegroundColor Yellow
            Write-Host "  Backend will show connection status" -ForegroundColor Yellow
        } else {
            Write-Host "+ MySQL connection OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "- MySQL test skipped" -ForegroundColor Yellow
    }
}

function Start-AIService {
    Write-Host "`n=== AI Service 启动 (端口: 8000) ===" -ForegroundColor Cyan
    $aiDir = Join-Path $root 'ai'
    if (-not (Test-Path $aiDir)) {
        throw "AI directory not found: $aiDir"
    }

    $venvPython = Join-Path $aiDir '.venv/Scripts/python.exe'
    $venvPip    = Join-Path $aiDir '.venv/Scripts/pip.exe'
    $uvicornExe = Join-Path $aiDir '.venv/Scripts/uvicorn.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host "创建AI服务虚拟环境..." -ForegroundColor Blue
        & python -m venv (Join-Path $aiDir '.venv')
        Write-Host "安装AI服务依赖（首次安装）..." -ForegroundColor Blue
        & $venvPip install -r (Join-Path $aiDir 'requirements.txt') | Out-Null
    } else {
        Write-Host "AI服务虚拟环境就绪" -ForegroundColor Green
    }

    Write-Host "启动AI FastAPI服务..." -ForegroundColor Yellow
    $cmd = "`"$uvicornExe`" main:app --host 127.0.0.1 --port 8000 --reload"
    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$aiDir`"; $cmd" -WindowStyle Minimized | Out-Null
    Write-Host "✓ AI服务启动中: http://127.0.0.1:8000" -ForegroundColor Green
    Start-Sleep -Seconds 5
}

function Start-Backend {
    Write-Host "`n=== Backend Service 启动 (端口: 8080) ===" -ForegroundColor Cyan
    $beDir = Join-Path $root 'backend'
    if (-not (Test-Path $beDir)) {
        throw "Backend directory not found: $beDir"
    }

    # API Key检查
    $hasValidKey = $false
    if ($env:DEEPSEEK_API_KEY -and $env:DEEPSEEK_API_KEY -ne "your_deepseek_api_key_here") {
        $hasValidKey = $true
        Write-Host "+ DeepSeek API Key 已配置 (推荐)" -ForegroundColor Green
    }
    elseif ($env:KIMI_API_KEY -and $env:KIMI_API_KEY -ne "your_kimi_api_key_here") {
        $hasValidKey = $true
        Write-Host "+ KIMI API Key 已配置" -ForegroundColor Green
    }
    elseif ($env:QWEN_API_KEY -and $env:QWEN_API_KEY -ne "your_qwen_api_key_here") {
        $hasValidKey = $true
        Write-Host "+ Qwen API Key 已配置" -ForegroundColor Green
    }
    elseif ($env:ANTHROPIC_AUTH_TOKEN -and $env:ANTHROPIC_AUTH_TOKEN -ne "your_glm_api_key_here") {
        $hasValidKey = $true
        Write-Host "+ GLM API Key 已配置" -ForegroundColor Green
    }

    if (-not $hasValidKey) {
        Write-Host "! 警告: 未配置有效的LLM API Key" -ForegroundColor Yellow
        Write-Host "  请设置 DEEPSEEK_API_KEY 或其他API Key" -ForegroundColor Yellow
        Write-Host "  推荐获取免费API密钥: https://platform.deepseek.com" -ForegroundColor Yellow
    }

    # 优先使用Maven wrapper
    if (Test-Path (Join-Path $beDir 'mvnw')) {
        $cmd = '.\mvnw spring-boot:run'
        Write-Host "使用Maven wrapper启动" -ForegroundColor Green
    } else {
        $cmd = 'mvn spring-boot:run'
        Write-Host "使用系统Maven启动" -ForegroundColor Green
    }

    Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$beDir`"; $cmd" -WindowStyle Minimized | Out-Null
    Write-Host "✓ Backend服务启动中: http://127.0.0.1:8080" -ForegroundColor Green
    Start-Sleep -Seconds 8
}

function Start-Frontend {
    Write-Host "`n=== Frontend Service 启动 (端口: 5173) ===" -ForegroundColor Cyan
    $feDir = Join-Path $root 'frontend'
    if (-not (Test-Path $feDir)) {
        throw "Frontend directory not found: $feDir"
    }

    if (-not (Test-Path (Join-Path $feDir 'node_modules'))) {
        Write-Host "安装前端依赖..." -ForegroundColor Blue
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$feDir`"; npm install; npm run dev" -WindowStyle Minimized | Out-Null
    } else {
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$feDir`"; npm run dev" -WindowStyle Minimized | Out-Null
    }
    Write-Host "✓ Frontend服务启动中: http://127.0.0.1:5173" -ForegroundColor Green
    Start-Sleep -Seconds 6
}

function Start-Agent {
    Write-Host "`n=== Agent Service 启动 (手势+语音控制) ===" -ForegroundColor Cyan
    $agentDir = Join-Path $root 'agent'
    if (-not (Test-Path $agentDir)) {
        Write-Host "X Agent目录未找到，跳过Agent启动" -ForegroundColor Red
        return
    }

    $venvPython = Join-Path $agentDir '.venv/Scripts/python.exe'
    $venvPip    = Join-Path $agentDir '.venv/Scripts/pip.exe'

    if (-not (Test-Path $venvPython)) {
        Write-Host "创建Agent虚拟环境..." -ForegroundColor Blue
        & python -m venv (Join-Path $agentDir '.venv')
        Write-Host "安装Agent依赖（首次安装）..." -ForegroundColor Blue
        & $venvPip install -r (Join-Path $agentDir 'requirements.txt') | Out-Null
    } else {
        Write-Host "Agent虚拟环境就绪" -ForegroundColor Green
    }

    # 分离启动：先摄像头，后语音
    Write-Host "步骤1: 启动手势识别摄像头..." -ForegroundColor Yellow
    $cameraCmd = "`"$venvPython`" main.py --realtime"
    try {
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$agentDir`"; $cameraCmd" -WindowStyle Normal -ErrorAction Stop | Out-Null
        Write-Host "✓ 摄像头手势识别已启动" -ForegroundColor Green
        Write-Host "  查找窗口: 'YOLO-LLM Agent - Gesture Detection'" -ForegroundColor Cyan
    } catch {
        Write-Host "❌ 摄像头启动失败: $($_.Exception.Message)" -ForegroundColor Red
        return
    }

    # 等待摄像头初始化
    Write-Host "等待摄像头初始化..." -ForegroundColor Yellow
    for ($i = 8; $i -gt 0; $i--) {
        Write-Host -NoNewLine "`r  $i 秒后启动语音... "
        Start-Sleep -Seconds 1
    }
    Write-Host "`r✓ 摄像头就绪！                              " -ForegroundColor Green

    # 启动语音控制
    Write-Host "步骤2: 启动语音控制..." -ForegroundColor Yellow
    $voiceCmd = "`"$venvPython`" main.py --voice"
    try {
        Start-Process powershell -ArgumentList "-NoProfile","-NoExit","-ExecutionPolicy","Bypass","-Command","cd `"$agentDir`"; $voiceCmd" -WindowStyle Minimized -ErrorAction Stop | Out-Null
        Write-Host "✓ 语音控制已启动（后台运行）" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ 语音控制启动失败，但摄像头仍可工作" -ForegroundColor Yellow
    }

    Write-Host ""
    Write-Host "🎯 Agent状态:" -ForegroundColor White
    Write-Host "  📹 摄像头: 独立窗口运行" -ForegroundColor Green
    Write-Host "  🎤 语音: 后台进程运行" -ForegroundColor Green
    Write-Host "  💡 提示: 如看不到摄像头窗口，请检查任务栏" -ForegroundColor Cyan
}

function Test-ServiceHealth {
    Write-Host "`n=== 服务健康检查 ===" -ForegroundColor Cyan

    $services = @(
        @{Name="Frontend"; Url="http://localhost:5173"},
        @{Name="Backend"; Url="http://localhost:8080"},
        @{Name="AI Service"; Url="http://localhost:8000"}
    )

    $allHealthy = $true
    foreach ($service in $services) {
        try {
            $response = Invoke-WebRequest -Uri $service.Url -TimeoutSec 3 -UseBasicParsing -ErrorAction SilentlyContinue
            if ($response.StatusCode -eq 200) {
                Write-Host "✅ $($service.Name): $($service.Url) - 运行正常" -ForegroundColor Green
            } else {
                Write-Host "⏳ $($service.Name): $($service.Url) - 启动中" -ForegroundColor Yellow
                $allHealthy = $false
            }
        } catch {
            Write-Host "⏳ $($service.Name): $($service.Url) - 启动中" -ForegroundColor Yellow
            $allHealthy = $false
        }
    }

    return $allHealthy
}

# 主要启动流程
try {
    Write-Host "`n开始启动 YOLO-LLM 系统..." -ForegroundColor Cyan

    # 环境检测
    if (-not (Test-DevelopmentEnvironment)) {
        Write-Host "`n❌ 环境检测失败，请安装缺失的依赖" -ForegroundColor Red
        Write-Host "按任意键退出..." -ForegroundColor Yellow
        $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
        exit 1
    }

    # 数据库连接测试
    Test-MySQLConnection

    # 按顺序启动服务
    Start-AIService
    Start-Backend
    Start-Frontend
    Start-Agent

    # 等待服务启动并检查状态
    Write-Host "`n等待服务完全启动..." -ForegroundColor Cyan
    Start-Sleep -Seconds 8
    Test-ServiceHealth

    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host "       🎉 所有服务启动完成！" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📱 Web 界面:     http://localhost:5173" -ForegroundColor White
    Write-Host "🔧 后端API:     http://localhost:8080" -ForegroundColor White
    Write-Host "🤖 AI服务:       http://localhost:8000" -ForegroundColor White
    Write-Host "📚 API文档:     http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "🎯 Agent状态:" -ForegroundColor Cyan
    Write-Host "  📹 摄像头手势识别: 独立窗口运行" -ForegroundColor Green
    Write-Host "  🎤 语音控制: 后台监听命令" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 使用提示:" -ForegroundColor Yellow
    Write-Host "  • 摄像头窗口显示实时手势识别" -ForegroundColor Gray
    Write-Host "  • 语音控制支持中文命令" -ForegroundColor Gray
    Write-Host "  • 使用 .\stop-all.ps1 停止所有服务" -ForegroundColor Gray
    Write-Host ""

    Write-Host "✅ YOLO-LLM 系统启动完成！按任意键退出启动器..." -ForegroundColor Green
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

} catch {
    Write-Host "`n❌ 启动失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请检查错误信息并重试" -ForegroundColor Yellow
    Write-Host "按任意键退出..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}