"""
执行完整工作流脚本

实现用户要求的完整工作流：
1. 打开记事本，记录今日头条新闻top10和天气
2. 发送第一条内容邮件到1730495747@qq.com
3. 截图并包含到邮件中

使用真实API和邮件发送
"""

import os
import sys
import time
import pyautogui
import yaml
import json
from typing import Dict, Any

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from real_news_weather import create_news_weather_service
from workflow_executor import WorkflowExecutor, ScreenshotConfig
from email_client import EmailClient, EmailConfig, EmailTemplate


def load_config():
    """加载所有配置"""
    config = {}

    # 加载API配置
    if os.path.exists("api_config.json"):
        try:
            with open("api_config.json", 'r', encoding='utf-8') as f:
                api_config = json.load(f)
            config['api'] = api_config
        except Exception as e:
            print(f"API配置加载失败: {str(e)}")
            config['api'] = {}

    # 加载邮件配置
    if os.path.exists("email_config.yaml"):
        try:
            with open("email_config.yaml", 'r', encoding='utf-8') as f:
                email_config = yaml.safe_load(f)
            config['email'] = email_config
        except Exception as e:
            print(f"邮件配置加载失败: {str(e)}")
            config['email'] = {}

    return config


def check_config_status():
    """检查配置状态"""
    print("检查配置状态...")
    print("="*50)

    config = load_config()

    # API配置检查
    api_config = config.get('api', {})
    news_key_configured = bool(api_config.get('news_api_key'))
    weather_key_configured = bool(api_config.get('weather_api_key'))

    print(f"新闻API密钥: {'已配置' if news_key_configured else '未配置 - 使用模拟数据'}")
    print(f"天气API密钥: {'已配置' if weather_key_configured else '未配置 - 使用模拟数据'}")

    if not news_key_configured or not weather_key_configured:
        print("\\n提示: 要获取真实新闻天气，请配置 api_config.json")
        print("  - NewsAPI.org: https://newsapi.org/register")
        print("  - OpenWeatherMap: https://openweathermap.org/api")

    # 邮件配置检查
    email_config = config.get('email', {})
    provider = email_config.get('default_provider', 'gmail')
    provider_config = email_config.get(provider, {})

    email_configured = bool(provider_config.get('sender_email') and provider_config.get('sender_password'))
    print(f"邮件配置: {'已配置' if email_configured else '未配置 - 无法发送真实邮件'}")

    if not email_configured:
        print("\\n提示: 要发送真实邮件，请配置 email_config.yaml")
        print("  - Gmail: 需要应用专用密码")
        print("  - QQ邮箱: 需要授权码")
        print("  - 163邮箱: 需要SMTP服务密码")

    return config


