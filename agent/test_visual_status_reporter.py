"""
VisualStatusReporter单元测试

测试视觉状态上报器的功能
"""

import unittest
import sys
import os
import time
import requests
from unittest.mock import Mock, patch, MagicMock
from threading import Event

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from context_manager import ContextManager
from visual_status_reporter import VisualStatusReporter, VisualStatusReport, SceneChange

class TestVisualStatusReporter(unittest.TestCase):
    """VisualStatusReporter测试类"""

    def setUp(self):
        """测试前准备"""
        self.base_url = "http://127.0.0.1:8080"
        self.context_manager = ContextManager({
            "max_history_size": 10,
            "object_timeout": 2.0
        })
        self.config = {
            "report_interval": 0.1,  # 0.1秒用于快速测试
            "api_timeout": 5.0,
            "enable_change_detection": True,
            "max_scene_changes": 5
        }
        self.reporter = VisualStatusReporter(self.base_url, self.context_manager, self.config)

    def tearDown(self):
        """测试后清理"""
        if self.reporter.running:
            self.reporter.stop()

    def test_visual_status_reporter_initialization(self):
        """测试VisualStatusReporter初始化"""
        self.assertIsNotNone(self.reporter)
        self.assertEqual(self.reporter.base_url, self.base_url)
        self.assertEqual(self.reporter.context_manager, self.context_manager)
        self.assertFalse(self.reporter.running)
        self.assertEqual(len(self.reporter.scene_changes), 0)

    def test_report_generation(self):
        """测试报告生成"""
        # 添加一些上下文数据
        detected_objects = [
            {"name": "cup", "confidence": 0.85, "bbox": [100, 100, 200, 200]},
            {"name": "laptop", "confidence": 0.92, "bbox": [300, 300, 500, 400]}
        ]

        gesture_data = {
            "gesture_type": "POINT_UP",
            "confidence": 0.78,
            "action": "select"
        }

        self.context_manager.update_context(
            detected_objects=detected_objects,
            gesture_info=gesture_data,
            frame_id=1
        )

        # 生成报告
        report = self.reporter._generate_current_report()

        # 验证报告内容
        self.assertIsNotNone(report)
        self.assertIsInstance(report, VisualStatusReport)
        self.assertEqual(len(report.detected_objects), 2)
        self.assertEqual(report.detected_objects[0]["name"], "cup")
        self.assertEqual(report.detected_objects[1]["name"], "laptop")
        self.assertIsNotNone(report.current_gesture)
        self.assertEqual(report.current_gesture["gesture_type"], "POINT_UP")
        self.assertEqual(report.object_count, 2)
        self.assertEqual(report.gesture_count, 1)

    def test_scene_change_detection(self):
        """测试场景变化检测"""
        # 第一次更新
        detected_objects_1 = [
            {"name": "book", "confidence": 0.9, "bbox": [200, 200, 300, 300]}
        ]
        context_1 = self.context_manager.update_context(detected_objects=detected_objects_1, frame_id=1)

        # 更新reporter的last_objects状态
        self.reporter._update_last_state(VisualStatusReport(
            timestamp=context_1.timestamp,
            detected_objects=[{"name": obj.name, "confidence": obj.confidence, "bbox": obj.bbox} for obj in context_1.detected_objects],
            current_gesture=None,
            scene_description=context_1.scene_description,
            object_count=len(context_1.detected_objects),
            gesture_count=0,
            scene_changes=[],
            context_summary="Test",
            frame_id=context_1.frame_id
        ))

        # 第二次更新 - 添加新物体
        detected_objects_2 = [
            {"name": "book", "confidence": 0.9, "bbox": [200, 200, 300, 300]},
            {"name": "phone", "confidence": 0.85, "bbox": [50, 50, 150, 150]}
        ]
        context_2 = self.context_manager.update_context(detected_objects=detected_objects_2, frame_id=2)

        # 检测场景变化
        self.reporter._detect_scene_changes(context_2)

        # 验证检测到物体添加
        self.assertTrue(len(self.reporter.scene_changes) > 0)
        added_changes = [change for change in self.reporter.scene_changes if change.change_type == "object_added"]
        self.assertTrue(len(added_changes) > 0)
        self.assertTrue("phone" in added_changes[0].description)

    def test_context_summary_generation(self):
        """测试上下文摘要生成"""
        # 添加多种类型的信息
        detected_objects = [
            {"name": "keyboard", "confidence": 0.93, "bbox": [100, 300, 400, 350]},
            {"name": "mouse", "confidence": 0.81, "bbox": [450, 320, 500, 370]}
        ]

        gesture_data = {
            "gesture_type": "OK_SIGN",
            "confidence": 0.87,
            "action": "confirm"
        }

        emotion_data = {
            "emotion": "happy",
            "confidence": 0.76,
            "face_bbox": [150, 100, 250, 200]
        }

        context = self.context_manager.update_context(
            detected_objects=detected_objects,
            gesture_info=gesture_data,
            emotion_info=emotion_data,
            frame_id=1
        )

        # 生成摘要
        summary = self.reporter._generate_context_summary(context)

        # 验证摘要内容
        self.assertIn("keyboard", summary)
        self.assertIn("OK_SIGN", summary)
        self.assertIn("happy", summary)

    @patch('requests.post')
    def test_send_report_to_backend_success(self, mock_post):
        """测试成功发送报告到后端"""
        # 模拟成功的API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        # 创建测试报告
        report = VisualStatusReport(
            timestamp=time.time(),
            detected_objects=[{"name": "test", "confidence": 0.9, "bbox": [0, 0, 10, 10]}],
            current_gesture=None,
            scene_description="Test scene",
            object_count=1,
            gesture_count=0,
            scene_changes=[],
            context_summary="Test summary",
            frame_id=1
        )

        # 发送报告
        success = self.reporter._send_report_to_backend(report)

        # 验证API调用
        self.assertTrue(success)
        mock_post.assert_called_once()

        # 验证请求数据
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], f"{self.base_url}/api/event")
        payload = call_args[1]["json"]
        self.assertEqual(payload["eventType"], "visual_status_report")

    @patch('requests.post')
    def test_send_report_to_backend_failure(self, mock_post):
        """测试发送报告到后端失败"""
        # 模拟失败的API响应
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response

        # 创建测试报告
        report = VisualStatusReport(
            timestamp=time.time(),
            detected_objects=[],
            current_gesture=None,
            scene_description="Test scene",
            object_count=0,
            gesture_count=0,
            scene_changes=[],
            context_summary="Test summary",
            frame_id=1
        )

        # 发送报告
        success = self.reporter._send_report_to_backend(report)

        # 验证失败
        self.assertFalse(success)

    @patch('requests.post')
    def test_send_report_to_backend_timeout(self, mock_post):
        """测试发送报告到后端超时"""
        # 模拟超时异常
        mock_post.side_effect = requests.exceptions.Timeout()

        # 创建测试报告
        report = VisualStatusReport(
            timestamp=time.time(),
            detected_objects=[],
            current_gesture=None,
            scene_description="Test scene",
            object_count=0,
            gesture_count=0,
            scene_changes=[],
            context_summary="Test summary",
            frame_id=1
        )

        # 发送报告
        success = self.reporter._send_report_to_backend(report)

        # 验证超时处理
        self.assertFalse(success)

    def test_statistics_tracking(self):
        """测试统计信息跟踪"""
        # 初始统计信息
        stats = self.reporter.get_statistics()
        self.assertEqual(stats["total_reports"], 0)
        self.assertEqual(stats["successful_reports"], 0)
        self.assertEqual(stats["failed_reports"], 0)
        self.assertEqual(stats["scene_changes_detected"], 0)

        # 更新统计信息
        self.reporter._update_stats(True)  # 成功的报告
        self.reporter._update_stats(False)  # 失败的报告
        self.reporter.stats["scene_changes_detected"] = 5

        # 验证统计信息更新
        stats = self.reporter.get_statistics()
        self.assertEqual(stats["total_reports"], 2)
        self.assertEqual(stats["successful_reports"], 1)
        self.assertEqual(stats["failed_reports"], 1)
        self.assertEqual(stats["scene_changes_detected"], 5)
        self.assertEqual(stats["success_rate"], 50.0)

    def test_immediate_report(self):
        """测试立即发送报告"""
        # 添加上下文数据
        self.context_manager.update_context(
            detected_objects=[{"name": "test", "confidence": 0.9, "bbox": [0, 0, 10, 10]}],
            frame_id=1
        )

        with patch.object(self.reporter, '_generate_and_send_report') as mock_generate:
            mock_generate.return_value = True

            # 发送立即报告
            success = self.reporter.send_immediate_report()

            # 验证调用
            mock_generate.assert_called_once()

    def test_scene_changes_management(self):
        """测试场景变化管理"""
        # 添加一些场景变化
        for i in range(10):  # 超过max_scene_changes的限制
            change = SceneChange(
                change_type="object_added",
                description=f"Test change {i}",
                confidence=0.9,
                timestamp=time.time()
            )
            self.reporter.scene_changes.append(change)

        # 获取最近的场景变化
        recent_changes = self.reporter.get_recent_scene_changes(limit=5)

        # 验证限制
        self.assertEqual(len(recent_changes), 5)
        self.assertTrue(all("Test change" in change["description"] for change in recent_changes))

        # 清空场景变化
        self.reporter.clear_scene_changes()
        self.assertEqual(len(self.reporter.scene_changes), 0)

    def test_report_interval_update(self):
        """测试上报间隔更新"""
        original_interval = self.reporter.report_interval

        # 更新间隔
        self.reporter.set_report_interval(60.0)

        # 验证更新
        self.assertEqual(self.reporter.report_interval, 60.0)
        self.assertNotEqual(self.reporter.report_interval, original_interval)

    def test_string_representation(self):
        """测试字符串表示"""
        str_repr = str(self.reporter)
        self.assertIn("VisualStatusReporter", str_repr)
        self.assertIn("running=False", str_repr)

    def test_start_stop_lifecycle(self):
        """测试启动停止生命周期"""
        # 初始状态
        self.assertFalse(self.reporter.running)

        # 启动
        self.reporter.start()
        self.assertTrue(self.reporter.running)
        self.assertIsNotNone(self.reporter.report_thread)

        # 等待一小段时间确保线程启动
        time.sleep(0.05)

        # 停止
        self.reporter.stop()
        self.assertFalse(self.reporter.running)

    def test_last_state_update(self):
        """测试上次状态更新"""
        # 创建测试报告
        report = VisualStatusReport(
            timestamp=time.time(),
            detected_objects=[
                {"name": "cup", "confidence": 0.85, "bbox": [100, 100, 200, 200]},
                {"name": "laptop", "confidence": 0.92, "bbox": [300, 300, 500, 400]}
            ],
            current_gesture={"gesture_type": "POINT_UP", "confidence": 0.78, "action": "select"},
            scene_description="Test scene",
            object_count=2,
            gesture_count=1,
            scene_changes=[],
            context_summary="Test summary",
            frame_id=1
        )

        # 更新上次状态
        self.reporter._update_last_state(report)

        # 验证状态更新
        self.assertEqual(len(self.reporter.last_objects), 2)
        self.assertIn("cup", self.reporter.last_objects)
        self.assertIn("laptop", self.reporter.last_objects)
        self.assertEqual(self.reporter.last_gesture, "POINT_UP")

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)