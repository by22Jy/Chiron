#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能语音控制程序 - 集成LLM的自然语言电脑控制
"""

import sys
import os
import time
import signal
from pathlib import Path

# 添加agent目录到路径
agent_dir = Path(__file__).parent / "agent"
sys.path.insert(0, str(agent_dir))

class SmartVoiceController:
    """智能语音控制器"""

    def __init__(self):
        self.voice_controller = None
        self.is_running = False

    async def initialize(self):
        """初始化智能语音控制器"""
        try:
            from speech_controller import VoiceController

            print("🧠 正在创建智能语音控制器...")
            # 启用智能控制
            self.voice_controller = VoiceController(enable_intelligent_control=True)

            print("🔧 正在初始化语音识别...")
            if self.voice_controller.initialize():
                print("✅ 智能语音控制器初始化成功！")

                # 显示状态
                status = self.voice_controller.get_status()
                print(f"📊 控制器状态: {status}")
                print(f"🧠 智能控制: {'✅ 启用' if self.voice_controller.enable_intelligent_control else '❌ 禁用'}")

                return True
            else:
                print("❌ 语音控制器初始化失败！")
                return False

        except Exception as e:
            print(f"初始化错误: {e}")
            return False

    def start_smart_voice_control(self):
        """开始智能语音控制"""
        if not self.voice_controller:
            print("❌ 智能语音控制器未初始化")
            return

        print("\n" + "="*60)
        print("🎤 智能语音控制系统已启动")
        print("="*60)
        print("🧠 AI能力:")
        print("   • 自然语言理解 - 理解复杂的语音请求")
        print("   • 智能应用启动 - 自动匹配和启动应用程序")
        print("   • 系统控制 - 音量、屏幕、设置等")
        print("   • 网页搜索 - 语音搜索互联网内容")
        print("   • 文件操作 - 智能文件管理")
        print("")
        print("💡 语音命令示例:")
        print("   📱 应用控制:")
        print("     - '请帮我打开微信'")
        print("     - '启动Photoshop处理图片'")
        print("     - '关闭所有浏览器窗口'")
        print("")
        print("   🔍 搜索功能:")
        print("     - '搜索Python编程教程'")
        print("     - '帮我查找AI相关资料'")
        print("     - '在网上找找最新科技新闻'")
        print("")
        print("   ⚙️ 系统控制:")
        print("     - '调高音量'")
        print("     - '关闭屏幕'")
        print("     - '查看系统信息'")
        print("     - '截图保存到桌面'")
        print("")
        print("   📂 文件操作:")
        print("     - '打开我的文档'")
        print("     - '创建一个新的文件夹'")
        print("     - '显示最近下载的文件'")
        print("")
        print("🎯 传统命令依然支持:")
        print("   - '左滑' / '右滑'")
        print("   - '调高音量'")
        print("   - '锁定屏幕'")
        print("")
        print("🛑 按 Ctrl+C 停止智能语音控制")
        print("="*60)

        self.is_running = True

        try:
            self.voice_controller.start_listening()
            # 保持程序运行
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⚠️ 用户中断智能语音控制")
        finally:
            self.stop()

    def stop(self):
        """停止智能语音控制"""
        self.is_running = False
        if self.voice_controller:
            try:
                self.voice_controller.stop_listening()
                print("🔇 智能语音控制已停止")
            except:
                pass

    async def test_intelligent_commands(self):
        """测试智能命令解析"""
        if not self.voice_controller:
            print("❌ 智能语音控制器未初始化")
            return

        print("\n🧪 智能命令解析测试:")
        print("-" * 50)

        test_commands = [
            # 传统命令
            "左滑",
            "右滑",
            "调高音量",

            # 智能命令
            "请帮我打开微信",
            "我想搜索Python教程",
            "启动Photoshop",
            "打开我的文档",
            "调高屏幕亮度",
            "截图保存"
        ]

        for cmd in test_commands:
            try:
                result = self.voice_controller._parse_command(cmd)
                if result:
                    if result.command_type == "intelligent_control":
                        print(f"✨ {cmd} -> 🧠 智能控制 (置信度: {result.confidence:.2f})")
                    else:
                        print(f"🔧 {cmd} -> {result.command_type} (置信度: {result.confidence:.2f})")
                else:
                    print(f"❌ {cmd} -> 未识别")
            except Exception as e:
                print(f"⚠️ {cmd} -> 错误: {e}")

    def display_system_info(self):
        """显示系统信息"""
        try:
            from intelligent_controller import IntelligentController

            print("\n🖥️ 系统信息:")
            print("-" * 30)

            controller = IntelligentController()
            apps = controller.get_available_apps()

            print(f"📱 检测到应用程序: {len(apps)} 个")
            print("🔧 常用应用:", ', '.join(apps[:10]))

            if len(apps) > 10:
                print(f"   ... 还有 {len(apps) - 10} 个应用")

        except Exception as e:
            print(f"获取系统信息失败: {e}")

async def main():
    """主函数"""
    print("🚀 智能语音控制系统")
    print("=" * 50)

    # 检查信号处理
    def signal_handler(sig, frame):
        print('\n🛑 接收到中断信号，正在停止...')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    controller = SmartVoiceController()

    try:
        # 初始化
        if not await controller.initialize():
            print("❌ 初始化失败，退出")
            return 1

        # 显示系统信息
        controller.display_system_info()

        # 测试智能命令
        await controller.test_intelligent_commands()

        # 询问是否启动实时智能语音控制
        choice = input("\n🎤 是否启动实时智能语音控制? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            controller.start_smart_voice_control()
        else:
            print("✅ 测试完成")
            return 0

    except KeyboardInterrupt:
        print("\n⚠️ 程序被用户中断")
    except Exception as e:
        print(f"💥 程序错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await controller.stop()

    return 0

if __name__ == "__main__":
    try:
        import asyncio
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 程序被中断")
        sys.exit(1)
    except Exception as e:
        print(f"💥 意外错误: {e}")
        sys.exit(1)