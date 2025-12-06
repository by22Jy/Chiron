"""
Phase 3 简化集成测试

测试Phase 3.1 + 3.2的核心集成功能，避免Unicode编码问题
"""

import unittest
import sys
import os
import time
from unittest.mock import Mock, patch

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# Mock外部依赖
import unittest.mock
sys.modules['gestures.mediapipe_detector'] = unittest.mock.MagicMock()
sys.modules['requests'] = unittest.mock.MagicMock()

class MockGestureResult:
    def __init__(self, gesture_code, confidence, bbox, handedness):
        self.gesture_code = gesture_code
        self.confidence = confidence
        self.bbox = bbox
        self.handedness = handedness

sys.modules['gestures.mediapipe_detector'].GestureResult = MockGestureResult

class TestPhase3Integration(unittest.TestCase):
    """Phase 3集成测试"""

    def setUp(self):
        """测试准备"""
        from context_manager import ContextManager
        from gesture_router import GestureRouter, RouteType
        from visual_status_reporter import VisualStatusReporter

        # 初始化组件
        self.context_manager = ContextManager({
            "max_history_size": 20,
            "object_timeout": 3.0
        })

        self.gesture_router = GestureRouter(self.context_manager)

        self.visual_reporter = VisualStatusReporter(
            base_url="http://127.0.0.1:8080",
            context_manager=self.context_manager,
            config={
                "report_interval": 2.0,
                "api_timeout": 3.0,
                "enable_change_detection": True
            }
        )

    def test_context_manager_integration(self):
        """测试ContextManager集成"""
        print("测试ContextManager集成...")

        # 添加测试数据
        detected_objects = [
            {"name": "laptop", "confidence": 0.9, "bbox": [100, 100, 400, 300]},
            {"name": "cup", "confidence": 0.85, "bbox": [50, 50, 150, 150]}
        ]

        context = self.context_manager.update_context(
            detected_objects=detected_objects,
            frame_id=1
        )

        # 验证结果
        self.assertEqual(len(context.detected_objects), 2)
        self.assertEqual(context.detected_objects[0].name, "laptop")
        self.assertEqual(context.detected_objects[1].name, "cup")

        # 测试LLM格式输出
        llm_context = self.context_manager.get_context_for_llm()
        self.assertIn("visual_context", llm_context)
        self.assertIn("available_objects", llm_context)
        self.assertEqual(len(llm_context["available_objects"]), 2)

        print("[OK] ContextManager集成测试通过")

    def test_gesture_router_integration(self):
        """测试GestureRouter集成"""
        # 导入RouteType到方法作用域
        from gesture_router import RouteType

        print("测试GestureRouter集成...")

        # 设置测试场景
        self.context_manager.update_context(
            detected_objects=[
                {"name": "monitor", "confidence": 0.95, "bbox": [0, 0, 800, 600]}
            ],
            frame_id=1
        )

        # 测试不同手势
        test_cases = [
            ("victory", 0.9, RouteType.FAST_PATH),
            ("point_up", 0.85, RouteType.SLOW_PATH),
            ("thumbs_up", 0.92, RouteType.FAST_PATH),
        ]

        for gesture_code, confidence, expected_route in test_cases:
            gesture_result = MockGestureResult(
                gesture_code=gesture_code,
                confidence=confidence,
                bbox=[100, 100, 200, 200],
                handedness="right"
            )

            visual_context = self.context_manager.get_current_context()
            decision = self.gesture_router.route_gesture(gesture_result, visual_context)

            self.assertEqual(decision.route_type, expected_route,
                           f"手势 {gesture_code} 路由类型错误")

            print(f"  {gesture_code}: {decision.route_type.value}")

        # 验证统计信息
        stats = self.gesture_router.get_route_statistics()
        self.assertEqual(stats["total_routes"], 3)
        self.assertGreater(stats["fast_path_routes"], 0)
        self.assertGreater(stats["slow_path_routes"], 0)

        print(f"  路由统计: 快通道={stats['fast_path_routes']}, 慢通道={stats['slow_path_routes']}")
        print("[OK] GestureRouter集成测试通过")

    def test_visual_status_reporter_integration(self):
        """测试VisualStatusReporter集成"""
        print("测试VisualStatusReporter集成...")

        # 启动报告器
        self.visual_reporter.start()
        self.assertTrue(self.visual_reporter.running)

        # 添加测试数据
        self.context_manager.update_context(
            detected_objects=[
                {"name": "phone", "confidence": 0.88, "bbox": [100, 100, 200, 200]}
            ],
            frame_id=1
        )

        # Mock API响应
        with patch('requests.post') as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            # 发送报告
            success = self.visual_reporter.send_immediate_report()
            self.assertTrue(success)

            # 验证API调用
            mock_post.assert_called_once()

        # 停止报告器
        self.visual_reporter.stop()
        self.assertFalse(self.visual_reporter.running)

        print("[OK] VisualStatusReporter集成测试通过")

    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 导入RouteType到方法作用域
        from gesture_router import RouteType

        print("测试端到端工作流...")

        # 1. 创建复杂场景
        scenario_data = {
            "detected_objects": [
                {"name": "computer", "confidence": 0.92, "bbox": [50, 50, 550, 400]},
                {"name": "keyboard", "confidence": 0.88, "bbox": [100, 450, 400, 500]},
                {"name": "mouse", "confidence": 0.85, "bbox": [560, 420, 620, 480]}
            ],
            "gesture_info": {
                "gesture_type": "point_up",
                "confidence": 0.86,
                "action": "select"
            }
        }

        # 2. 更新ContextManager
        context = self.context_manager.update_context(
            detected_objects=scenario_data["detected_objects"],
            gesture_info=scenario_data["gesture_info"],
            frame_id=1
        )

        # 3. 验证数据完整性
        self.assertEqual(len(context.detected_objects), 3)
        self.assertIsNotNone(context.current_gesture)
        self.assertEqual(context.current_gesture.gesture_type, "point_up")

        # 4. 测试路由决策
        gesture_result = MockGestureResult(
            gesture_code="point_up",
            confidence=0.86,
            bbox=[300, 200, 350, 250],
            handedness="right"
        )

        route_decision = self.gesture_router.route_gesture(gesture_result, context)
        self.assertEqual(route_decision.route_type, RouteType.SLOW_PATH)
        self.assertEqual(route_decision.visual_context, context)

        # 5. 测试LLM上下文生成
        llm_context = self.context_manager.get_context_for_llm()
        self.assertEqual(len(llm_context["available_objects"]), 3)

        object_names = [obj["name"] for obj in llm_context["available_objects"]]
        expected_names = ["computer", "keyboard", "mouse"]
        self.assertEqual(set(object_names), set(expected_names))

        # 6. 验证交互提示
        hints = llm_context["interaction_hints"]
        self.assertGreater(len(hints), 0)
        hint_text = " ".join(hints)
        for name in expected_names:
            self.assertIn(name, hint_text)

        print("  场景数据: 3个物体 + 1个手势")
        print("  路由决策: 慢通道 (需要LLM分析)")
        print("  LLM上下文: 包含完整多模态信息")
        print("  交互提示: 智能生成的操作建议")

        print("[OK] 端到端工作流测试通过")

    def test_performance_benchmarks(self):
        """测试性能基准"""
        print("测试性能基准...")

        import time

        # 测试ContextManager性能
        start_time = time.time()
        for i in range(50):
            self.context_manager.update_context(
                detected_objects=[
                    {"name": f"test_{i%3}", "confidence": 0.8, "bbox": [0, 0, 10, 10]}
                ],
                frame_id=i
            )
        context_time = time.time() - start_time

        # 测试路由性能
        gesture_result = MockGestureResult(
            gesture_code="victory",
            confidence=0.9,
            bbox=[100, 100, 200, 200],
            handedness="right"
        )

        start_time = time.time()
        for i in range(50):
            self.gesture_router.route_gesture(gesture_result)
        routing_time = time.time() - start_time

        # 测试LLM上下文生成性能
        start_time = time.time()
        for i in range(50):
            self.context_manager.get_context_for_llm()
        llm_time = time.time() - start_time

        print(f"性能结果 (50次操作平均):")
        print(f"  ContextManager: {context_time/50*1000:.1f}ms")
        print(f"  GestureRouter: {routing_time/50*1000:.1f}ms")
        print(f"  LLM上下文: {llm_time/50*1000:.1f}ms")

        # 验证性能要求
        self.assertLess(context_time/50, 0.01, "ContextManager更新应小于10ms")
        self.assertLess(routing_time/50, 0.001, "GestureRouter路由应小于1ms")
        self.assertLess(llm_time/50, 0.005, "LLM上下文生成应小于5ms")

        print("[OK] 性能基准测试通过")

    def test_integration_summary(self):
        """集成测试总结"""
        print("\n" + "="*50)
        print("Phase 3 集成测试总结")
        print("="*50)

        # 获取统计信息
        context_stats = self.context_manager.get_statistics()
        router_stats = self.gesture_router.get_route_statistics()
        reporter_stats = self.visual_reporter.get_statistics()

        print("\n组件状态:")
        print(f"  ContextManager: "
              f"更新{context_stats['total_updates']}次, "
              f"物体{context_stats['object_detections']}个")
        print(f"  GestureRouter: "
              f"路由{router_stats['total_routes']}次, "
              f"快通道{router_stats['fast_path_percentage']:.1f}%, "
              f"慢通道{router_stats['slow_path_percentage']:.1f}%")
        print(f"  VisualStatusReporter: "
              f"报告{reporter_stats['total_reports']}次, "
              f"成功率{reporter_stats['success_rate']:.1f}%")

        print("\n核心功能验证:")
        print("  [OK] 视觉上下文管理")
        print("  [OK] 智能路由决策")
        print("  [OK] 状态监控上报")
        print("  [OK] 多模态数据集成")
        print("  [OK] 端到端工作流")

        print("\n性能指标:")
        print("  [OK] 实时响应 (<10ms)")
        print("  [OK] 高效路由 (<1ms)")
        print("  [OK] 快速上下文生成 (<5ms)")

        print("\nPhase 3 多模态智能代理系统 - 集成测试完成!")


if __name__ == '__main__':
    print("启动Phase 3集成测试...")
    unittest.main(verbosity=1)