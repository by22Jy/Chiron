"""
GestureRouter - 手势路由器

实现快慢通道路由策略，区分：
1. 快捷手势（快通道）：直接映射到固定动作
2. 复杂手势（慢通道）：需要LLM意图理解和上下文分析
"""

import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from gestures.mediapipe_detector import GestureResult
from context_manager import ContextManager, VisualContext

# 设置路由器日志
logger = logging.getLogger(__name__)


class RouteType(Enum):
    """路由类型"""
    FAST_PATH = "fast_path"      # 快通道：直接执行
    SLOW_PATH = "slow_path"      # 慢通道：LLM分析
    IGNORE = "ignore"            # 忽略：不处理


@dataclass
class RouteDecision:
    """路由决策结果"""
    route_type: RouteType
    confidence: float
    reasoning: str
    gesture_result: Optional[GestureResult] = None
    visual_context: Optional[VisualContext] = None
    expected_action: Optional[Dict[str, Any]] = None


@dataclass
class GestureRoute:
    """手势路由规则"""
    gesture_code: str
    route_type: RouteType
    priority: int = 0  # 优先级，数字越大优先级越高
    confidence_threshold: float = 0.7  # 置信度阈值
    context_required: bool = False  # 是否需要上下文
    description: str = ""
    fast_action: Optional[Dict[str, Any]] = None  # 快通道对应的固定动作


