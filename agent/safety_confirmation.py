"""
安全确认机制模块

为敏感操作提供手势确认和用户确认功能
"""

import time
import threading
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging

from gestures.mediapipe_detector import GestureResult

# 设置安全确认日志
logger = logging.getLogger(__name__)


class ConfirmationType(Enum):
    """确认类型"""
    YES_NO = "yes_no"
    OK_CANCEL = "ok_cancel"
    CUSTOM = "custom"


class ConfirmationStatus(Enum):
    """确认状态"""
    PENDING = "pending"  # 等待确认
    APPROVED = "approved"  # 已确认
    REJECTED = "rejected"  # 已拒绝
    TIMEOUT = "timeout"    # 超时
    CANCELLED = "cancelled"  # 已取消


class ConfirmationLevel(Enum):
    """确认级别"""
    LOW = "low"       # 低风险操作
    MEDIUM = "medium"   # 中等风险操作
    HIGH = "high"     # 高风险操作
    CRITICAL = "critical"  # 关键风险操作


@dataclass
class ConfirmationRequest:
    """确认请求"""
    request_id: str
    action_type: str
    action_value: str
    action_payload: Optional[Dict[str, Any]]
    confirmation_type: ConfirmationType
    confirmation_level: ConfirmationLevel
    message: str
    timeout: float = 30.0  # 确认超时时间（秒）
    required_gestures: List[str] = None  # 需要的手势
    custom_options: List[str] = None  # 自定义选项
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.required_gestures is None:
            self.required_gestures = ["thumbs_up", "thumbs_down"]  # 默认手势
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConfirmationResponse:
    """确认响应"""
    request_id: str
    status: ConfirmationStatus
    confirmed_action: Optional[str] = None  # 确认的动作
    confidence: float = 0.0
    gesture_used: Optional[str] = None
    timestamp: float = None
    response_time: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class SafetyConfirmationManager:
    """安全确认管理器"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.pending_requests: Dict[str, ConfirmationRequest] = {}
        self.response_callbacks: Dict[str, Callable[[ConfirmationResponse], None]] = {}
        self.gesture_handlers: Dict[str, Callable[[GestureResult], bool]] = {}

        # 线程安全
        self._lock = threading.RLock()

        # 默认配置
        self.default_timeout = self.config.get("default_timeout", 30.0)
        self.max_pending_requests = self.config.get("max_pending_requests", 5)
        self.auto_approve_safe_actions = self.config.get("auto_approve_safe_actions", True)

        # 手势映射
        self.gesture_mappings = {
            "thumbs_up": "approve",
            "ok": "approve",
            "victory": "approve",
            "thumbs_down": "reject",
            "point_down": "reject",
            "fist": "reject",
            "open_palm": "cancel"
        }

        # 危险操作类型映射
        self.dangerous_action_types = {
            "email_send": ConfirmationLevel.HIGH,
            "file_delete": ConfirmationLevel.HIGH,
            "system_shutdown": ConfirmationLevel.CRITICAL,
            "hotkey_ctrl_alt_delete": ConfirmationLevel.CRITICAL,
            "web_submit": ConfirmationLevel.MEDIUM,
            "text_send": ConfirmationLevel.LOW
        }

    def is_action_dangerous(self, action_type: str, action_value: str = None) -> tuple[bool, ConfirmationLevel]:
        """检查操作是否危险"""
        level = self.dangerous_action_types.get(action_type, ConfirmationLevel.LOW)

        # 检查特定的危险操作值
        dangerous_keywords = ["delete", "remove", "shutdown", "restart", "send", "submit"]
        if action_value and any(keyword in action_value.lower() for keyword in dangerous_keywords):
            if level == ConfirmationLevel.LOW:
                level = ConfirmationLevel.MEDIUM

        # 特殊组合检测
        if action_type == "hotkey" and action_value:
            if any(key in action_value.upper() for key in ["DELETE", "ALT+F4", "CTRL+ALT+DEL"]):
                level = ConfirmationLevel.CRITICAL

        return level != ConfirmationLevel.LOW, level

    def request_confirmation(
        self,
        action_type: str,
        action_value: str,
        action_payload: Optional[Dict[str, Any]] = None,
        custom_message: str = None,
        confirmation_callback: Callable[[ConfirmationResponse], None] = None
    ) -> Optional[str]:
        """请求确认"""
        with self._lock:
            # 检查是否需要确认
            is_dangerous, level = self.is_action_dangerous(action_type, action_value)

            if not is_dangerous and self.auto_approve_safe_actions:
                logger.info(f"Safe action auto-approved: {action_type} - {action_value}")
                return None

            # 生成请求ID
            request_id = f"conf_{int(time.time() * 1000000)}_{len(self.pending_requests)}"

            # 确定确认类型和消息
            confirmation_type = ConfirmationType.YES_NO
            custom_options = None
            if level in [ConfirmationLevel.CRITICAL]:
                confirmation_type = ConfirmationType.CUSTOM
                custom_options = ["确认执行", "取消操作", "了解更多"]
                message = custom_message or f"确认执行关键操作: {action_type} - {action_value}?"
            elif level == ConfirmationLevel.HIGH:
                message = custom_message or f"确认执行危险操作: {action_type} - {action_value}?"
            else:
                message = custom_message or f"确认操作: {action_type} - {action_value}?"

            # 创建确认请求
            request = ConfirmationRequest(
                request_id=request_id,
                action_type=action_type,
                action_value=action_value,
                action_payload=action_payload,
                confirmation_type=confirmation_type,
                confirmation_level=level,
                message=message,
                timeout=self.default_timeout,
                required_gestures=self._get_required_gestures(level),
                custom_options=custom_options,
                metadata={"created_at": time.time()}
            )

            # 检查 pending请求数量限制
            if len(self.pending_requests) >= self.max_pending_requests:
                logger.warning("Too many pending confirmation requests")
                return None

            # 存储请求和回调
            self.pending_requests[request_id] = request
            if confirmation_callback:
                self.response_callbacks[request_id] = confirmation_callback

            # 启动超时定时器
            self._start_timeout_timer(request_id)

            logger.info(f"Confirmation requested: {request_id} - {message}")
            return request_id

    def handle_gesture_confirmation(self, gesture_result: GestureResult) -> bool:
        """处理手势确认"""
        with self._lock:
            if not self.pending_requests:
                return False

            # 获取最新的待确认请求
            latest_request_id = max(self.pending_requests.keys())
            request = self.pending_requests[latest_request_id]

            # 检查手势是否在要求的手势列表中
            if gesture_result.gesture_code not in request.required_gestures:
                return False

            # 解析手势意图
            gesture_intent = self._parse_gesture_intent(gesture_result)

            # 生成确认响应
            response = ConfirmationResponse(
                request_id=latest_request_id,
                status=self._map_intent_to_status(gesture_intent),
                gesture_used=gesture_result.gesture_code,
                confidence=gesture_result.confidence,
                timestamp=time.time(),
                response_time=time.time() - request.metadata["created_at"]
            )

            # 处理确认结果
            self._handle_confirmation_response(response)

            logger.info(f"Gesture confirmation: {latest_request_id} - {gesture_intent} (confidence: {gesture_result.confidence:.2f})")
            return True

    def cancel_confirmation(self, request_id: str) -> bool:
        """取消确认请求"""
        with self._lock:
            if request_id not in self.pending_requests:
                return False

            request = self.pending_requests[request_id]
            response = ConfirmationResponse(
                request_id=request_id,
                status=ConfirmationStatus.CANCELLED
            )

            self._handle_confirmation_response(response)
            logger.info(f"Confirmation cancelled: {request_id}")
            return True

    def get_pending_requests(self) -> List[ConfirmationRequest]:
        """获取待确认请求列表"""
        with self._lock:
            return list(self.pending_requests.values())

    def get_request_status(self, request_id: str) -> Optional[ConfirmationRequest]:
        """获取请求状态"""
        with self._lock:
            return self.pending_requests.get(request_id)

    def _get_required_gestures(self, level: ConfirmationLevel) -> List[str]:
        """根据风险级别获取需要的手势"""
        if level == ConfirmationLevel.CRITICAL:
            return ["thumbs_up", "thumbs_down", "ok"]
        elif level == ConfirmationLevel.HIGH:
            return ["thumbs_up", "thumbs_down"]
        else:
            return ["ok", "victory"]

    def _parse_gesture_intent(self, gesture_result: GestureResult) -> str:
        """解析手势意图"""
        return self.gesture_mappings.get(gesture_result.gesture_code, "unknown")

    def _map_intent_to_status(self, intent: str) -> ConfirmationStatus:
        """将手势意图映射到确认状态"""
        if intent in ["approve", "yes", "ok"]:
            return ConfirmationStatus.APPROVED
        elif intent in ["reject", "no", "cancel"]:
            return ConfirmationStatus.REJECTED
        else:
            return ConfirmationStatus.CANCELLED

    def _handle_confirmation_response(self, response: ConfirmationResponse):
        """处理确认响应"""
        request_id = response.request_id

        # 移除待确认请求
        if request_id in self.pending_requests:
            del self.pending_requests[request_id]

        # 调用回调函数
        if request_id in self.response_callbacks:
            callback = self.response_callbacks[request_id]
            try:
                callback(response)
            except Exception as e:
                logger.error(f"Error in confirmation callback: {e}")
            finally:
                del self.response_callbacks[request_id]

    def _start_timeout_timer(self, request_id: str):
        """启动超时定时器"""
        def timeout_callback():
            self._handle_confirmation_timeout(request_id)

        timer = threading.Timer(self.pending_requests[request_id].timeout, timeout_callback)
        timer.daemon = True
        timer.start()

    def _handle_confirmation_timeout(self, request_id: str):
        """处理确认超时"""
        with self._lock:
            if request_id in self.pending_requests:
                request = self.pending_requests[request_id]
                response = ConfirmationResponse(
                    request_id=request_id,
                    status=ConfirmationStatus.TIMEOUT
                )
                self._handle_confirmation_response(response)
                logger.warning(f"Confirmation timeout: {request_id}")

    def configure_action_requirements(self, action_type: str, level: ConfirmationLevel, custom_message: str = None):
        """配置特定操作的要求"""
        self.dangerous_action_types[action_type] = level
        if custom_message:
            self.action_messages = getattr(self, 'action_messages', {})
            self.action_messages[action_type] = custom_message

    def get_confirmation_statistics(self) -> Dict[str, Any]:
        """获取确认统计信息"""
        with self._lock:
            stats = {
                "pending_requests": len(self.pending_requests),
                "max_pending": self.max_pending_requests,
                "auto_approve_safe": self.auto_approve_safe_actions,
                "dangerous_action_types": len([t for t in self.dangerous_action_types.values()
                                                if t != ConfirmationLevel.LOW])
            }

            # 按级别统计待确认请求
            level_counts = {}
            for request in self.pending_requests.values():
                level = request.confirmation_level.value
                level_counts[level] = level_counts.get(level, 0) + 1

            stats["pending_by_level"] = level_counts
            return stats


# 全局安全确认管理器实例
_safety_confirmation_manager: Optional[SafetyConfirmationManager] = None


def get_safety_confirmation_manager(config: Dict[str, Any] = None) -> SafetyConfirmationManager:
    """获取全局安全确认管理器实例"""
    global _safety_confirmation_manager
    if _safety_confirmation_manager is None:
        _safety_confirmation_manager = SafetyConfirmationManager(config)
    return _safety_confirmation_manager


# 便捷函数
def request_action_confirmation(
    action_type: str,
    action_value: str,
    action_payload: Optional[Dict[str, Any]] = None,
    custom_message: str = None,
    callback: Callable[[ConfirmationResponse], None] = None
) -> Optional[str]:
    """请求操作确认（便捷函数）"""
    manager = get_safety_confirmation_manager()
    return manager.request_confirmation(
        action_type,
        action_value,
        action_payload,
        custom_message=custom_message,
        confirmation_callback=callback
    )


def handle_confirmation_gesture(gesture_result: GestureResult) -> bool:
    """处理确认手势（便捷函数）"""
    manager = get_safety_confirmation_manager()
    return manager.handle_gesture_confirmation(gesture_result)