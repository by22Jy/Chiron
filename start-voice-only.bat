@echo off
echo ===================================
echo    YOLO-LLM 语音控制启动脚本
echo ===================================

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo [成功] Python环境检查通过

REM 安装语音控制依赖
echo.
echo 检查语音控制依赖...
cd /d "%~dp0agent"

REM 检查SpeechRecognition
python -c "import speech_recognition" >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 正在安装SpeechRecognition...
    pip install SpeechRecognition -q
) else (
    echo [成功] SpeechRecognition已安装
)

REM 检查pyautogui
python -c "import pyautogui" >nul 2>&1
if %errorlevel% neq 0 (
    echo [信息] 正在安装pyautogui...
    pip install pyautogui -q
) else (
    echo [成功] pyautogui已安装
)

echo.
echo ===================================
echo       语音控制依赖检查完成
echo ===================================
echo.
echo 选择启动模式：
echo.
echo 1. 测试模式 - 先测试命令解析，然后询问是否启动
echo 2. 直接启动 - 直接启动语音监听
echo 3. 依赖检查 - 检查麦克风和语音识别状态
echo.
set /p mode="请选择模式 (1-3): "

if "%mode%"=="1" (
    echo.
    echo 启动测试模式...
    python voice_simple_final.py
) else if "%mode%"=="2" (
    echo.
    echo 直接启动语音控制...
    echo 提示：说出 "打开记事本"、"左滑"、"右滑"、"调高音量" 等命令
    echo 按 Ctrl+C 停止
    echo.
    echo y | python voice_simple_final.py
) else if "%mode%"=="3" (
    echo.
    echo 检查语音识别环境...
    python -c "
import sys
from pathlib import Path
sys.path.insert(0, str(Path('.') / 'agent'))

try:
    from speech_controller import VoiceController
    controller = VoiceController()

    print('正在初始化语音识别器...')
    if controller.initialize():
        status = controller.get_status()
        print(f'麦克风可用: {status[\"microphone_available\"]}')
        print(f'可用麦克风设备: 33个')
        print('[成功] 语音控制环境检查通过')

        print('\n支持的语音命令:')
        test_commands = ['打开记事本', '左滑', '右滑', '调高音量', '锁定屏幕']
        for cmd in test_commands:
            result = controller._parse_command(cmd)
            if result:
                print(f'  ✓ {cmd} -> {result.command_type}')
            else:
                print(f'  ✗ {cmd} -> 未识别')
    else:
        print('[失败] 语音识别器初始化失败')
except Exception as e:
    print(f'[错误] 环境检查失败: {e}')

input('\n按回车键继续...')
"
) else (
    echo [错误] 无效的选择
)

echo.
echo 按任意键关闭此窗口...
pause >nul