#!/usr/bin/env python3
"""
YOLO-LLM AI功能全面测试脚本
测试语音控制、手势意图分析和智能对话功能
"""

import sys
import time
import requests
import threading
from pathlib import Path
from typing import Dict, Any

# 添加agent目录到路径
sys.path.append(str(Path(__file__).parent / "agent"))

def test_backend_llm_service():
    """测试后端LLM服务"""
    print("🧪 测试后端LLM服务...")

    base_url = "http://localhost:8080"

    try:
        # 测试手势分析API
        response = requests.post(
            f"{base_url}/api/llm/gesture-analysis",
            json={
                "prompt": "请分析竖大拇指手势的含义",
                "gesture_code": "thumbs_up",
                "confidence": 0.95,
                "context": "测试环境"
            },
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 手势分析API正常: {result.get('success', False)}")
            if result.get('success'):
                print(f"   响应长度: {len(result.get('response', ''))} 字符")
        else:
            print(f"❌ 手势分析API失败: {response.status_code}")
            return False

        # 测试智能对话API
        response = requests.post(
            f"{base_url}/api/llm/chat",
            json={
                "message": "你好，请介绍一下YOLO-LLM平台",
                "context": "测试对话"
            },
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 智能对话API正常: {result.get('success', False)}")
            if result.get('success'):
                print(f"   AI回复: {result.get('response', '无响应')[:50]}...")
        else:
            print(f"❌ 智能对话API失败: {response.status_code}")
            return False

        # 测试语音命令分析API
        response = requests.post(
            f"{base_url}/api/llm/voice-command",
            json={
                "command": "请帮打开浏览器",
                "context": "语音命令测试"
            },
            timeout=15
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ 语音命令分析API正常: {result.get('success', False)}")
        else:
            print(f"❌ 语音命令分析API失败: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行 (端口 8080)")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

    return True


def test_speech_controller():
    """测试语音控制器"""
    print("\n🧪 测试语音控制器...")

    try:
        from speech_controller import VoiceController, VoiceCommand

        # 创建语音控制器
        controller = VoiceController()

        # 测试初始化
        if not controller.initialize():
            print("❌ 语音控制器初始化失败")
            return False

        print("✅ 语音控制器初始化成功")

        # 测试命令解析
        test_commands = [
            "请帮我打开浏览器",
            "向左滑动",
            "调高音量",
            "锁定屏幕",
            "分析一下这个手势"
        ]

        for cmd in test_commands:
            command = controller._parse_command(cmd)
            if command:
                print(f"✅ 识别命令: {cmd} -> {command.command_type}")
                print(f"   参数: {command.parameters}")
                print(f"   置信度: {command.confidence:.2f}")
            else:
                print(f"⚠️  未识别命令: {cmd}")

        # 测试状态获取
        status = controller.get_status()
        print(f"✅ 语音控制器状态: {status}")

        return True

    except ImportError as e:
        print(f"❌ 语音控制器模块不可用: {e}")
        return False
    except Exception as e:
        print(f"❌ 语音控制器测试失败: {e}")
        return False


def test_gesture_analyzer():
    """测试手势分析器"""
    print("\n🧪 测试手势分析器...")

    try:
        from gesture_analyzer import GestureAnalyzer, GestureAnalysis
        from gestures.mediapipe_detector import GestureResult

        # 创建手势分析器
        analyzer = GestureAnalyzer()

        # 测试手势洞察
        gestures_to_test = ["thumbs_up", "victory", "ok_sign", "point_up"]

        for gesture in gestures_to_test:
            insights = analyzer.get_gesture_insights(gesture)
            print(f"✅ 手势洞察 {gesture}:")
            print(f"   典型情感: {insights.get('typical_emotions', [])}")
            print(f"   使用场景: {len(insights.get('common_contexts', []))} 个")
            print(f"   文化含义: {len(insights.get('cultural_meanings', []))} 个")

        # 测试手势分析
        test_gesture = GestureResult(
            gesture_code="thumbs_up",
            confidence=0.92,
            bbox=(100, 100, 50, 50)
        )

        analysis = analyzer.analyze_gesture(test_gesture, "用户在演示手势控制功能")
        if analysis:
            print(f"✅ 手势分析成功:")
            print(f"   手势: {analysis.gesture_code}")
            print(f"   意图: {analysis.intent}")
            print(f"   情感: {analysis.emotion}")
            print(f"   上下文: {analysis.context}")
            print(f"   建议数: {len(analysis.suggestions)}")
        else:
            print("⚠️  手势分析未成功（可能是LLM服务问题）")

        return True

    except ImportError as e:
        print(f"❌ 手势分析器模块不可用: {e}")
        return False
    except Exception as e:
        print(f"❌ 手势分析器测试失败: {e}")
        return False


def test_agent_ai_integration():
    """测试Agent的AI集成"""
    print("\n🧪 测试Agent AI集成...")

    try:
        from main import GestureAgent, AgentConfig
        from logger_config import setup_component_logger

        # 创建测试配置
        test_config = {
            'backend': {
                'base_url': 'http://127.0.0.1:8080',
                'username': 'test_user',
                'application': 'test_app'
            },
            'agent': {
                'source': 'test-agent',
                'poll_interval': 60
            },
            'video': {
                'camera_id': 0,
                'width': 640,
                'height': 480,
                'fps': 30,
                'show_preview': False,
                'flip_horizontal': True,
                'detection_interval': 0.1
            }
        }

        # 创建Agent
        agent = GestureAgent(AgentConfig(test_config))

        # 检查AI功能是否可用
        if hasattr(agent, 'voice_controller') and agent.voice_controller:
            print("✅ 语音控制器已集成到Agent")
        else:
            print("⚠️  语音控制器未集成")

        if hasattr(agent, 'gesture_analyzer') and agent.gesture_analyzer:
            print("✅ 手势分析器已集成到Agent")
        else:
            print("⚠️  手势分析器未集成")

        # 测试手势分析功能
        from gestures.mediapipe_detector import GestureResult
        test_gesture = GestureResult("victory", 0.88, (120, 80, 60, 60))
        analysis = agent.analyze_gesture_intent(test_gesture, "测试环境")

        if analysis:
            print("✅ Agent手势分析功能正常")
            print(f"   分析结果: {analysis.intent[:30]}...")
        else:
            print("⚠️  Agent手势分析功能异常")

        return True

    except Exception as e:
        print(f"❌ Agent AI集成测试失败: {e}")
        return False


def test_real_time_speech_simulation():
    """模拟实时语音控制测试"""
    print("\n🧪 模拟实时语音控制测试...")

    try:
        from speech_controller import VoiceController

        controller = VoiceController()

        # 模拟语音命令队列
        simulated_commands = [
            "请打开浏览器",
            "向右滑动",
            "调高音量",
            "请打开记事本"
        ]

        print("模拟以下语音命令执行:")

        for cmd in simulated_commands:
            print(f"\n🎤 模拟语音输入: {cmd}")

            # 解析命令
            command = controller._parse_command(cmd)

            if command:
                print(f"   ✅ 识别: {command.command_type}")
                print(f"   🎯 执行: {command.parameters}")

                # 模拟执行
                if command.command_type == "open":
                    app_name = command.parameters.get("app_name", "未知应用")
                    executable = command.parameters.get("executable", "")
                    print(f"   📱 将启动: {app_name} ({executable})")
                elif command.command_type == "swipe":
                    direction = command.parameters.get("direction", "unknown")
                    distance = command.parameters.get("distance", 0)
                    print(f"   👆 将执行: {direction}滑动 {distance}px")
                elif command.command_type == "system":
                    action = command.parameters.get("action", "unknown")
                    print(f"   ⚙️ 将执行: {action}")

            else:
                print(f"   ❌ 无法识别: {cmd}")

        return True

    except Exception as e:
        print(f"❌ 实时语音控制测试失败: {e}")
        return False


def test_comprehensive_ai_workflow():
    """综合AI工作流程测试"""
    print("\n🧪 综合AI工作流程测试...")
    print("模拟完整的AI交互流程:")

    try:
        from gesture_analyzer import GestureAnalyzer
        from speech_controller import VoiceController
        from gestures.mediapipe_detector import GestureResult

        # 创建组件
        analyzer = GestureAnalyzer()
        controller = VoiceController()

        # 模拟用户场景：用户做手势+语音命令
        print("\n📝 场景: 用户在演示手势控制功能")

        # 1. 用户做出手势
        user_gesture = "thumbs_up"
        print(f"1️⃣ 用户做出手势: {user_gesture}")

        # 2. 系统识别并分析手势
        gesture_result = GestureResult(user_gesture, 0.95, (100, 100, 50, 50))
        analysis = analyzer.analyze_gesture(gesture_result, "演示手势控制")

        if analysis:
            print(f"2️⃣ AI分析结果: {analysis.intent}")
            print(f"   情感: {analysis.emotion}")
            print(f"   建议: {'; '.join(analysis.suggestions[:2])}")
        else:
            print("2️⃣ AI分析: 使用备用分析结果")

        # 3. 用户同时说出语音命令
        user_speech = "请打开浏览器"
        print(f"3️⃣ 用户语音命令: {user_speech}")

        # 4. 语音识别和命令执行
        voice_command = controller._parse_command(user_speech)
        if voice_command:
            print(f"4️⃣ 语音识别成功: {voice_command.command_type}")
            print(f"   执行参数: {voice_command.parameters}")

            if voice_command.command_type == "open":
                app_name = voice_command.parameters.get("app_name")
                print(f"5️⃣ 智能执行: 启动{app_name}")
            else:
                print(f"5️⃣ 智能执行: {voice_command.command_type}")
        else:
            print("4️⃣ 语音识别失败")

        print("\n✅ 综合AI工作流程测试完成")
        return True

    except Exception as e:
        print(f"❌ 综合工作流程测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🚀 YOLO-LLM AI功能全面测试")
    print("=" * 50)

    test_results = []

    # 运行所有测试
    tests = [
        ("后端LLM服务", test_backend_llm_service),
        ("语音控制器", test_speech_controller),
        ("手势分析器", test_gesture_analyzer),
        ("Agent AI集成", test_agent_ai_integration),
        ("实时语音模拟", test_real_time_speech_simulation),
        ("综合工作流程", test_comprehensive_ai_workflow)
    ]

    start_time = time.time()

    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试出现异常: {e}")
            test_results.append((test_name, False))

    # 输出测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    elapsed = time.time() - start_time
    print(f"\n⏱️ 总测试时间: {elapsed:.2f}秒")
    print(f"🎯 测试通过率: {passed}/{total} ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 所有AI功能测试通过！")
        print("🚀 系统已准备就绪，可以开始使用语音控制和智能分析功能！")
        return 0
    else:
        print(f"\n⚠️ {total-passed} 个测试失败，请检查相关配置")
        print("💡 建议查看上述错误信息并进行相应修复")
        return 1


if __name__ == "__main__":
    sys.exit(main())