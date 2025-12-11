#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件工具模块
提供邮件发送和管理功能
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
from .base_tool import BaseTool, ToolResponse, ToolError

class EmailTool(BaseTool):
    """邮件工具类"""

    def __init__(self):
        super().__init__(
            name="email",
            description="发送和管理邮件",
            version="2.0.0"
        )

        # 邮件API配置
        self.brevo_api_key = os.getenv("BREVO_API_KEY", "")
        self.sender_email = os.getenv("SENDER_EMAIL", "by2022jy@gmail.com")
        self.sender_name = "YOLO-LLM 系统"

    async def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """执行邮件工具操作"""
        try:
            if action == "send_email":
                return await self._send_email(parameters)
            elif action == "send_bulk_email":
                return await self._send_bulk_email(parameters)
            elif action == "validate_email":
                return await self._validate_email(parameters)
            elif action == "get_email_status":
                return await self._get_email_status(parameters)
            elif action == "create_email_template":
                return await self._create_email_template(parameters)
            else:
                raise ToolError(f"不支持的操作: {action}", self.name)

        except Exception as e:
            self.logger.error(f"邮件工具执行失败: {action} - {str(e)}")
            raise ToolError(f"邮件工具执行异常: {str(e)}", self.name)

    async def _send_email(self, params: Dict[str, Any]) -> ToolResponse:
        """发送单封邮件"""
        to_email = params.get("to")
        subject = params.get("subject")
        content = params.get("content")
        content_type = params.get("content_type", "html")  # html 或 text
        cc = params.get("cc", [])
        bcc = params.get("bcc", [])
        attachments = params.get("attachments", [])

        # 验证必填参数
        if not all([to_email, subject, content]):
            raise ToolError("邮件参数不完整：需要to、subject、content", self.name)

        try:
            if self.brevo_api_key:
                email_id = await self._send_real_email(
                    to_email=to_email,
                    subject=subject,
                    content=content,
                    content_type=content_type,
                    cc=cc,
                    bcc=bcc,
                    attachments=attachments
                )
                source = "brevo_api"
            else:
                email_id = await self._send_mock_email(
                    to_email=to_email,
                    subject=subject,
                    content=content
                )
                source = "mock"

            return ToolResponse(
                success=True,
                data={
                    "email_id": email_id,
                    "to": to_email,
                    "subject": subject,
                    "cc": cc,
                    "bcc": bcc,
                    "content_type": content_type,
                    "attachment_count": len(attachments) if attachments else 0,
                    "source": source,
                    "sent_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"发送邮件失败: {str(e)}")
            raise ToolError(f"发送邮件失败: {str(e)}", self.name)

    async def _send_bulk_email(self, params: Dict[str, Any]) -> ToolResponse:
        """批量发送邮件"""
        to_emails = params.get("to_emails", [])
        subject = params.get("subject")
        content = params.get("content")
        delay_between_emails = params.get("delay_between_emails", 1)  # 秒

        if not to_emails or not subject or not content:
            raise ToolError("批量邮件参数不完整", self.name)

        try:
            results = []
            success_count = 0
            error_count = 0

            for i, email in enumerate(to_emails):
                try:
                    result = await self._send_email({
                        "to": email,
                        "subject": subject,
                        "content": content,
                        "content_type": params.get("content_type", "html")
                    })

                    if result.success:
                        results.append({
                            "email": email,
                            "email_id": result.data["email_id"],
                            "status": "success"
                        })
                        success_count += 1
                    else:
                        results.append({
                            "email": email,
                            "status": "failed",
                            "error": result.error
                        })
                        error_count += 1

                    # 延迟发送，避免触发限制
                    if delay_between_emails > 0 and i < len(to_emails) - 1:
                        await asyncio.sleep(delay_between_emails)

                except Exception as e:
                    results.append({
                        "email": email,
                        "status": "failed",
                        "error": str(e)
                    })
                    error_count += 1

            return ToolResponse(
                success=True,
                data={
                    "total_emails": len(to_emails),
                    "success_count": success_count,
                    "error_count": error_count,
                    "results": results,
                    "bulk_send_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"批量发送邮件失败: {str(e)}")
            raise ToolError(f"批量发送邮件失败: {str(e)}", self.name)

    async def _validate_email(self, params: Dict[str, Any]) -> ToolResponse:
        """验证邮箱地址"""
        email = params.get("email")

        if not email:
            raise ToolError("邮箱地址不能为空", self.name)

        try:
            # 基础格式验证
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            is_valid_format = bool(re.match(email_pattern, email))

            # 可以添加更多验证逻辑，如MX记录检查等
            validation_result = {
                "email": email,
                "is_valid_format": is_valid_format,
                "domain": email.split('@')[1] if '@' in email else None,
                "validation_time": datetime.now().isoformat()
            }

            return ToolResponse(
                success=True,
                data=validation_result
            )

        except Exception as e:
            self.logger.error(f"邮箱验证失败: {str(e)}")
            raise ToolError(f"邮箱验证失败: {str(e)}", self.name)

    async def _get_email_status(self, params: Dict[str, Any]) -> ToolResponse:
        """获取邮件状态"""
        email_id = params.get("email_id")

        if not email_id:
            raise ToolError("邮件ID不能为空", self.name)

        try:
            # 这里应该调用实际API查询邮件状态
            # 目前返回模拟状态
            from datetime import timedelta
            status_info = {
                "email_id": email_id,
                "status": "delivered",  # sent, delivered, opened, clicked, bounced
                "sent_time": (datetime.now() - timedelta(hours=1)).isoformat(),
                "delivered_time": (datetime.now() - timedelta(minutes=50)).isoformat(),
                "opened": True,
                "clicked": False,
                "bounced": False
            }

            return ToolResponse(
                success=True,
                data=status_info
            )

        except Exception as e:
            self.logger.error(f"获取邮件状态失败: {str(e)}")
            raise ToolError(f"获取邮件状态失败: {str(e)}", self.name)

    async def _create_email_template(self, params: Dict[str, Any]) -> ToolResponse:
        """创建邮件模板"""
        template_name = params.get("template_name")
        subject = params.get("subject")
        content = params.get("content")
        variables = params.get("variables", {})

        if not all([template_name, subject, content]):
            raise ToolError("邮件模板参数不完整", self.name)

        try:
            template_info = {
                "template_id": f"template_{hash(template_name)}",
                "template_name": template_name,
                "subject": subject,
                "content": content,
                "variables": variables,
                "created_time": datetime.now().isoformat()
            }

            return ToolResponse(
                success=True,
                data=template_info
            )

        except Exception as e:
            self.logger.error(f"创建邮件模板失败: {str(e)}")
            raise ToolError(f"创建邮件模板失败: {str(e)}", self.name)

    async def _send_real_email(self, to_email: str, subject: str, content: str,
                              content_type: str = "html", cc: List[str] = None,
                              bcc: List[str] = None, attachments: List[Dict] = None) -> str:
        """使用Brevo API发送真实邮件"""
        try:
            from brevo import ApiClient
            from brevo.api import TransactionalEmailsApi
            from brevo.models import SendSmtpEmail

            api_instance = TransactionalEmailsApi(ApiClient())
            api_instance.api_client.configuration.api_key['api-key'] = self.brevo_api_key

            # 构建邮件对象
            sender = {"name": self.sender_name, "email": self.sender_email}
            to = [{"email": to_email}]

            # 添加抄送和密送
            if cc:
                to.extend([{"email": email} for email in cc])
            if bcc:
                to.extend([{"email": email} for email in bcc])

            # 构建邮件内容
            email_data = {
                "sender": sender,
                "to": to[:1],  # 主收件人
                "subject": subject
            }

            if content_type == "html":
                email_data["html_content"] = content
                email_data["text_content"] = self._html_to_text(content)
            else:
                email_data["text_content"] = content

            # 添加抄送密送
            if cc:
                email_data["cc"] = [{"email": email} for email in cc]
            if bcc:
                email_data["bcc"] = [{"email": email} for email in bcc]

            # 添加附件
            if attachments:
                email_data["attachment"] = attachments

            send_smtp_email = SendSmtpEmail(**email_data)

            # 发送邮件
            result = api_instance.send_transac_email(send_smtp_email)
            return str(result.message_id)

        except ImportError:
            self.logger.warning("Brevo库未安装，使用模拟发送")
            return await self._send_mock_email(to_email, subject, content)
        except Exception as e:
            self.logger.error(f"发送真实邮件失败: {str(e)}")
            raise e

    async def _send_mock_email(self, to_email: str, subject: str, content: str) -> str:
        """模拟发送邮件"""
        email_id = f"mock_email_{hash(content)}_{datetime.now().timestamp()}"

        self.logger.info(f"模拟发送邮件到 {to_email}")
        self.logger.info(f"主题: {subject}")
        self.logger.info(f"内容长度: {len(content)} 字符")
        self.logger.info(f"邮件ID: {email_id}")

        return email_id

    def _html_to_text(self, html_content: str) -> str:
        """将HTML内容转换为纯文本"""
        # 简单的HTML标签移除
        import re
        text = re.sub(r'<[^>]+>', '', html_content)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        return text.strip()

    def get_capabilities(self) -> List[str]:
        """获取工具能力列表"""
        return [
            "send_email",
            "send_bulk_email",
            "validate_email",
            "get_email_status",
            "create_email_template"
        ]

    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数模式"""
        return {
            "actions": {
                "send_email": {
                    "description": "发送单封邮件",
                    "parameters": {
                        "to": {"type": "string", "required": True, "description": "收件人邮箱"},
                        "subject": {"type": "string", "required": True, "description": "邮件主题"},
                        "content": {"type": "string", "required": True, "description": "邮件内容"},
                        "content_type": {"type": "string", "default": "html", "description": "内容类型(html/text)"},
                        "cc": {"type": "array", "description": "抄送邮箱列表"},
                        "bcc": {"type": "array", "description": "密送邮箱列表"},
                        "attachments": {"type": "array", "description": "附件列表"}
                    }
                },
                "send_bulk_email": {
                    "description": "批量发送邮件",
                    "parameters": {
                        "to_emails": {"type": "array", "required": True, "description": "收件人邮箱列表"},
                        "subject": {"type": "string", "required": True, "description": "邮件主题"},
                        "content": {"type": "string", "required": True, "description": "邮件内容"},
                        "content_type": {"type": "string", "default": "html", "description": "内容类型"},
                        "delay_between_emails": {"type": "integer", "default": 1, "description": "邮件发送间隔(秒)"}
                    }
                },
                "validate_email": {
                    "description": "验证邮箱地址",
                    "parameters": {
                        "email": {"type": "string", "required": True, "description": "待验证的邮箱地址"}
                    }
                },
                "get_email_status": {
                    "description": "获取邮件状态",
                    "parameters": {
                        "email_id": {"type": "string", "required": True, "description": "邮件ID"}
                    }
                },
                "create_email_template": {
                    "description": "创建邮件模板",
                    "parameters": {
                        "template_name": {"type": "string", "required": True, "description": "模板名称"},
                        "subject": {"type": "string", "required": True, "description": "邮件主题"},
                        "content": {"type": "string", "required": True, "description": "邮件内容"},
                        "variables": {"type": "object", "description": "模板变量"}
                    }
                }
            }
        }

    async def _perform_health_check(self) -> bool:
        """执行健康检查"""
        try:
            # 检查API密钥是否配置
            if not self.brevo_api_key:
                self.logger.warning("Brevo API密钥未配置，将使用模拟发送")

            # 测试基本功能
            test_result = await self._validate_email({"email": "test@example.com"})
            return test_result.success
        except Exception as e:
            self.logger.error(f"邮件工具健康检查失败: {str(e)}")
            return False

# 创建全局邮件工具实例
email_tool = EmailTool()