"""
GestureRouter集成测试

测试手势路由器与主Agent的集成功能
"""

import unittest
import sys
import os
import time
from unittest.mock import Mock, patch, MagicMock

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# Mock MediaPipe imports
import unittest.mock
sys.modules['gestures.mediapipe_detector'] = unittest.mock.MagicMock()

class MockGestureResult:
    def __init__(self, gesture_code, confidence, bbox, handedness):
        self.gesture_code = gesture_code
        self.confidence = confidence
        self.bbox = bbox
        self.handedness = handedness

sys.modules['gestures.mediapipe_detector'].GestureResult = MockGestureResult

from gesture_router import GestureRouter, RouteType, RouteDecision
from context_manager import ContextManager, VisualContext, DetectedObject
from actions.executor import execute_action


class TestGestureRouterIntegration(unittest.TestCase):
    """GestureRouter集成测试类"""

    def setUp(self):
        """测试前准备"""
        # Mock dependencies
        self.mock_agent = Mock()
        self.mock_agent.base_url = "http://127.0.0.1:8080"
        self.mock_agent.mapping = {}
        self.mock_agent.send_event = Mock()
        self.mock_agent.post_log = Mock()
        self.mock_agent.on_action_executed = Mock()

        # Initialize context manager
        self.context_manager = ContextManager({
            "max_history_size": 10,
            "object_timeout": 2.0
        })
        self.mock_agent.context_manager = self.context_manager

        # Initialize gesture router
        self.mock_agent.gesture_router = GestureRouter(self.context_manager)

        # Import agent methods for testing
        from main import GestureAgent
        self.agent = GestureAgent(config=None)
        self.agent.context_manager = self.context_manager
        self.agent.gesture_router = self.mock_agent.gesture_router
        self.agent.mapping = self.mock_agent.mapping
        self.agent.send_event = self.mock_agent.send_event
        self.agent.post_log = self.mock_agent.post_log
        self.agent.on_action_executed = self.mock_agent.on_action_executed

    def test_fast_path_routing_integration(self):
        """测试快通道路由集成"""
        # 创建victory手势（快通道）
        gesture_result = MockGestureResult(
            gesture_code="victory",
            confidence=0.9,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 模拟execute_action返回成功
        with patch('main.execute_action') as mock_execute:
            mock_execute.return_value = (True, "Action executed successfully")

            # 调用手势处理
            self.agent._on_gesture_detected(gesture_result)

            # 验证快通道动作被执行
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args[0]  # positional args
            self.assertEqual(call_args[0], "system")  # action_type
            self.assertEqual(call_args[1], "toggle_control")  # action_value

            # 验证事件记录
            self.agent.post_log.assert_called_once()

    def test_slow_path_routing_integration(self):
        """测试慢通道路由集成"""
        # 添加一些视觉上下文
        self.context_manager.update_context(
            detected_objects=[
                {"name": "laptop", "confidence": 0.9, "bbox": [50, 50, 150, 150]}
            ],
            frame_id=1
        )

        # 创建open_palm手势（慢通道，需要上下文）
        gesture_result = MockGestureResult(
            gesture_code="open_palm",
            confidence=0.8,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 调用手势处理
        self.agent._on_gesture_detected(gesture_result)

        # 验证慢通道手势被发送到后端
        self.agent.send_event.assert_called_once()
        call_args = self.agent.send_event.call_args[0]
        self.assertEqual(call_args[0], "slow_path_gesture")  # event_type

        # 验证事件数据包含必要信息
        event_data = call_args[1]
        self.assertEqual(event_data["gesture_code"], "open_palm")
        self.assertEqual(event_data["gesture_confidence"], 0.8)
        self.assertTrue(event_data["intent_analysis_required"])
        self.assertIn("visual_context", event_data)

    def test_ignore_routing_integration(self):
        """测试忽略路由集成"""
        # 创建低置信度手势
        gesture_result = MockGestureResult(
            gesture_code="thumbs_up",
            confidence=0.5,  # 低于阈值
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 调用手势处理
        self.agent._on_gesture_detected(gesture_result)

        # 验证没有执行任何动作或发送事件
        self.assertEqual(self.agent.send_event.call_count, 0)
        self.assertEqual(self.agent.post_log.call_count, 0)

    def test_context_enhanced_point_up_routing(self):
        """测试上下文增强的指向手势路由"""
        # 添加物体上下文
        self.context_manager.update_context(
            detected_objects=[
                {"name": "monitor", "confidence": 0.9, "bbox": [0, 0, 800, 600]}
            ],
            frame_id=1
        )

        # 创建指向手势
        gesture_result = MockGestureResult(
            gesture_code="point_up",
            confidence=0.85,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 调用手势处理
        self.agent._on_gesture_detected(gesture_result)

        # 验证慢通道路由被触发（因为有物体上下文）
        self.agent.send_event.assert_called_once()
        call_args = self.agent.send_event.call_args[0]
        self.assertEqual(call_args[0], "slow_path_gesture")

        event_data = call_args[1]
        self.assertEqual(event_data["gesture_code"], "point_up")
        self.assertIn("monitor", str(event_data.get("available_objects", [])))

    def test_fallback_to_mapping(self):
        """测试回退到传统映射处理"""
        # 设置路由器为None以测试回退机制
        self.agent.gesture_router = None

        # 添加传统映射
        self.agent.mapping = {
            "custom_gesture": {
                "type": "hotkey",
                "value": "ctrl+c"
            }
        }

        # 创建映射中定义的手势
        gesture_result = MockGestureResult(
            gesture_code="custom_gesture",
            confidence=0.9,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 模拟execute_action返回成功
        with patch('main.execute_action') as mock_execute:
            mock_execute.return_value = (True, "Hotkey executed")

            # 调用手势处理
            self.agent._on_gesture_detected(gesture_result)

            # 验证回退动作被执行
            mock_execute.assert_called_once()
            call_args = mock_execute.call_args[0]
            self.assertEqual(call_args[0], "hotkey")  # action_type
            self.assertEqual(call_args[1], "ctrl+c")  # action_value

    def test_error_handling(self):
        """测试错误处理"""
        # 创建会导致异常的手势（模拟execute_action失败）
        gesture_result = MockGestureResult(
            gesture_code="victory",
            confidence=0.9,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 模拟execute_action抛出异常
        with patch('main.execute_action') as mock_execute:
            mock_execute.side_effect = Exception("Test error")

            # 调用手势处理
            self.agent._on_gesture_detected(gesture_result)

            # 验证错误被正确处理并记录
            self.agent.post_log.assert_called()
            call_args = self.agent.post_log.call_args[1]  # kwargs
            self.assertEqual(call_args["action_type"], "error")
            self.assertEqual(call_args["status"], "failure")

    def test_visual_context_integration(self):
        """测试视觉上下文集成"""
        # 添加复杂视觉上下文
        detected_objects = [
            {"name": "cup", "confidence": 0.9, "bbox": [50, 50, 100, 100]},
            {"name": "laptop", "confidence": 0.85, "bbox": [200, 150, 500, 400]}
        ]

        gesture_info = {
            "gesture_type": "point_up",
            "confidence": 0.8,
            "action": "select"
        }

        self.context_manager.update_context(
            detected_objects=detected_objects,
            gesture_info=gesture_info,
            frame_id=1
        )

        # 创建需要上下文的手势
        gesture_result = MockGestureResult(
            gesture_code="fist",
            confidence=0.85,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        # 调用手势处理
        self.agent._on_gesture_detected(gesture_result)

        # 验证视觉上下文被包含在慢通道事件中
        self.agent.send_event.assert_called_once()
        event_data = self.agent.send_event.call_args[0][1]

        # 验证视觉上下文信息
        self.assertIn("visual_context", event_data)
        self.assertIn("available_objects", event_data)
        self.assertIn("scene_description", event_data)

        available_objects = event_data["available_objects"]
        self.assertGreater(len(available_objects), 0)
        object_names = [obj.get("name") for obj in available_objects]
        self.assertIn("cup", object_names)
        self.assertIn("laptop", object_names)

    def test_route_statistics_tracking(self):
        """测试路由统计跟踪"""
        # 执行多种路由类型的手势
        gestures = [
            ("victory", 0.9),     # 快通道
            ("thumbs_up", 0.8),   # 快通道
            ("open_palm", 0.7),   # 慢通道（有上下文时）
            ("unknown", 0.9),     # 忽略
        ]

        # 添加上下文以支持慢通道路由
        self.context_manager.update_context(
            detected_objects=[{"name": "test", "confidence": 0.9, "bbox": [0, 0, 10, 10]}],
            frame_id=1
        )

        # 模拟execute_action以支持快通道
        with patch('main.execute_action') as mock_execute:
            mock_execute.return_value = (True, "Success")

            for gesture_code, confidence in gestures:
                gesture_result = MockGestureResult(
                    gesture_code=gesture_code,
                    confidence=confidence,
                    bbox=[100, 100, 200, 200],
                    handedness="right"
                )
                self.agent._on_gesture_detected(gesture_result)

        # 验证路由统计信息
        stats = self.agent.gesture_router.get_route_statistics()
        self.assertGreater(stats["total_routes"], 0)
        self.assertGreater(stats["fast_path_routes"], 0)
        self.assertGreater(stats["slow_path_routes"], 0)
        self.assertGreater(stats["ignored_routes"], 0)

    def test_string_representation(self):
        """测试路由器字符串表示"""
        # 添加一些路由决策以生成统计信息
        with patch('agent.main.execute_action') as mock_execute:
            mock_execute.return_value = (True, "Success")

            gesture_result = MockGestureResult(
                gesture_code="victory",
                confidence=0.9,
                bbox=[100, 100, 200, 200],
                handedness="right"
            )
            self.agent._on_gesture_detected(gesture_result)

        # 测试字符串表示
        str_repr = str(self.agent.gesture_router)
        self.assertIn("GestureRouter", str_repr)
        self.assertIn("total_routes", str_repr)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)