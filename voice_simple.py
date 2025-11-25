#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import asyncio
from pathlib import Path

# 添加agent目录到路径
agent_dir = Path(__file__).parent / "agent"
sys.path.insert(0, str(agent_dir))

async def test_voice_parsing():
    """测试语音命令解析"""
    print("Voice Command Parsing Test")
    print("=" * 40)

    try:
        from speech_controller import VoiceController

        controller = VoiceController()
        print("Voice controller created successfully")

        # 测试命令
        commands = [
            "打开记事本",
            "左滑",
            "右滑",
            "调高音量",
            "锁定屏幕",
            "打开浏览器",
            "截图",
            "打开计算器"
        ]

        print("Testing command parsing:")
        recognized = 0
        for cmd in commands:
            try:
                result = controller._parse_command(cmd)
                if result:
                    print(f"{cmd} -> {result.command_type}: {result.parameters}")
                    recognized += 1
                else:
                    print(f"{cmd} -> NOT RECOGNIZED")
            except Exception as e:
                print(f"{cmd} -> ERROR: {e}")

        print(f"\nRecognition rate: {recognized}/{len(commands)} ({recognized/len(commands)*100:.1f}%)")

        return True

    except Exception as e:
        print(f"Test failed: {e}")
        return False

async def test_voice_initialization():
    """测试语音控制器初始化"""
    print("\nVoice Controller Initialization Test")
    print("=" * 40)

    try:
        from speech_controller import VoiceController

        controller = VoiceController()
        print("Voice controller created")

        # 异步初始化
        print("Initializing voice controller...")
        result = await controller.initialize_async()

        if result:
            print("Initialization successful!")

            # 获取状态
            status = controller.get_status()
            print(f"Status: {status}")

            print("Voice controller is ready for testing!")
            return True
        else:
            print("Initialization failed!")
            return False

    except Exception as e:
        print(f"Initialization test failed: {e}")
        return False

async def main():
    """主函数"""
    print("Voice Module Test Suite")
    print("=" * 50)

    # 测试1: 命令解析
    parsing_success = await test_voice_parsing()

    # 测试2: 初始化
    init_success = await test_voice_initialization()

    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Command Parsing: {'PASS' if parsing_success else 'FAIL'}")
    print(f"Initialization: {'PASS' if init_success else 'FAIL'}")

    if parsing_success and init_success:
        print("\nAll tests passed!")
        print("You can now use voice control with:")
        print("  python main.py --voice")
        print("  python main.py --realtime")
        return 0
    else:
        print("\nSome tests failed!")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)