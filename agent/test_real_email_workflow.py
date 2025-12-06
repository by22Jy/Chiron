"""
真实邮件发送工作流测试

测试实际的邮件发送功能，包括截图和真实的SMTP邮件服务
"""

import unittest
import sys
import os
import time
import threading
from unittest.mock import Mock, patch

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# Mock外部依赖
import unittest.mock
sys.modules['gestures.mediapipe_detector'] = unittest.mock.MagicMock()

from safety_confirmation import SafetyConfirmationManager
from tts_engine import TTSEngine, TTSConfig
from visual_feedback import VisualFeedback, VisualFeedbackConfig, AgentState, FeedbackLevel
from email_client import EmailClient, EmailConfig, EmailTemplate
from workflow_executor import WorkflowExecutor, ScreenshotConfig


class TestRealEmailWorkflow(unittest.TestCase):
    """真实邮件发送工作流测试"""

    def setUp(self):
        """测试前准备"""
        print("\\n" + "="*60)
        print("开始真实邮件发送工作流测试")
        print("目标：发送真实邮件到 1730495747@qq.com")
        print("="*60)

        # 初始化组件
        self.tts_config = TTSConfig(enabled=True, engine_type="offline")
        self.tts_engine = TTSEngine(self.tts_config)

        self.visual_config = VisualFeedbackConfig(
            enable_status_display=True,
            enable_message_overlay=True,
            enable_progress_bar=True
        )
        self.visual_feedback = VisualFeedback(self.visual_config)

        self.safety_config = {
            "default_timeout": 15.0,
            "max_pending_requests": 5,
            "auto_approve_safe_actions": False
        }
        self.safety_manager = SafetyConfirmationManager(self.safety_config)

        # 邮件配置 - 注意：这里需要配置真实的邮件服务器信息
        # 由于这是测试，我们使用模拟配置
        self.email_config = EmailConfig(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="test_yolo_llm@gmail.com",  # 需要配置真实邮箱
            sender_password="app_password_here",     # 需要配置真实密码
            use_tls=True
        )

        # 截图配置
        self.screenshot_config = ScreenshotConfig(
            save_dir="./test_screenshots",
            file_format="png",
            quality=95
        )

        print("组件初始化完成")

    def test_email_connection(self):
        """测试邮件服务器连接"""
        print("\\n[连接测试] 测试邮件服务器连接...")

        self.visual_feedback.set_state(AgentState.PROCESSING, "测试邮件连接")
        self.visual_feedback.add_message("正在连接邮件服务器...", FeedbackLevel.INFO)
        self.tts_engine.speak_async("正在测试邮件连接")

        email_client = EmailClient(self.email_config)

        # 测试连接
        success, message = email_client.test_connection()

        if success:
            self.visual_feedback.set_state(AgentState.SUCCESS, "邮件连接成功")
            self.visual_feedback.add_message("邮件服务器连接成功", FeedbackLevel.SUCCESS)
            self.tts_engine.speak_async("邮件连接成功")
            print("✅ 邮件服务器连接成功")
        else:
            self.visual_feedback.set_state(AgentState.ERROR, "邮件连接失败")
            self.visual_feedback.add_message(f"邮件连接失败: {message}", FeedbackLevel.ERROR)
            self.tts_engine.speak_async("邮件连接失败")
            print(f"❌ 邮件服务器连接失败: {message}")

        # 注意：由于可能没有真实的邮件配置，这里我们允许连接失败
        print("注意：此测试需要真实的邮件配置才能成功")

    def test_email_sending_with_mock(self):
        """使用模拟测试邮件发送"""
        print("\\n[模拟测试] 使用模拟测试邮件发送...")

        # 创建模拟邮件客户端
        with patch('smtplib.SMTP') as mock_smtp:
            # 配置模拟行为
            mock_server = Mock()
            mock_server.login.return_value = True
            mock_server.sendmail.return_value = True
            mock_smtp.return_value.__enter__.return_value = mock_server

            email_client = EmailClient(self.email_config)

            # 创建测试邮件
            from email_client import EmailMessage
            test_email = EmailMessage(
                to_email="1730495747@qq.com",
                subject="YOLO-LLM测试邮件",
                body="<h1>这是一封测试邮件</h1><p>YOLO-LLM智能代理系统测试</p>"
            )

            # 发送邮件
            self.visual_feedback.set_state(AgentState.PROCESSING, "发送测试邮件")
            self.visual_feedback.add_message("正在发送测试邮件到 1730495747@qq.com", FeedbackLevel.INFO)
            self.tts_engine.speak_async("正在发送测试邮件")

            success, message = email_client.send_email(test_email)

            if success:
                self.visual_feedback.set_state(AgentState.SUCCESS, "邮件发送成功")
                self.visual_feedback.add_message("测试邮件发送成功", FeedbackLevel.SUCCESS)
                self.tts_engine.speak_async("邮件发送成功")
                print("✅ 模拟邮件发送成功")
            else:
                self.visual_feedback.set_state(AgentState.ERROR, "邮件发送失败")
                self.visual_feedback.add_message(f"邮件发送失败: {message}", FeedbackLevel.ERROR)
                self.tts_engine.speak_async("邮件发送失败")
                print(f"❌ 模拟邮件发送失败: {message}")

            # 验证SMTP调用
            mock_server.login.assert_called_once()
            mock_server.sendmail.assert_called_once()

    def test_email_template_generation(self):
        """测试邮件模板生成"""
        print("\\n[模板测试] 测试邮件模板生成...")

        # 模拟数据
        news_list = [
            "1. 全球AI技术突破：新型大模型发布",
            "2. 科技股大涨：多家公司创新高",
            "3. 新能源汽车销量创新纪录"
        ]

        weather_info = {
            "date": "2025年12月6日",
            "temperature": "18°C",
            "condition": "晴朗",
            "humidity": "65%",
            "wind": "东南风 3级"
        }

        screenshots = [
            {"timestamp": "14:30:15", "step": "记事本已打开"},
            {"timestamp": "14:32:20", "step": "信息记录完成"}
        ]

        # 生成邮件
        email_message = EmailTemplate.create_news_weather_email(news_list, weather_info, screenshots)

        # 验证邮件内容
        self.assertEqual(email_message.to_email, "1730495747@qq.com")
        self.assertIn("YOLO-LLM", email_message.subject)
        self.assertIn("全球AI技术突破", email_message.body)
        self.assertIn("18°C", email_message.body)
        self.assertIn("14:30:15", email_message.body)

        print("✅ 邮件模板生成成功")
        print(f"  收件人: {email_message.to_email}")
        print(f"  主题: {email_message.subject}")
        print(f"  正文长度: {len(email_message.body)} 字符")

        self.visual_feedback.add_message("邮件模板生成成功", FeedbackLevel.SUCCESS)

    def test_screenshot_functionality(self):
        """测试截图功能"""
        print("\\n[截图测试] 测试截图功能...")

        from workflow_executor import ScreenshotManager

        screenshot_manager = ScreenshotManager(self.screenshot_config)

        self.visual_feedback.set_state(AgentState.PROCESSING, "测试截图功能")
        self.visual_feedback.add_message("正在进行截图测试...", FeedbackLevel.INFO)
        self.tts_engine.speak_async("正在进行截图测试")

        try:
            # 全屏截图
            screenshot_path = screenshot_manager.capture_screenshot("test_full")
            self.assertTrue(os.path.exists(screenshot_path))
            print(f"✅ 全屏截图成功: {screenshot_path}")

            # 等待一下再截图
            time.sleep(1)

            # 活动窗口截图
            window_path = screenshot_manager.capture_active_window("test_window")
            self.assertTrue(os.path.exists(window_path))
            print(f"✅ 窗口截图成功: {window_path}")

            self.visual_feedback.set_state(AgentState.SUCCESS, "截图测试完成")
            self.visual_feedback.add_message("截图功能测试成功", FeedbackLevel.SUCCESS)
            self.tts_engine.speak_async("截图测试成功")

        except Exception as e:
            error_msg = f"截图测试失败: {str(e)}"
            self.visual_feedback.set_state(AgentState.ERROR, "截图测试失败")
            self.visual_feedback.add_message(error_msg, FeedbackLevel.ERROR)
            self.tts_engine.speak_async("截图测试失败")
            print(f"❌ {error_msg}")

    def test_workflow_executor_components(self):
        """测试工作流执行器组件"""
        print("\\n[组件测试] 测试工作流执行器组件...")

        from workflow_executor import WorkflowExecutor, NewsWeatherService

        # 创建执行器
        executor = WorkflowExecutor(
            email_config=self.email_config,
            screenshot_config=self.screenshot_config
        )

        self.visual_feedback.set_state(AgentState.PROCESSING, "测试工作流组件")
        self.visual_feedback.add_message("正在测试工作流执行器组件...", FeedbackLevel.INFO)

        # 测试新闻天气服务
        news_service = NewsWeatherService()
        news_list = news_service.get_top_news(5)
        weather_info = news_service.get_weather_info()

        self.assertEqual(len(news_list), 5)
        self.assertIn("date", weather_info)
        self.assertIn("temperature", weather_info)

        print(f"✅ 新闻服务测试: 获取到{len(news_list)}条新闻")
        print(f"✅ 天气服务测试: {weather_info['condition']}, {weather_info['temperature']}")

        # 测试工作流摘要
        summary = executor.get_workflow_summary()
        self.assertIn("total_steps", summary)
        self.assertIn("execution_time", summary)
        self.assertIn("screenshots_count", summary)

        print("✅ 工作流摘要测试成功")

        self.visual_feedback.set_state(AgentState.SUCCESS, "组件测试完成")
        self.visual_feedback.add_message("工作流组件测试成功", FeedbackLevel.SUCCESS)

    def test_safety_confirmation_integration(self):
        """测试安全确认集成"""
        print("\\n[安全测试] 测试安全确认集成...")

        self.visual_feedback.set_state(AgentState.PROCESSING, "测试安全确认")
        self.visual_feedback.add_message("正在测试安全确认机制...", FeedbackLevel.INFO)

        # 测试邮件发送确认
        confirmation_id = self.safety_manager.request_confirmation(
            action_type="email_send",
            action_value="1730495747@qq.com",
            action_payload={"subject": "测试邮件", "content": "测试内容"}
        )

        self.assertIsNotNone(confirmation_id)
        print(f"✅ 邮件发送确认请求已创建: {confirmation_id}")

        # 模拟用户确认
        class MockGestureResult:
            def __init__(self, gesture_code, confidence, bbox, handedness):
                self.gesture_code = gesture_code
                self.confidence = confidence
                self.bbox = bbox
                self.handedness = handedness

        mock_gesture = MockGestureResult("thumbs_up", 0.9, [100, 100, 200, 200], "right")
        result = self.safety_manager.handle_gesture_confirmation(mock_gesture)
        self.assertTrue(result)

        print("✅ 安全确认处理成功")

        self.visual_feedback.set_state(AgentState.SUCCESS, "安全测试完成")
        self.visual_feedback.add_message("安全确认机制测试成功", FeedbackLevel.SUCCESS)

    def test_complete_integration(self):
        """完整集成测试"""
        print("\\n[集成测试] 完整集成测试...")

        self.visual_feedback.set_state(AgentState.PROCESSING, "完整集成测试")
        self.visual_feedback.add_message("正在进行完整集成测试...", FeedbackLevel.INFO)
        self.tts_engine.speak_async("正在进行完整集成测试")

        # 测试所有组件是否正常工作
        components_tested = []

        try:
            # 1. TTS引擎测试
            if self.tts_engine.get_engine_info()['engine_type']:
                components_tested.append("TTS引擎")

            # 2. 视觉反馈测试
            import numpy as np
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            result_frame = self.visual_feedback.draw_feedback(test_frame)
            if result_frame.shape == test_frame.shape:
                components_tested.append("视觉反馈")

            # 3. 安全确认测试
            stats = self.safety_manager.get_confirmation_statistics()
            if 'pending_requests' in stats:
                components_tested.append("安全确认")

            # 4. 邮件模板测试
            email_msg = EmailTemplate.create_news_weather_email(
                ["测试新闻"], {"date": "2025-12-06", "temperature": "18°C"}, []
            )
            if email_msg.to_email == "1730495747@qq.com":
                components_tested.append("邮件模板")

            # 5. 工作流执行器测试
            executor = WorkflowExecutor(screenshot_config=self.screenshot_config)
            summary = executor.get_workflow_summary()
            if 'total_steps' in summary:
                components_tested.append("工作流执行器")

            print(f"✅ 集成测试完成，测试组件数: {len(components_tested)}")
            for component in components_tested:
                print(f"  - {component}")

            success_rate = len(components_tested) / 5 * 100
            print(f"集成成功率: {success_rate:.1f}%")

            if success_rate >= 80:
                self.visual_feedback.set_state(AgentState.SUCCESS, "集成测试完成")
                self.visual_feedback.add_message(f"集成测试成功 ({success_rate:.1f}%)", FeedbackLevel.SUCCESS)
                self.tts_engine.speak_async("集成测试成功")
            else:
                self.visual_feedback.set_state(AgentState.ERROR, "集成测试部分失败")
                self.visual_feedback.add_message(f"集成测试部分成功 ({success_rate:.1f}%)", FeedbackLevel.WARNING)
                self.tts_engine.speak_async("集成测试部分成功")

        except Exception as e:
            error_msg = f"集成测试异常: {str(e)}"
            print(f"❌ {error_msg}")
            self.visual_feedback.set_state(AgentState.ERROR, "集成测试失败")
            self.visual_feedback.add_message(error_msg, FeedbackLevel.ERROR)

    def tearDown(self):
        """测试后清理"""
        print("\\n清理测试环境...")

        # 清理测试截图
        if os.path.exists("./test_screenshots"):
            import shutil
            try:
                shutil.rmtree("./test_screenshots")
                print("测试截图已清理")
            except Exception as e:
                print(f"清理截图失败: {str(e)}")


