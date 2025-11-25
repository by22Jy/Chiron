#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用模拟LLM服务器测试智能控制
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# 添加agent目录到路径
agent_dir = Path(__file__).parent / "agent"
sys.path.insert(0, str(agent_dir))

def start_mock_server():
    """启动模拟LLM服务器"""
    print("🤖 启动模拟LLM服务器...")

    try:
        # 在后台启动模拟服务器
        process = subprocess.Popen([
            sys.executable, "mock_llm_server.py"
        ], cwd=agent_dir)

        # 等待服务器启动
        time.sleep(3)

        # 检查服务器是否正常运行
        try:
            import requests
            response = requests.get("http://localhost:8081/health", timeout=5)
            if response.status_code == 200:
                print("✅ 模拟LLM服务器启动成功")
                return process
            else:
                print("❌ 模拟LLM服务器启动失败")
                process.terminate()
                return None
        except Exception as e:
            print(f"❌ 无法连接到模拟服务器: {e}")
            process.terminate()
            return None

    except Exception as e:
        print(f"❌ 启动模拟服务器失败: {e}")
        return None

def test_intelligent_control_with_mock():
    """使用模拟服务器测试智能控制"""
    try:
        from intelligent_controller import IntelligentController

        # 创建使用模拟服务器的控制器
        print("🧠 创建智能控制器 (连接到模拟服务器)...")
        controller = IntelligentController(backend_url="http://localhost:8081")
        print("✅ 智能控制器创建成功")

        # 测试命令列表
        test_commands = [
            "打开记事本",
            "启动微信",
            "搜索Python教程",
            "调高音量",
            "截图",
            "播放音乐",
            "打开我的文档",
            "关闭屏幕"
        ]

        print(f"\n🎯 测试 {len(test_commands)} 个智能命令:")
        print("-" * 50)

        success_count = 0
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

                    if result.get('processing_time', 0) > 1.0:
                        print("   ⚠️  响应较慢，可能是网络问题")

                    success_count += 1
                else:
                    print(f"   ❌ 失败: {result.get('error', '未知错误')}")

            except Exception as e:
                print(f"   ⚠️ 测试异常: {e}")

        print(f"\n📊 测试结果: {success_count}/{len(test_commands)} 成功")
        print(f"成功率: {success_count/len(test_commands)*100:.1f}%")

        return success_count == len(test_commands)

    except Exception as e:
        print(f"❌ 智能控制测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_controller_with_mock():
    """测试语音控制器集成"""
    try:
        from speech_controller import VoiceController

        print("\n🎤 测试语音控制器 (使用模拟服务器)...")

        # 创建连接到模拟服务器的语音控制器
        controller = VoiceController(
            backend_url="http://localhost:8081",
            enable_intelligent_control=True
        )

        print(f"✅ 语音控制器创建成功")
        print(f"🧠 智能控制启用: {controller.enable_intelligent_control}")

        # 测试混合命令
        test_commands = [
            "左滑",                    # 传统命令
            "调高音量",              # 传统命令
            "请帮我打开记事本",      # 智能命令
            "我想搜索Python教程",    # 智能命令
            "启动微信",              # 智能命令
            "截图"                   # 智能命令
        ]

        print(f"\n🎯 测试 {len(test_commands)} 个混合命令:")
        print("-" * 40)

        intelligent_count = 0
        traditional_count = 0

        for cmd in test_commands:
            try:
                result = controller._parse_command(cmd)
                if result:
                    if result.command_type == "intelligent_control":
                        print(f"✨ '{cmd}' -> 🧠 智能控制 (置信度: {result.confidence:.2f})")
                        intelligent_count += 1
                    else:
                        print(f"🔧 '{cmd}' -> {result.command_type} (置信度: {result.confidence:.2f})")
                        traditional_count += 1
                else:
                    print(f"❌ '{cmd}' -> 未识别")

            except Exception as e:
                print(f"⚠️ '{cmd}' -> 错误: {e}")

        print(f"\n📊 解析结果:")
        print(f"   智能控制命令: {intelligent_count}")
        print(f"   传统控制命令: {traditional_count}")
        print(f"   总计: {intelligent_count + traditional_count}")

        return True

    except Exception as e:
        print(f"❌ 语音控制器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 智能控制系统 - 模拟服务器测试")
    print("=" * 60)

    mock_server_process = None

    try:
        # 启动模拟服务器
        mock_server_process = start_mock_server()
        if not mock_server_process:
            print("❌ 无法启动模拟服务器，测试终止")
            return 1

        # 测试1: 智能控制
        test1_success = test_intelligent_control_with_mock()

        # 测试2: 语音控制器
        test2_success = test_voice_controller_with_mock()

        # 总结
        print("\n" + "=" * 60)
        print("📊 模拟服务器测试结果")
        print("=" * 60)
        print(f"智能控制测试: {'✅ 通过' if test1_success else '❌ 失败'}")
        print(f"语音控制测试: {'✅ 通过' if test2_success else '❌ 失败'}")

        if test1_success and test2_success:
            print("\n🎉 所有测试通过！")
            print("\n🎯 接下来你可以:")
            print("1. 保持模拟服务器运行")
            print("2. 启动智能语音控制: python smart_voice_control.py")
            print("3. 体验完整的智能控制功能")
            print("\n💡 或者使用真实LLM服务:")
            print("1. 配置KIMI或Qwen API密钥")
            print("2. 启动真实后端服务: cd backend && mvn spring-boot:run")
            print("3. 享受更强大的智能控制功能")
            return 0
        else:
            print("\n⚠️ 部分测试失败，请检查相关配置")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"💥 测试异常: {e}")
        return 1
    finally:
        # 清理：关闭模拟服务器
        if mock_server_process:
            print("\n🔄 正在关闭模拟服务器...")
            mock_server_process.terminate()
            try:
                mock_server_process.wait(timeout=5)
                print("✅ 模拟服务器已关闭")
            except subprocess.TimeoutExpired:
                print("⚠️ 强制关闭模拟服务器")
                mock_server_process.kill()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        print(f"💥 程序异常: {e}")
        sys.exit(1)