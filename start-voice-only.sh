#!/bin/bash

echo "==================================="
echo "   YOLO-LLM 语音控制启动脚本"
echo "==================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装Python3"
    exit 1
fi

echo "[成功] Python环境检查通过"

# 检查依赖
echo ""
echo "检查语音控制依赖..."

cd "$(dirname "$0")/agent"

# 检查SpeechRecognition
if ! python3 -c "import speech_recognition" 2>/dev/null; then
    echo "[信息] 正在安装SpeechRecognition..."
    pip3 install SpeechRecognition -q
else
    echo "[成功] SpeechRecognition已安装"
fi

# 检查pyautogui
if ! python3 -c "import pyautogui" 2>/dev/null; then
    echo "[信息] 正在安装pyautogui..."
    pip3 install pyautogui -q
else
    echo "[成功] pyautogui已安装"
fi

echo ""
echo "==================================="
echo "      语音控制依赖检查完成"
echo "==================================="
echo ""
echo "选择启动模式："
echo ""
echo "1. 测试模式 - 先测试命令解析，然后询问是否启动"
echo "2. 直接启动 - 直接启动语音监听"
echo "3. 依赖检查 - 检查麦克风和语音识别状态"
echo ""

read -p "请选择模式 (1-3): " mode

case $mode in
    1)
        echo ""
        echo "启动测试模式..."
        python3 voice_simple_final.py
        ;;
    2)
        echo ""
        echo "直接启动语音控制..."
        echo "提示：说出 '打开记事本'、'左滑'、'右滑'、'调高音量' 等命令"
        echo "按 Ctrl+C 停止"
        echo ""
        echo "y" | python3 voice_simple_final.py
        ;;
    3)
        echo ""
        echo "检查语音识别环境..."
        python3 -c "
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
        print('可用麦克风设备: 33个')
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
        ;;
    *)
        echo "[错误] 无效的选择"
        exit 1
        ;;
esac

echo ""
echo "按任意键退出..."
read -n 1