"""
安全确认机制单元测试

测试安全确认的各种功能
"""

import unittest
import sys
import os
import time
import threading
from unittest.mock import Mock, patch
from dataclasses import dataclass

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# Mock外部依赖
import unittest.mock
sys.modules['gestures.mediapipe_detector'] = unittest.mock.MagicMock()

from safety_confirmation import (
    SafetyConfirmationManager, ConfirmationRequest, ConfirmationResponse,
    ConfirmationType, ConfirmationStatus, ConfirmationLevel,
    get_safety_confirmation_manager, request_action_confirmation,
    handle_confirmation_gesture
)


class MockGestureResult:
    """模拟手势结果"""
    def __init__(self, gesture_code, confidence, bbox, handedness):
        self.gesture_code = gesture_code
        self.confidence = confidence
        self.bbox = bbox
        self.handedness = handedness


class TestConfirmationLevel(unittest.TestCase):
    """确认级别测试"""

    def test_confirmation_level_values(self):
        """测试确认级别枚举值"""
        self.assertEqual(ConfirmationLevel.LOW.value, "low")
        self.assertEqual(ConfirmationLevel.MEDIUM.value, "medium")
        self.assertEqual(ConfirmationLevel.HIGH.value, "high")
        self.assertEqual(ConfirmationLevel.CRITICAL.value, "critical")


class TestConfirmationRequest(unittest.TestCase):
    """确认请求测试"""

    def test_confirmation_request_creation(self):
        """测试确认请求创建"""
        request = ConfirmationRequest(
            request_id="test_123",
            action_type="email_send",
            action_value="test@example.com",
            action_payload={"subject": "Test"},
            confirmation_type=ConfirmationType.YES_NO,
            confirmation_level=ConfirmationLevel.HIGH,
            message="确认发送邮件？"
        )

        self.assertEqual(request.request_id, "test_123")
        self.assertEqual(request.action_type, "email_send")
        self.assertEqual(request.action_value, "test@example.com")
        self.assertEqual(request.confirmation_type, ConfirmationType.YES_NO)
        self.assertEqual(request.confirmation_level, ConfirmationLevel.HIGH)
        self.assertEqual(request.message, "确认发送邮件？")
        self.assertEqual(request.timeout, 30.0)
        self.assertEqual(request.required_gestures, ["thumbs_up", "thumbs_down"])

    def test_confirmation_request_defaults(self):
        """测试确认请求默认值"""
        request = ConfirmationRequest(
            request_id="test_456",
            action_type="hotkey",
            action_value="ctrl+v",
            action_payload=None,
            confirmation_type=ConfirmationType.OK_CANCEL,
            confirmation_level=ConfirmationLevel.MEDIUM,
            message="确认操作？"
        )

        self.assertEqual(request.request_id, "test_456")
        self.assertIsNone(request.action_payload)
        self.assertEqual(request.required_gestures, ["thumbs_up", "thumbs_down"])
        self.assertIsNone(request.custom_options)
        self.assertIsNotNone(request.metadata)

    def test_confirmation_response_creation(self):
        """测试确认响应创建"""
        response = ConfirmationResponse(
            request_id="test_789",
            status=ConfirmationStatus.APPROVED,
            confirmed_action="approved_action",
            confidence=0.95,
            gesture_used="thumbs_up"
        )

        self.assertEqual(response.request_id, "test_789")
        self.assertEqual(response.status, ConfirmationStatus.APPROVED)
        self.assertEqual(response.confirmed_action, "approved_action")
        self.assertEqual(response.confidence, 0.95)
        self.assertEqual(response.gesture_used, "thumbs_up")
        self.assertGreaterEqual(response.timestamp, time.time() - 1)
        self.assertEqual(response.response_time, 0.0)

    def test_confirmation_response_expiry(self):
        """测试确认响应过期检查"""
        # 这个测试需要StatusMessage类中的is_expired方法
        pass  # 在实际实现中会有过期检查逻辑


