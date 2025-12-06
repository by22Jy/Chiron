"""
MessagingTool - 通信工具

提供邮件、消息、通知等通信功能
支持多种发送方式和模板管理
"""

import smtplib
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime

try:
    from .base_tool import BaseTool, ToolResult
except ImportError:
    from base_tool import BaseTool, ToolResult


class MessagingTool(BaseTool):
    """通信工具"""

    def __init__(self):
        super().__init__()
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        # 默认配置
        default_config = {
            "smtp": {
                "server": "smtp.gmail.com",
                "port": 587,
                "username": "",
                "password": "",
                "use_tls": True
            },
            "webhook": {
                "slack_webhook": "",
                "discord_webhook": "",
                "teams_webhook": ""
            },
            "templates": {
                "default": {
                    "subject": "来自YOLO-LLM Agent的消息",
                    "greeting": "您好，",
                    "signature": "\n\n此消息由YOLO-LLM智能助手发送"
                }
            }
        }

        # 尝试从配置文件加载
        try:
            config_path = os.path.join(os.path.dirname(__file__), "..", "config", "messaging.json")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置
                    default_config.update(user_config)
        except Exception as e:
            self.logger.warning(f"加载邮件配置失败，使用默认配置: {e}")

        return default_config

    @property
    def name(self) -> str:
        return "messaging"

    @property
    def description(self) -> str:
        return "通信工具：发送邮件、即时消息、通知等"

    @property
    def supported_actions(self) -> List[str]:
        return [
            "send_email",
            "send_slack_message",
            "send_discord_message",
            "send_notification",
            "create_email_draft",
            "save_email_template",
            "list_templates"
        ]

    @property
    def required_permissions(self) -> List[str]:
        return ["network_access", "notification"]

    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """验证参数有效性"""
        if action in ["send_email"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["to", "subject", "content"],
                optional_params=["cc", "bcc", "attachments", "template", "priority"]
            )

        elif action in ["send_slack_message", "send_discord_message"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["message"],
                optional_params=["channel", "username", "webhook_url"]
            )

        elif action in ["send_notification"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["title", "message"],
                optional_params=["type", "urgency", "actions"]
            )

        elif action in ["create_email_draft"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["to", "subject", "content"],
                optional_params=["cc", "bcc", "attachments"]
            )

        elif action in ["save_email_template"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["template_name", "subject", "content"],
                optional_params=["description"]
            )

        elif action in ["list_templates"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=[],
                optional_params=[]
            )

        else:
            self.logger.error(f"不支持的动作: {action}")
            return False

    def execute_action(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """执行具体动作"""
        try:
            if action == "send_email":
                return self._send_email(parameters, context)
            elif action == "send_slack_message":
                return self._send_slack_message(parameters, context)
            elif action == "send_discord_message":
                return self._send_discord_message(parameters, context)
            elif action == "send_notification":
                return self._send_notification(parameters, context)
            elif action == "create_email_draft":
                return self._create_email_draft(parameters, context)
            elif action == "save_email_template":
                return self._save_email_template(parameters, context)
            elif action == "list_templates":
                return self._list_templates(parameters, context)
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的通信动作: {action}"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"执行通信动作 {action} 失败: {str(e)}"
            )

    def _send_email(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """发送邮件"""
        to_addr = parameters["to"]
        subject = parameters["subject"]
        content = parameters["content"]
        cc = parameters.get("cc", [])
        bcc = parameters.get("bcc", [])
        attachments = parameters.get("attachments", [])
        template = parameters.get("template", "default")
        priority = parameters.get("priority", "normal")

        try:
            # 使用模板格式化内容
            if template in self.config.get("templates", {}):
                template_data = self.config["templates"][template]
                formatted_content = f"{template_data.get('greeting', '')}\n\n{content}{template_data.get('signature', '')}"
                formatted_subject = f"{template_data.get('subject_prefix', '')}{subject}"
            else:
                formatted_content = content
                formatted_subject = subject

            # 检查SMTP配置
            smtp_config = self.config.get("smtp", {})
            if not smtp_config.get("username") or not smtp_config.get("password"):
                # Mock模式 - 模拟发送邮件
                self.logger.info(f"[MOCK] 发送邮件到: {to_addr}")
                self.logger.info(f"[MOCK] 主题: {formatted_subject}")
                self.logger.info(f"[MOCK] 内容: {formatted_content[:100]}...")

                return ToolResult(
                    success=True,
                    message=f"邮件已模拟发送到 {to_addr}",
                    data={
                        "to": to_addr,
                        "subject": formatted_subject,
                        "priority": priority,
                        "mode": "mock"
                    }
                )

            # 真实发送邮件
            msg = MIMEMultipart()
            msg['From'] = smtp_config["username"]
            msg['To'] = ', '.join(to_addr) if isinstance(to_addr, list) else to_addr
            msg['Subject'] = formatted_subject
            msg['X-Priority'] = self._get_priority_value(priority)

            # 添加收件人
            if cc:
                msg['Cc'] = ', '.join(cc) if isinstance(cc, list) else cc
            if bcc:
                msg['Bcc'] = ', '.join(bcc) if isinstance(bcc, list) else bcc

            # 添加正文
            msg.attach(MIMEText(formatted_content, 'plain', 'utf-8'))

            # 添加附件
            for attachment in attachments:
                if os.path.exists(attachment):
                    self._add_attachment(msg, attachment)

            # 发送邮件
            server = smtplib.SMTP(smtp_config["server"], smtp_config["port"])
            if smtp_config.get("use_tls", True):
                server.starttls()

            server.login(smtp_config["username"], smtp_config["password"])

            all_recipients = to_addr + cc + bcc
            if isinstance(all_recipients, list):
                all_recipients = ', '.join(all_recipients)

            text = msg.as_string()
            server.sendmail(smtp_config["username"], all_recipients.split(', '), text)
            server.quit()

            return ToolResult(
                success=True,
                message=f"邮件成功发送到 {to_addr}",
                data={
                    "to": to_addr,
                    "subject": formatted_subject,
                    "priority": priority,
                    "mode": "smtp"
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"发送邮件失败: {str(e)}"
            )

    def _send_slack_message(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """发送Slack消息"""
        message = parameters["message"]
        channel = parameters.get("channel", "#general")
        username = parameters.get("username", "YOLO-LLM Agent")
        webhook_url = parameters.get("webhook_url") or self.config["webhook"].get("slack_webhook")

        try:
            if not webhook_url:
                # Mock模式
                self.logger.info(f"[MOCK] 发送Slack消息到 {channel}: {message}")
                return ToolResult(
                    success=True,
                    message=f"Slack消息已模拟发送到 {channel}",
                    data={
                        "channel": channel,
                        "message": message,
                        "mode": "mock"
                    }
                )

            # 真实发送
            payload = {
                "text": message,
                "channel": channel,
                "username": username
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            return ToolResult(
                success=True,
                message=f"Slack消息成功发送到 {channel}",
                data={
                    "channel": channel,
                    "message": message,
                    "mode": "webhook"
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"发送Slack消息失败: {str(e)}"
            )

    def _send_discord_message(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """发送Discord消息"""
        message = parameters["message"]
        webhook_url = parameters.get("webhook_url") or self.config["webhook"].get("discord_webhook")

        try:
            if not webhook_url:
                # Mock模式
                self.logger.info(f"[MOCK] 发送Discord消息: {message}")
                return ToolResult(
                    success=True,
                    message="Discord消息已模拟发送",
                    data={
                        "message": message,
                        "mode": "mock"
                    }
                )

            # 真实发送
            payload = {
                "content": message
            }

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            return ToolResult(
                success=True,
                message="Discord消息成功发送",
                data={
                    "message": message,
                    "mode": "webhook"
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"发送Discord消息失败: {str(e)}"
            )

    def _send_notification(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """发送系统通知"""
        title = parameters["title"]
        message = parameters["message"]
        notification_type = parameters.get("type", "info")
        urgency = parameters.get("urgency", "normal")
        actions = parameters.get("actions", [])

        try:
            # 记录通知
            self.logger.info(f"发送通知: {title} - {message}")

            # 这里可以集成不同的通知系统
            # Windows: 使用toast notifications
            # macOS: 使用osascript
            # Linux: 使用notify-send

            notification_data = {
                "title": title,
                "message": message,
                "type": notification_type,
                "urgency": urgency,
                "timestamp": datetime.now().isoformat(),
                "actions": actions
            }

            return ToolResult(
                success=True,
                message=f"通知已发送: {title}",
                data=notification_data
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"发送通知失败: {str(e)}"
            )

    def _create_email_draft(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """创建邮件草稿"""
        to_addr = parameters["to"]
        subject = parameters["subject"]
        content = parameters["content"]
        cc = parameters.get("cc", [])
        bcc = parameters.get("bcc", [])
        attachments = parameters.get("attachments", [])

        try:
            # 创建草稿数据
            draft_data = {
                "to": to_addr,
                "subject": subject,
                "content": content,
                "cc": cc,
                "bcc": bcc,
                "attachments": attachments,
                "created_at": datetime.now().isoformat()
            }

            # 保存草稿到文件
            drafts_dir = os.path.join(os.path.dirname(__file__), "..", "data", "drafts")
            os.makedirs(drafts_dir, exist_ok=True)

            draft_file = os.path.join(drafts_dir, f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(draft_file, 'w', encoding='utf-8') as f:
                json.dump(draft_data, f, ensure_ascii=False, indent=2)

            return ToolResult(
                success=True,
                message=f"邮件草稿已创建: {draft_file}",
                data=draft_data
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"创建邮件草稿失败: {str(e)}"
            )

    def _save_email_template(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """保存邮件模板"""
        template_name = parameters["template_name"]
        subject = parameters["subject"]
        content = parameters["content"]
        description = parameters.get("description", "")

        try:
            template_data = {
                "name": template_name,
                "description": description,
                "subject": subject,
                "content": content,
                "created_at": datetime.now().isoformat()
            }

            # 保存模板到配置
            if "templates" not in self.config:
                self.config["templates"] = {}

            self.config["templates"][template_name] = {
                "subject_prefix": "",
                "greeting": "",
                "signature": "",
                "description": description,
                "subject_template": subject,
                "content_template": content
            }

            # 保存到文件
            config_file = os.path.join(os.path.dirname(__file__), "..", "config", "messaging.json")
            os.makedirs(os.path.dirname(config_file), exist_ok=True)

            # 只保存模板部分
            templates_data = {"templates": self.config["templates"]}
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, ensure_ascii=False, indent=2)

            return ToolResult(
                success=True,
                message=f"邮件模板已保存: {template_name}",
                data=template_data
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"保存邮件模板失败: {str(e)}"
            )

    def _list_templates(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """列出所有邮件模板"""
        try:
            templates = self.config.get("templates", {})

            template_list = []
            for name, template_data in templates.items():
                template_list.append({
                    "name": name,
                    "description": template_data.get("description", ""),
                    "subject_template": template_data.get("subject_template", ""),
                    "content_preview": template_data.get("content_template", "")[:100] + "..."
                })

            return ToolResult(
                success=True,
                message=f"找到 {len(template_list)} 个邮件模板",
                data={
                    "templates": template_list,
                    "count": len(template_list)
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"列出邮件模板失败: {str(e)}"
            )

    def _get_priority_value(self, priority: str) -> str:
        """获取邮件优先级值"""
        priority_map = {
            "low": "5",
            "normal": "3",
            "high": "1",
            "urgent": "1"
        }
        return priority_map.get(priority, "3")

    def _add_attachment(self, msg: MIMEMultipart, file_path: str):
        """添加邮件附件"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}'
            )

            msg.attach(part)
        except Exception as e:
            self.logger.warning(f"添加附件失败 {file_path}: {e}")