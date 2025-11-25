#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版语音控制 - 避免所有编码问题
"""

import sys
import os
import time
from pathlib import Path

# 添加agent目录到路径
agent_dir = Path(__file__).parent / "agent"
sys.path.insert(0, str(agent_dir))

def main():
    """主函数"""
    print("语音控制测试程序")
    print("=" * 40)

    try:
        # 导入语音控制器
        from speech_controller import VoiceController
        print("导入语音控制器成功")

        # 创建控制器
        controller = VoiceController()
        print("创建语音控制器成功")

        # 初始化
        print("正在初始化语音识别...")
        if controller.initialize():
            print("语音控制器初始化成功！")
        else:
            print("语音控制器初始化失败！")
            return 1

        # 获取状态
        status = controller.get_status()
        print(f"控制器状态: {status}")

        # 测试命令解析
        print("\n命令解析测试:")
        test_commands = [
            "打开记事本",
            "向左滑动",
            "右滑",
            "调高音量",
            "锁定屏幕",
            "打开浏览器"
        ]

        success_count = 0
        for cmd in test_commands:
            try:
                result = controller._parse_command(cmd)
                if result:
                    print(f"  {cmd} -> {result.command_type}")
                    success_count += 1
                else:
                    print(f"  {cmd} -> 未识别")
            except Exception as e:
                print(f"  {cmd} -> 错误: {e}")

        print(f"\n解析成功率: {success_count}/{len(test_commands)} ({success_count/len(test_commands)*100:.1f}%)")

        # 询问是否启动实时语音控制
        choice = input("\n是否启动实时语音控制? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            print("\n启动语音控制...")
            print("支持的命令:")
            print("  - 打开记事本")
            print("  - 打开浏览器")
            print("  - 左滑/右滑")
            print("  - 调高音量")
            print("  - 锁定屏幕")
            print("\n按 Ctrl+C 停止")
            print("-" * 40)

            try:
                controller.start_listening()
                # 保持程序运行
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n用户停止语音控制")
                controller.stop_listening()
                print("语音控制已停止")
        else:
            print("测试完成")

        return 0

    except ImportError as e:
        print(f"导入错误: {e}")
        print("请确保已安装SpeechRecognition和pyautogui")
        return 1
    except Exception as e:
        print(f"程序错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(1)