"""
视觉反馈系统单元测试

测试视觉反馈的各种功能
"""

import unittest
import sys
import os
import time
import numpy as np
from unittest.mock import Mock, patch

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from visual_feedback import (
    VisualFeedback, VisualFeedbackConfig, AgentState, FeedbackLevel,
    StatusMessage, get_visual_feedback, set_agent_state,
    add_status_message, set_progress, draw_feedback_on_frame
)


class TestVisualFeedbackConfig(unittest.TestCase):
    """视觉反馈配置测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = VisualFeedbackConfig()
        self.assertTrue(config.enable_status_display)
        self.assertTrue(config.enable_message_overlay)
        self.assertEqual(config.font_scale, 0.8)
        self.assertEqual(config.thickness, 2)
        self.assertIsNotNone(config.colors)

    def test_custom_config(self):
        """测试自定义配置"""
        custom_colors = {"test": (1, 2, 3)}
        config = VisualFeedbackConfig(
            enable_status_display=False,
            font_scale=1.0,
            colors=custom_colors
        )
        self.assertFalse(config.enable_status_display)
        self.assertEqual(config.font_scale, 1.0)
        self.assertEqual(config.colors, custom_colors)


class TestStatusMessage(unittest.TestCase):
    """状态消息测试"""

    def test_message_creation(self):
        """测试消息创建"""
        message = StatusMessage("测试消息", FeedbackLevel.SUCCESS)
        self.assertEqual(message.text, "测试消息")
        self.assertEqual(message.level, FeedbackLevel.SUCCESS)
        self.assertAlmostEqual(message.timestamp, time.time(), delta=0.1)

    def test_custom_duration(self):
        """测试自定义持续时间"""
        message = StatusMessage("测试", duration=5.0)
        self.assertEqual(message.duration, 5.0)

    def test_is_expired(self):
        """测试过期检查"""
        # 创建一个已经过期的消息
        message = StatusMessage("测试", duration=0.001)
        time.sleep(0.01)  # 等待超过持续时间
        self.assertTrue(message.is_expired())

    def test_not_expired(self):
        """测试未过期检查"""
        message = StatusMessage("测试", duration=10.0)
        self.assertFalse(message.is_expired())


class TestVisualFeedback(unittest.TestCase):
    """视觉反馈系统测试"""

    def setUp(self):
        """测试前准备"""
        self.config = VisualFeedbackConfig()
        self.feedback = VisualFeedback(self.config)

    def test_initial_state(self):
        """测试初始状态"""
        self.assertEqual(self.feedback.current_state, AgentState.IDLE)
        self.assertEqual(len(self.feedback.status_messages), 0)
        self.assertEqual(self.feedback.progress_value, 0.0)

    def test_set_state(self):
        """测试设置状态"""
        self.feedback.set_state(AgentState.PROCESSING)
        self.assertEqual(self.feedback.current_state, AgentState.PROCESSING)

        # 测试带消息的状态设置
        self.feedback.set_state(AgentState.SUCCESS, "任务完成")
        self.assertEqual(self.feedback.current_state, AgentState.SUCCESS)
        self.assertEqual(len(self.feedback.status_messages), 1)
        self.assertEqual(self.feedback.status_messages[0].text, "任务完成")
        self.assertEqual(self.feedback.status_messages[0].level, FeedbackLevel.SUCCESS)

    def test_add_message(self):
        """测试添加消息"""
        self.feedback.add_message("信息消息", FeedbackLevel.INFO)
        self.feedback.add_message("成功消息", FeedbackLevel.SUCCESS, 5.0)

        self.assertEqual(len(self.feedback.status_messages), 2)
        self.assertEqual(self.feedback.status_messages[0].level, FeedbackLevel.INFO)
        self.assertEqual(self.feedback.status_messages[1].level, FeedbackLevel.SUCCESS)
        self.assertEqual(self.feedback.status_messages[1].duration, 5.0)

    def test_set_progress(self):
        """测试设置进度"""
        self.feedback.set_progress(0.5, "处理中")
        self.assertEqual(self.feedback.progress_value, 0.5)
        self.assertEqual(self.feedback.progress_text, "处理中")

        # 测试边界值
        self.feedback.set_progress(1.5)  # 应该被限制为1.0
        self.assertEqual(self.feedback.progress_value, 1.0)

        self.feedback.set_progress(-0.5)  # 应该被限制为0.0
        self.assertEqual(self.feedback.progress_value, 0.0)

    def test_state_texts_and_icons(self):
        """测试状态文本和图标"""
        # 测试所有状态都有对应的文本
        for state in AgentState:
            self.assertIn(state, self.feedback.state_texts)
            self.assertIn(state, self.feedback.state_icons)

    def test_cleanup_expired_messages(self):
        """测试清理过期消息"""
        # 添加消息
        self.feedback.add_message("消息1", duration=0.001)
        self.feedback.add_message("消息2", duration=10.0)

        time.sleep(0.01)  # 让第一个消息过期

        # 手动触发清理
        self.feedback._cleanup_expired_messages()

        # 应该只剩一个消息
        self.assertEqual(len(self.feedback.status_messages), 1)
        self.assertEqual(self.feedback.status_messages[0].text, "消息2")

    def test_draw_feedback(self):
        """测试绘制反馈"""
        # 创建测试帧
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        original_shape = frame.shape

        # 设置一些状态
        self.feedback.set_state(AgentState.PROCESSING, "处理中...")
        self.feedback.set_progress(0.7, "进度")

        # 绘制反馈
        result_frame = self.feedback.draw_feedback(frame)

        # 检查形状不变
        self.assertEqual(result_frame.shape, original_shape)
        # 检查确实有变化（不是全黑）
        self.assertTrue(np.any(result_frame != 0))

    def test_draw_feedback_with_disabled_features(self):
        """测试禁用功能时的绘制"""
        # 禁用所有功能
        config = VisualFeedbackConfig(
            enable_status_display=False,
            enable_message_overlay=False,
            enable_progress_bar=False
        )
        feedback = VisualFeedback(config)

        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # 设置状态和消息
        feedback.set_state(AgentState.PROCESSING, "处理中")
        feedback.add_message("消息")
        feedback.set_progress(0.5)

        # 绘制应该不会报错
        result_frame = feedback.draw_feedback(frame)
        self.assertEqual(result_frame.shape, frame.shape)

    def test_get_current_status(self):
        """测试获取当前状态"""
        self.feedback.set_state(AgentState.THINKING, "思考中...")
        self.feedback.set_progress(0.3, "处理")
        self.feedback.add_message("测试消息")

        status = self.feedback.get_current_status()

        self.assertEqual(status["state"], AgentState.THINKING.value)
        self.assertIn("正在思考", status["state_text"])
        self.assertEqual(status["progress"], 0.3)
        self.assertEqual(status["progress_text"], "处理")
        self.assertGreaterEqual(status["active_messages"], 1)

    def test_clear_messages(self):
        """测试清除消息"""
        self.feedback.add_message("消息1")
        self.feedback.add_message("消息2")
        self.assertEqual(len(self.feedback.status_messages), 2)

        self.feedback.clear_messages()
        self.assertEqual(len(self.feedback.status_messages), 0)

    def test_reset(self):
        """测试重置"""
        self.feedback.set_state(AgentState.ERROR, "错误")
        self.feedback.add_message("消息")
        self.feedback.set_progress(0.8, "进度")

        self.feedback.reset()

        self.assertEqual(self.feedback.current_state, AgentState.IDLE)
        self.assertEqual(len(self.feedback.status_messages), 0)
        self.assertEqual(self.feedback.progress_value, 0.0)
        self.assertEqual(self.feedback.progress_text, "")

    def test_gesture_indicators(self):
        """测试手势指示器"""
        # 创建模拟手势
        mock_gesture = Mock()
        mock_gesture.gesture_code = "victory"
        mock_gesture.confidence = 0.85

        gestures = [mock_gesture]

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result_frame = self.feedback.draw_feedback(frame, gestures)

        # 应该没有错误
        self.assertEqual(result_frame.shape, frame.shape)

    def test_feedback_level_from_state(self):
        """测试从状态获取反馈级别"""
        self.assertEqual(
            self.feedback._get_feedback_level_from_state(AgentState.SUCCESS),
            FeedbackLevel.SUCCESS
        )
        self.assertEqual(
            self.feedback._get_feedback_level_from_state(AgentState.ERROR),
            FeedbackLevel.ERROR
        )
        self.assertEqual(
            self.feedback._get_feedback_level_from_state(AgentState.PROCESSING),
            FeedbackLevel.INFO
        )


class TestGlobalInstance(unittest.TestCase):
    """全局实例测试"""

    def setUp(self):
        """测试前准备"""
        # 清除全局实例
        import visual_feedback
        visual_feedback._visual_feedback_instance = None

    def test_global_instance_singleton(self):
        """测试全局实例单例"""
        feedback1 = get_visual_feedback()
        feedback2 = get_visual_feedback()
        self.assertIs(feedback1, feedback2)

    def test_global_instance_with_config(self):
        """测试带配置的全局实例"""
        config = VisualFeedbackConfig(font_scale=1.5)
        feedback = get_visual_feedback(config)
        self.assertEqual(feedback.config.font_scale, 1.5)

    def test_convenience_functions(self):
        """测试便捷函数"""
        # 这些函数应该不会抛出异常
        set_agent_state(AgentState.PROCESSING, "测试")
        add_status_message("测试消息", FeedbackLevel.INFO)
        set_progress(0.5, "进度")

        # 验证状态已设置
        feedback = get_visual_feedback()
        self.assertEqual(feedback.current_state, AgentState.PROCESSING)
        self.assertEqual(feedback.progress_value, 0.5)


class TestVisualFeedbackIntegration(unittest.TestCase):
    """视觉反馈集成测试"""

    def test_workflow_simulation(self):
        """测试工作流模拟"""
        feedback = VisualFeedback()
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # 模拟完整工作流
        workflow_steps = [
            (AgentState.LISTENING, "开始听取指令"),
            (AgentState.THINKING, "分析指令意图"),
            (AgentState.PROCESSING, "准备执行"),
            (AgentState.EXECUTING, "正在执行任务"),
            (AgentState.SUCCESS, "任务完成")
        ]

        for i, (state, message) in enumerate(workflow_steps):
            feedback.set_state(state, message)
            feedback.set_progress((i + 1) / len(workflow_steps), f"步骤{i+1}")

            # 绘制反馈
            result_frame = feedback.draw_feedback(frame)
            self.assertEqual(result_frame.shape, frame.shape)

            # 验证状态
            self.assertEqual(feedback.current_state, state)
            self.assertGreater(len(feedback.status_messages), 0)

        # 验证最终状态
        self.assertEqual(feedback.current_state, AgentState.SUCCESS)
        self.assertEqual(feedback.progress_value, 1.0)

    def test_error_handling(self):
        """测试错误处理"""
        feedback = VisualFeedback()

        # 模拟错误情况
        feedback.set_state(AgentState.ERROR, "执行失败")
        feedback.add_message("错误详情：权限不足", FeedbackLevel.ERROR)

        status = feedback.get_current_status()
        self.assertEqual(status["state"], AgentState.ERROR.value)
        self.assertGreater(status["active_messages"], 0)

    def test_thread_safety(self):
        """测试线程安全性"""
        feedback = VisualFeedback()
        results = []

        def worker_function():
            for i in range(10):
                feedback.set_state(AgentState.PROCESSING, f"消息{i}")
                feedback.add_message(f"测试消息{i}")
                feedback.set_progress(i / 10)
                results.append(i)

        # 创建多个线程
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=worker_function)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证没有崩溃
        self.assertEqual(len(results), 30)


if __name__ == '__main__':
    import threading  # 需要导入threading用于测试

    # 运行测试
    unittest.main(verbosity=2)