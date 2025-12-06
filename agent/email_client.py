"""
邮件客户端模块

提供真实的邮件发送功能
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import os
import time
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# 设置邮件日志
logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """邮件配置"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    sender_email: str = ""
    sender_password: str = ""
    use_tls: bool = True


@dataclass
class EmailMessage:
    """邮件消息"""
    to_email: str
    subject: str
    body: str
    attachments: List[str] = None

    def __post_init__(self):
        if self.attachments is None:
            self.attachments = []


class EmailClient:
    """邮件客户端"""

    def __init__(self, config: EmailConfig = None):
        self.config = config or EmailConfig()
        self.last_sent_time = 0
        self.send_interval = 5  # 发送间隔（秒）

    def send_email(self, message: EmailMessage) -> tuple[bool, str]:
        """发送邮件"""
        try:
            # 检查发送间隔
            current_time = time.time()
            if current_time - self.last_sent_time < self.send_interval:
                wait_time = self.send_interval - (current_time - self.last_sent_time)
                time.sleep(wait_time)

            # 创建邮件消息
            msg = MIMEMultipart()
            msg['From'] = self.config.sender_email
            msg['To'] = message.to_email
            msg['Subject'] = message.subject

            # 添加邮件正文
            msg.attach(MIMEText(message.body, 'html', 'utf-8'))

            # 添加附件
            for attachment_path in message.attachments:
                if os.path.exists(attachment_path):
                    self._add_attachment(msg, attachment_path)
                else:
                    logger.warning(f"附件不存在: {attachment_path}")

            # 发送邮件
            success, result_msg = self._send_smtp_email(msg)

            if success:
                self.last_sent_time = time.time()
                logger.info(f"邮件发送成功: {message.to_email}")
            else:
                logger.error(f"邮件发送失败: {result_msg}")

            return success, result_msg

        except Exception as e:
            error_msg = f"邮件发送异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """添加附件"""
        try:
            with open(file_path, 'rb') as f:
                # 获取文件扩展名
                file_ext = os.path.splitext(file_path)[1].lower()

                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    # 图片附件
                    img = MIMEImage(f.read())
                    img.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
                    msg.attach(img)
                else:
                    # 其他文件类型
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
                    msg.attach(part)

        except Exception as e:
            logger.error(f"添加附件失败 {file_path}: {str(e)}")

    def _send_smtp_email(self, msg: MIMEMultipart) -> tuple[bool, str]:
        """通过SMTP发送邮件"""
        try:
            # 创建SSL上下文
            context = ssl.create_default_context()

            # 连接到SMTP服务器
            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls(context=context)

                # 登录
                server.login(self.config.sender_email, self.config.sender_password)

                # 发送邮件
                text = msg.as_string()
                server.sendmail(self.config.sender_email, msg['To'], text)

            return True, "邮件发送成功"

        except smtplib.SMTPAuthenticationError:
            return False, "SMTP认证失败：用户名或密码错误"
        except smtplib.SMTPRecipientsRefused:
            return False, "收件人被拒绝"
        except smtplib.SMTPServerDisconnected:
            return False, "SMTP服务器连接断开"
        except Exception as e:
            return False, f"SMTP发送失败: {str(e)}"

    def test_connection(self) -> tuple[bool, str]:
        """测试邮件服务器连接"""
        try:
            context = ssl.create_default_context()

            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                if self.config.use_tls:
                    server.starttls(context=context)

                # 测试登录
                server.login(self.config.sender_email, self.config.sender_password)

            return True, "邮件服务器连接成功"

        except Exception as e:
            return False, f"连接测试失败: {str(e)}"


class EmailTemplate:
    """邮件模板"""

    @staticmethod
    def create_news_weather_email(news_list: List[str], weather_info: Dict[str, Any],
                                 screenshots: List[Dict[str, Any]]) -> EmailMessage:
        """创建新闻天气邮件"""
        # 生成邮件正文
        body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .news-section {{ background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
                .weather-section {{ background-color: #e8f4f8; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
                .screenshot-section {{ background-color: #fff0f5; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
                .news-item {{ margin-bottom: 10px; padding: 8px; background-color: white; border-radius: 5px; }}
                .weather-info {{ display: flex; justify-content: space-between; align-items: center; }}
                .timestamp {{ color: #666; font-size: 12px; text-align: right; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; }}
                h3 {{ color: #e67e22; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📰 YOLO-LLM智能代理 - 今日信息报告</h1>
                <p class="timestamp">生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <div class="news-section">
                <h2>📰 今日头条新闻 Top10</h2>
        """

        # 添加新闻列表
        for i, news in enumerate(news_list, 1):
            body += f'<div class="news-item">{i}. {news}</div>'

        body += f"""
            </div>

            <div class="weather-section">
                <h2>🌤️ 今日天气情况</h2>
                <div class="weather-info">
                    <p><strong>日期：</strong>{weather_info.get('date', '未知')}</p>
                    <p><strong>温度：</strong>{weather_info.get('temperature', '未知')}</p>
                    <p><strong>天气：</strong>{weather_info.get('condition', '未知')}</p>
                    <p><strong>湿度：</strong>{weather_info.get('humidity', '未知')}</p>
                    <p><strong>风力：</strong>{weather_info.get('wind', '未知')}</p>
                </div>
            </div>
        """

        # 添加截图信息
        if screenshots:
            body += """
            <div class="screenshot-section">
                <h2>📸 工作流截图记录</h2>
            """
            for i, screenshot in enumerate(screenshots, 1):
                body += f'<div class="news-item">截图 {i}: {screenshot.get("timestamp", "未知时间")} - {screenshot.get("step", "未知步骤")}</div>'

            body += "</div>"

        body += """
            <div class="header">
                <p><em>此邮件由 YOLO-LLM 智能代理自动生成并发送</em></p>
                <p><em>🤖 智能工作流代理 | 安全确认 | 多模态反馈</em></p>
            </div>
        </body>
        </html>
        """

        return EmailMessage(
            to_email="1730495747@qq.com",
            subject=f"YOLO-LLM今日信息报告 - {time.strftime('%Y%m%d')}",
            body=body
        )

    @staticmethod
    def create_workflow_complete_email(workflow_steps: List[str], total_time: float) -> EmailMessage:
        """创建工作流完成邮件"""
        body = f"""
        <html>
        <body>
            <h2>🎉 YOLO-LLM 工作流完成报告</h2>
            <p><strong>完成时间：</strong>{time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>总耗时：</strong>{total_time:.2f} 秒</p>

            <h3>📋 执行步骤：</h3>
            <ul>
        """

        for step in workflow_steps:
            body += f"<li>{step}</li>"

        body += """
            </ul>

            <p><em>🤖 由 YOLO-LLM 智能代理执行</em></p>
        </body>
        </html>
        """

        return EmailMessage(
            to_email="1730495747@qq.com",
            subject=f"YOLO-LLM工作流完成 - {time.strftime('%Y%m%d')}",
            body=body
        )


