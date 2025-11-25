#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
独立语音控制测试脚本
避免protobuf版本冲突，直接测试语音功能
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加agent目录到路径
agent_dir = Path(__file__).parent / "agent"
sys.path.insert(0, str(agent_dir))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class StandaloneVoiceTest:
    """独立语音测试类"""

    def __init__(self):
        self.voice_controller = None

    async def test_voice_only(self):
        """测试纯语音控制功能"""
        print("\n" + "="*50)
        print("🎤 语音控制测试")
        print("="*50)

        try:
            from speech_controller import VoiceController

            # 创建语音控制器
            self.voice_controller = VoiceController()
            print("✅ 语音控制器创建成功")

            # 初始化
            print("🔧 正在初始化语音控制器...")
            initialized = await self.voice_controller.initialize_async()
            if initialized:
                print("✅ 语音控制器初始化成功")
            else:
                print("❌ 语音控制器初始化失败")
                return

            # 获取状态
            status = self.voice_controller.get_status()
            print(f"📊 控制器状态: {status}")

            # 开始语音监听
            print("\n🎧 开始语音监听...")
            print("请说出以下命令之一:")
            print("  - '打开记事本'")
            print("  - '左滑' 或 '向左滑动'")
            print("  - '右滑' 或 '向右滑动'")
            print("  - '调高音量'")
            print("  - '截图'")
            print("  - '打开浏览器'")
            print("  - '锁定屏幕'")
            print("\n按 Ctrl+C 停止监听...")

            await self.voice_controller.start_listening()

        except KeyboardInterrupt:
            print("\n⚠️ 用户中断测试")
        except ImportError as e:
            print(f"❌ 导入错误: {e}")
        except Exception as e:
            print(f"❌ 测试错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.voice_controller:
                try:
                    await self.voice_controller.stop_listening()
                    print("🔇 语音监听已停止")
                except:
                    pass

    async def test_command_parsing(self):
        """测试命令解析功能"""
        print("\n" + "="*50)
        print("🧪 命令解析测试")
        print("="*50)

        try:
            from speech_controller import VoiceController

            controller = VoiceController()
            print("✅ 语音控制器创建成功")

            # 测试命令列表
            test_commands = [
                "请帮我打开浏览器",
                "向左滑动",
                "右滑",
                "调高音量",
                "打开记事本",
                "锁定屏幕",
                "截图",
                "打开计算器",
                "关闭窗口",
                "播放音乐",
                "暂停视频",
                "最小化窗口",
                "最大化窗口"
            ]

            print("📝 测试命令解析:")
            print("-" * 40)

            recognized_count = 0
            for cmd in test_commands:
                try:
                    command = controller._parse_command(cmd)
                    if command:
                        print(f"✅ '{cmd}'")
                        print(f"   类型: {command.command_type}")
                        print(f"   参数: {command.parameters}")
                        print(f"   置信度: {command.confidence:.2f}")
                        recognized_count += 1
                    else:
                        print(f"❌ '{cmd}' -> 未识别")
                except Exception as e:
                    print(f"⚠️ '{cmd}' -> 错误: {e}")
                print()

            success_rate = (recognized_count / len(test_commands)) * 100
            print(f"📊 识别统计: {recognized_count}/{len(test_commands)} ({success_rate:.1f}%)")

        except Exception as e:
            print(f"❌ 命令解析测试失败: {e}")

    async def run_tests(self):
        """运行所有测试"""
        print("🚀 开始独立语音功能测试")

        # 测试1: 命令解析
        await self.test_command_parsing()

        # 测试2: 实时语音监听 (可选)
        choice = input("\n是否测试实时语音监听? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            await self.test_voice_only()

        print("\n🏁 语音测试完成")

async def main():
    """主函数"""
    try:
        tester = StandaloneVoiceTest()
        await tester.run_tests()
        return 0
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))