def execute_workflow_interactive():
    """交互式执行工作流"""
    print("\\n交互式工作流执行器")
    print("="*50)

    # 检查配置
    config = load_config()

    # 创建服务
    print("初始化服务...")
    news_weather_service = create_news_weather_service()

    # 步骤1: 获取新闻和天气
    print("\\n[步骤 1/4] 获取新闻和天气信息...")
    try:
        news_list = news_weather_service.get_top_news(10)
        weather_info = news_weather_service.get_weather_info()

        print(f"✓ 获取新闻: {len(news_list)} 条")
        print(f"✓ 获取天气: {weather_info.get('temperature')} - {weather_info.get('condition')}")

        # 显示部分新闻预览
        print("\\n新闻预览:")
        for i, news in enumerate(news_list[:3], 1):
            print(f"  {i}. {news[:80]}...")

    except Exception as e:
        print(f"✗ 获取新闻天气失败: {str(e)}")
        return

    # 步骤2: 打开记事本并记录
    print("\\n[步骤 2/4] 打开记事本并记录信息...")
    try:
        # 截图前状态
        screenshot_manager = ScreenshotConfig()

        # 打开记事本
        print("打开记事本...")
        pyautogui.hotkey('win', 'r')
        time.sleep(1)
        pyautogui.write('notepad')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(2)

        # 构建记录内容
        content_lines = [
            "=" * 60,
            f"日期: {weather_info.get('date', time.strftime('%Y年%m月%d日'))}",
            "=" * 60,
            "",
            "今日头条新闻 Top10:",
            ""
        ]

        # 添加新闻
        for news in news_list:
            content_lines.append(news)

        content_lines.extend([
            "",
            "今日天气情况:",
            f"温度: {weather_info.get('temperature', '未知')}",
            f"天气: {weather_info.get('condition', '未知')}",
            f"湿度: {weather_info.get('humidity', '未知')}",
            f"风速: {weather_info.get('wind', '未知')}",
            "",
            "=" * 60,
            f"记录时间: {time.strftime('%H:%M:%S')}",
            f"生成系统: YOLO-LLM智能代理"
        ])

        # 输入到记事本
        content = "\\n".join(content_lines)
        pyautogui.write(content, interval=0.01)

        print("✓ 信息记录完成")

    except Exception as e:
        print(f"✗ 记事本操作失败: {str(e)}")
        return

    # 步骤3: 截图
    print("\\n[步骤 3/4] 截图记录...")
    screenshots = []

    try:
        from workflow_executor import ScreenshotManager
        screenshot_config = ScreenshotConfig(
            save_dir="./workflow_screenshots",
            file_format="png",
            quality=95
        )
        screenshot_manager = ScreenshotManager(screenshot_config)

        # 截取活动窗口
        screenshot_path = screenshot_manager.capture_active_window("notepad_with_news")
        if os.path.exists(screenshot_path):
            screenshots.append({
                "timestamp": time.strftime('%H:%M:%S'),
                "step": "记事本记录完成",
                "path": screenshot_path
            })
            print(f"✓ 截图保存: {os.path.basename(screenshot_path)}")

    except Exception as e:
        print(f"✗ 截图失败: {str(e)}")

    # 步骤4: 发送邮件
    print("\\n[步骤 4/4] 发送邮件...")
    target_email = "1730495747@qq.com"

    try:
        # 检查邮件配置
        email_config = config.get('email', {})
        provider = email_config.get('default_provider', 'gmail')
        provider_config = email_config.get(provider, {})

        if provider_config.get('sender_email') and provider_config.get('sender_password'):
            # 配置了真实邮件，发送真实邮件
            print("使用真实邮件发送...")

            email_client_config = EmailConfig(
                smtp_server=provider_config['smtp_server'],
                smtp_port=provider_config['smtp_port'],
                sender_email=provider_config['sender_email'],
                sender_password=provider_config['sender_password'],
                use_tls=provider_config['use_tls']
            )

            email_client = EmailClient(email_client_config)

            # 创建邮件
            email_message = EmailTemplate.create_news_weather_email(
                news_list=news_list,
                weather_info=weather_info,
                screenshots=screenshots
            )

            # 添加截图附件
            for screenshot in screenshots:
                if os.path.exists(screenshot['path']):
                    email_message.attachments.append(screenshot['path'])

            # 发送邮件
            success, message = email_client.send_email(email_message)

            if success:
                print(f"✓ 邮件发送成功到 {target_email}")
                print("请检查您的邮箱确认收到邮件")
            else:
                print(f"✗ 邮件发送失败: {message}")

        else:
            # 未配置邮件，模拟发送
            print("邮件未配置，进行模拟发送...")

            # 创建模拟邮件内容预览
            email_message = EmailTemplate.create_news_weather_email(
                news_list=news_list,
                weather_info=weather_info,
                screenshots=screenshots
            )

            print(f"✓ 模拟邮件准备完成")
            print(f"  收件人: {target_email}")
            print(f"  主题: {email_message.subject}")
            print(f"  正文长度: {len(email_message.body)} 字符")
            print(f"  附件数量: {len(screenshots)} 个截图")
            print("\\n提示: 配置 email_config.yaml 后可发送真实邮件")

    except Exception as e:
        print(f"✗ 邮件发送失败: {str(e)}")

    # 完成
    print("\\n" + "="*50)
    print("工作流执行完成!")
    print("="*50)

    print(f"处理结果:")
    print(f"  新闻数量: {len(news_list)} 条")
    print(f"  天气信息: {weather_info.get('condition')} ({weather_info.get('temperature')})")
    print(f"  截图数量: {len(screenshots)} 个")
    print(f"  目标邮箱: {target_email}")