# 全局邮件客户端实例
_email_client: Optional[EmailClient] = None


def get_email_client(config: EmailConfig = None) -> EmailClient:
    """获取全局邮件客户端实例"""
    global _email_client
    if _email_client is None:
        _email_client = EmailClient(config)
    return _email_client


def send_email_quick(message: EmailMessage) -> tuple[bool, str]:
    """快速发送邮件（便捷函数）"""
    client = get_email_client()
    return client.send_email(message)


if __name__ == '__main__':
    # 测试邮件客户端
    print("测试邮件客户端...")

    # 配置邮件（需要用户配置实际的邮件服务器信息）
    email_config = EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email="your_email@gmail.com",  # 需要配置
        sender_password="your_password",      # 需要配置
        use_tls=True
    )

    client = EmailClient(email_config)

    # 测试连接
    success, msg = client.test_connection()
    print(f"连接测试: {success} - {msg}")

    if success:
        # 创建测试邮件
        test_email = EmailMessage(
            to_email="1730495747@qq.com",
            subject="YOLO-LLM 测试邮件",
            body="<h1>这是一封测试邮件</h1><p>YOLO-LLM智能代理系统测试</p>"
        )

        # 发送邮件
        success, msg = client.send_email(test_email)
        print(f"邮件发送: {success} - {msg}")
    else:
        print("邮件服务器连接失败，请检查配置")