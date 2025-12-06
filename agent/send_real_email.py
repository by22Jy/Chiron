"""
真实邮件发送脚本

使用配置好的邮箱信息发送真实邮件到 1730495747@qq.com
"""

import os
import sys
import time
import yaml
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from email_client import EmailClient, EmailConfig, EmailMessage
from workflow_executor import WorkflowExecutor, ScreenshotConfig, NewsWeatherService


def load_email_config():
    """加载邮件配置"""
    config_file = "email_config.yaml"
    if not os.path.exists(config_file):
        print(f"错误：配置文件 {config_file} 不存在")
        print("请先配置 email_config.yaml 文件")
        return None

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        provider = config.get('default_provider', 'gmail')
        provider_config = config.get(provider, {})

        if not provider_config.get('sender_email') or not provider_config.get('sender_password'):
            print(f"错误：{provider} 配置不完整")
            print(f"请配置 sender_email 和 sender_password")
            return None

        email_config = EmailConfig(
            smtp_server=provider_config['smtp_server'],
            smtp_port=provider_config['smtp_port'],
            sender_email=provider_config['sender_email'],
            sender_password=provider_config['sender_password'],
            use_tls=provider_config['use_tls']
        )

        return email_config, config

    except Exception as e:
        print(f"加载配置失败: {str(e)}")
        return None


