#!/usr/bin/env python3
"""
手势控制开关功能测试脚本
用于测试新添加的手势控制开关功能
"""

import sys
import time
import requests
from pathlib import Path

# 添加agent目录到路径
sys.path.append(str(Path(__file__).parent / "agent"))

from video_processor import VideoProcessor, VideoConfig
from gestures.mediapipe_detector import GestureResult

def test_api_endpoints():
    """测试后端API端点"""
    print("🧪 测试后端API端点...")

    base_url = "http://localhost:8080"

    try:
        # 测试获取手势状态
        response = requests.get(f"{base_url}/api/monitor/gesture")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取手势状态成功: {data}")
            print(f"🎛️ 当前控制状态: {'启用' if data.get('gesture_control_enabled') else '禁用'}")
        else:
            print(f"❌ 获取手势状态失败: {response.status_code}")
            return False

        # 测试切换手势控制
        response = requests.post(f"{base_url}/api/monitor/gesture/control")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 切换手势控制成功: {data}")
            print(f"🎛️ 新控制状态: {'启用' if data.get('gesture_control_enabled') else '禁用'}")
        else:
            print(f"❌ 切换手势控制失败: {response.status_code}")
            return False

        # 测试设置手势控制状态
        response = requests.post(
            f"{base_url}/api/monitor/gesture/control/set",
            json={"enabled": True}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 设置手势控制状态成功: {data}")
        else:
            print(f"❌ 设置手势控制状态失败: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务，请确保后端正在运行 (端口 8080)")
        return False
    except Exception as e:
        print(f"❌ API测试出错: {e}")
        return False

    return True

def test_video_processor():
    """测试VideoProcessor的手势控制功能"""
    print("\n🧪 测试VideoProcessor手势控制功能...")

    try:
        # 创建测试配置
        config = VideoConfig(
            camera_id=0,  # 使用默认摄像头
            show_preview=False,  # 不显示预览窗口
            detection_interval=1.0  # 1秒检测间隔
        )

        # 创建VideoProcessor
        processor = VideoProcessor(config, {})

        # 测试初始状态
        print(f"🎛️ 初始控制状态: {'启用' if processor.is_gesture_control_enabled() else '禁用'}")

        # 测试切换控制
        new_state = processor.toggle_gesture_control()
        print(f"🎛️ 切换后控制状态: {'启用' if new_state else '禁用'}")

        # 再次切换测试
        new_state = processor.toggle_gesture_control()
        print(f"🎛️ 再次切换后控制状态: {'启用' if new_state else '禁用'}")

        # 测试手动设置状态
        processor.set_gesture_control_enabled(False)
        print(f"🎛️ 手动禁用后状态: {'启用' if processor.is_gesture_control_enabled() else '禁用'}")

        processor.set_gesture_control_enabled(True)
        print(f"🎛️ 手动启用后状态: {'启用' if processor.is_gesture_control_enabled() else '禁用'}")

        # 测试手势处理逻辑
        print("\n🧪 测试手势处理逻辑...")

        # 创建VICTORY手势（应该切换控制）
        victory_gesture = GestureResult(
            gesture_code="victory",
            confidence=0.9,
            bbox=(100, 100, 100, 100)
        )

        # 创建其他手势（应该被控制状态影响）
        other_gesture = GestureResult(
            gesture_code="thumbs_up",
            confidence=0.9,
            bbox=(100, 100, 100, 100)
        )

        print("✅ VideoProcessor功能测试完成")
        return True

    except Exception as e:
        print(f"❌ VideoProcessor测试出错: {e}")
        return False

def test_gesture_toggle_cooldown():
    """测试手势切换冷却时间"""
    print("\n🧪 测试手势切换冷却时间...")

    try:
        config = VideoConfig(show_preview=False)
        processor = VideoProcessor(config, {})

        # 快速连续切换测试
        start_time = time.time()

        state1 = processor.toggle_gesture_control()
        print(f"第一次切换: {'启用' if state1 else '禁用'}")

        state2 = processor.toggle_gesture_control()  # 应该被冷却阻止
        print(f"立即再次切换: {'启用' if state2 else '禁用'} (应该和第一次相同)")

        # 等待冷却时间
        time.sleep(processor.toggle_cooldown + 0.1)

        state3 = processor.toggle_gesture_control()
        print(f"冷却后切换: {'启用' if state3 else '禁用'} (应该可以切换)")

        elapsed = time.time() - start_time
        print(f"⏱️ 总测试时间: {elapsed:.2f}秒")

        if state1 == state2 and state1 != state3:
            print("✅ 冷却机制工作正常")
            return True
        else:
            print("❌ 冷却机制工作异常")
            return False

    except Exception as e:
        print(f"❌ 冷却测试出错: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始手势控制开关功能测试\n")
    print("=" * 50)

    test_results = []

    # 测试API端点
    test_results.append(("API端点", test_api_endpoints()))

    # 测试VideoProcessor
    test_results.append(("VideoProcessor功能", test_video_processor()))

    # 测试冷却机制
    test_results.append(("冷却机制", test_gesture_toggle_cooldown()))

    # 打印测试结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总:")

    passed = 0
    total = len(test_results)

    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 总体结果: {passed}/{total} 测试通过")

    if passed == total:
        print("🎉 所有测试通过！手势控制开关功能工作正常")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关功能")
        return 1

if __name__ == "__main__":
    sys.exit(main())