class GestureRouter:
    """手势路由器

    根据手势类型、置信度、视觉上下文等因素，决定手势的处理路由：
    - 快通道：简单、明确的手势，直接执行预定义动作
    - 慢通道：复杂、需要理解意图的手势，交给LLM处理
    """

    def __init__(self, context_manager: Optional[ContextManager] = None):
        self.context_manager = context_manager
        self.routes: Dict[str, GestureRoute] = {}
        self.route_history: List[RouteDecision] = []
        self.max_history_size = 100

        # 统计信息
        self.stats = {
            "total_routes": 0,
            "fast_path_routes": 0,
            "slow_path_routes": 0,
            "ignored_routes": 0,
            "route_accuracy": 0.0,
            "average_confidence": 0.0,
            "context_usage_count": 0
        }

        # 初始化默认路由规则
        self._initialize_default_routes()

        logger.info("GestureRouter initialized with default routing rules")

    def _initialize_default_routes(self):
        """初始化默认的路由规则"""

        # 快通道手势 - 简单、明确的控制手势
        fast_path_gestures = {
            "victory": GestureRoute(
                gesture_code="victory",
                route_type=RouteType.FAST_PATH,
                priority=10,
                confidence_threshold=0.6,
                context_required=False,
                description="切换手势控制开关",
                fast_action={"type": "system", "value": "toggle_control"}
            ),
            "thumbs_up": GestureRoute(
                gesture_code="thumbs_up",
                route_type=RouteType.FAST_PATH,
                priority=9,
                confidence_threshold=0.7,
                context_required=False,
                description="确认/同意",
                fast_action={"type": "hotkey", "value": "enter"}
            ),
            "thumbs_down": GestureRoute(
                gesture_code="thumbs_down",
                route_type=RouteType.FAST_PATH,
                priority=9,
                confidence_threshold=0.7,
                context_required=False,
                description="取消/不同意",
                fast_action={"type": "hotkey", "value": "escape"}
            ),
            "ok_sign": GestureRoute(
                gesture_code="ok_sign",
                route_type=RouteType.FAST_PATH,
                priority=8,
                confidence_threshold=0.7,
                context_required=False,
                description="确定/完成",
                fast_action={"type": "hotkey", "value": "space"}
            ),
            "point_up": GestureRoute(
                gesture_code="point_up",
                route_type=RouteType.FAST_PATH,
                priority=7,
                confidence_threshold=0.8,
                context_required=True,  # 指向手势需要上下文
                description="指向选择，需要上下文理解",
                fast_action=None  # 需要根据上下文动态确定
            )
        }

        # 慢通道手势 - 需要意图理解的复杂手势
        slow_path_gestures = {
            "open_palm": GestureRoute(
                gesture_code="open_palm",
                route_type=RouteType.SLOW_PATH,
                priority=5,
                confidence_threshold=0.7,
                context_required=True,
                description="张开手掌，可能表示停止、展示或需要更多信息"
            ),
            "fist": GestureRoute(
                gesture_code="fist",
                route_type=RouteType.SLOW_PATH,
                priority=5,
                confidence_threshold=0.7,
                context_required=True,
                description="握拳，可能表示抓取、启动或强调"
            ),
            "peace": GestureRoute(
                gesture_code="peace",
                route_type=RouteType.SLOW_PATH,
                priority=4,
                confidence_threshold=0.6,
                context_required=True,
                description="和平手势，可能具有多重含义"
            ),
            "rock": GestureRoute(
                gesture_code="rock",
                route_type=RouteType.SLOW_PATH,
                priority=3,
                confidence_threshold=0.7,
                context_required=True,
                description="摇滚手势，通常用于娱乐控制"
            )
        }

        # 合并所有路由规则
        all_routes = {**fast_path_gestures, **slow_path_gestures}

        for gesture_code, route in all_routes.items():
            self.routes[gesture_code] = route

        logger.info(f"Initialized {len(fast_path_gestures)} fast path and {len(slow_path_gestures)} slow path routes")

    def route_gesture(self, gesture_result: GestureResult,
                     visual_context: Optional[VisualContext] = None) -> RouteDecision:
        """路由手势到合适的处理通道"""

        start_time = time.time()
        self.stats["total_routes"] += 1

        try:
            # 1. 获取手势的路由规则
            gesture_code_lower = gesture_result.gesture_code.lower()
            route = self.routes.get(gesture_code_lower)

            if not route:
                # 未知手势，忽略处理
                decision = RouteDecision(
                    route_type=RouteType.IGNORE,
                    confidence=0.0,
                    reasoning=f"Unknown gesture: {gesture_result.gesture_code}",
                    gesture_result=gesture_result,
                    visual_context=visual_context
                )
                self._update_stats(decision)
                return decision

            # 2. 检查置信度
            if gesture_result.confidence < route.confidence_threshold:
                decision = RouteDecision(
                    route_type=RouteType.IGNORE,
                    confidence=gesture_result.confidence,
                    reasoning=f"Gesture confidence {gesture_result.confidence:.2f} below threshold {route.confidence_threshold}",
                    gesture_result=gesture_result,
                    visual_context=visual_context
                )
                self._update_stats(decision)
                return decision

            # 3. 检查上下文需求
            if route.context_required and not visual_context:
                if self.context_manager:
                    visual_context = self.context_manager.get_current_context()

                if not visual_context:
                    # 需要上下文但没有提供，降级到快通道或忽略
                    if route.fast_action:
                        decision = RouteDecision(
                            route_type=RouteType.FAST_PATH,
                            confidence=gesture_result.confidence,
                            reasoning=f"No context available, using fallback fast action",
                            gesture_result=gesture_result,
                            visual_context=visual_context,
                            expected_action=route.fast_action
                        )
                    else:
                        decision = RouteDecision(
                            route_type=RouteType.IGNORE,
                            confidence=gesture_result.confidence,
                            reasoning=f"Context required but not available: {route.description}",
                            gesture_result=gesture_result,
                            visual_context=visual_context
                        )
                    self._update_stats(decision)
                    return decision
                else:
                    self.stats["context_usage_count"] += 1

            # 4. 上下文增强决策（针对需要上下文的手势）
            if route.context_required and visual_context:
                enhanced_decision = self._enhance_decision_with_context(
                    route, gesture_result, visual_context
                )
                if enhanced_decision:
                    self._update_stats(enhanced_decision)
                    return enhanced_decision

            # 5. 基础路由决策
            decision = RouteDecision(
                route_type=route.route_type,
                confidence=gesture_result.confidence,
                reasoning=f"Standard routing: {route.description}",
                gesture_result=gesture_result,
                visual_context=visual_context,
                expected_action=route.fast_action
            )

            self._update_stats(decision)

            processing_time = (time.time() - start_time) * 1000
            logger.debug(f"Gesture routed in {processing_time:.1f}ms: {route.route_type.value} for {gesture_result.gesture_code}")

            return decision

        except Exception as e:
            logger.error(f"Error routing gesture: {e}")
            decision = RouteDecision(
                route_type=RouteType.IGNORE,
                confidence=0.0,
                reasoning=f"Routing error: {str(e)}",
                gesture_result=gesture_result,
                visual_context=visual_context
            )
            self._update_stats(decision)
            return decision

    def _enhance_decision_with_context(self, route: GestureRoute,
                                     gesture_result: GestureResult,
                                     visual_context: VisualContext) -> Optional[RouteDecision]:
        """使用上下文信息增强路由决策"""

        try:
            gesture_code = gesture_result.gesture_code.lower()

            # 指向手势的特殊处理
            if gesture_code == "point_up":
                return self._handle_point_up_gesture(gesture_result, visual_context, route)

            # 张开手掌的上下文理解
            elif gesture_code == "open_palm":
                return self._handle_open_palm_gesture(gesture_result, visual_context, route)

            # 握拳的上下文理解
            elif gesture_code == "fist":
                return self._handle_fist_gesture(gesture_result, visual_context, route)

            return None

        except Exception as e:
            logger.warning(f"Context enhancement failed: {e}")
            return None

    def _handle_point_up_gesture(self, gesture_result: GestureResult,
                                visual_context: VisualContext,
                                route: GestureRoute) -> Optional[RouteDecision]:
        """处理指向手势的上下文理解"""

        if not visual_context or not visual_context.detected_objects:
            # 没有检测到物体，使用默认点击动作
            return RouteDecision(
                route_type=RouteType.FAST_PATH,
                confidence=gesture_result.confidence,
                reasoning="Point gesture without detected objects, using default click",
                gesture_result=gesture_result,
                visual_context=visual_context,
                expected_action={"type": "click", "value": "center"}
            )

        # 检测到物体，需要慢通道理解具体指向哪个物体
        high_conf_objects = [obj for obj in visual_context.detected_objects if obj.confidence > 0.6]

        if len(high_conf_objects) == 1:
            # 只有一个高置信度物体，可能是指向它
            object_name = high_conf_objects[0].name
            return RouteDecision(
                route_type=RouteType.SLOW_PATH,
                confidence=gesture_result.confidence,
                reasoning=f"Point gesture detected near object: {object_name}, needs intent analysis",
                gesture_result=gesture_result,
                visual_context=visual_context
            )
        elif len(high_conf_objects) > 1:
            # 多个物体，需要更复杂的意图理解
            return RouteDecision(
                route_type=RouteType.SLOW_PATH,
                confidence=gesture_result.confidence,
                reasoning=f"Point gesture with multiple objects ({len(high_conf_objects)}), requires complex intent analysis",
                gesture_result=gesture_result,
                visual_context=visual_context
            )

        return None

    def _handle_open_palm_gesture(self, gesture_result: GestureResult,
                                 visual_context: VisualContext,
                                 route: GestureRoute) -> Optional[RouteDecision]:
        """处理张开手掌手势的上下文理解"""

        # 根据当前场景判断意图
        if visual_context.detected_objects:
            # 有物体时，可能是想要停止操作或展示物体
            return RouteDecision(
                route_type=RouteType.SLOW_PATH,
                confidence=gesture_result.confidence,
                reasoning="Open palm with objects detected, intent unclear (stop/show/pause?)",
                gesture_result=gesture_result,
                visual_context=visual_context
            )
        else:
            # 没有物体时，可能是想要暂停或停止
            return RouteDecision(
                route_type=RouteType.FAST_PATH,
                confidence=gesture_result.confidence,
                reasoning="Open palm without objects, interpreted as pause/stop",
                gesture_result=gesture_result,
                visual_context=visual_context,
                expected_action={"type": "hotkey", "value": "space"}  # 暂停/播放
            )

    def _handle_fist_gesture(self, gesture_result: GestureResult,
                            visual_context: VisualContext,
                            route: GestureRoute) -> Optional[RouteDecision]:
        """处理握拳手势的上下文理解"""

        # 握拳通常表示确认、选择或抓取
        if visual_context.detected_objects:
            return RouteDecision(
                route_type=RouteType.SLOW_PATH,
                confidence=gesture_result.confidence,
                reasoning="Fist gesture with objects, could mean select/grab/confirm",
                gesture_result=gesture_result,
                visual_context=visual_context
            )
        else:
            return RouteDecision(
                route_type=RouteType.FAST_PATH,
                confidence=gesture_result.confidence,
                reasoning="Fist gesture without objects, interpreted as confirmation",
                gesture_result=gesture_result,
                visual_context=visual_context,
                expected_action={"type": "hotkey", "value": "enter"}
            )

    def _update_stats(self, decision: RouteDecision):
        """更新统计信息"""
        # 更新路由计数
        if decision.route_type == RouteType.FAST_PATH:
            self.stats["fast_path_routes"] += 1
        elif decision.route_type == RouteType.SLOW_PATH:
            self.stats["slow_path_routes"] += 1
        else:
            self.stats["ignored_routes"] += 1

        # 更新平均置信度
        total_routes = self.stats["total_routes"]
        current_avg = self.stats["average_confidence"]
        self.stats["average_confidence"] = ((current_avg * (total_routes - 1)) + decision.confidence) / total_routes

        # 添加到历史记录
        self.route_history.append(decision)
        if len(self.route_history) > self.max_history_size:
            self.route_history.pop(0)

    def add_custom_route(self, gesture_code: str, route: GestureRoute):
        """添加自定义路由规则"""
        self.routes[gesture_code.lower()] = route
        logger.info(f"Added custom route for {gesture_code}: {route.route_type.value}")

    def remove_route(self, gesture_code: str):
        """移除路由规则"""
        gesture_code_lower = gesture_code.lower()
        if gesture_code_lower in self.routes:
            del self.routes[gesture_code_lower]
            logger.info(f"Removed route for {gesture_code}")

    def get_route_statistics(self) -> Dict[str, Any]:
        """获取路由统计信息"""
        stats = self.stats.copy()
        total_routes = stats["total_routes"]

        # 计算路由分布
        if total_routes > 0:
            stats["fast_path_percentage"] = (stats["fast_path_routes"] / total_routes) * 100
            stats["slow_path_percentage"] = (stats["slow_path_routes"] / total_routes) * 100
            stats["ignored_percentage"] = (stats["ignored_routes"] / total_routes) * 100
        else:
            stats["fast_path_percentage"] = 0
            stats["slow_path_percentage"] = 0
            stats["ignored_percentage"] = 0

        stats["total_routes_configured"] = len(self.routes)
        stats["context_usage_percentage"] = (
            (stats["context_usage_count"] / total_routes) * 100 if total_routes > 0 else 0
        )

        return stats

    def get_recent_routes(self, limit: int = 10) -> List[RouteDecision]:
        """获取最近的路由决策"""
        return self.route_history[-limit:] if self.route_history else []

    def clear_history(self):
        """清空路由历史"""
        self.route_history.clear()
        logger.info("Route history cleared")

    def __str__(self) -> str:
        """字符串表示"""
        stats = self.get_route_statistics()
        return (f"GestureRouter(total_routes={stats['total_routes']}, "
                f"fast={stats['fast_path_percentage']:.1f}%, "
                f"slow={stats['slow_path_percentage']:.1f}%, "
                f"ignored={stats['ignored_percentage']:.1f}%)")