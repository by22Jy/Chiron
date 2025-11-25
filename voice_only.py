#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立语音控制脚本
避免protobuf版本冲突，专注于语音功能
"""

import sys
import os
import asyncio
import threading
import time
from pathlib import Path

# 添加agent目录到路径
agent_dir = Path(__file__).parent / "agent"
sys.path.insert(0, str(agent_dir))

class VoiceOnlyController:
    """纯语音控制，避免导入有冲突的模块"""

    def __init__(self):
        self.voice_controller = None
        self.is_running = False

    async def initialize(self):
        """初始化语音控制器"""
        try:
            from speech_controller import VoiceController

            print("正在创建语音控制器...")
            self.voice_controller = VoiceController()

            print("正在初始化语音识别...")
            if self.voice_controller.initialize():
                print("语音控制器初始化成功！")
                return True
            else:
                print("语音控制器初始化失败！")
                return False

        except Exception as e:
            print(f"初始化错误: {e}")
            return False

    async def start_voice_control(self):
        """开始语音控制"""
        if not self.voice_controller:
            print("语音控制器未初始化")
            return

        print("\n" + "="*50)
        print("语音控制已启动")
        print("支持的命令:")
        print("  - 打开记事本")
        print("  - 打开浏览器")
        print("  - 打开计算器")
        print("  - 左滑 / 向左滑动")
        print("  - 右滑 / 向右滑动")
        print("  - 调高音量")
        print("  - 锁定屏幕")
        print("  - 截图")
        print("\n按 Ctrl+C 停止")
        print("="*50)

        self.is_running = True

        try:
            await self.voice_controller.start_listening()
        except KeyboardInterrupt:
            print("\n用户中断语音控制")
        finally:
            await self.stop()

    async def stop(self):
        """停止语音控制"""
        self.is_running = False
        if self.voice_controller:
            try:
                await self.voice_controller.stop_listening()
                print("语音控制已停止")
            except:
                pass

    async def test_commands(self):
        """测试命令解析"""
        if not self.voice_controller:
            print("语音控制器未初始化")
            return

        test_commands = [
            "打开记事本",
            "向左滑动",
            "右滑",
            "调高音量",
            "锁定屏幕",
            "打开浏览器",
            "截图"
        ]

        print("\n命令解析测试:")
        print("-" * 30)

        for cmd in test_commands:
            try:
                result = self.voice_controller._parse_command(cmd)
                if result:
                    print(f"✓ {cmd} -> {result.command_type}")
                else:
                    print(f"✗ {cmd} -> 未识别")
            except Exception as e:
                print(f"✗ {cmd} -> 错误: {e}")

async def main():
    """主函数"""
    print("独立语音控制程序")
    print("="*30)

    controller = VoiceOnlyController()

    try:
        # 初始化
        if not await controller.initialize():
            print("初始化失败，退出")
            return 1

        # 测试命令解析
        await controller.test_commands()

        # 询问是否开始语音控制
        choice = input("\n是否开始语音控制? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            await controller.start_voice_control()
        else:
            print("测试完成")
            return 0

    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await controller.stop()

    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n程序被中断")
        sys.exit(1)