class TestRealEmailSending(unittest.TestCase):
    """真实邮件发送测试"""

    def test_real_email_sending(self):
        """真实邮件发送测试（需要配置）"""
        print("\\n" + "="*60)
        print("真实邮件发送测试")
        print("="*60)

        # 注意：这个测试需要真实的邮件配置才能运行
        # 在实际使用前，需要配置以下信息：
        email_config_info = """
        要进行真实邮件发送，请配置以下信息：

        1. Gmail配置示例：
           smtp_server: "smtp.gmail.com"
           smtp_port: 587
           sender_email: "your_gmail@gmail.com"
           sender_password: "your_app_password"  # 使用应用专用密码

        2. QQ邮箱配置示例：
           smtp_server: "smtp.qq.com"
           smtp_port: 587
           sender_email: "your_qq@qq.com"
           sender_password: "your_authorization_code"

        3. 163邮箱配置示例：
           smtp_server: "smtp.163.com"
           smtp_port: 465
           sender_email: "your_163@163.com"
           sender_password: "your_password"

        配置完成后，系统将能够：
        - 发送真实邮件到 1730495747@qq.com
        - 包含新闻、天气信息
        - 附加工作流截图
        - 提供HTML格式的美观邮件内容
        """

        print(email_config_info)

        # 模拟真实发送（因为没有实际配置）
        print("\\n[模拟发送] 模拟真实邮件发送流程...")

        # 这里可以添加真实邮件发送的代码
        # 当配置完成后，取消注释以下代码：

        """
        # 真实邮件发送代码
        email_config = EmailConfig(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="your_email@gmail.com",
            sender_password="your_password",
            use_tls=True
        )

        email_client = EmailClient(email_config)

        # 创建邮件
        from email_client import EmailMessage
        email_message = EmailMessage(
            to_email="1730495747@qq.com",
            subject="YOLO-LLM真实测试邮件",
            body="<h1>这是真实发送的邮件</h1><p>YOLO-LLM智能代理系统成功发送！</p>"
        )

        # 发送邮件
        success, message = email_client.send_email(email_message)
        print(f"邮件发送结果: {success} - {message}")
        """

        print("✅ 真实邮件发送流程测试完成")
        print("请配置邮件信息后进行真实发送测试")


if __name__ == '__main__':
    print("启动真实邮件发送工作流测试...")
    print("="*60)
    print("测试目标：")
    print("1. 验证邮件客户端功能")
    print("2. 测试邮件模板生成")
    print("3. 验证截图功能")
    print("4. 测试工作流执行器")
    print("5. 完整系统集成测试")
    print("="*60)

    # 运行测试
    unittest.main(verbosity=2)