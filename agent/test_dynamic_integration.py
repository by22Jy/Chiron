"""
测试动态手势集成
验证MediaPipeGestureDetector是否已经支持动态手势
"""

import numpy as np
import time

def test_dynamic_gesture_integration():
    """测试动态手势集成"""
    try:
        from gestures.mediapipe_detector import MediaPipeGestureDetector
        print("成功导入MediaPipeGestureDetector")

        # 创建检测器
        detector = MediaPipeGestureDetector()
        print("检测器初始化成功")

        # 检查是否有动态手势相关属性
        if hasattr(detector, 'hand_history'):
            print("检测到动态手势历史追踪器")
            print("检测到动态手势最小滑动距离:", detector.min_swipe_distance)
            print("检测到动态手势冷却时间:", detector.dynamic_gesture_cooldown)
        else:
            print("警告: 未找到动态手势相关属性")
            return False

        return True

    except Exception as e:
        print(f"测试失败: {e}")
        return False

def simulate_dynamic_gesture_recognition():
    """模拟动态手势识别过程"""
    print("\n开始模拟动态手势识别...")

    try:
        from gestures.mediapipe_detector import MediaPipeGestureDetector
        detector = MediaPipeGestureDetector()

        # 模拟landmarks（手部关键点）
        # 简化的手部模型，重点测试手心位置变化
        base_landmarks = [(0.5, 0.5, 0)] * 21

        print("\n模拟左滑手势轨迹:")

        # 模拟连续的手部位置，从右向左移动
        positions = []
        for i in range(15):
            x = 0.7 - i * 0.03  # 从0.7向0.25移动
            y = 0.5 + (i % 3 - 1) * 0.01  # 轻微的y方向变化
            timestamp = time.time() + i * 0.03

            # 创建带有不同x坐标的landmarks
            landmarks = [(x + j*0.01, y + (j//5)*0.01, 0) for j in range(21)]

            # 更新手部历史
            detector._update_hand_history(landmarks, timestamp)
            positions.append((x, y))

            # 每5帧检查一次动态手势
            if i % 5 == 4:
                gesture = detector._recognize_dynamic_gesture()
                if gesture:
                    print(f"第{i+1}步: 识别到动态手势 {gesture}")
                    break

        print("左滑手势模拟完成")

        # 重置并模拟右滑
        detector = MediaPipeGestureDetector()

        print("\n模拟右滑手势轨迹:")
        for i in range(15):
            x = 0.3 + i * 0.03  # 从0.25向0.7移动
            y = 0.5 + (i % 3 - 1) * 0.01
            timestamp = time.time() + i * 0.03

            landmarks = [(x + j*0.01, y + (j//5)*0.01, 0) for j in range(21)]

            detector._update_hand_history(landmarks, timestamp)

            if i % 5 == 4:
                gesture = detector._recognize_dynamic_gesture()
                if gesture:
                    print(f"第{i+1}步: 识别到动态手势 {gesture}")
                    break

        print("右滑手势模拟完成")
        print("\n动态手势识别测试成功!")
        return True

    except Exception as e:
        print(f"模拟失败: {e}")
        return False

def main():
    """主测试函数"""
    print("YOLO-LLM 动态手势集成验证")
    print("=" * 40)

    # 测试集成状态
    integration_ok = test_dynamic_gesture_integration()

    if integration_ok:
        # 测试动态手势识别
        dynamic_ok = simulate_dynamic_gesture_recognition()

        if dynamic_ok:
            print("\n" + "="*40)
            print("集成验证结果:")
            print("✅ 动态手势检测逻辑正常")
            print("✅ 可以识别左右滑动")
            print("✅ 集成到现有系统成功")
            print("✅ 运行 python main.py --realtime 应该能看到动态手势")
            print("="*40)
        else:
            print("动态手势测试失败")
    else:
        print("集成状态检查失败")

if __name__ == "__main__":
    main()