def execute_full_workflow():
    """执行完整工作流（自动模式）"""
    print("自动完整工作流执行")
    print("="*50)

    config = load_config()

    # 检查邮件配置
    email_config = config.get('email', {})
    provider = email_config.get('default_provider', 'gmail')
    provider_config = email_config.get(provider, {})

    email_client_config = None
    if provider_config.get('sender_email') and provider_config.get('sender_password'):
        email_client_config = EmailConfig(
            smtp_server=provider_config['smtp_server'],
            smtp_port=provider_config['smtp_port'],
            sender_email=provider_config['sender_email'],
            sender_password=provider_config['sender_password'],
            use_tls=provider_config['use_tls']
        )

    # 创建工作流执行器
    screenshot_config = ScreenshotConfig(
        save_dir="./workflow_screenshots",
        file_format="png",
        quality=95
    )

    executor = WorkflowExecutor(
        email_config=email_client_config,
        screenshot_config=screenshot_config
    )

    # 执行工作流
    print("开始执行完整工作流...")
    success, message = executor.execute_complex_workflow()

    # 显示结果
    print(f"\\n执行结果: {'成功' if success else '失败'}")
    print(f"详细信息: {message}")

    if success:
        summary = executor.get_workflow_summary()
        print(f"\\n执行摘要:")
        print(f"  执行时间: {summary['execution_time']:.2f} 秒")
        print(f"  执行步骤: {summary['total_steps']} 步")
        print(f"  截图数量: {summary['screenshots_count']} 个")

        print(f"\\n执行步骤:")
        for i, step in enumerate(summary['steps'], 1):
            print(f"  {i}. {step}")


def main():
    """主函数"""
    print("YOLO-LLM 完整工作流执行器")
    print("功能: 记事本 + 新闻天气 + 邮件发送 + 截图")
    print("="*60)

    # 检查配置状态
    check_config_status()

    # 选择执行模式
    print("\\n请选择执行模式:")
    print("1. 交互式执行（逐步执行，显示进度）")
    print("2. 自动执行（一键完成，适合测试）")
    print("3. 查看配置指南")

    try:
        choice = input("\\n请输入选择 (1-3): ").strip()

        if choice == "1":
            execute_workflow_interactive()
        elif choice == "2":
            execute_full_workflow()
        elif choice == "3":
            show_configuration_guide()
        else:
            print("无效选择")
    except KeyboardInterrupt:
        print("\\n用户取消操作")
    except Exception as e:
        print(f"\\n执行异常: {str(e)}")


def show_configuration_guide():
    """显示配置指南"""
    print("\\n配置指南")
    print("="*50)

    print("\\n1. 新闻API配置 (api_config.json):")
    print("   - 注册: https://newsapi.org/register")
    print("   - 获取API密钥后填入 news_api_key 字段")
    print("   - 免费额度: 每月1000次请求")

    print("\\n2. 天气API配置 (api_config.json):")
    print("   - 注册: https://openweathermap.org/api")
    print("   - 获取API密钥后填入 weather_api_key 字段")
    print("   - 免费额度: 每月1000000次调用")

    print("\\n3. 邮件配置 (email_config.yaml):")
    print("   Gmail:")
    print("     - 开启两步验证")
    print("     - 生成应用专用密码")
    print("     - 配置 sender_email 和 sender_password")
    print("   QQ邮箱:")
    print("     - 开启SMTP服务")
    print("     - 获取授权码")
    print("     - 配置相应字段")

    print("\\n4. 完成配置后重新运行此脚本")


if __name__ == '__main__':
    main()