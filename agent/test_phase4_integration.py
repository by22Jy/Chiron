"""
Phase 4 集成测试

测试TTS语音反馈和视觉反馈系统的集成
"""

import unittest
import sys
import os
import time
import numpy as np
from unittest.mock import Mock, patch

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# Mock外部依赖以避免protobuf冲突
import unittest.mock
sys.modules['gestures.mediapipe_detector'] = unittest.mock.MagicMock()
sys.modules['mediapipe'] = unittest.mock.MagicMock()

from tts_engine import TTSEngine, TTSConfig, VoiceFeedback
from visual_feedback import VisualFeedback, VisualFeedbackConfig, AgentState, FeedbackLevel


class TestPhase4Integration(unittest.TestCase):
    """Phase 4集成测试"""

    def setUp(self):
        """测试前准备"""
        self.tts_config = TTSConfig(enabled=True, engine_type="offline")
        self.visual_config = VisualFeedbackConfig(
            enable_status_display=True,
            enable_message_overlay=True,
            enable_progress_bar=True
        )
        self.tts_engine = TTSEngine(self.tts_config)
        self.visual_feedback = VisualFeedback(self.visual_config)

    def test_tts_visual_feedback_workflow(self):
        """测试TTS和视觉反馈的工作流"""
        # 创建测试帧
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # 模拟完整工作流
        workflow_steps = [
            (AgentState.LISTENING, "开始听取指令", VoiceFeedback.LISTENING),
            (AgentState.THINKING, "分析指令意图", VoiceFeedback.THINKING),
            (AgentState.PROCESSING, "准备执行", VoiceFeedback.PROCESSING),
            (AgentState.EXECUTING, "正在执行任务", VoiceFeedback.WORKFLOW_START),
            (AgentState.SUCCESS, "任务完成", VoiceFeedback.WORKFLOW_COMPLETE)
        ]

        for i, (state, message, voice_message) in enumerate(workflow_steps):
            # 设置视觉状态
            self.visual_feedback.set_state(state, message)
            self.visual_feedback.set_progress((i + 1) / len(workflow_steps), f"步骤{i+1}")

            # 添加状态消息
            self.visual_feedback.add_message(message, FeedbackLevel.INFO, duration=2.0)

            # 语音反馈
            voice_success = VoiceFeedback.speak_feedback(voice_message)

            # 绘制视觉反馈
            result_frame = self.visual_feedback.draw_feedback(frame)

            # 验证状态
            self.assertEqual(self.visual_feedback.current_state, state)
            self.assertEqual(self.visual_feedback.progress_value, (i + 1) / len(workflow_steps))
            self.assertGreater(len(self.visual_feedback.status_messages), 0)

            # 验证结果
            self.assertEqual(result_frame.shape, frame.shape)
            self.assertTrue(voice_success)

        print("[OK] TTS和视觉反馈工作流测试通过")

    def test_fast_path_execution_feedback(self):
        """测试快通道执行的反馈"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # 模拟快通道执行
        action_type = "hotkey"
        action_value = "ctrl+c"

        # 执行前反馈
        self.visual_feedback.set_state(AgentState.EXECUTING, f"执行{action_type}")
        self.visual_feedback.set_progress(0.5, "执行动作")
        self.visual_feedback.add_message(f"正在执行: {action_type}", FeedbackLevel.INFO)

        # 模拟语音反馈
        tts_success = self.tts_engine.speak_async("正在执行操作")
        self.assertTrue(tts_success)

        # 模拟执行成功
        success = True
        message = "操作执行成功"

        # 执行后反馈
        if success:
            self.visual_feedback.set_state(AgentState.SUCCESS, "操作完成")
            self.visual_feedback.add_message("执行成功", FeedbackLevel.SUCCESS)
            self.visual_feedback.set_progress(1.0)
            VoiceFeedback.speak_feedback(VoiceFeedback.SUCCESS)
        else:
            self.visual_feedback.set_state(AgentState.ERROR, "操作失败")
            self.visual_feedback.add_message(f"执行失败: {message}", FeedbackLevel.ERROR)
            VoiceFeedback.speak_feedback(VoiceFeedback.FAILED)

        # 验证最终状态
        self.assertEqual(self.visual_feedback.current_state, AgentState.SUCCESS)
        self.assertEqual(self.visual_feedback.progress_value, 1.0)

        # 绘制反馈
        result_frame = self.visual_feedback.draw_feedback(frame)
        self.assertEqual(result_frame.shape, frame.shape)

        print("[OK] 快通道执行反馈测试通过")

    def test_slow_path_analysis_feedback(self):
        """测试慢通道分析的反馈"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # 模拟慢通道分析
        self.visual_feedback.set_state(AgentState.THINKING, "分析意图中...")
        self.visual_feedback.set_progress(0.3, "LLM分析")
        self.visual_feedback.add_message("正在分析复杂指令", FeedbackLevel.INFO, duration=5.0)

        # 语音反馈
        tts_success = self.tts_engine.speak_async("正在分析指令意图")
        self.assertTrue(tts_success)

        # 验证状态
        self.assertEqual(self.visual_feedback.current_state, AgentState.THINKING)
        self.assertEqual(self.visual_feedback.progress_value, 0.3)

        # 绘制反馈
        result_frame = self.visual_feedback.draw_feedback(frame)
        self.assertEqual(result_frame.shape, frame.shape)

        print("[OK] 慢通道分析反馈测试通过")

    def test_error_handling_feedback(self):
        """测试错误处理的反馈"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # 模拟执行错误
        self.visual_feedback.set_state(AgentState.ERROR, "执行失败")
        self.visual_feedback.add_message("操作执行失败: 权限不足", FeedbackLevel.ERROR, duration=3.0)
        self.visual_feedback.set_progress(0.7)  # 失败时的进度

        # 错误语音反馈
        tts_success = VoiceFeedback.speak_feedback(VoiceFeedback.FAILED)
        self.assertTrue(tts_success)

        # 验证状态
        self.assertEqual(self.visual_feedback.current_state, AgentState.ERROR)
        self.assertGreater(len(self.visual_feedback.status_messages), 0)

        # 验证有错误级别的消息
        error_messages = [msg for msg in self.visual_feedback.status_messages
                         if msg.level == FeedbackLevel.ERROR]
        self.assertGreater(len(error_messages), 0)

        # 绘制反馈
        result_frame = self.visual_feedback.draw_feedback(frame)
        self.assertEqual(result_frame.shape, frame.shape)

        print("[OK] 错误处理反馈测试通过")

    def test_concurrent_feedback_safety(self):
        """测试并发反馈的安全性"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        import threading
        results = []

        def feedback_worker():
            """反馈工作线程"""
            try:
                for i in range(10):
                    # 设置状态
                    self.visual_feedback.set_state(AgentState.PROCESSING, f"处理任务{i}")
                    self.visual_feedback.add_message(f"消息{i}", FeedbackLevel.INFO)
                    self.visual_feedback.set_progress(i / 10)

                    # 语音反馈
                    self.tts_engine.speak_async(f"正在处理{i}")

                    # 绘制反馈
                    result_frame = self.visual_feedback.draw_feedback(frame)
                    self.assertEqual(result_frame.shape, frame.shape)

                    results.append(i)
            except Exception as e:
                print(f"Feedback worker error: {e}")

        # 创建多个线程
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=feedback_worker)
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证没有崩溃
        self.assertEqual(len(results), 30)
        self.assertGreaterEqual(self.visual_feedback.progress_value, 0.0)
        self.assertLessEqual(self.visual_feedback.progress_value, 1.0)

        print("[OK] 并发反馈安全性测试通过")

    def test_feedback_configuration_flexibility(self):
        """测试反馈配置的灵活性"""
        # 测试不同的配置
        configs = [
            VisualFeedbackConfig(enable_status_display=False),
            VisualFeedbackConfig(enable_message_overlay=False),
            VisualFeedbackConfig(enable_progress_bar=False),
            VisualFeedbackConfig(enable_gesture_indicators=False),
        ]

        for config in configs:
            feedback = VisualFeedback(config)
            frame = np.zeros((480, 640, 3), dtype=np.uint8)

            # 设置状态和消息
            feedback.set_state(AgentState.PROCESSING, "测试")
            feedback.add_message("测试消息", FeedbackLevel.INFO)
            feedback.set_progress(0.5)

            # 绘制反馈应该不会出错
            result_frame = feedback.draw_feedback(frame)
            self.assertEqual(result_frame.shape, frame.shape)

        print("[OK] 反馈配置灵活性测试通过")

    def test_feedback_message_expiry(self):
        """测试反馈消息过期"""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # 添加短时间的消息
        self.visual_feedback.add_message("短期消息", FeedbackLevel.INFO, duration=0.01)
        self.visual_feedback.add_message("长期消息", FeedbackLevel.SUCCESS, duration=10.0)

        # 等待短期消息过期
        time.sleep(0.02)

        # 手动触发清理
        self.visual_feedback._cleanup_expired_messages()

        # 应该只剩一个消息
        self.assertEqual(len(self.visual_feedback.status_messages), 1)
        self.assertEqual(self.visual_feedback.status_messages[0].text, "长期消息")

        print("[OK] 反馈消息过期测试通过")

    def test_tts_engine_fallback(self):
        """测试TTS引擎回退机制"""
        # 测试不同的TTS引擎类型
        engine_configs = [
            TTSConfig(enabled=False),  # 禁用TTS
            TTSConfig(engine_type="offline"),  # 离线模式
        ]

        for config in engine_configs:
            engine = TTSEngine(config)

            # 所有引擎都应该可以播报
            success = engine.speak("测试消息")
            self.assertTrue(success)

            # 验证引擎信息
            info = engine.get_engine_info()
            self.assertIn("available", info)
            self.assertIn("engine_type", info)

        print("[OK] TTS引擎回退机制测试通过")


if __name__ == '__main__':
    print("启动Phase 4集成测试...")
    print("=" * 50)

    # 运行测试
    unittest.main(verbosity=2)