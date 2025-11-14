"""
混合手势检测器 - 支持静态和动态手势
解决扩展性和动态手势问题
"""

import cv2
import mediapipe as mp
import numpy as np
import logging
import math
import time
from collections import deque
from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass

# 导入现有的静态检测器
from mediapipe_detector import GestureResult, MediaPipeGestureDetector, HandPoint

@dataclass
class TrajectoryPoint:
    position: Tuple[float, float]  # (x, y)
    velocity: Tuple[float, float]  # (vx, vy)
    timestamp: float

class DynamicGestureDetector:
    """动态手势检测器 - 基于轨迹分析"""

    def __init__(self, history_size=20, min_swipe_distance=0.1):
        self.history_size = history_size
        self.min_swipe_distance = min_swipe_distance
        self.trajectory_history = deque(maxlen=history_size)
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5  # 避免重复识别

    def add_position(self, landmarks: List[HandPoint], timestamp: float) -> Optional[str]:
        """添加手部位置，检测动态手势"""
        # 计算手心位置
        palm_center = self._calculate_palm_center(landmarks)

        # 计算速度（如果有历史数据）
        velocity = (0, 0)
        if self.trajectory_history:
            last_point = self.trajectory_history[-1]
            dt = timestamp - last_point.timestamp
            if dt > 0:
                dx = palm_center[0] - last_point.position[0]
                dy = palm_center[1] - last_point.position[1]
                velocity = (dx / dt, dy / dt)

        # 添加到轨迹历史
        trajectory_point = TrajectoryPoint(palm_center, velocity, timestamp)
        self.trajectory_history.append(trajectory_point)

        # 尝试识别手势
        return self._recognize_dynamic_gesture(timestamp)

    def _calculate_palm_center(self, landmarks: List[HandPoint]) -> Tuple[float, float]:
        """计算手心位置"""
        # 使用手腕和多个手指根部的平均值
        palm_indices = [0, 1, 5, 9, 13, 17]  # 手腕 + 各手指根部
        palm_x = sum(landmarks[i].x for i in palm_indices) / len(palm_indices)
        palm_y = sum(landmarks[i].y for i in palm_indices) / len(palm_indices)
        return (palm_x, palm_y)

    def _recognize_dynamic_gesture(self, timestamp: float) -> Optional[str]:
        """识别动态手势"""
        # 手势冷却
        if timestamp - self.last_gesture_time < self.gesture_cooldown:
            return None

        if len(self.trajectory_history) < 10:
            return None

        # 分析轨迹
        gesture = self._analyze_trajectory()
        if gesture:
            self.last_gesture_time = timestamp
            # 清空历史，准备下一次手势
            self.trajectory_history.clear()

        return gesture

    def _analyze_trajectory(self) -> Optional[str]:
        """分析轨迹模式"""
        points = list(self.trajectory_history)

        # 计算总位移
        start_pos = points[0].position
        end_pos = points[-1].position
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        # 检查最小距离
        if distance < self.min_swipe_distance:
            return None

        # 计算平均速度
        total_velocity = sum(math.sqrt(v[0]**2 + v[1]**2) for v in [p.velocity for p in points])
        avg_speed = total_velocity / len(points)

        # 计算主要方向
        if abs(dx) > abs(dy):  # 水平主导
            if dx > 0:
                return "SWIPE_RIGHT"
            else:
                return "SWIPE_LEFT"
        else:  # 垂直主导
            if dy > 0:
                return "SWIPE_DOWN"
            else:
                return "SWIPE_UP"