def send_test_email(email_config, target_email):
    """发送测试邮件"""
    print(f"正在发送测试邮件到 {target_email}...")

    # 创建测试邮件内容
    test_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: #2c3e50;">🤖 YOLO-LLM 智能代理测试邮件</h1>
            <p style="color: #666;">发送时间：{time.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="color: #3498db;">📧 邮件发送测试</h2>
            <p>这是一封测试邮件，验证 YOLO-LLM 智能代理的邮件发送功能是否正常工作。</p>

            <h3>测试内容包括：</h3>
            <ul>
                <li>✓ HTML格式邮件内容</li>
                <li>✓ 中文字符显示</li>
                <li>✓ SMTP服务器连接</li>
                <li>✓ 邮件模板系统</li>
                <li>✓ 目标邮箱: {target_email}</li>
            </ul>
        </div>

        <div style="background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="color: #e67e22;">🔧 系统信息</h2>
            <p><strong>发送方：</strong>{email_config.sender_email}</p>
            <p><strong>SMTP服务器：</strong>{email_config.smtp_server}:{email_config.smtp_port}</p>
            <p><strong>加密方式：</strong>TLS</p>
        </div>

        <div style="background-color: #fff0f5; padding: 15px; border-radius: 8px;">
            <h2 style="color: #9b59b6;">🚀 下一步</h2>
            <p>如果您收到此邮件，说明邮件发送功能配置正确。</p>
            <p>接下来您可以测试完整的工作流：记事本+新闻天气+邮件发送+截图。</p>
        </div>

        <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #f8f9fa; border-radius: 8px;">
            <p style="color: #666; font-style: italic;">
                <em>此邮件由 YOLO-LLM 智能代理自动生成并发送</em><br>
                <em>🤖 智能工作流代理 | 多模态感知 | 安全确认</em>
            </p>
        </div>
    </body>
    </html>
    """

    # 创建邮件消息
    email_message = EmailMessage(
        to_email=target_email,
        subject=f"YOLO-LLM邮件发送测试 - {time.strftime('%Y%m%d_%H%M%S')}",
        body=test_content
    )

    # 发送邮件
    try:
        email_client = EmailClient(email_config)
        success, message = email_client.send_email(email_message)

        if success:
            print("✅ 测试邮件发送成功！")
            print(f"请检查您的邮箱 {target_email}")
            return True
        else:
            print(f"❌ 测试邮件发送失败: {message}")
            return False

    except Exception as e:
        print(f"❌ 邮件发送异常: {str(e)}")
        return False


def send_news_weather_email(email_config, target_email, include_screenshot=False):
    """发送新闻天气邮件"""
    print("正在发送新闻天气邮件...")

    # 获取新闻和天气信息
    news_service = NewsWeatherService()
    news_list = news_service.get_top_news(10)
    weather_info = news_service.get_weather_info()

    screenshots = []
    screenshot_path = ""

    # 如果包含截图
    if include_screenshot:
        try:
            from workflow_executor import ScreenshotManager
            screenshot_config = ScreenshotConfig(
                save_dir="./screenshots",
                file_format="png",
                quality=95
            )
            screenshot_manager = ScreenshotManager(screenshot_config)
            screenshot_path = screenshot_manager.capture_screenshot("news_weather_report")

            if screenshot_path:
                screenshots.append({
                    "timestamp": time.strftime('%H:%M:%S'),
                    "step": "新闻天气报告生成",
                    "path": screenshot_path
                })
                print(f"✓ 截图已保存: {screenshot_path}")

        except Exception as e:
            print(f"⚠ 截图失败: {str(e)}")

    # 使用邮件模板生成邮件
    email_message = EmailTemplate.create_news_weather_email(
        news_list=news_list,
        weather_info=weather_info,
        screenshots=screenshots
    )

    # 添加截图附件
    if screenshot_path and os.path.exists(screenshot_path):
        email_message.attachments.append(screenshot_path)
        print(f"✓ 截图已添加到邮件附件")

    # 发送邮件
    try:
        email_client = EmailClient(email_config)
        success, message = email_client.send_email(email_message)

        if success:
            print("✅ 新闻天气邮件发送成功！")
            print(f"包含 {len(news_list)} 条新闻和天气信息")
            if include_screenshot:
                print("✓ 包含截图附件")
            return True
        else:
            print(f"❌ 新闻天气邮件发送失败: {message}")
            return False

    except Exception as e:
        print(f"❌ 邮件发送异常: {str(e)}")
        return False


def execute_full_workflow(email_config, target_email):
    """执行完整工作流"""
    print("正在执行完整工作流...")
    print("工作流：记事本 + 新闻天气 + 邮件发送 + 截图")

    # 创建工作流执行器
    screenshot_config = ScreenshotConfig(
        save_dir="./screenshots",
        file_format="png",
        quality=95
    )

    executor = WorkflowExecutor(
        email_config=email_config,
        screenshot_config=screenshot_config
    )

    # 执行工作流
    success, message = executor.execute_complex_workflow()

    if success:
        print("✅ 完整工作流执行成功！")

        # 获取工作流摘要
        summary = executor.get_workflow_summary()
        print(f"执行时间: {summary['execution_time']:.2f} 秒")
        print(f"执行步骤: {summary['total_steps']} 步")
        print(f"截图数量: {summary['screenshots_count']} 个")

        print("执行步骤详情:")
        for i, step in enumerate(summary['steps'], 1):
            print(f"  {i}. {step}")

        return True
    else:
        print(f"❌ 完整工作流执行失败: {message}")
        return False


def main():
    """主函数"""
    print("🚀 YOLO-LLM 真实邮件发送系统")
    print("="*50)

    # 加载配置
    config_result = load_email_config()
    if not config_result:
        print("\n❌ 配置加载失败，请检查 email_config.yaml 文件")
        return

    email_config, full_config = config_result
    target_email = full_config['target_emails']['primary']

    print(f"✓ 配置加载成功")
    print(f"✓ 发送邮箱: {email_config.sender_email}")
    print(f"✓ SMTP服务器: {email_config.smtp_server}:{email_config.smtp_port}")
    print(f"✓ 目标邮箱: {target_email}")

    # 测试连接
    print(f"\n🔗 测试SMTP连接...")
    email_client = EmailClient(email_config)
    success, message = email_client.test_connection()

    if success:
        print("✅ SMTP连接成功")
    else:
        print(f"❌ SMTP连接失败: {message}")
        return

    # 菜单选择
    print(f"\n📋 请选择要执行的操作:")
    print("1. 发送测试邮件")
    print("2. 发送新闻天气邮件")
    print("3. 发送新闻天气邮件（含截图）")
    print("4. 执行完整工作流")
    print("5. 全部测试")

    try:
        choice = input(f"\\n请输入选择 (1-5): ").strip()
    except KeyboardInterrupt:
        print(f"\\n用户取消操作")
        return

    success_count = 0
    total_tests = 0

    if choice == "1":
        # 发送测试邮件
        total_tests = 1
        if send_test_email(email_config, target_email):
            success_count = 1

    elif choice == "2":
        # 发送新闻天气邮件
        total_tests = 1
        if send_news_weather_email(email_config, target_email, include_screenshot=False):
            success_count = 1

    elif choice == "3":
        # 发送新闻天气邮件（含截图）
        total_tests = 1
        if send_news_weather_email(email_config, target_email, include_screenshot=True):
            success_count = 1

    elif choice == "4":
        # 执行完整工作流
        total_tests = 1
        if execute_full_workflow(email_config, target_email):
            success_count = 1

    elif choice == "5":
        # 全部测试
        total_tests = 4
        print(f"\\n🧪 开始全部测试...")

        # 测试1：测试邮件
        print(f"\\n--- 测试1: 发送测试邮件 ---")
        if send_test_email(email_config, target_email):
            success_count += 1
        time.sleep(3)

        # 测试2：新闻天气邮件
        print(f"\\n--- 测试2: 发送新闻天气邮件 ---")
        if send_news_weather_email(email_config, target_email, include_screenshot=False):
            success_count += 1
        time.sleep(3)

        # 测试3：新闻天气邮件（含截图）
        print(f"\\n--- 测试3: 发送新闻天气邮件（含截图） ---")
        if send_news_weather_email(email_config, target_email, include_screenshot=True):
            success_count += 1
        time.sleep(3)

        # 测试4：完整工作流
        print(f"\\n--- 测试4: 执行完整工作流 ---")
        if execute_full_workflow(email_config, target_email):
            success_count += 1

    else:
        print("❌ 无效选择")
        return

    # 显示结果
    print(f"\\n" + "="*50)
    print(f"📊 测试结果")
    print(f"="*50)
    print(f"成功: {success_count}/{total_tests}")
    print(f"成功率: {success_count/total_tests*100:.1f}%")

    if success_count == total_tests:
        print("🎉 所有测试通过！邮件发送功能正常工作")
    elif success_count > 0:
        print("⚠ 部分测试通过，请检查失败的测试")
    else:
        print("❌ 所有测试失败，请检查配置")

    print(f"\\n请检查您的邮箱 {target_email} 确认是否收到邮件")


if __name__ == '__main__':
    main()