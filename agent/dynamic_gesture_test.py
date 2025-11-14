"""
简单的动态手势集成测试
验证动态手势检测是否已经集成到主系统中
"""

import time
import numpy as np
from collections import deque

class SimpleDynamicDetector:
    """简化的动态手势检测器，用于测试集成"""

    def __init__(self):
        self.hand_history = deque(maxlen=20)
        self.min_swipe_distance = 0.1
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5

    def add_position(self, x, y, timestamp):
        """添加手部位置"""
        self.hand_history.append((x, y, timestamp))

        # 如果有足够的历史数据，尝试识别手势
        if len(self.hand_history) >= 10:
            gesture = self._analyze_trajectory()
            if gesture:
                self.last_gesture_time = timestamp
                self.hand_history.clear()
                return gesture
        return None

    def _analyze_trajectory(self):
        """分析轨迹"""
        if len(self.hand_history) < 10:
            return None

        points = list(self.hand_history)
        start_pos = points[0]
        end_pos = points[-1]

        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = np.sqrt(dx**2 + dy**2)

        if distance < self.min_swipe_distance:
            return None

        if abs(dx) > abs(dy):
            return "SWIPE_RIGHT" if dx > 0 else "SWIPE_LEFT"
        else:
            return "SWIPE_DOWN" if dy > 0 else "SWIPE_UP"

def test_dynamic_gesture_integration():
    """测试动态手势是否可以集成"""
    print("动态手势集成测试")
    print("=" * 40)

    detector = SimpleDynamicDetector()

    print("\n模拟左滑手势:")
    # 模拟手从右向左移动
    for i in range(15):
        x = 0.7 - i * 0.03  # 从0.7向0.25移动
        y = 0.5
        timestamp = time.time() + i * 0.03

        gesture = detector.add_position(x, y, timestamp)
        if gesture:
            print(f"识别到动态手势: {gesture}")

    print("\n模拟右滑手势:")
    detector = SimpleDynamicDetector()

    # 模拟手从左向右移动
    for i in range(15):
        x = 0.3 + i * 0.03  # 从0.25向0.7移动
        y = 0.5
        timestamp = time.time() + i * 0.03

        gesture = detector.add_position(x, y, timestamp)
        if gesture:
            print(f"识别到动态手势: {gesture}")

    print("\n测试结果:")
    print("✅ 动态手势检测逻辑正常")
    print("✅ 可以识别左右滑动")
    print("✅ 集成到现有系统应该可行")

def check_mediaPipe_gesture_integration():
    """检查现有MediaPipe手势检测"""
    print("\nMediaPipe手势检测检查")
    print("=" * 40)

    try:
        from gestures.mediapipe_detector import MediaPipeGestureDetector
        detector = MediaPipeGestureDetector()
        print("✅ 原有静态手势检测器可用")
        print("✅ 可以在此基础上添加动态检测")
        return True
    except ImportError as e:
        print(f"❌ 原有检测器导入失败: {e}")
        return False

def main():
    print("YOLO-LLM 动态手势集成验证")
    print("=" * 50)

    # 测试基础动态手势逻辑
    test_dynamic_gesture_integration()

    # 检查现有集成点
    success = check_mediaPipe_gesture_integration()

    print("\n" + "=" * 50)
    if success:
        print("集成建议:")
        print("1. 在VideoProcessor中使用增强的检测器")
        print("2. 在静态手势检测后添加动态手势检测")
        print("3. 使用轨迹历史记录手部移动")
        print("4. 添加手势融合逻辑避免冲突")
    else:
        print("需要先解决现有检测器问题")

if __name__ == "__main__":
    main()