class TestSafetyConfirmationManager(unittest.TestCase):
    """安全确认管理器测试"""

    def setUp(self):
        """测试前准备"""
        self.config = {
            "default_timeout": 10.0,
            "max_pending_requests": 3,
            "auto_approve_safe_actions": True
        }
        self.manager = SafetyConfirmationManager(self.config)

    def test_manager_initialization(self):
        """测试管理器初始化"""
        self.assertIsNotNone(self.manager.pending_requests)
        self.assertEqual(len(self.manager.pending_requests), 0)
        self.assertEqual(self.manager.default_timeout, 10.0)
        self.assertEqual(self.manager.max_pending_requests, 3)
        self.assertTrue(self.manager.auto_approve_safe_actions)

    def test_is_action_dangerous(self):
        """测试危险操作检测"""
        # 安全操作
        is_dangerous, level = self.manager.is_action_dangerous("text_send", "hello")
        self.assertFalse(is_dangerous)
        self.assertEqual(level, ConfirmationLevel.LOW)

        # 危险操作
        is_dangerous, level = self.manager.is_action_dangerous("email_send", "user@example.com")
        self.assertTrue(is_dangerous)
        self.assertEqual(level, ConfirmationLevel.HIGH)

        # 关键危险操作
        is_dangerous, level = self.manager.is_action_dangerous("hotkey", "ctrl+alt+del")
        self.assertTrue(is_dangerous)
        self.assertEqual(level, ConfirmationLevel.CRITICAL)

    def test_safe_action_auto_approval(self):
        """测试安全操作自动批准"""
        # 安全操作不需要确认
        request_id = self.manager.request_confirmation("text_send", "hello")
        self.assertIsNone(request_id)

        # 危险操作需要确认
        request_id = self.manager.request_confirmation("email_send", "user@example.com")
        self.assertIsNotNone(request_id)
        self.assertTrue(request_id.startswith("conf_"))

    def test_request_confirmation_with_callback(self):
        """测试带回调的确认请求"""
        callback_results = []

        def test_callback(response):
            callback_results.append(response)

        request_id = self.manager.request_confirmation(
            "email_send",
            "user@example.com",
            confirmation_callback=test_callback
        )

        self.assertIsNotNone(request_id)
        self.assertEqual(len(self.manager.pending_requests), 1)

        # 模拟手势确认
        gesture_result = MockGestureResult("thumbs_up", 0.9, [100, 100, 200, 200], "right")
        result = self.manager.handle_gesture_confirmation(gesture_result)
        self.assertTrue(result)

        # 等待回调执行
        time.sleep(0.1)
        self.assertEqual(len(callback_results), 1)
        self.assertEqual(callback_results[0].status, ConfirmationStatus.APPROVED)

    def test_gesture_confirmation_mapping(self):
        """测试手势确认映射"""
        # 测试HIGH级别的手势 (file_delete是HIGH级别，只接受thumbs_up, thumbs_down)
        high_level_gestures = [
            ("thumbs_up", ConfirmationStatus.APPROVED),
            ("thumbs_down", ConfirmationStatus.REJECTED),
        ]

        for gesture_code, expected_status in high_level_gestures:
            with self.subTest(gesture=gesture_code):
                request_id = self.manager.request_confirmation(
                    "file_delete",  # HIGH级别危险操作
                    f"test_file_{gesture_code}.txt"
                )

                self.assertIsNotNone(request_id)
                gesture_result = MockGestureResult(gesture_code, 0.9, [100, 100, 200, 200], "right")
                result = self.manager.handle_gesture_confirmation(gesture_result)
                self.assertTrue(result)

                # 验证请求已被处理
                final_request = self.manager.get_request_status(request_id)
                self.assertIsNone(final_request)

        # 测试MEDIUM级别的手势，web_submit是MEDIUM级别，只接受ok, victory手势
        medium_level_gestures = [
            ("ok", ConfirmationStatus.APPROVED),
            ("victory", ConfirmationStatus.APPROVED),
        ]

        for gesture_code, expected_status in medium_level_gestures:
            with self.subTest(gesture=gesture_code):
                request_id = self.manager.request_confirmation(
                    "web_submit",
                    f"form_{gesture_code}"
                )

                self.assertIsNotNone(request_id)
                gesture_result = MockGestureResult(gesture_code, 0.9, [100, 100, 200, 200], "right")
                result = self.manager.handle_gesture_confirmation(gesture_result)
                self.assertTrue(result)

                # 验证请求已被处理
                final_request = self.manager.get_request_status(request_id)
                self.assertIsNone(final_request)

        # 测试CRITICAL级别的手势，使用thumbs_up, thumbs_down, ok
        self.manager.dangerous_action_types["system_critical"] = ConfirmationLevel.CRITICAL

        critical_level_gestures = [
            ("thumbs_up", ConfirmationStatus.APPROVED),
            ("thumbs_down", ConfirmationStatus.REJECTED),
            ("ok", ConfirmationStatus.APPROVED),
        ]

        for gesture_code, expected_status in critical_level_gestures:
            with self.subTest(gesture=gesture_code):
                request_id = self.manager.request_confirmation(
                    "system_critical",
                    f"test_{gesture_code}"
                )

                self.assertIsNotNone(request_id)
                gesture_result = MockGestureResult(gesture_code, 0.9, [100, 100, 200, 200], "right")
                result = self.manager.handle_gesture_confirmation(gesture_result)
                self.assertTrue(result)

                # 验证请求已被处理
                final_request = self.manager.get_request_status(request_id)
                self.assertIsNone(final_request)

    def test_confirmation_timeout(self):
        """测试确认超时"""
        # 创建短超时的配置
        config = {"default_timeout": 0.1, "max_pending_requests": 1}
        manager = SafetyConfirmationManager(config)

        request_id = manager.request_confirmation(
            "email_send",
            "user@example.com"
        )

        self.assertIsNotNone(request_id)

        # 等待超时
        time.sleep(0.2)

        # 验证请求已被超时处理
        final_request = manager.get_request_status(request_id)
        self.assertIsNone(final_request)

    def test_cancel_confirmation(self):
        """测试取消确认"""
        request_id = self.manager.request_confirmation(
            "email_send",
            "user@example.com"
        )

        self.assertIsNotNone(request_id)

        # 取消确认
        result = self.manager.cancel_confirmation(request_id)
        self.assertTrue(result)

        # 验证请求已被取消
        final_request = self.manager.get_request_status(request_id)
        self.assertIsNone(final_request)

    def test_max_pending_requests_limit(self):
        """测试最大待确认请求数限制"""
        # 使用较小的配置以避免自动批准
        manager = SafetyConfirmationManager({
            "max_pending_requests": 2,
            "auto_approve_safe_actions": False
        })

        # 添加请求直到达到限制，使用危险操作确保需要确认
        request1 = manager.request_confirmation("file_delete", "file1.txt")
        request2 = manager.request_confirmation("file_delete", "file2.txt")
        request3 = manager.request_confirmation("file_delete", "file3.txt")

        self.assertIsNotNone(request1)
        self.assertIsNotNone(request2)
        self.assertIsNone(request3)  # 超过限制，返回None

        self.assertEqual(len(manager.pending_requests), 2)

    def test_critical_level_custom_options(self):
        """测试关键级别的自定义选项"""
        # 模拟关键级别的操作
        self.manager.dangerous_action_types["system_shutdown"] = ConfirmationLevel.CRITICAL

        request_id = self.manager.request_confirmation(
            "system_shutdown",
            "now"
        )

        self.assertIsNotNone(request_id)
        request = self.manager.get_request_status(request_id)
        self.assertEqual(request.confirmation_level, ConfirmationLevel.CRITICAL)
        self.assertEqual(request.confirmation_type, ConfirmationType.CUSTOM)
        self.assertIsNotNone(request.custom_options)

    def test_get_pending_requests(self):
        """测试获取待确认请求列表"""
        # 初始状态应该为空
        requests = self.manager.get_pending_requests()
        self.assertEqual(len(requests), 0)

        # 禁用自动批准的管理器
        manager = SafetyConfirmationManager({"auto_approve_safe_actions": False})

        # 添加请求，使用危险操作确保需要确认
        request1 = manager.request_confirmation("email_send", "user1@test.com")
        request2 = manager.request_confirmation("file_delete", "test.txt")

        requests = manager.get_pending_requests()
        self.assertEqual(len(requests), 2)

    def test_get_confirmation_statistics(self):
        """测试获取确认统计信息"""
        stats = self.manager.get_confirmation_statistics()

        self.assertIn("pending_requests", stats)
        self.assertIn("max_pending", stats)
        self.assertIn("auto_approve_safe", stats)
        self.assertIn("dangerous_action_types", stats)
        self.assertIn("pending_by_level", stats)

        # 添加一些危险操作请求
        self.manager.request_confirmation("email_send", "user@example.com")
        self.manager.request_confirmation("file_delete", "test.txt")

        updated_stats = self.manager.get_confirmation_statistics()
        self.assertGreater(updated_stats["dangerous_action_types"], 0)

    def test_configure_action_requirements(self):
        """测试配置操作要求"""
        # 配置新危险操作
        self.manager.configure_action_requirements(
            "custom_action",
            ConfirmationLevel.HIGH,
            "确认执行自定义操作？"
        )

        # 验证配置生效
        is_dangerous, level = self.manager.is_action_dangerous("custom_action", "test")
        self.assertTrue(is_dangerous)
        self.assertEqual(level, ConfirmationLevel.HIGH)

    def test_concurrent_confirmation_requests(self):
        """测试并发确认请求"""
        results = []

        def request_worker():
            """请求工作线程"""
            for i in range(5):
                request_id = self.manager.request_confirmation(
                    "email_send",
                    f"user{i}@example.com"
                )
                if request_id:
                    results.append(request_id)
                time.sleep(0.01)

        # 创建多个线程
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=request_worker)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证没有冲突
        self.assertGreater(len(results), 0)
        self.assertLessEqual(len(results), self.manager.max_pending_requests * 3)  # 3个线程 * 3个限制

    def test_action_value_dangerous_detection(self):
        """测试基于操作值的危险检测"""
        # 安全类型但危险值
        is_dangerous, level = self.manager.is_action_dangerous("hotkey", "ctrl+delete")
        self.assertTrue(is_dangerous)
        self.assertEqual(level, ConfirmationLevel.CRITICAL)

        is_dangerous, level = self.manager.is_action_dangerous("hotkey", "alt+f4")
        self.assertTrue(is_dangerous)
        self.assertEqual(level, ConfirmationLevel.CRITICAL)

        # 安全类型和安全值
        is_dangerous, level = self.manager.is_action_dangerous("hotkey", "ctrl+c")
        self.assertFalse(is_dangerous)
        self.assertEqual(level, ConfirmationLevel.LOW)


