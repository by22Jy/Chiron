#!/usr/bin/env python3
"""
动态手势识别演示
实现手部移动轨迹的追踪和识别
"""

import math
import time
from collections import deque
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class HandPoint:
    x: float
    y: float
    timestamp: float

class DynamicGestureDetector:
    def __init__(self, history_size=30, min_swipe_distance=0.1):
        # 轨迹历史
        self.hand_history = deque(maxlen=history_size)
        self.history_size = history_size
        self.min_swipe_distance = min_swipe_distance

        # 手势状态
        self.current_gesture = None
        self.gesture_start_pos = None
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0  # 手势冷却时间

        # 统计信息
        self.gesture_count = 0

    def add_hand_position(self, landmarks: List[Tuple[float, float, float]], timestamp: float):
        """添加手部位置到轨迹历史"""
        # 计算手心位置作为追踪点（使用关键点0, 5, 9, 13, 17的平均值）
        palm_points = [landmarks[0], landmarks[5], landmarks[9], landmarks[13], landmarks[17]]
        palm_x = sum(p[0] for p in palm_points) / len(palm_points)
        palm_y = sum(p[1] for p in palm_points) / len(palm_points)

        hand_point = HandPoint(palm_x, palm_y, timestamp)
        self.hand_history.append(hand_point)

        # 尝试识别手势
        gesture = self._detect_dynamic_gesture()
        if gesture:
            self.gesture_count += 1
            return gesture

        return None

    def _detect_dynamic_gesture(self) -> Optional[str]:
        """检测动态手势"""
        current_time = time.time()

        # 手势冷却，避免重复触发
        if current_time - self.last_gesture_time < self.gesture_cooldown:
            return None

        if len(self.hand_history) < 10:
            return None  # 轨迹数据不足

        # 获取最近的轨迹点
        recent_points = list(self.hand_history)[-10:]

        # 计算起点和终点
        start_point = recent_points[0]
        end_point = recent_points[-1]

        # 计算位移
        dx = end_point.x - start_point.x
        dy = end_point.y - start_point.y
        distance = math.sqrt(dx**2 + dy**2)

        # 检查是否为有效手势
        if distance < self.min_swipe_distance:
            return None

        # 识别手势类型
        gesture = self._classify_gesture(dx, dy, distance, recent_points)

        if gesture:
            self.last_gesture_time = current_time
            # 清空历史，准备下一个手势
            self.hand_history.clear()

        return gesture

    def _classify_gesture(self, dx: float, dy: float, distance: float, trajectory: List[HandPoint]) -> Optional[str]:
        """根据轨迹分类手势"""

        # 计算移动方向
        angle = math.atan2(dy, dx)  # 弧度
        angle_deg = math.degrees(angle)

        # 计算移动速度
        time_span = trajectory[-1].timestamp - trajectory[0].timestamp
        speed = distance / time_span if time_span > 0 else 0

        print(f"轨迹分析: 位移={distance:.3f}, 角度={angle_deg:.1f}°, 速度={speed:.3f}")

        # 水平滑动 (左右)
        if abs(dx) > abs(dy) * 1.5:  # 水平分量主导
            if dx > 0:
                return "SWIPE_RIGHT"
            else:
                return "SWIPE_LEFT"

        # 垂直滑动 (上下)
        elif abs(dy) > abs(dx) * 1.5:  # 垂直分量主导
            if dy > 0:
                return "SWIPE_DOWN"
            else:
                return "SWIPE_UP"

        # 对角线滑动
        else:
            # 根据角度判断对角线方向
            if -45 <= angle_deg <= 45:  # 右上
                return "SWIPE_UP_RIGHT"
            elif 45 < angle_deg <= 135:  # 右下
                return "SWIPE_DOWN_RIGHT"
            elif -135 <= angle_deg < -45:  # 左上
                return "SWIPE_UP_LEFT"
            else:  # 左下
                return "SWIPE_DOWN_LEFT"

    def get_trajectory_stats(self) -> dict:
        """获取轨迹统计信息"""
        if not self.hand_history:
            return {}

        points = list(self.hand_history)

        # 计算边界框
        x_coords = [p.x for p in points]
        y_coords = [p.y for p in points]

        return {
            'points_count': len(points),
            'duration': points[-1].timestamp - points[0].timestamp,
            'bbox': {
                'min_x': min(x_coords),
                'max_x': max(x_coords),
                'min_y': min(y_coords),
                'max_y': max(y_coords)
            },
            'gesture_count': self.gesture_count
        }

def demo_trajectory_analysis():
    """演示轨迹分析"""
    print("动态手势识别演示")
    print("=" * 40)

    detector = DynamicGestureDetector()

    # 模拟手势轨迹
    print("\n1. 模拟左滑手势")
    # 从右向左的轨迹
    for i in range(15):
        x = 0.8 - i * 0.04  # 从0.8向0.2移动
        y = 0.5 + math.sin(i * 0.3) * 0.05  # 略微波动
        landmarks = [(x, y, 0)] * 21  # 简化的landmarks

        gesture = detector.add_hand_position(landmarks, time.time())
        if gesture:
            print(f"识别到动态手势: {gesture}")

    print(f"\n轨迹统计: {detector.get_trajectory_stats()}")

    # 重置检测器
    detector = DynamicGestureDetector()

    print("\n2. 模拟右滑手势")
    # 从左向右的轨迹
    for i in range(15):
        x = 0.2 + i * 0.04  # 从0.2向0.8移动
        y = 0.5 + math.cos(i * 0.3) * 0.05
        landmarks = [(x, y, 0)] * 21

        gesture = detector.add_hand_position(landmarks, time.time())
        if gesture:
            print(f"识别到动态手势: {gesture}")

if __name__ == "__main__":
    demo_trajectory_analysis()