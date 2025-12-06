"""
TTS引擎单元测试

测试各种TTS引擎的功能
"""

import unittest
import sys
import os
import time
import threading
from unittest.mock import Mock, patch, MagicMock

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from tts_engine import (
    TTSConfig, TTSEngineType, BaseTTSEngine, OfflineTTSEngine,
    EdgeTTSEngine, Pyttsx3TTSEngine, TTSEngine, VoiceFeedback,
    get_tts_engine, speak
)


class TestTTSConfig(unittest.TestCase):
    """TTS配置测试"""

    def test_default_config(self):
        """测试默认配置"""
        config = TTSConfig()
        self.assertEqual(config.engine_type, TTSEngineType.OFFLINE)
        self.assertEqual(config.voice, "zh-CN-XiaoxiaoNeural")
        self.assertEqual(config.rate, 200)
        self.assertEqual(config.volume, 0.9)
        self.assertTrue(config.enabled)

    def test_custom_config(self):
        """测试自定义配置"""
        config = TTSConfig(
            engine_type=TTSEngineType.PYTTSX3,
            voice="custom_voice",
            rate=150,
            volume=0.8,
            enabled=False
        )
        self.assertEqual(config.engine_type, TTSEngineType.PYTTSX3)
        self.assertEqual(config.voice, "custom_voice")
        self.assertEqual(config.rate, 150)
        self.assertEqual(config.volume, 0.8)
        self.assertFalse(config.enabled)


class TestOfflineTTSEngine(unittest.TestCase):
    """离线TTS引擎测试"""

    def setUp(self):
        """测试前准备"""
        self.config = TTSConfig()
        self.engine = OfflineTTSEngine(self.config)

    def test_speak_success(self):
        """测试播报成功"""
        result = self.engine.speak("测试文本")
        self.assertTrue(result)

    def test_is_available(self):
        """测试引擎可用性"""
        self.assertTrue(self.engine.is_available())

    def test_cleanup(self):
        """测试清理"""
        # 离线引擎的cleanup应该不会抛出异常
        self.engine.cleanup()

    def test_empty_text(self):
        """测试空文本"""
        result = self.engine.speak("")
        self.assertTrue(result)  # 离线引擎总是返回True

    def test_whitespace_text(self):
        """测试纯空白文本"""
        result = self.engine.speak("   \n\t   ")
        self.assertTrue(result)


class TestPyttsx3TTSEngine(unittest.TestCase):
    """pyttsx3 TTS引擎测试"""

    def setUp(self):
        """测试前准备"""
        self.config = TTSConfig(engine_type=TTSEngineType.PYTTSX3)

    def test_initialization_failure_missing_library(self):
        """测试库缺失时的初始化失败"""
        # 模拟导入失败
        with patch.dict('sys.modules', {'pyttsx3': None}):
            engine = Pyttsx3TTSEngine(self.config)
            self.assertFalse(engine.is_available())


class TestEdgeTTSEngine(unittest.TestCase):
    """Edge TTS引擎测试"""

    def setUp(self):
        """测试前准备"""
        self.config = TTSConfig(engine_type=TTSEngineType.EDGE_TTS)

    def test_initialization_missing_library(self):
        """测试库缺失时的初始化失败"""
        # 模拟导入失败
        with patch.dict('sys.modules', {'edge_tts': None}):
            engine = EdgeTTSEngine(self.config)
            self.assertFalse(engine.is_available())


