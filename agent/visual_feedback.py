"""
视觉反馈系统模块

在摄像头画面上绘制Agent状态和反馈信息
"""

import cv2
import time
import threading
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import numpy as np


class AgentState(Enum):
    """Agent状态枚举"""
    IDLE = "idle"
    LISTENING = "listening"
    THINKING = "thinking"
    PROCESSING = "processing"
    EXECUTING = "executing"
    SUCCESS = "success"
    ERROR = "error"
    CONFIRMING = "confirming"


class FeedbackLevel(Enum):
    """反馈级别"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class StatusMessage:
    """状态消息"""
    text: str
    level: FeedbackLevel = FeedbackLevel.INFO
    timestamp: float = None
    duration: float = 3.0  # 显示时长（秒）

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def is_expired(self) -> bool:
        """检查消息是否过期"""
        return time.time() - self.timestamp > self.duration


@dataclass
class VisualFeedbackConfig:
    """视觉反馈配置"""
    enable_status_display: bool = True
    enable_message_overlay: bool = True
    enable_progress_bar: bool = True
    enable_gesture_indicators: bool = True

    # 显示位置和样式
    status_position: Tuple[int, int] = (10, 30)  # (x, y)
    message_position: Tuple[int, int] = (10, 80)  # (x, y)
    progress_bar_position: Tuple[int, int] = (10, 120)  # (x, y)

    # 字体设置
    font_scale: float = 0.8
    thickness: int = 2
    line_type: int = cv2.LINE_AA

    # 颜色配置 (BGR格式)
    colors: Dict[str, Tuple[int, int, int]] = None

    def __post_init__(self):
        if self.colors is None:
            self.colors = {
                "background": (40, 40, 40),
                "text": (255, 255, 255),
                "success": (0, 255, 0),
                "warning": (0, 255, 255),
                "error": (0, 0, 255),
                "processing": (255, 165, 0),
                "thinking": (147, 112, 219),
                "idle": (128, 128, 128),
                "accent": (255, 255, 0)
            }


class VisualFeedback:
    """视觉反馈系统"""

    def __init__(self, config: VisualFeedbackConfig = None):
        self.config = config or VisualFeedbackConfig()
        self.current_state = AgentState.IDLE
        self.status_messages: List[StatusMessage] = []
        self.progress_value = 0.0
        self.progress_text = ""

        # 线程安全
        self._lock = threading.RLock()

        # 状态图标映射
        self.state_icons = {
            AgentState.IDLE: "⚪",
            AgentState.LISTENING: "🎤",
            AgentState.THINKING: "🤔",
            AgentState.PROCESSING: "⚙️",
            AgentState.EXECUTING: "🚀",
            AgentState.SUCCESS: "✅",
            AgentState.ERROR: "❌",
            AgentState.CONFIRMING: "❓"
        }

        # 状态文本映射
        self.state_texts = {
            AgentState.IDLE: "待机中",
            AgentState.LISTENING: "正在听取...",
            AgentState.THINKING: "正在思考...",
            AgentState.PROCESSING: "正在处理...",
            AgentState.EXECUTING: "正在执行...",
            AgentState.SUCCESS: "执行成功",
            AgentState.ERROR: "执行错误",
            AgentState.CONFIRMING: "等待确认..."
        }

    def set_state(self, state: AgentState, message: str = None):
        """设置Agent状态"""
        with self._lock:
            self.current_state = state

            # 如果提供了消息，添加到消息列表
            if message:
                self.add_message(message, self._get_feedback_level_from_state(state))

    def add_message(self, text: str, level: FeedbackLevel = FeedbackLevel.INFO, duration: float = 3.0):
        """添加状态消息"""
        with self._lock:
            message = StatusMessage(text, level, duration=duration)
            self.status_messages.append(message)

    def set_progress(self, value: float, text: str = ""):
        """设置进度条"""
        with self._lock:
            self.progress_value = max(0.0, min(1.0, value))
            self.progress_text = text

    def _get_feedback_level_from_state(self, state: AgentState) -> FeedbackLevel:
        """从状态获取反馈级别"""
        level_mapping = {
            AgentState.SUCCESS: FeedbackLevel.SUCCESS,
            AgentState.ERROR: FeedbackLevel.ERROR,
            AgentState.PROCESSING: FeedbackLevel.INFO,
            AgentState.CONFIRMING: FeedbackLevel.WARNING,
            AgentState.THINKING: FeedbackLevel.INFO
        }
        return level_mapping.get(state, FeedbackLevel.INFO)

    def _cleanup_expired_messages(self):
        """清理过期消息"""
        with self._lock:
            self.status_messages = [
                msg for msg in self.status_messages
                if not msg.is_expired()
            ]

    def _draw_status_box(self, frame: np.ndarray):
        """绘制状态框"""
        if not self.config.enable_status_display:
            return

        x, y = self.config.status_position

        # 准备状态文本
        icon = self.state_icons.get(self.current_state, "⚪")
        text = self.state_texts.get(self.current_state, "未知状态")
        status_text = f"{icon} {text}"

        # 获取状态颜色
        color_name = self.current_state.value
        color = self.config.colors.get(color_name, self.config.colors["text"])

        # 绘制半透明背景
        overlay = frame.copy()
        cv2.rectangle(overlay, (x-5, y-25), (x + 400, y+5),
                     self.config.colors["background"], -1)
        frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)

        # 绘制状态文本
        cv2.putText(frame, status_text, (x, y),
                   cv2.FONT_HERSHEY_SIMPLEX, self.config.font_scale,
                   color, self.config.thickness, self.config.line_type)

    def _draw_messages(self, frame: np.ndarray):
        """绘制消息"""
        if not self.config.enable_message_overlay or not self.status_messages:
            return

        x, y = self.config.message_position

        # 清理过期消息
        self._cleanup_expired_messages()

        # 绘制消息（最多显示3条）
        for i, message in enumerate(self.status_messages[-3:]):
            msg_y = y + i * 30

            # 获取消息颜色
            color = self.config.colors.get(message.level.value, self.config.colors["text"])

            # 绘制消息背景
            overlay = frame.copy()
            cv2.rectangle(overlay, (x-5, msg_y-25), (x + 600, msg_y+5),
                         self.config.colors["background"], -1)
            frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)

            # 绘制消息文本
            cv2.putText(frame, message.text[:50], (x, msg_y),
                       cv2.FONT_HERSHEY_SIMPLEX, self.config.font_scale * 0.8,
                       color, 1, self.config.line_type)

    def _draw_progress_bar(self, frame: np.ndarray):
        """绘制进度条"""
        if not self.config.enable_progress_bar or self.progress_value <= 0:
            return

        x, y = self.config.progress_bar_position
        bar_width = 300
        bar_height = 20

        # 绘制进度条背景
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height),
                     self.config.colors["background"], -1)
        cv2.rectangle(frame, (x, y), (x + bar_width, y + bar_height),
                     self.config.colors["text"], 1)

        # 绘制进度条填充
        fill_width = int(bar_width * self.progress_value)
        cv2.rectangle(frame, (x, y), (x + fill_width, y + bar_height),
                     self.config.colors["processing"], -1)

        # 绘制进度文本
        if self.progress_text:
            progress_text = f"{self.progress_text} {int(self.progress_value * 100)}%"
        else:
            progress_text = f"{int(self.progress_value * 100)}%"

        cv2.putText(frame, progress_text, (x + bar_width + 10, y + 15),
                   cv2.FONT_HERSHEY_SIMPLEX, self.config.font_scale * 0.7,
                   self.config.colors["text"], 1, self.config.line_type)

    def _draw_gesture_indicators(self, frame: np.ndarray, gestures: List[Any] = None):
        """绘制手势指示器"""
        if not self.config.enable_gesture_indicators or not gestures:
            return

        # 在左下角绘制手势指示器
        h, w = frame.shape[:2]
        indicator_y = h - 30

        for i, gesture in enumerate(gestures[-3:]):  # 最多显示3个手势
            indicator_x = 10 + i * 120

            # 获取手势信息
            gesture_name = getattr(gesture, 'gesture_code', 'unknown')
            confidence = getattr(gesture, 'confidence', 0.0)

            # 绘制手势背景
            overlay = frame.copy()
            cv2.rectangle(overlay, (indicator_x-5, indicator_y-25),
                         (indicator_x + 110, indicator_y+5),
                         self.config.colors["background"], -1)
            frame = cv2.addWeighted(frame, 0.7, overlay, 0.3, 0)

            # 绘制手势文本
            gesture_text = f"{gesture_name}: {confidence:.2f}"
            cv2.putText(frame, gesture_text, (indicator_x, indicator_y),
                       cv2.FONT_HERSHEY_SIMPLEX, self.config.font_scale * 0.6,
                       self.config.colors["accent"], 1, self.config.line_type)

    def draw_feedback(self, frame: np.ndarray, gestures: List[Any] = None) -> np.ndarray:
        """在帧上绘制所有视觉反馈"""
        with self._lock:
            # 创建帧的副本
            result_frame = frame.copy()

            # 绘制各种反馈元素
            self._draw_status_box(result_frame)
            self._draw_messages(result_frame)
            self._draw_progress_bar(result_frame)
            self._draw_gesture_indicators(result_frame, gestures)

            return result_frame

    def get_current_status(self) -> Dict[str, Any]:
        """获取当前状态信息"""
        with self._lock:
            return {
                "state": self.current_state.value,
                "state_text": self.state_texts.get(self.current_state, ""),
                "active_messages": len([msg for msg in self.status_messages if not msg.is_expired()]),
                "progress": self.progress_value,
                "progress_text": self.progress_text
            }

    def clear_messages(self):
        """清除所有消息"""
        with self._lock:
            self.status_messages.clear()

    def reset(self):
        """重置反馈系统"""
        with self._lock:
            self.current_state = AgentState.IDLE
            self.status_messages.clear()
            self.progress_value = 0.0
            self.progress_text = ""


# 全局视觉反馈实例
_visual_feedback_instance: Optional[VisualFeedback] = None


def get_visual_feedback(config: VisualFeedbackConfig = None) -> VisualFeedback:
    """获取全局视觉反馈实例"""
    global _visual_feedback_instance
    if _visual_feedback_instance is None:
        _visual_feedback_instance = VisualFeedback(config)
    return _visual_feedback_instance


# 便捷函数
def set_agent_state(state: AgentState, message: str = None):
    """设置Agent状态"""
    feedback = get_visual_feedback()
    feedback.set_state(state, message)


def add_status_message(text: str, level: FeedbackLevel = FeedbackLevel.INFO, duration: float = 3.0):
    """添加状态消息"""
    feedback = get_visual_feedback()
    feedback.add_message(text, level, duration)


def set_progress(value: float, text: str = ""):
    """设置进度"""
    feedback = get_visual_feedback()
    feedback.set_progress(value, text)


def draw_feedback_on_frame(frame: np.ndarray, gestures: List[Any] = None) -> np.ndarray:
    """在帧上绘制反馈（便捷函数）"""
    feedback = get_visual_feedback()
    return feedback.draw_feedback(frame, gestures)