class HybridGestureDetector:
    """混合手势检测器 - 结合静态和动态检测"""

    def __init__(self,
                 static_min_confidence=0.5,
                 dynamic_min_confidence=0.3,
                 max_hands=2):
        self.static_detector = MediaPipeGestureDetector(
            min_detection_confidence=static_min_confidence,
            min_tracking_confidence=static_min_confidence,
            max_hands=max_hands
        )
        self.dynamic_detector = DynamicGestureDetector()

        # 模式切换阈值
        self.mode = "hybrid"  # "static", "dynamic", "hybrid"
        self.last_static_gesture = None
        self.static_gesture_count = 0

        logging.info('Hybrid gesture detector initialized')

    def detect_hands(self, image: np.ndarray) -> Optional[List[GestureResult]]:
        """检测手部和手势"""
        if image is None:
            return None

        # 转换颜色空间
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # MediaPipe处理
        results = self.static_detector.hands.process(rgb_image)

        if not results.multi_hand_landmarks:
            return None

        gesture_results = []
        current_time = time.time()

        for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            # 转换landmarks格式
            landmarks = [
                (landmark.x, landmark.y, landmark.z if hasattr(landmark, 'z') else 0)
                for landmark in hand_landmarks.landmark
            ]

            # 静态手势检测
            static_gesture = self._detect_static_gesture(landmarks, current_time)

            # 动态手势检测
            dynamic_gesture = self.dynamic_detector.add_position(
                [HandPoint(x, y, z) for x, y, z in landmarks],
                current_time
            )

            # 融合结果
            fused_gesture = self._fuse_gesture_results(static_gesture, dynamic_gesture)

            if fused_gesture:
                # 创建边界框（使用MediaPipe的边界框）
                if hasattr(results.multi_hand_landmarks[hand_idx], 'bounding_box'):
                    bbox = results.multi_hand_landmarks[hand_idx].bounding_box
                else:
                    # 手动计算边界框
                    xs = [landmark.x for landmark in landmarks]
                    ys = [landmark.y for landmark in landmarks]
                    bbox = (min(xs), min(ys), max(xs), max(ys))

                gesture_results.append(GestureResult(
                    gesture_code=fused_gesture,
                    confidence=0.85,  # 混合手势的置信度
                    landmarks=landmarks,
                    timestamp=current_time,
                    bbox=bbox
                ))

        return gesture_results if gesture_results else None

    def _detect_static_gesture(self, landmarks: List[Tuple[float, float, float]], timestamp: float) -> Optional[str]:
        """检测静态手势"""
        finger_states = self.static_detector._get_finger_states(landmarks)

        # 静态手势检测逻辑
        if self.static_detector._is_pointing_up(finger_states):
            return 'POINT_UP'
        elif self.static_detector._is_pointing_index(finger_states):
            return 'POINT_INDEX'
        elif self.static_detector._is_thumbs_up(finger_states):
            return 'THUMBS_UP'
        elif self.static_detector._is_thumbs_down(finger_states):
            return 'THUMBS_DOWN'
        elif self.static_detector._is_open_palm(finger_states):
            return 'OPEN_PALM'
        elif self.static_detector._is_closed_fist(finger_states):
            return 'CLOSED_FIST'
        elif self.static_detector._is_victory(finger_states):
            return 'VICTORY'
        elif self.static_detector._is_ok_sign(landmarks):
            return 'OK_SIGN'

        return None

    def _fuse_gesture_results(self, static_gesture: Optional[str], dynamic_gesture: Optional[str]) -> Optional[str]:
        """融合静态和动态手势结果"""
        # 根据模式决定融合策略
        if self.mode == "static":
            return static_gesture
        elif self.mode == "dynamic":
            return dynamic_gesture
        else:  # hybrid模式
            # 优先动态手势（通常更有意义）
            if dynamic_gesture:
                # 检查是否与静态手势冲突
                if self._is_gesture_compatible(dynamic_gesture, static_gesture):
                    return dynamic_gesture
            # 否则返回静态手势
            return static_gesture

    def _is_gesture_compatible(self, dynamic_gesture: str, static_gesture: Optional[str]) -> bool:
        """检查动态和静态手势是否兼容"""
        if not static_gesture:
            return True

        # 定义冲突的规则
        incompatible_pairs = {
            ('SWIPE_LEFT', 'THUMBS_UP'),
            ('SWIPE_RIGHT', 'THUMBS_UP'),
            ('SWIPE_DOWN', 'OPEN_PALM'),
            ('SWIPE_UP', 'CLOSED_FIST')
        }

        return (dynamic_gesture, static_gesture) not in incompatible_pairs

    def set_mode(self, mode: str):
        """设置检测模式"""
        if mode in ["static", "dynamic", "hybrid"]:
            self.mode = mode
            logging.info(f'Gesture detection mode set to: {mode}')
        else:
            logging.warning(f'Invalid gesture detection mode: {mode}')

# 为了兼容性，重新定义GestureResult
@dataclass
class GestureResult:
    gesture_code: str
    confidence: float
    landmarks: List[Tuple[float, float, float]]
    timestamp: float
    bbox: Optional[Tuple[int, int, int, int]] = None

# 为了兼容性，定义HandPoint
@dataclass
class HandPoint:
    x: float
    y: float
    z: float = 0.0

def test_hybrid_detector():
    """测试混合手势检测器"""
    print("🎯 混合手势检测器测试")
    print("=" * 40)

    detector = HybridGestureDetector()

    # 模拟一些手势序列
    test_landmarks = []

    # 生成21个关键点的模拟数据
    for i in range(21):
        # 简单的手部模型
        x = 0.5 + (i % 5) * 0.02
        y = 0.3 + (i // 5) * 0.1
        z = 0.0
        test_landmarks.append(HandPoint(x, y, z))

    print("测试静态手势识别...")
    static_result = detector._detect_static_gesture([(p.x, p.y, p.z) for p in test_landmarks], time.time())
    print(f"静态检测结果: {static_result}")

    print("\n测试动态手势检测...")
    # 模拟轨迹
    detector.dynamic_detector.trajectory_history.clear()

    # 模拟左滑轨迹
    for i in range(15):
        x = 0.8 - i * 0.02  # 从右向左
        y = 0.5 + math.sin(i * 0.5) * 0.05
        timestamp = time.time() + i * 0.03

        # 更新测试数据
        for j, point in enumerate(test_landmarks):
            point.x = x + (j % 5 - 2) * 0.01
            point.y = y + (j // 5 - 1) * 0.01

        landmarks = [(p.x, p.y, p.z) for p in test_landmarks]
        dynamic_result = detector.dynamic_detector.add_position(
            [HandPoint(x, y, z) for x, y, z in landmarks],
            timestamp
        )

        if dynamic_result:
            print(f"动态检测结果: {dynamic_result}")

    print("\n测试完成！")

if __name__ == "__main__":
    test_hybrid_detector()