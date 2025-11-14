"""
增强手势检测器 - 集成静态和动态手势识别
直接替换原有的MediaPipeGestureDetector使用
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

# 从原有的MediaPipe检测器导入
try:
    from mediapipe_detector import GestureResult, HandPoint
except ImportError:
    # 如果导入失败，自己定义
    @dataclass
    class GestureResult:
        gesture_code: str
        confidence: float
        landmarks: List[Tuple[float, float, float]]
        timestamp: float
        bbox: Optional[Tuple[int, int, int, int]] = None

    @dataclass
    class HandPoint:
        x: float
        y: float
        z: float = 0.0

class TrajectoryPoint:
    def __init__(self, position: Tuple[float, float], velocity: Tuple[float, float], timestamp: float):
        self.position = position
        self.velocity = velocity
        self.timestamp = timestamp

class DynamicGestureDetector:
    """动态手势检测器"""

    def __init__(self, history_size=20, min_swipe_distance=0.1):
        self.history_size = history_size
        self.min_swipe_distance = min_swipe_distance
        self.trajectory_history = deque(maxlen=history_size)
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.5  # 避免重复识别

    def add_hand_position(self, landmarks: List[Tuple[float, float, float]], timestamp: float) -> Optional[str]:
        """添加手部位置，检测动态手势"""
        # 计算手心位置
        palm_center = self._calculate_palm_center(landmarks)

        # 计算速度
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
        gesture = self._recognize_dynamic_gesture(timestamp)
        if gesture:
            self.last_gesture_time = timestamp
            # 清空历史，准备下一次手势
            self.trajectory_history.clear()
            return gesture

        return None

    def _calculate_palm_center(self, landmarks: List[Tuple[float, float, float]]) -> Tuple[float, float]:
        """计算手心位置"""
        palm_indices = [0, 1, 5, 9, 13, 17]  # 手腕 + 各手指根部
        palm_x = sum(landmarks[i][0] for i in palm_indices) / len(palm_indices)
        palm_y = sum(landmarks[i][1] for i in palm_indices) / len(palm_indices)
        return (palm_x, palm_y)

    def _recognize_dynamic_gesture(self, timestamp: float) -> Optional[str]:
        """识别动态手势"""
        # 手势冷却
        if timestamp - self.last_gesture_time < self.gesture_cooldown:
            return None

        if len(self.trajectory_history) < 10:
            return None  # 轨迹数据不足

        # 分析轨迹
        gesture = self._analyze_trajectory()
        return gesture

    def _analyze_trajectory(self) -> Optional[str]:
        """分析轨迹模式"""
        points = list(self.trajectory_history)
        start_pos = points[0].position
        end_pos = points[-1].position

        # 计算位移
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        # 检查最小距离
        if distance < self.min_swipe_distance:
            return None

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

class EnhancedGestureDetector:
    """增强手势检测器 - 兼容原有接口，添加动态手势支持"""

    def __init__(self,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5,
                 max_hands: int = 2):
        # 保持原有的MediaPipe设置
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        # 添加动态手势检测器
        self.dynamic_detector = DynamicGestureDetector()

        # 手势状态控制
        self.last_gesture_time = 0
        self.gesture_cooldown = 1.0

        logging.info('Enhanced gesture detector initialized with dynamic gesture support')

    def detect_hands(self, image: np.ndarray) -> Optional[List[GestureResult]]:
        """检测手部和手势 - 兼容原有接口，但支持动态手势"""
        if image is None:
            return None

        # 转换颜色空间
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_image)

        if not results.multi_hand_landmarks:
            return None

        gesture_results = []
        current_time = time.time()

        for hand_landmarks in results.multi_hand_landmarks:
            # 转换landmarks格式
            landmarks = [
                (landmark.x, landmark.y, landmark.z if hasattr(landmark, 'z') else 0)
                for landmark in hand_landmarks.landmark
            ]

            # 1. 静态手势检测（原有逻辑）
            static_gesture = self._recognize_static_gesture(landmarks)

            # 2. 动态手势检测（新增功能）
            dynamic_gesture = self.dynamic_detector.add_hand_position(landmarks, current_time)

            # 3. 融合结果 - 优先动态手势
            final_gesture = dynamic_gesture if dynamic_gesture else static_gesture

            if final_gesture:
                # 计算边界框
                xs = [landmark[0] for landmark in landmarks]
                ys = [landmark[1] for landmark in landmarks]
                bbox = (min(xs), min(ys), max(xs), max(ys))

                gesture_results.append(GestureResult(
                    gesture_code=final_gesture,
                    confidence=0.85,
                    landmarks=landmarks,
                    timestamp=current_time,
                    bbox=bbox
                ))

        return gesture_results if gesture_results else None

    def _recognize_static_gesture(self, landmarks: List[Tuple[float, float, float]]) -> Optional[str]:
        """静态手势检测 - 保留原有逻辑"""
        if not landmarks or len(landmarks) < 21:
            return None

        # 获取手指状态
        finger_states = self._get_finger_states(landmarks)

        # 定义手势
        if self._is_pointing_up(finger_states):
            return 'POINT_UP'
        elif self._is_pointing_index(finger_states):
            return 'POINT_INDEX'
        elif self._is_thumbs_up(finger_states):
            return 'THUMBS_UP'
        elif self._is_thumbs_down(finger_states):
            return 'THUMBS_DOWN'
        elif self._is_open_palm(finger_states):
            return 'OPEN_PALM'
        elif self._is_closed_fist(finger_states):
            return 'CLOSED_FIST'
        elif self._is_victory(finger_states):
            return 'VICTORY'
        elif self._is_ok_sign(landmarks):
            return 'OK_SIGN'

        return None

    # 以下方法保持原有实现
    def _get_finger_states(self, landmarks: List[Tuple[float, float, float]]) -> Dict[str, bool]:
        finger_tips = [4, 8, 12, 16, 20]
        finger_bases = [3, 6, 10, 14, 18]
        finger_names = ['thumb', 'index', 'middle', 'ring', 'pinky']

        finger_states = {}
        for i, name in enumerate(finger_names):
            tip_y = landmarks[finger_tips[i]][1]
            base_y = landmarks[finger_bases[i]][1]

            if name == 'thumb':
                tip_x = landmarks[finger_tips[i]][0]
                base_x = landmarks[finger_bases[i]][0]
                finger_states[name] = tip_x > base_x
            else:
                finger_states[name] = tip_y < base_y

        return finger_states

    def _is_pointing_up(self, finger_states: Dict[str, bool]) -> bool:
        return (finger_states['index'] and not finger_states['middle'] and
                not finger_states['ring'] and not finger_states['pinky'] and
                not finger_states['thumb'])

    def _is_pointing_index(self, finger_states: Dict[str, bool]) -> bool:
        return (finger_states['index'] and not finger_states['middle'] and
                not finger_states['ring'] and not finger_states['pinky'])

    def _is_thumbs_up(self, finger_states: Dict[str, bool]) -> bool:
        return (finger_states['thumb'] and not finger_states['index'] and
                not finger_states['middle'] and not finger_states['ring'] and
                not finger_states['pinky'])

    def _is_thumbs_down(self, finger_states: Dict[str, bool]) -> bool:
        return (not finger_states['thumb'] and not finger_states['index'] and
                not finger_states['middle'] and not finger_states['ring'] and
                not finger_states['pinky'])

    def _is_open_palm(self, finger_states: Dict[str, bool]) -> bool:
        return all(finger_states.values())

    def _is_closed_fist(self, finger_states: Dict[str, bool]) -> bool:
        return not any(finger_states.values())

    def _is_victory(self, finger_states: Dict[str, bool]) -> bool:
        return (finger_states['index'] and finger_states['middle'] and
                not finger_states['ring'] and not finger_states['pinky'])

    def _is_ok_sign(self, landmarks: List[Tuple[float, float, float]]) -> bool:
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        distance = np.sqrt((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)
        return distance < 0.05

    def draw_landmarks(self, image: np.ndarray, hand_landmarks) -> np.ndarray:
        """绘制手部关键点 - 保持原有功能"""
        if hand_landmarks:
            self.mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_drawing_styles.get_default_hand_landmarks_style(),
                self.mp_drawing_styles.get_default_hand_connections_style()
            )
        return image

    def close(self):
        """关闭检测器 - 保持原有功能"""
        if self.hands is not None:
            self.hands.close()