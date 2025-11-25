#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能控制系统离线测试 - 不依赖LLM服务
"""

import sys
import os
from pathlib import Path

# 添加agent目录到路径
agent_dir = Path(__file__).parent / "agent"
sys.path.insert(0, str(agent_dir))

def test_intelligent_controller_offline():
    """离线测试智能控制器基本功能"""
    print("=" * 60)
    print("🧠 智能控制系统离线测试")
    print("=" * 60)

    try:
        from intelligent_controller import IntelligentController

        # 创建智能控制器
        print("正在初始化智能控制器...")
        controller = IntelligentController()
        print("✅ 智能控制器初始化成功")

        # 显示检测到的应用
        apps = controller.get_available_apps()
        print(f"\n📱 检测到 {len(apps)} 个应用程序:")
        print("所有应用:", ', '.join(apps))

        # 显示系统信息
        system_info = controller._get_system_info()
        print(f"\n🖥️ 系统信息:")
        print(f"平台: {system_info.get('platform', 'Unknown')}")
        print(f"CPU核心: {system_info.get('cpu_count', 'Unknown')}")
        print(f"内存: {system_info.get('memory_total', 0) / 1024 / 1024 / 1024:.1f} GB")

        # 测试离线命令处理
        print(f"\n🧪 离线功能测试:")
        print("-" * 40)

        # 1. 测试应用检测
        test_apps = ["微信", "chrome", "记事本", "计算器"]
        print("📱 应用检测测试:")
        for app in test_apps:
            found = any(app.lower() in installed_app.lower() for installed_app in apps)
            status = "✅" if found else "❌"
            print(f"   {status} {app}")

        # 2. 测试系统操作（不依赖LLM）
        print(f"\n⚙️ 系统操作测试:")

        # 测试文件操作
        try:
            import webbrowser
            print("   ✅ 网页浏览器模块可用")
        except ImportError:
            print("   ❌ 网页浏览器模块不可用")

        # 测试文件系统操作
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            print(f"   ✅ 桌面路径: {desktop_path}")
        except Exception as e:
            print(f"   ❌ 桌面路径获取失败: {e}")

        # 3. 模拟LLM响应（用于测试解析逻辑）
        print(f"\n🎯 命令解析测试 (模拟LLM响应):")

        # 模拟LLM返回的JSON响应
        mock_responses = {
            "打开微信": {
                "action_type": "open_app",
                "command": "wechat.exe",
                "description": "启动微信应用",
                "confidence": 0.9,
                "safety_level": "safe"
            },
            "调高音量": {
                "action_type": "system_control",
                "command": "nircmd.exe setsysvolume 65535",
                "description": "调高系统音量",
                "confidence": 0.95,
                "safety_level": "safe"
            },
            "搜索Python教程": {
                "action_type": "web_search",
                "command": "https://www.google.com/search?q=Python教程",
                "description": "搜索Python编程教程",
                "confidence": 0.85,
                "safety_level": "safe"
            }
        }

        for command, mock_data in mock_responses.items():
            try:
                # 模拟LLM响应
                import json
                mock_json = json.dumps(mock_data, ensure_ascii=False)

                # 测试解析逻辑
                action = controller._parse_llm_response(mock_json)
                if action:
                    print(f"   ✅ '{command}' -> {action.action_type}: {action.description}")
                else:
                    print(f"   ❌ '{command}' -> 解析失败")
            except Exception as e:
                print(f"   ⚠️ '{command}' -> 错误: {e}")

        return True

    except Exception as e:
        print(f"❌ 离线测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_controller_integration():
    """测试语音控制器集成"""
    print("\n" + "=" * 60)
    print("🎤 语音控制器集成测试")
    print("=" * 60)

    try:
        from speech_controller import VoiceController

        # 创建语音控制器
        print("正在创建语音控制器...")
        controller = VoiceController(enable_intelligent_control=False)  # 禁用LLM以避免依赖
        print("✅ 语音控制器创建成功")

        # 显示智能控制状态
        print(f"🧠 智能控制启用: {controller.enable_intelligent_control}")
        print(f"🔧 智能控制器可用: {controller.intelligent_controller is not None}")

        # 测试传统命令解析
        print(f"\n🔧 传统命令解析测试:")
        traditional_commands = [
            "左滑",
            "右滑",
            "调高音量",
            "打开记事本",
            "锁定屏幕"
        ]

        for cmd in traditional_commands:
            try:
                result = controller._parse_command(cmd)
                if result:
                    print(f"   ✅ '{cmd}' -> {result.command_type} (置信度: {result.confidence:.2f})")
                else:
                    print(f"   ❌ '{cmd}' -> 未识别")
            except Exception as e:
                print(f"   ⚠️ '{cmd}' -> 错误: {e}")

        return True

    except Exception as e:
        print(f"❌ 语音控制器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 智能控制系统离线测试套件")

    # 测试1: 智能控制器离线功能
    test1_success = test_intelligent_controller_offline()

    # 测试2: 语音控制器集成
    test2_success = test_voice_controller_integration()

    # 总结
    print("\n" + "=" * 60)
    print("📊 离线测试结果总结")
    print("=" * 60)
    print(f"智能控制器离线测试: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"语音控制器集成测试: {'✅ 通过' if test2_success else '❌ 失败'}")

    if test1_success and test2_success:
        print("\n🎉 离线测试通过！")
        print("\n📝 下一步操作:")
        print("1. 确保后端LLM服务正在运行")
        print("2. 检查API密钥配置 (KIMI_API_KEY 或 QWEN_API_KEY)")
        print("3. 运行在线测试: python test_intelligent_control.py")
        print("4. 启动智能语音控制: python smart_voice_control.py")
        return 0
    else:
        print("\n⚠️ 离线测试失败，请检查基础环境")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"💥 程序异常: {e}")
        sys.exit(1)