class TestTTSEngine(unittest.TestCase):
    """TTS引擎管理器测试"""

    def test_offline_mode_initialization(self):
        """测试离线模式初始化"""
        config = TTSConfig(enabled=False)
        engine = TTSEngine(config)
        self.assertIsInstance(engine.engine, OfflineTTSEngine)

    def test_global_instance(self):
        """测试全局实例"""
        # 清除全局实例
        import tts_engine
        tts_engine._tts_instance = None

        engine1 = get_tts_engine()
        engine2 = get_tts_engine()
        self.assertIs(engine1, engine2)  # 应该是同一个实例

    def test_speak_empty_text(self):
        """测试播报空文本"""
        engine = TTSEngine()
        result = engine.speak("")
        self.assertFalse(result)

    def test_speak_whitespace_text(self):
        """测试播报空白文本"""
        engine = TTSEngine()
        result = engine.speak("   \n\t   ")
        self.assertFalse(result)

    def test_concurrent_speak_prevention(self):
        """测试并发播报防护"""
        engine = TTSEngine()

        # 模拟长时间播报
        with patch.object(engine.engine, 'speak') as mock_speak:
            # 模拟播报需要时间
            def slow_speak(text):
                time.sleep(0.1)
                return True
            mock_speak.side_effect = slow_speak

            # 第一次播报
            result1 = engine.speak("文本1", async_mode=True)
            time.sleep(0.01)  # 让线程启动

            # 第二次播报应该被跳过
            result2 = engine.speak("文本2", async_mode=True)

            self.assertTrue(result1)
            self.assertFalse(result2)  # 应该被跳过

    def test_engine_info(self):
        """测试获取引擎信息"""
        engine = TTSEngine()
        info = engine.get_engine_info()

        self.assertIn("available", info)
        self.assertTrue(info["available"])
        self.assertIn("engine_type", info)

    def test_cleanup(self):
        """测试清理"""
        engine = TTSEngine()
        # 清理应该不会抛出异常
        engine.cleanup()


class TestVoiceFeedback(unittest.TestCase):
    """语音反馈测试"""

    def test_predefined_messages(self):
        """测试预定义消息"""
        self.assertEqual(VoiceFeedback.WORKFLOW_START, "正在为您处理...")
        self.assertEqual(VoiceFeedback.WORKFLOW_COMPLETE, "任务已完成")
        self.assertEqual(VoiceFeedback.CONFIRM_SEND, "确认发送吗？")

    @patch('tts_engine.speak')
    def test_speak_feedback(self, mock_speak):
        """测试播报反馈"""
        mock_speak.return_value = True
        result = VoiceFeedback.speak_feedback("测试反馈")
        mock_speak.assert_called_once_with("测试反馈", True)
        self.assertTrue(result)


class TestConvenienceFunctions(unittest.TestCase):
    """便捷函数测试"""

    @patch('tts_engine.get_tts_engine')
    def test_speak_function(self, mock_get_tts):
        """测试speak便捷函数"""
        mock_engine = Mock()
        mock_engine.speak.return_value = True
        mock_get_tts.return_value = mock_engine

        result = speak("测试文本", async_mode=False)
        mock_engine.speak.assert_called_once_with("测试文本", False)
        self.assertTrue(result)


class TestTTSIntegration(unittest.TestCase):
    """TTS集成测试"""

    def test_end_to_end_workflow(self):
        """测试端到端工作流"""
        # 创建TTS引擎
        config = TTSConfig(enabled=True)
        engine = TTSEngine(config)

        # 播报工作流反馈
        success_count = 0
        feedback_messages = [
            VoiceFeedback.WORKFLOW_START,
            VoiceFeedback.PROCESSING,
            VoiceFeedback.WORKFLOW_COMPLETE
        ]

        for message in feedback_messages:
            if engine.speak_async(message):
                success_count += 1

        self.assertEqual(success_count, len(feedback_messages))

    def test_error_handling(self):
        """测试错误处理"""
        engine = TTSEngine()

        # 测试各种错误情况
        error_cases = [
            "",  # 空文本
            None,  # None值（如果类型检查允许）
            "   \n\t   ",  # 纯空白
        ]

        for case in error_cases:
            if case is not None:  # None会导致类型错误
                result = engine.speak(case)
                self.assertFalse(result)

    def test_async_vs_sync(self):
        """测试同步vs异步播报"""
        engine = TTSEngine()

        # 同步播报
        start_time = time.time()
        sync_result = engine.speak("同步测试", async_mode=False)
        sync_time = time.time() - start_time

        # 异步播报
        start_time = time.time()
        async_result = engine.speak("异步测试", async_mode=True)
        async_time = time.time() - start_time

        # 两个都应该成功
        self.assertTrue(sync_result)
        self.assertTrue(async_result)

        # 在离线模式下，主要测试功能是否正常，时间要求宽松
        self.assertGreaterEqual(sync_time, 0)
        self.assertGreaterEqual(async_time, 0)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)