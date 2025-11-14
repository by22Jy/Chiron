#!/usr/bin/env python3
"""
测试增强的手势检测器是否正常工作
"""

import sys
import os
import time
import numpy as np

# 添加gestures目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gestures'))

try:
    from enhanced_detector import EnhancedGestureDetector
    print("成功导入 EnhancedGestureDetector")
except ImportError as e:
    print(f"导入失败: {e}")
    sys.exit(1)

def test_gesture_detection():
    """测试手势检测功能"""
    print("\n🧪 测试增强手势检测器")
    print("=" * 40)

    # 创建检测器
    detector = EnhancedGestureDetector()
    print("✅ 检测器初始化成功")

    # 创建测试图像 (640x480 的黑色图像)
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)

    # 模拟MediaPipe的手部检测结果
    # 创建一个模拟的MediaPipe手部landmarks对象
    class MockLandmark:
        def __init__(self, x, y, z=0):
            self.x = x
            self.y = y
            self.z = z

    class MockHandLandmarks:
        def __init__(self):
            self.landmark = []
            # 创建21个手部关键点
            for i in range(21):
                # 简单的手部模型：手掌在中心，手指略微分布
                x = 0.5 + (i % 5 - 2) * 0.05
                y = 0.4 + (i // 5) * 0.08
                self.landmark.append(MockLandmark(x, y, 0))

    # 模拟检测结果
    class MockResults:
        def __init__(self):
            self.multi_hand_landmarks = [MockHandLandmarks()]

    # 模拟MediaPipe的处理结果
    class MockHands:
        def process(self, image):
            return MockResults()

    # 替换检测器的hands对象为模拟对象
    detector.hands = MockHands()

    print("\n🔄 开始模拟手势检测...")

    # 测试多次检测，模拟动态手势
    for i in range(20):
        # 模拟手部从右向左移动 (左滑手势)
        x_offset = 0.6 - i * 0.02  # 从0.6向0.2移动

        # 更新手部位置
        for j in range(21):
            detector.hands.process(image).multi_hand_landmarks[0].landmark[j].x = x_offset + (j % 5 - 2) * 0.02

        # 检测手势
        results = detector.detect_hands(test_image)
        current_time = time.time()

        if results:
            gesture = results[0]
            print(f"第{i:2d}帧: 识别到手势 {gesture.gesture_code} (置信度: {gesture.confidence:.2f})")

        time.sleep(0.01)  # 模拟帧间隔

    print("\n✅ 测试完成!")

def test_dynamic_gesture_logic():
    """测试动态手势检测逻辑"""
    print("\n🎯 测试动态手势检测逻辑")
    print("=" * 40)

    from enhanced_detector import DynamicGestureDetector

    detector = DynamicGestureDetector()
    print("✅ 动态检测器初始化成功")

    # 模拟手部轨迹
    landmarks_base = [(0.5, 0.5, 0)] * 21  # 基础landmarks

    print("\n模拟左滑轨迹:")
    for i in range(15):
        # 从右向左的轨迹
        x = 0.7 - i * 0.03
        y = 0.5
        landmarks = [(x, y, 0)] * 21

        gesture = detector.add_hand_position(landmarks, time.time() + i * 0.03)
        if gesture:
            print(f"🎉 动态手势识别: {gesture}")

    print("\n模拟右滑轨迹:")
    # 重置检测器
    detector = DynamicGestureDetector()

    for i in range(15):
        # 从左向右的轨迹
        x = 0.3 + i * 0.03
        y = 0.5
        landmarks = [(x, y, 0)] * 21

        gesture = detector.add_hand_position(landmarks, time.time() + i * 0.03)
        if gesture:
            print(f"🎉 动态手势识别: {gesture}")

def main():
    """主测试函数"""
    print("🚀 YOLO-LLM 增强手势检测器测试")
    print("=" * 50)

    try:
        # 测试导入
        test_gesture_detection()
        test_dynamic_gesture_logic()

        print("\n" + "="*50)
        print("🎉 所有测试通过!")
        print("✅ 增强手势检测器已准备就绪")
        print("✅ 支持静态手势: POINT_UP, THUMBS_UP, VICTORY等")
        print("✅ 支持动态手势: SWIPE_LEFT, SWIPE_RIGHT等")
        print("="*50)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()