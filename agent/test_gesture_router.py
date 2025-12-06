"""
GestureRouter单元测试

测试手势路由器的快慢通道路由策略
"""

import unittest
import sys
import os
import time
from unittest.mock import Mock, patch

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# Mock GestureResult to avoid MediaPipe dependency
class MockGestureResult:
    def __init__(self, gesture_code, confidence, bbox, handedness):
        self.gesture_code = gesture_code
        self.confidence = confidence
        self.bbox = bbox
        self.handedness = handedness

# Mock the import to avoid MediaPipe issues
import unittest.mock
sys.modules['gestures.mediapipe_detector'] = unittest.mock.MagicMock()
sys.modules['gestures.mediapipe_detector'].GestureResult = MockGestureResult

from gesture_router import GestureRouter, RouteType, RouteDecision, GestureRoute
from context_manager import ContextManager, VisualContext, DetectedObject

# Use MockGestureResult as GestureResult
GestureResult = MockGestureResult


class TestGestureRouter(unittest.TestCase):
    """GestureRouter测试类"""

    def setUp(self):
        """测试前准备"""
        self.context_manager = ContextManager({
            "max_history_size": 10,
            "object_timeout": 2.0
        })
        self.router = GestureRouter(self.context_manager)

    def test_gesture_router_initialization(self):
        """测试GestureRouter初始化"""
        self.assertIsNotNone(self.router)
        self.assertIsNotNone(self.router.routes)
        self.assertGreater(len(self.router.routes), 0)
        self.assertEqual(self.router.stats["total_routes"], 0)

    def test_fast_path_routing(self):
        """测试快通道路由"""
        # 创建高置信度的victory手势
        gesture_result = GestureResult(
            gesture_code="victory",
            confidence=0.9,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        decision = self.router.route_gesture(gesture_result)

        # 验证快通道决策
        self.assertEqual(decision.route_type, RouteType.FAST_PATH)
        self.assertEqual(decision.confidence, 0.9)
        self.assertIsNotNone(decision.expected_action)
        self.assertEqual(decision.expected_action["type"], "system")
        self.assertEqual(decision.expected_action["value"], "toggle_control")

    def test_slow_path_routing(self):
        """测试慢通道路由"""
        # 创建需要上下文的open_palm手势
        gesture_result = GestureResult(
            gesture_code="open_palm",
            confidence=0.8,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 添加一些视觉上下文
        visual_context = VisualContext(
            timestamp=time.time(),
            frame_id=1,
            detected_objects=[
                DetectedObject(name="cup", confidence=0.9, bbox=[50, 50, 150, 150], timestamp=time.time())
            ],
            current_gesture=None,
            current_pose=None,
            current_emotion=None,
            scene_description="A cup on table"
        )

        decision = self.router.route_gesture(gesture_result, visual_context)

        # 验证慢通道决策
        self.assertEqual(decision.route_type, RouteType.SLOW_PATH)
        self.assertEqual(decision.confidence, 0.8)
        self.assertIsNone(decision.expected_action)  # 慢通道没有预定义动作

    def test_confidence_threshold_filtering(self):
        """测试置信度阈值过滤"""
        # 创建低置信度的手势
        gesture_result = GestureResult(
            gesture_code="thumbs_up",
            confidence=0.5,  # 低于默认阈值0.7
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        decision = self.router.route_gesture(gesture_result)

        # 验证被忽略
        self.assertEqual(decision.route_type, RouteType.IGNORE)
        self.assertIn("below threshold", decision.reasoning)

    def test_unknown_gesture_handling(self):
        """测试未知手势处理"""
        # 创建未知手势
        gesture_result = GestureResult(
            gesture_code="unknown_gesture",
            confidence=0.9,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        decision = self.router.route_gesture(gesture_result)

        # 验证被忽略
        self.assertEqual(decision.route_type, RouteType.IGNORE)
        self.assertIn("Unknown gesture", decision.reasoning)

    def test_context_enhanced_point_up_gesture(self):
        """测试指向手势的上下文增强"""
        gesture_result = GestureResult(
            gesture_code="point_up",
            confidence=0.85,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 添加单个物体上下文
        visual_context = VisualContext(
            timestamp=time.time(),
            frame_id=1,
            detected_objects=[
                DetectedObject(name="laptop", confidence=0.9, bbox=[50, 50, 150, 150], timestamp=time.time())
            ],
            current_gesture=None,
            current_pose=None,
            current_emotion=None,
            scene_description="A laptop on desk"
        )

        decision = self.router.route_gesture(gesture_result, visual_context)

        # 指向手势在有物体时应该走慢通道
        self.assertEqual(decision.route_type, RouteType.SLOW_PATH)
        self.assertIn("object: laptop", decision.reasoning)

    def test_context_enhanced_point_up_without_objects(self):
        """测试没有物体时的指向手势"""
        gesture_result = GestureResult(
            gesture_code="point_up",
            confidence=0.85,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 没有物体的上下文
        visual_context = VisualContext(
            timestamp=time.time(),
            frame_id=1,
            detected_objects=[],
            current_gesture=None,
            current_pose=None,
            current_emotion=None,
            scene_description="Empty scene"
        )

        decision = self.router.route_gesture(gesture_result, visual_context)

        # 没有物体时应该走快通道，使用默认点击
        self.assertEqual(decision.route_type, RouteType.FAST_PATH)
        self.assertIsNotNone(decision.expected_action)
        self.assertEqual(decision.expected_action["type"], "click")

    def test_context_enhanced_open_palm_with_objects(self):
        """测试有物体时的张开手掌手势"""
        gesture_result = GestureResult(
            gesture_code="open_palm",
            confidence=0.8,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 有物体的上下文
        visual_context = VisualContext(
            timestamp=time.time(),
            frame_id=1,
            detected_objects=[
                DetectedObject(name="book", confidence=0.9, bbox=[50, 50, 150, 150], timestamp=time.time())
            ],
            current_gesture=None,
            current_pose=None,
            current_emotion=None,
            scene_description="A book on table"
        )

        decision = self.router.route_gesture(gesture_result, visual_context)

        # 有物体时应该走慢通道进行意图分析
        self.assertEqual(decision.route_type, RouteType.SLOW_PATH)
        self.assertIn("objects detected", decision.reasoning)

    def test_context_enhanced_open_palm_without_objects(self):
        """测试没有物体时的张开手掌手势"""
        gesture_result = GestureResult(
            gesture_code="open_palm",
            confidence=0.8,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 没有物体的上下文
        visual_context = VisualContext(
            timestamp=time.time(),
            frame_id=1,
            detected_objects=[],
            current_gesture=None,
            current_pose=None,
            current_emotion=None,
            scene_description="Empty scene"
        )

        decision = self.router.route_gesture(gesture_result, visual_context)

        # 没有物体时应该走快通道，使用默认暂停动作
        self.assertEqual(decision.route_type, RouteType.FAST_PATH)
        self.assertIsNotNone(decision.expected_action)
        self.assertEqual(decision.expected_action["type"], "hotkey")
        self.assertEqual(decision.expected_action["value"], "space")

    def test_fist_gesture_with_context(self):
        """测试握拳手势的上下文处理"""
        gesture_result = GestureResult(
            gesture_code="fist",
            confidence=0.85,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 有物体的上下文
        visual_context = VisualContext(
            timestamp=time.time(),
            frame_id=1,
            detected_objects=[
                DetectedObject(name="document", confidence=0.9, bbox=[50, 50, 150, 150], timestamp=time.time())
            ],
            current_gesture=None,
            current_pose=None,
            current_emotion=None,
            scene_description="Document on screen"
        )

        decision = self.router.route_gesture(gesture_result, visual_context)

        # 有物体时应该走慢通道
        self.assertEqual(decision.route_type, RouteType.SLOW_PATH)
        self.assertIn("objects", decision.reasoning)

    def test_case_insensitive_gesture_matching(self):
        """测试大小写不敏感的手势匹配"""
        # 测试不同大小写的手势码
        gesture_variants = ["VICTORY", "Victory", "victory", "VICTORY"]

        for gesture_code in gesture_variants:
            gesture_result = GestureResult(
                gesture_code=gesture_code,
                confidence=0.9,
                bbox=[100, 100, 200, 200],
                handedness="right"
            )

            decision = self.router.route_gesture(gesture_result)
            self.assertEqual(decision.route_type, RouteType.FAST_PATH)
            self.assertEqual(decision.confidence, 0.9)

    def test_statistics_tracking(self):
        """测试统计信息跟踪"""
        # 执行多个路由决策
        gestures = [
            ("victory", 0.9, RouteType.FAST_PATH),
            ("thumbs_up", 0.8, RouteType.FAST_PATH),
            ("open_palm", 0.7, RouteType.IGNORE),  # 需要上下文但没有提供，会被忽略
            ("unknown", 0.9, RouteType.IGNORE),
            ("thumbs_down", 0.5, RouteType.IGNORE)  # 低置信度
        ]

        for gesture_code, confidence, expected_route in gestures:
            gesture_result = GestureResult(
                gesture_code=gesture_code,
                confidence=confidence,
                bbox=[100, 100, 200, 200],
                handedness="right"
            )
            decision = self.router.route_gesture(gesture_result)
            self.assertEqual(decision.route_type, expected_route)

        # 测试open_palm在有上下文时的慢通道路由
        visual_context = VisualContext(
            timestamp=time.time(),
            frame_id=1,
            detected_objects=[
                DetectedObject(name="test_object", confidence=0.9, bbox=[50, 50, 150, 150], timestamp=time.time())
            ],
            current_gesture=None,
            current_pose=None,
            current_emotion=None,
            scene_description="Test scene"
        )
        open_palm_result = GestureResult(
            gesture_code="open_palm",
            confidence=0.8,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )
        open_palm_decision = self.router.route_gesture(open_palm_result, visual_context)
        self.assertEqual(open_palm_decision.route_type, RouteType.SLOW_PATH)

        # 验证统计信息
        stats = self.router.get_route_statistics()
        self.assertEqual(stats["total_routes"], 6)
        self.assertEqual(stats["fast_path_routes"], 2)
        self.assertEqual(stats["slow_path_routes"], 1)
        self.assertEqual(stats["ignored_routes"], 3)
        self.assertGreater(stats["average_confidence"], 0.6)  # 平均值是0.616...

        # 验证百分比计算（使用近似比较）
        self.assertAlmostEqual(stats["fast_path_percentage"], 33.33, places=1)  # 2/6 * 100
        self.assertAlmostEqual(stats["slow_path_percentage"], 16.67, places=1)  # 1/6 * 100
        self.assertAlmostEqual(stats["ignored_percentage"], 50.0, places=1)   # 3/6 * 100

    def test_custom_route_addition(self):
        """测试自定义路由添加"""
        # 添加自定义路由
        custom_route = GestureRoute(
            gesture_code="custom_gesture",
            route_type=RouteType.FAST_PATH,
            priority=15,
            confidence_threshold=0.6,
            context_required=False,
            description="Custom test gesture",
            fast_action={"type": "hotkey", "value": "c"}
        )

        self.router.add_custom_route("custom_gesture", custom_route)

        # 测试自定义路由
        gesture_result = GestureResult(
            gesture_code="custom_gesture",
            confidence=0.8,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        decision = self.router.route_gesture(gesture_result)
        self.assertEqual(decision.route_type, RouteType.FAST_PATH)
        self.assertEqual(decision.expected_action["type"], "hotkey")
        self.assertEqual(decision.expected_action["value"], "c")

    def test_route_removal(self):
        """测试路由移除"""
        # 确保victory路由存在
        gesture_result = GestureResult(
            gesture_code="victory",
            confidence=0.9,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )
        decision = self.router.route_gesture(gesture_result)
        self.assertEqual(decision.route_type, RouteType.FAST_PATH)

        # 移除路由
        self.router.remove_route("victory")

        # 再次测试应该被忽略
        decision = self.router.route_gesture(gesture_result)
        self.assertEqual(decision.route_type, RouteType.IGNORE)

    def test_route_history_management(self):
        """测试路由历史管理"""
        # 创建一些路由决策
        for i in range(5):
            gesture_result = GestureResult(
                gesture_code="victory",
                confidence=0.9,
                bbox=[100, 100, 200, 200],
                handedness="right"
            )
            self.router.route_gesture(gesture_result)

        # 验证历史记录
        recent_routes = self.router.get_recent_routes(3)
        self.assertEqual(len(recent_routes), 3)

        # 清空历史
        self.router.clear_history()
        recent_routes = self.router.get_recent_routes()
        self.assertEqual(len(recent_routes), 0)

    def test_context_manager_integration(self):
        """测试与ContextManager的集成"""
        # 添加一些上下文数据
        self.context_manager.update_context(
            detected_objects=[
                {"name": "phone", "confidence": 0.9, "bbox": [50, 50, 150, 150]}
            ],
            frame_id=1
        )

        # 创建需要上下文的手势
        gesture_result = GestureResult(
            gesture_code="point_up",
            confidence=0.85,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 不提供visual_context，应该自动从context_manager获取
        decision = self.router.route_gesture(gesture_result)

        # 应该能够获取到上下文并正确路由
        self.assertEqual(decision.route_type, RouteType.SLOW_PATH)
        self.assertIsNotNone(decision.visual_context)
        self.assertGreater(len(decision.visual_context.detected_objects), 0)

    def test_string_representation(self):
        """测试字符串表示"""
        # 添加一些路由决策以生成统计数据
        for gesture_code, confidence, _ in [
            ("victory", 0.9, None),
            ("open_palm", 0.8, None),
            ("unknown", 0.7, None)
        ]:
            gesture_result = GestureResult(
                gesture_code=gesture_code,
                confidence=confidence,
                bbox=[100, 100, 200, 200],
                handedness="right"
            )
            self.router.route_gesture(gesture_result)

        # 测试字符串表示
        str_repr = str(self.router)
        self.assertIn("GestureRouter", str_repr)
        self.assertIn("total_routes=3", str_repr)
        self.assertIn("fast=", str_repr)
        self.assertIn("slow=", str_repr)
        self.assertIn("ignored=", str_repr)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)