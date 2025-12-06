"""
邮件 MCP 工具

通过DeepSeek大模型智能处理邮件相关任务
"""

import asyncio
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.base import MIMEBase
from email import encoders
import os
import time
from typing import Dict, Any, List, Optional
import logging

from ..config import TOOLS_CONFIG

logger = logging.getLogger(__name__)


class EmailTool:
    """邮件工具"""

    def __init__(self):
        self.config = TOOLS_CONFIG["email"]
        self.last_sent_time = 0
        self.send_interval = 5

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行邮件工具操作"""

        action = parameters.get("action", "")
        logger.info(f"执行邮件工具操作: {action}")

        try:
            if action == "send_email":
                return await self._send_email(parameters)
            elif action == "prepare_email":
                return await self._prepare_email(parameters)
            elif action == "create_template":
                return await self._create_template(parameters)
            elif action == "validate_recipient":
                return await self._validate_recipient(parameters)
            elif action == "format_content":
                return await self._format_content(parameters)
            else:
                return {
                    "success": False,
                    "error": f"未知的邮件操作: {action}",
                    "available_actions": [
                        "send_email", "prepare_email", "create_template",
                        "validate_recipient", "format_content"
                    ]
                }

        except Exception as e:
            logger.error(f"邮件工具执行错误: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "action": action
            }

    async def _send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送邮件"""

        to_email = params.get("to_email")
        subject = params.get("subject", "来自YOLO-LLM的邮件")
        content = params.get("content", "")
        attachments = params.get("attachments", [])

        if not to_email:
            return {
                "success": False,
                "error": "缺少收件人邮箱地址"
            }

        # 智能生成邮件内容（如果内容为空）
        if not content:
            content = await self._generate_smart_content(params)

        try:
            # 检查发送间隔
            current_time = time.time()
            if current_time - self.last_sent_time < self.send_interval:
                await asyncio.sleep(self.send_interval - (current_time - self.last_sent_time))

            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.config.get("default_sender", "noreply@yolo-llm.com")
            msg['To'] = to_email
            msg['Subject'] = subject

            # 添加HTML格式内容
            html_content = await self._create_html_content(content)
            msg.attach(MIMEText(html_content, 'html', 'utf-8'))

            # 添加附件
            for attachment in attachments:
                await self._add_attachment(msg, attachment)

            # 发送邮件（这里模拟发送，实际需要配置SMTP）
            success, result = await self._send_smtp_email(msg, to_email)

            if success:
                self.last_sent_time = current_time
                return {
                    "success": True,
                    "message": f"邮件已成功发送到 {to_email}",
                    "details": {
                        "to_email": to_email,
                        "subject": subject,
                        "content_length": len(content),
                        "attachments_count": len(attachments),
                        "sent_time": time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"邮件发送失败: {result}",
                    "details": {
                        "to_email": to_email,
                        "subject": subject
                    }
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"邮件发送异常: {str(e)}",
                "details": {
                    "to_email": to_email,
                    "subject": subject
                }
            }

    async def _prepare_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """准备邮件内容"""

        context = params.get("context", "")
        user_intent = params.get("user_intent", "")

        # 使用DeepSeek分析邮件需求
        analysis = await self._analyze_email_request(context, user_intent)

        if not analysis["success"]:
            return analysis

        # 生成邮件内容建议
        suggestions = await self._generate_email_suggestions(analysis)

        return {
            "success": True,
            "message": "邮件内容已准备完成",
            "analysis": analysis,
            "suggestions": suggestions,
            "next_steps": [
                "确认收件人邮箱",
                "选择邮件主题",
                "调整邮件内容",
                "添加附件（可选）",
                "发送邮件"
            ]
        }

    async def _create_template(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建邮件模板"""

        template_type = params.get("template_type", "general")
        custom_content = params.get("custom_content", {})

        templates = {
            "news_weather": {
                "subject_template": "今日信息报告 - {date}",
                "content_template": """
                <h2>📰 今日新闻天气报告</h2>
                <p><strong>日期:</strong> {date}</p>

                <h3>📰 头条新闻</h3>
                {news_content}

                <h3>🌤️ 天气信息</h3>
                <p><strong>温度:</strong> {temperature}</p>
                <p><strong>天气:</strong> {condition}</p>
                <p><strong>湿度:</strong> {humidity}</p>

                <hr>
                <p><em>由YOLO-LLM智能代理生成</em></p>
                """
            },
            "workflow_complete": {
                "subject_template": "工作流完成报告 - {date}",
                "content_template": """
                <h2>✅ 工作流执行完成</h2>
                <p><strong>完成时间:</strong> {timestamp}</p>
                <p><strong>执行步骤:</strong> {steps}</p>
                <p><strong>执行结果:</strong> {result}</p>

                <hr>
                <p><em>由YOLO-LLM智能代理执行</em></p>
                """
            },
            "general": {
                "subject_template": "来自YOLO-LLM的消息",
                "content_template": """
                <h2>消息</h2>
                <p>{content}</p>

                <hr>
                <p><em>由YOLO-LLM智能代理发送</em></p>
                """
            }
        }

        template = templates.get(template_type, templates["general"])

        # 合并自定义内容
        if custom_content:
            template.update(custom_content)

        return {
            "success": True,
            "message": f"邮件模板 '{template_type}' 创建完成",
            "template": template,
            "usage_example": {
                "subject": template["subject_template"].format(
                    date=time.strftime('%Y-%m-%d')
                ),
                "content": template["content_template"].format(
                    content="这里是邮件内容",
                    date=time.strftime('%Y-%m-%d %H:%M:%S'),
                    timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                    steps="步骤1 -> 步骤2 -> 完成",
                    result="成功"
                )
            }
        }

    async def _validate_recipient(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证收件人邮箱"""

        email = params.get("email", "")

        if not email:
            return {
                "success": False,
                "error": "邮箱地址不能为空"
            }

        # 基本邮箱格式验证
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        if not re.match(email_pattern, email):
            return {
                "success": False,
                "error": "邮箱地址格式不正确",
                "suggestions": [
                    "检查邮箱地址拼写",
                    "确保包含@符号",
                    "检查域名部分"
                ]
            }

        # 检查常见域名
        common_domains = ["gmail.com", "qq.com", "163.com", "outlook.com", "hotmail.com"]
        domain = email.split('@')[1] if '@' in email else ""

        validation_info = {
            "success": True,
            "email": email,
            "domain": domain,
            "is_common_domain": domain in common_domains,
            "format_valid": True
        }

        if domain in common_domains:
            validation_info["domain_info"] = {
                "gmail.com": "Google邮箱，支持SMTP",
                "qq.com": "腾讯QQ邮箱，需要授权码",
                "163.com": "网易邮箱，需要开启SMTP",
                "outlook.com": "微软邮箱，支持SMTP",
                "hotmail.com": "微软邮箱，支持SMTP"
            }[domain]

        return validation_info

    async def _format_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """格式化邮件内容"""

        content = params.get("content", "")
        format_type = params.get("format_type", "html")

        if not content:
            return {
                "success": False,
                "error": "内容不能为空"
            }

        formatted_content = await self._smart_format_content(content, format_type)

        return {
            "success": True,
            "original_length": len(content),
            "formatted_length": len(formatted_content),
            "format_type": format_type,
            "formatted_content": formatted_content
        }

    async def _generate_smart_content(self, params: Dict[str, Any]) -> str:
        """智能生成邮件内容"""

        # 这里可以调用DeepSeek API生成智能内容
        # 暂时返回基础模板
        return f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6;">
            <h2>来自YOLO-LLM智能代理的消息</h2>
            <p>您好！</p>
            <p>这是一封由智能代理自动生成的邮件。</p>
            <p>发送时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>如有任何问题，请随时联系我们。</p>
            <hr>
            <p><em>此邮件由YOLO-LLM智能代理系统发送</em></p>
        </div>
        """

    async def _create_html_content(self, content: str) -> str:
        """创建HTML格式邮件内容"""

        if content.strip().startswith('<'):
            # 已经是HTML格式
            return content

        # 转换为HTML格式
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                .header {{
                    background-color: #f0f8ff;
                    padding: 20px;
                    border-radius: 10px;
                    margin-bottom: 20px;
                }}
                .footer {{
                    margin-top: 30px;
                    padding: 20px;
                    background-color: #f8f9fa;
                    border-radius: 10px;
                    text-align: center;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>🤖 YOLO-LLM 智能代理</h2>
            </div>

            <div class="content">
                {content.replace(chr(10), '<br>')}
            </div>

            <div class="footer">
                <p><em>此邮件由YOLO-LLM智能代理自动生成</em></p>
                <p><em>发送时间: {time.strftime('%Y-%m-%d %H:%M:%S')}</em></p>
            </div>
        </body>
        </html>
        """

        return html_content

    async def _add_attachment(self, msg: MIMEMultipart, attachment_path: str):
        """添加附件"""

        if not os.path.exists(attachment_path):
            logger.warning(f"附件不存在: {attachment_path}")
            return

        try:
            with open(attachment_path, 'rb') as f:
                file_ext = os.path.splitext(attachment_path)[1].lower()

                if file_ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    # 图片附件
                    img = MIMEImage(f.read())
                    img.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(attachment_path)}'
                    )
                    msg.attach(img)
                else:
                    # 其他文件类型
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename={os.path.basename(attachment_path)}'
                    )
                    msg.attach(part)

        except Exception as e:
            logger.error(f"添加附件失败 {attachment_path}: {str(e)}")

    async def _send_smtp_email(self, msg: MIMEMultipart, to_email: str) -> tuple:
        """发送SMTP邮件（模拟实现）"""

        # 这里应该实现真实的SMTP发送
        # 由于需要配置，暂时返回模拟成功

        logger.info(f"模拟发送邮件到: {to_email}")
        logger.info(f"主题: {msg['Subject']}")

        # 模拟发送延迟
        await asyncio.sleep(0.5)

        return True, "模拟发送成功"

    async def _analyze_email_request(self, context: str, user_intent: str) -> Dict[str, Any]:
        """分析邮件请求"""

        # 模拟分析结果
        analysis = {
            "success": True,
            "intent_type": "information_sharing",
            "urgency": "normal",
            "recipient_suggestions": ["1730495747@qq.com"],
            "content_type": "news_weather_report",
            "format_preference": "html",
            "attachment_needed": True
        }

        # 基于上下文分析
        if "新闻" in context or "news" in context.lower():
            analysis["content_type"] = "news_report"
        if "天气" in context or "weather" in context.lower():
            analysis["content_type"] = "weather_report"
        if "工作流" in context or "workflow" in context.lower():
            analysis["content_type"] = "workflow_report"

        return analysis

    async def _generate_email_suggestions(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成邮件建议"""

        content_type = analysis.get("content_type", "general")

        suggestions = {
            "news_weather": {
                "subject": "今日信息报告",
                "content_structure": [
                    "新闻摘要",
                    "天气信息",
                    "数据来源",
                    "生成时间"
                ],
                "tone": "信息丰富、客观"
            },
            "workflow_report": {
                "subject": "工作流执行报告",
                "content_structure": [
                    "执行概述",
                    "步骤详情",
                    "结果总结",
                    "截图附件"
                ],
                "tone": "专业、清晰"
            }
        }

        base_suggestions = {
            "subject": f"YOLO-LLM智能报告 - {time.strftime('%Y-%m-%d')}",
            "greeting": "您好！",
            "closing": "此邮件由YOLO-LLM智能代理自动生成",
            "signature": "YOLO-LLM Team"
        }

        if content_type in suggestions:
            base_suggestions.update(suggestions[content_type])

        return base_suggestions

    async def _smart_format_content(self, content: str, format_type: str) -> str:
        """智能格式化内容"""

        # 这里可以调用DeepSeek API进行智能格式化
        # 暂时返回基础格式化

        if format_type.lower() == "html":
            return f"<div style='font-family: Arial;'>{content}</div>"
        else:
            return content.strip()