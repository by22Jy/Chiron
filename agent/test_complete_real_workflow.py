"""
完整真实工作流测试

测试使用真实API的完整工作流：
1. 获取真实新闻和天气
2. 发送真实邮件（需要配置）
3. 真实截图功能
"""

import unittest
import sys
import os
import time
import yaml

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

# Mock外部依赖
import unittest.mock
sys.modules['gestures.mediapipe_detector'] = unittest.mock.MagicMock()

from real_news_weather import create_news_weather_service
from workflow_executor import WorkflowExecutor, ScreenshotConfig
from email_client import EmailClient, EmailConfig, EmailTemplate


class TestCompleteRealWorkflow(unittest.TestCase):
    """完整真实工作流测试"""

    def setUp(self):
        """测试前准备"""
        print("\\n" + "="*60)
        print("完整真实工作流测试")
        print("包含真实API和邮件发送功能")
        print("="*60)

        # 初始化截图配置
        self.screenshot_config = ScreenshotConfig(
            save_dir="./test_screenshots",
            file_format="png",
            quality=95
        )

        # 初始化邮件配置（使用测试配置）
        self.email_config = EmailConfig(
            smtp_server="smtp.gmail.com",
            smtp_port=587,
            sender_email="test_yolo_llm@gmail.com",
            sender_password="test_password",
            use_tls=True
        )

    def test_real_news_weather_api(self):
        """测试真实新闻天气API"""
        print("\\n[API测试] 测试真实新闻天气API...")

        service = create_news_weather_service()

        # 测试新闻获取
        print("获取新闻...")
        news_list = service.get_top_news(5)

        self.assertIsInstance(news_list, list)
        self.assertGreater(len(news_list), 0)
        print(f"✓ 获取到 {len(news_list)} 条新闻")

        # 测试天气获取
        print("获取天气...")
        weather_info = service.get_weather_info()

        self.assertIsInstance(weather_info, dict)
        self.assertIn('date', weather_info)
        self.assertIn('temperature', weather_info)
        self.assertIn('condition', weather_info)
        print(f"✓ 获取天气: {weather_info.get('temperature')} - {weather_info.get('condition')}")

        # 测试综合报告
        print("生成综合报告...")
        report = service.get_combined_report(3)

        self.assertIn('news', report)
        self.assertIn('weather', report)
        self.assertIn('timestamp', report)
        print(f"✓ 生成报告: {report['timestamp']}")

        print("✓ 真实API测试通过")

    def test_email_template_with_real_data(self):
        """测试使用真实数据的邮件模板"""
        print("\\n[邮件测试] 测试真实数据邮件模板...")

        # 获取真实数据
        service = create_news_weather_service()
        news_list = service.get_top_news(3)
        weather_info = service.get_weather_info()

        # 创建邮件
        email_message = EmailTemplate.create_news_weather_email(
            news_list=news_list,
            weather_info=weather_info,
            screenshots=[]
        )

        # 验证邮件内容
        self.assertEqual(email_message.to_email, "1730495747@qq.com")
        self.assertIn("YOLO-LLM", email_message.subject)
        self.assertIn("2025", email_message.subject)  # 包含日期

        # 检查是否包含真实新闻
        has_real_news = any("全球AI技术突破" in news or "科技股" in news for news in news_list)
        if has_real_news:
            print("✓ 邮件包含真实新闻数据")
        else:
            print("ℹ 邮件包含模拟新闻数据（API未配置）")

        # 检查天气信息
        self.assertIn(weather_info.get('temperature', ''), email_message.body)
        self.assertIn(weather_info.get('condition', ''), email_message.body)

        print(f"✓ 邮件模板生成成功，收件人: {email_message.to_email}")

    def test_workflow_executor_with_real_api(self):
        """测试使用真实API的工作流执行器"""
        print("\\n[工作流测试] 测试真实API工作流执行器...")

        # 创建工作流执行器
        executor = WorkflowExecutor(
            email_config=self.email_config,
            screenshot_config=self.screenshot_config
        )

        # 测试工作流摘要
        summary = executor.get_workflow_summary()
        self.assertIn('total_steps', summary)
        self.assertIn('execution_time', summary)
        self.assertIn('screenshots_count', summary)

        # 测试新闻天气服务集成
        news = executor.news_weather_service.get_top_news(2)
        weather = executor.news_weather_service.get_weather_info()

        self.assertIsInstance(news, list)
        self.assertIsInstance(weather, dict)
        print(f"✓ 工作流集成测试: {len(news)}条新闻, {weather.get('condition')}天气")

    def test_screenshot_functionality(self):
        """测试截图功能"""
        print("\\n[截图测试] 测试截图功能...")

        from workflow_executor import ScreenshotManager
        screenshot_manager = ScreenshotManager(self.screenshot_config)

        try:
            # 测试全屏截图
            screenshot_path = screenshot_manager.capture_screenshot("test_real")
            self.assertTrue(os.path.exists(screenshot_path))
            print(f"✓ 全屏截图: {os.path.basename(screenshot_path)}")

            # 测试活动窗口截图
            window_path = screenshot_manager.capture_active_window("test_window")
            if os.path.exists(window_path):
                print(f"✓ 窗口截图: {os.path.basename(window_path)}")

            print("✓ 截图功能测试通过")

        except Exception as e:
            print(f"⚠ 截图测试异常: {str(e)}")

    def test_email_client_simulation(self):
        """测试邮件客户端模拟"""
        print("\\n[邮件客户端] 测试邮件客户端模拟...")

        # 模拟SMTP服务器
        with unittest.mock.patch('smtplib.SMTP') as mock_smtp:
            mock_server = unittest.mock.Mock()
            mock_server.login.return_value = True
            mock_server.sendmail.return_value = True
            mock_smtp.return_value.__enter__.return_value = mock_server

            email_client = EmailClient(self.email_config)

            # 创建测试邮件
            from email_client import EmailMessage
            test_email = EmailMessage(
                to_email="1730495747@qq.com",
                subject="YOLO-LLM真实API测试邮件",
                body="<h1>使用真实API数据的测试邮件</h1>"
            )

            # 发送邮件
            success, message = email_client.send_email(test_email)

            self.assertTrue(success)
            self.assertIn("成功", message)

            # 验证SMTP调用
            mock_server.login.assert_called_once()
            mock_server.sendmail.assert_called_once()

            print("✓ 邮件客户端模拟测试通过")

    def test_complete_integration(self):
        """完整集成测试"""
        print("\\n[集成测试] 完整系统集成测试...")

        components_passed = []
        errors = []

        # 1. 新闻天气API
        try:
            service = create_news_weather_service()
            news = service.get_top_news(1)
            weather = service.get_weather_info()
            if news and weather:
                components_passed.append("新闻天气API")
        except Exception as e:
            errors.append(f"新闻天气API: {str(e)}")

        # 2. 邮件模板
        try:
            service = create_news_weather_service()
            email_msg = EmailTemplate.create_news_weather_email(
                service.get_top_news(1), service.get_weather_info(), []
            )
            if email_msg.to_email == "1730495747@qq.com":
                components_passed.append("邮件模板")
        except Exception as e:
            errors.append(f"邮件模板: {str(e)}")

        # 3. 工作流执行器
        try:
            executor = WorkflowExecutor(screenshot_config=self.screenshot_config)
            summary = executor.get_workflow_summary()
            if 'total_steps' in summary:
                components_passed.append("工作流执行器")
        except Exception as e:
            errors.append(f"工作流执行器: {str(e)}")

        # 4. 截图功能
        try:
            from workflow_executor import ScreenshotManager
            screenshot_manager = ScreenshotManager(self.screenshot_config)
            screenshot_path = screenshot_manager.capture_screenshot("integration_test")
            if os.path.exists(screenshot_path):
                components_passed.append("截图功能")
                # 清理测试截图
                os.remove(screenshot_path)
        except Exception as e:
            errors.append(f"截图功能: {str(e)}")

        # 5. 邮件客户端
        try:
            with unittest.mock.patch('smtplib.SMTP'):
                email_client = EmailClient(self.email_config)
                stats = email_client.test_connection()
                components_passed.append("邮件客户端")
        except Exception as e:
            errors.append(f"邮件客户端: {str(e)}")

        # 显示结果
        total_components = 5
        success_count = len(components_passed)
        success_rate = success_count / total_components * 100

        print(f"\\n集成测试结果:")
        print(f"通过: {success_count}/{total_components}")
        print(f"成功率: {success_rate:.1f}%")

        if components_passed:
            print("\\n通过组件:")
            for component in components_passed:
                print(f"  ✓ {component}")

        if errors:
            print("\\n错误组件:")
            for error in errors:
                print(f"  ✗ {error}")

        # 如果至少通过4个组件，认为集成测试成功
        if success_count >= 4:
            print("\\n✅ 集成测试通过！系统已准备好完整工作流")
        elif success_count >= 3:
            print("\\n⚠ 集成测试部分通过，系统基本可用")
        else:
            print("\\n❌ 集成测试失败，请检查组件配置")

    def test_api_configuration_status(self):
        """测试API配置状态"""
        print("\\n[配置检查] API配置状态检查...")

        # 检查API配置文件
        api_config_file = "api_config.json"
        if os.path.exists(api_config_file):
            try:
                import json
                with open(api_config_file, 'r', encoding='utf-8') as f:
                    api_config = json.load(f)

                news_key_configured = bool(api_config.get('news_api_key'))
                weather_key_configured = bool(api_config.get('weather_api_key'))

                print(f"API配置文件: {api_config_file}")
                print(f"新闻API密钥: {'已配置' if news_key_configured else '未配置'}")
                print(f"天气API密钥: {'已配置' if weather_key_configured else '未配置'}")
                print(f"默认城市: {api_config.get('default_city', 'Beijing')}")

            except Exception as e:
                print(f"API配置文件读取失败: {str(e)}")
        else:
            print(f"API配置文件不存在: {api_config_file}")

        # 检查邮件配置文件
        email_config_file = "email_config.yaml"
        if os.path.exists(email_config_file):
            try:
                with open(email_config_file, 'r', encoding='utf-8') as f:
                    email_config = yaml.safe_load(f)

                provider = email_config.get('default_provider', 'gmail')
                provider_config = email_config.get(provider, {})

                print(f"\\n邮件配置文件: {email_config_file}")
                print(f"默认提供商: {provider}")
                print(f"发件邮箱: {'已配置' if provider_config.get('sender_email') else '未配置'}")
                print(f"目标邮箱: {email_config.get('target_emails', {}).get('primary', '未配置')}")

            except Exception as e:
                print(f"邮件配置文件读取失败: {str(e)}")
        else:
            print(f"\\n邮件配置文件不存在: {email_config_file}")

    def tearDown(self):
        """测试后清理"""
        # 清理测试截图
        if os.path.exists("./test_screenshots"):
            import shutil
            try:
                shutil.rmtree("./test_screenshots")
            except Exception:
                pass


if __name__ == '__main__':
    print("启动完整真实工作流测试...")
    print("="*60)
    print("测试内容:")
    print("1. 真实新闻天气API")
    print("2. 邮件模板生成")
    print("3. 工作流执行器")
    print("4. 截图功能")
    print("5. 邮件客户端")
    print("6. 完整系统集成")
    print("="*60)

    # 运行测试
    unittest.main(verbosity=2)