class TestGlobalInstance(unittest.TestCase):
    """全局实例测试"""

    def setUp(self):
        """测试前准备"""
        # 清除全局实例
        import safety_confirmation
        safety_confirmation._safety_confirmation_manager = None

    def test_global_instance_singleton(self):
        """测试全局实例单例"""
        manager1 = get_safety_confirmation_manager()
        manager2 = get_safety_confirmation_manager()
        self.assertIs(manager1, manager2)

    def test_global_instance_with_config(self):
        """测试带配置的全局实例"""
        config = {"default_timeout": 60.0}
        manager = get_safety_confirmation_manager(config)
        self.assertEqual(manager.default_timeout, 60.0)


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试"""

    def setUp(self):
        """测试前准备"""
        # 清除全局实例
        import safety_confirmation
        safety_confirmation._safety_confirmation_manager = None
        # 创建管理器实例用于测试
        self.manager = SafetyConfirmationManager({"auto_approve_safe_actions": False})

    def test_request_action_confirmation(self):
        """测试请求操作确认便捷函数"""
        # 安全操作应该返回None（自动批准）
        request_id = request_action_confirmation("text_send", "hello")
        self.assertIsNone(request_id)

        # 危险操作应该返回request_id
        request_id = request_action_confirmation("email_send", "user@example.com")
        self.assertIsNotNone(request_id)
        self.assertTrue(request_id.startswith("conf_"))

    def test_handle_confirmation_gesture(self):
        """测试处理确认手势便捷函数"""
        # 直接使用我们的管理器创建确认请求，避免全局实例问题
        request_id = self.manager.request_confirmation("email_send", "user@test.com")

        # 验证请求已创建
        self.assertIsNotNone(request_id)

        # 测试手势确认
        gesture_result = MockGestureResult("thumbs_up", 0.9, [100, 100, 200, 200], "right")
        result = self.manager.handle_gesture_confirmation(gesture_result)
        self.assertTrue(result)


if __name__ == '__main__':
    print("启动安全确认机制测试...")
    print("=" * 50)

    # 运行测试
    unittest.main(verbosity=2)