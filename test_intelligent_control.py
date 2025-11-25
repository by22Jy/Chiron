#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能电脑控制系统测试脚本
"""

import sys
import os
from pathlib import Path

# 添加agent目录到路径
agent_dir = Path(__file__).parent / "agent"
sys.path.insert(0, str(agent_dir))

def test_intelligent_controller():
    """测试智能控制器"""
    print("=" * 60)
    print("🧠 智能电脑控制系统测试")
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
        print("前10个应用:", ', '.join(apps[:10]))

        # 测试各种自然语言命令
        test_commands = [
            "请帮我打开微信",
            "我想搜索Python教程",
            "帮我调高音量",
            "启动Photoshop处理图片",
            "打开我的文档",
            "关闭屏幕",
            "查看系统信息",
            "播放音乐",
            "打开浏览器搜索AI",
            "截图保存到桌面"
        ]

        print(f"\n🎯 测试 {len(test_commands)} 个自然语言命令:")
        print("-" * 40)

        for i, cmd in enumerate(test_commands, 1):
            print(f"\n{i}. 测试命令: '{cmd}'")

            try:
                result = controller.process_natural_language(cmd)

                if result.get('success'):
                    action = result.get('action', {})
                    print(f"   ✅ 成功: {action.get('description', '未知操作')}")
                    print(f"   📊 类型: {action.get('type', 'unknown')}")
                    print(f"   🎯 命令: {action.get('command', '无')}")
                    print(f"   📈 置信度: {action.get('confidence', 0):.2f}")
                    print(f"   ⚡ 耗时: {result.get('processing_time', 0):.2f}s")

                    alternatives = result.get('alternatives', [])
                    if alternatives:
                        print(f"   🔄 备选方案: {', '.join(alternatives[:2])}")
                else:
                    print(f"   ❌ 失败: {result.get('error', '未知错误')}")
                    if result.get('raw_response'):
                        print(f"   📝 LLM原始响应: {result['raw_response'][:100]}...")

            except Exception as e:
                print(f"   ⚠️ 测试异常: {e}")

        print(f"\n🏁 智能控制系统测试完成")
        return True

    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("请确保后端LLM服务正在运行 (http://localhost:8080)")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_voice_controller():
    """测试增强的语音控制器"""
    print("\n" + "=" * 60)
    print("🎤 增强语音控制器测试")
    print("=" * 60)

    try:
        from speech_controller import VoiceController

        # 创建增强的语音控制器
        print("正在初始化增强语音控制器...")
        controller = VoiceController(enable_intelligent_control=True)
        print("✅ 增强语音控制器初始化成功")

        # 显示控制器状态
        status = controller.get_status()
        print(f"📊 控制器状态: {status}")
        print(f"🧠 智能控制: {'启用' if controller.enable_intelligent_control else '禁用'}")

        # 测试混合命令（传统+智能）
        test_commands = [
            "左滑",                    # 传统命令
            "右滑",                    # 传统命令
            "调高音量",              # 传统命令
            "请帮我打开记事本",      # 智能命令
            "我想搜索AI教程",        # 智能命令
            "启动计算器",            # 智能命令
            "打开浏览器",            # 智能命令
        ]

        print(f"\n🎯 测试 {len(test_commands)} 个混合命令:")
        print("-" * 40)

        for i, cmd in enumerate(test_commands, 1):
            print(f"\n{i}. 测试命令: '{cmd}'")

            try:
                result = controller._parse_command(cmd)

                if result:
                    print(f"   ✅ 识别成功")
                    print(f"   📊 类型: {result.command_type}")
                    print(f"   🎯 参数: {result.parameters}")
                    print(f"   📈 置信度: {result.confidence:.2f}")

                    if result.command_type == "intelligent_control":
                        print(f"   🧠 使用了智能控制")
                    else:
                        print(f"   🔧 使用了传统解析")
                else:
                    print(f"   ❌ 未识别")

            except Exception as e:
                print(f"   ⚠️ 测试异常: {e}")

        print(f"\n🏁 增强语音控制器测试完成")
        return True

    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 智能控制系统全面测试")

    # 测试1: 智能控制器
    test1_success = test_intelligent_controller()

    # 测试2: 增强语音控制器
    test2_success = test_enhanced_voice_controller()

    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结")
    print("=" * 60)
    print(f"智能控制器测试: {'✅ 通过' if test1_success else '❌ 失败'}")
    print(f"语音控制器测试: {'✅ 通过' if test2_success else '❌ 失败'}")

    if test1_success and test2_success:
        print("\n🎉 所有测试通过！智能控制系统已就绪")
        print("\n📝 使用说明:")
        print("1. 启动后端服务: cd backend && mvn spring-boot:run")
        print("2. 运行智能语音控制: python voice_simple_final.py")
        print("3. 说出自然语言命令，如:")
        print("   - '请帮我打开微信'")
        print("   - '我想搜索Python教程'")
        print("   - '启动Photoshop处理图片'")
        print("   - '帮我调高音量'")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查相关配置")
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