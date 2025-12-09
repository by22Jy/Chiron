#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社交媒体工具集
支持微信、QQ等平台的群发和自动化功能
"""

import os
import time
import json
import requests
import pyautogui
import pyperclip
import win32gui
import win32con
import win32api
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import threading
import queue
from enum import Enum
import tempfile
import shutil

class SocialPlatform(Enum):
    """社交媒体平台枚举"""
    WECHAT = "wechat"
    QQ = "qq"
    DINGTALK = "dingtalk"
    EMAIL = "email"

class MessageStatus(Enum):
    """消息状态枚举"""
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class SocialContact:
    """社交联系人数据结构"""
    name: str
    platform: SocialPlatform
    identifier: str  # 微信号、QQ号、手机号等
    group_name: Optional[str] = None
    nickname: Optional[str] = None
    avatar_path: Optional[str] = None
    notes: Optional[str] = None

@dataclass
class SocialMessage:
    """社交消息数据结构"""
    id: str
    platform: SocialPlatform
    recipient: SocialContact
    content: str
    message_type: str = "text"  # text, image, file, voice
    attachments: List[str] = None
    scheduled_time: Optional[datetime] = None
    status: MessageStatus = MessageStatus.PENDING
    created_at: datetime = None
    sent_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.attachments is None:
            self.attachments = []

@dataclass
class MassMessage:
    """群发消息数据结构"""
    id: str
    platform: SocialPlatform
    recipients: List[SocialContact]
    content: str
    message_type: str = "text"
    attachments: List[str] = None
    send_interval: float = 2.0  # 发送间隔（秒）
    batch_size: int = 10  # 每批发送数量
    status: MessageStatus = MessageStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    sent_count: int = 0
    failed_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.attachments is None:
            self.attachments = []

class SocialMediaManager:
    """社交媒体管理器"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.contacts: Dict[str, SocialContact] = {}
        self.messages: List[SocialMessage] = []
        self.mass_messages: List[MassMessage] = []
        self.message_queue = queue.Queue()
        self.sending_active = False
        self.sending_thread: Optional[threading.Thread] = None

        # 加载联系人和历史消息
        self._load_contacts()
        self._load_message_history()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "auto_save_contacts": True,
            "message_retention_days": 30,
            "max_send_rate": 30,  # 每分钟最大发送数量
            "default_send_interval": 2.0,
            "enable_read_receipt": False,
            "contacts_file": "data/social_contacts.json",
            "message_history_file": "data/social_messages.json"
        }

    def _load_contacts(self):
        """加载联系人数据"""
        try:
            if os.path.exists(self.config["contacts_file"]):
                with open(self.config["contacts_file"], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for contact_data in data:
                        contact = SocialContact(
                            name=contact_data['name'],
                            platform=SocialPlatform(contact_data['platform']),
                            identifier=contact_data['identifier'],
                            group_name=contact_data.get('group_name'),
                            nickname=contact_data.get('nickname'),
                            avatar_path=contact_data.get('avatar_path'),
                            notes=contact_data.get('notes')
                        )
                        self.contacts[f"{contact.platform.value}_{contact.identifier}"] = contact
                print(f"加载了 {len(self.contacts)} 个联系人")
        except Exception as e:
            print(f"加载联系人失败: {str(e)}")

    def _load_message_history(self):
        """加载消息历史"""
        try:
            if os.path.exists(self.config["message_history_file"]):
                with open(self.config["message_history_file"], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for msg_data in data:
                        message = SocialMessage(
                            id=msg_data['id'],
                            platform=SocialPlatform(msg_data['platform']),
                            recipient=SocialContact(**msg_data['recipient']),
                            content=msg_data['content'],
                            message_type=msg_data.get('message_type', 'text'),
                            attachments=msg_data.get('attachments', []),
                            scheduled_time=datetime.fromisoformat(msg_data['scheduled_time']) if msg_data.get('scheduled_time') else None,
                            status=MessageStatus(msg_data.get('status', 'pending')),
                            created_at=datetime.fromisoformat(msg_data['created_at']),
                            sent_at=datetime.fromisoformat(msg_data['sent_at']) if msg_data.get('sent_at') else None,
                            retry_count=msg_data.get('retry_count', 0),
                            max_retries=msg_data.get('max_retries', 3)
                        )
                        self.messages.append(message)
                print(f"加载了 {len(self.messages)} 条历史消息")
        except Exception as e:
            print(f"加载消息历史失败: {str(e)}")

    def save_contacts(self):
        """保存联系人数据"""
        if not self.config["auto_save_contacts"]:
            return

        try:
            os.makedirs(os.path.dirname(self.config["contacts_file"]), exist_ok=True)
            contacts_data = []
            for contact in self.contacts.values():
                contacts_data.append({
                    'name': contact.name,
                    'platform': contact.platform.value,
                    'identifier': contact.identifier,
                    'group_name': contact.group_name,
                    'nickname': contact.nickname,
                    'avatar_path': contact.avatar_path,
                    'notes': contact.notes
                })

            with open(self.config["contacts_file"], 'w', encoding='utf-8') as f:
                json.dump(contacts_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存联系人失败: {str(e)}")

    def save_message_history(self):
        """保存消息历史"""
        try:
            os.makedirs(os.path.dirname(self.config["message_history_file"]), exist_ok=True)

            # 只保留最近的消息
            cutoff_date = datetime.now() - timedelta(days=self.config["message_retention_days"])
            recent_messages = [msg for msg in self.messages if msg.created_at > cutoff_date]

            messages_data = []
            for msg in recent_messages:
                messages_data.append({
                    'id': msg.id,
                    'platform': msg.platform.value,
                    'recipient': {
                        'name': msg.recipient.name,
                        'platform': msg.recipient.platform.value,
                        'identifier': msg.recipient.identifier,
                        'group_name': msg.recipient.group_name,
                        'nickname': msg.recipient.nickname,
                        'avatar_path': msg.recipient.avatar_path,
                        'notes': msg.recipient.notes
                    },
                    'content': msg.content,
                    'message_type': msg.message_type,
                    'attachments': msg.attachments,
                    'scheduled_time': msg.scheduled_time.isoformat() if msg.scheduled_time else None,
                    'status': msg.status.value,
                    'created_at': msg.created_at.isoformat(),
                    'sent_at': msg.sent_at.isoformat() if msg.sent_at else None,
                    'retry_count': msg.retry_count,
                    'max_retries': msg.max_retries
                })

            with open(self.config["message_history_file"], 'w', encoding='utf-8') as f:
                json.dump(messages_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存消息历史失败: {str(e)}")

    def add_contact(self, contact: SocialContact) -> bool:
        """添加联系人"""
        try:
            key = f"{contact.platform.value}_{contact.identifier}"
            self.contacts[key] = contact
            self.save_contacts()
            print(f"添加联系人成功: {contact.name} ({contact.platform.value})")
            return True
        except Exception as e:
            print(f"添加联系人失败: {str(e)}")
            return False

    def find_contact(self, platform: SocialPlatform, identifier: str) -> Optional[SocialContact]:
        """查找联系人"""
        key = f"{platform.value}_{identifier}"
        return self.contacts.get(key)

    def get_contacts_by_platform(self, platform: SocialPlatform) -> List[SocialContact]:
        """根据平台获取联系人"""
        return [contact for contact in self.contacts.values() if contact.platform == platform]

    def send_message(self, message: SocialMessage) -> bool:
        """发送单条消息"""
        try:
            print(f"准备发送消息: {message.recipient.name} - {message.content[:50]}...")

            # 根据平台发送消息
            if message.platform == SocialPlatform.WECHAT:
                success = self._send_wechat_message(message)
            elif message.platform == SocialPlatform.QQ:
                success = self._send_qq_message(message)
            elif message.platform == SocialPlatform.EMAIL:
                success = self._send_email_message(message)
            else:
                success = False
                print(f"不支持的平台: {message.platform.value}")

            if success:
                message.status = MessageStatus.SENT
                message.sent_at = datetime.now()
                print(f"消息发送成功: {message.recipient.name}")
            else:
                message.retry_count += 1
                if message.retry_count >= message.max_retries:
                    message.status = MessageStatus.FAILED
                print(f"消息发送失败: {message.recipient.name} (重试: {message.retry_count}/{message.max_retries})")

            self.messages.append(message)
            self.save_message_history()
            return success

        except Exception as e:
            print(f"发送消息异常: {str(e)}")
            message.status = MessageStatus.FAILED
            message.retry_count += 1
            self.messages.append(message)
            return False

    def _send_wechat_message(self, message: SocialMessage) -> bool:
        """发送微信消息"""
        try:
            # 查找微信窗口
            wechat_windows = []
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "微信" in title or "WeChat" in title:
                        windows.append((hwnd, title))

            win32gui.EnumWindows(enum_windows_callback, wechat_windows)

            if not wechat_windows:
                print("未找到微信窗口")
                return False

            # 激活微信窗口
            wechat_hwnd = wechat_windows[0][0]
            win32gui.ShowWindow(wechat_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(wechat_hwnd)
            time.sleep(1)

            # 搜索联系人
            if message.recipient.name or message.recipient.identifier:
                pyautogui.hotkey('ctrl', 'f')  # 打开搜索
                time.sleep(0.5)
                search_text = message.recipient.name or message.recipient.identifier
                pyperclip.copy(search_text)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1)
                pyautogui.press('enter')  # 选择第一个搜索结果
                time.sleep(1)

            # 发送消息
            pyperclip.copy(message.content)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('enter')

            # 如果有附件，发送附件
            for attachment in message.attachments:
                if os.path.exists(attachment):
                    self._send_wechat_file(attachment)

            return True

        except Exception as e:
            print(f"发送微信消息失败: {str(e)}")
            return False

    def _send_wechat_file(self, file_path: str):
        """发送微信文件"""
        try:
            # Ctrl+Shift+F 发送文件
            pyautogui.hotkey('ctrl', 'shift', 'f')
            time.sleep(1)

            # 将文件路径复制到剪贴板
            pyperclip.copy(file_path)

            # 粘贴文件路径
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)

            # 按回车发送
            pyautogui.press('enter')
            time.sleep(1)

        except Exception as e:
            print(f"发送微信文件失败: {str(e)}")

    def _send_qq_message(self, message: SocialMessage) -> bool:
        """发送QQ消息"""
        try:
            # 查找QQ窗口
            qq_windows = []
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "QQ" in title:
                        windows.append((hwnd, title))

            win32gui.EnumWindows(enum_windows_callback, qq_windows)

            if not qq_windows:
                print("未找到QQ窗口")
                return False

            # 激活QQ窗口
            qq_hwnd = qq_windows[0][0]
            win32gui.ShowWindow(qq_hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(qq_hwnd)
            time.sleep(1)

            # 搜索联系人（简化实现）
            if message.recipient.name or message.recipient.identifier:
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(0.5)
                search_text = message.recipient.name or message.recipient.identifier
                pyperclip.copy(search_text)
                pyautogui.hotkey('ctrl', 'v')
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(1)

            # 发送消息
            pyperclip.copy(message.content)
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            pyautogui.press('enter')

            return True

        except Exception as e:
            print(f"发送QQ消息失败: {str(e)}")
            return False

    def _send_email_message(self, message: SocialMessage) -> bool:
        """发送邮件消息"""
        try:
            import smtplib
            from email.mime.text import MimeText
            from email.mime.multipart import MimeMultipart
            from email.mime.base import MimeBase
            from email import encoders

            # 获取邮件配置（需要根据实际情况配置）
            smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
            smtp_port = self.config.get('smtp_port', 587)
            username = self.config.get('email_username')
            password = self.config.get('email_password')

            if not username or not password:
                print("邮件配置不完整")
                return False

            # 创建邮件
            msg = MimeMultipart()
            msg['From'] = username
            msg['To'] = message.recipient.identifier
            msg['Subject'] = f"消息 - {message.recipient.name}"

            # 添加正文
            msg.attach(MimeText(message.content, 'plain', 'utf-8'))

            # 添加附件
            for attachment in message.attachments:
                if os.path.exists(attachment):
                    part = MimeBase('application', 'octet-stream')
                    with open(attachment, 'rb') as file:
                        part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {os.path.basename(attachment)}'
                    )
                    msg.attach(part)

            # 发送邮件
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()

            return True

        except Exception as e:
            print(f"发送邮件失败: {str(e)}")
            return False

    def send_mass_message(self, mass_message: MassMessage) -> Dict[str, Any]:
        """发送群发消息"""
        try:
            print(f"开始群发消息: {len(mass_message.recipients)} 个联系人")
            mass_message.status = MessageStatus.SENDING
            mass_message.started_at = datetime.now()

            sent_count = 0
            failed_count = 0

            # 分批发送
            for i in range(0, len(mass_message.recipients), mass_message.batch_size):
                batch = mass_message.recipients[i:i + mass_message.batch_size]

                for recipient in batch:
                    message = SocialMessage(
                        id=f"mass_{mass_message.id}_{int(time.time())}_{recipient.identifier}",
                        platform=mass_message.platform,
                        recipient=recipient,
                        content=mass_message.content,
                        message_type=mass_message.message_type,
                        attachments=mass_message.attachments.copy()
                    )

                    try:
                        success = self.send_message(message)
                        if success:
                            sent_count += 1
                        else:
                            failed_count += 1

                        # 发送间隔
                        time.sleep(mass_message.send_interval)

                    except Exception as e:
                        print(f"群发消息异常: {str(e)}")
                        failed_count += 1

                # 批次间隔
                if i + mass_message.batch_size < len(mass_message.recipients):
                    time.sleep(mass_message.send_interval * 5)

            mass_message.sent_count = sent_count
            mass_message.failed_count = failed_count
            mass_message.completed_at = datetime.now()

            if failed_count == 0:
                mass_message.status = MessageStatus.SENT
            elif sent_count > 0:
                mass_message.status = MessageStatus.SENT  # 部分成功也算发送完成
            else:
                mass_message.status = MessageStatus.FAILED

            result = {
                "success": mass_message.status != MessageStatus.FAILED,
                "total_recipients": len(mass_message.recipients),
                "sent_count": sent_count,
                "failed_count": failed_count,
                "success_rate": sent_count / len(mass_message.recipients) * 100,
                "duration": (mass_message.completed_at - mass_message.started_at).total_seconds()
            }

            print(f"群发完成: 发送 {sent_count}/{len(mass_message.recipients)} 条消息")
            return result

        except Exception as e:
            print(f"群发消息失败: {str(e)}")
            mass_message.status = MessageStatus.FAILED
            mass_message.completed_at = datetime.now()
            return {"success": False, "error": str(e)}

    def get_message_statistics(self) -> Dict[str, Any]:
        """获取消息统计"""
        total_messages = len(self.messages)
        sent_messages = len([m for m in self.messages if m.status == MessageStatus.SENT])
        failed_messages = len([m for m in self.messages if m.status == MessageStatus.FAILED])

        platform_stats = {}
        for platform in SocialPlatform:
            platform_messages = [m for m in self.messages if m.platform == platform]
            platform_stats[platform.value] = {
                "total": len(platform_messages),
                "sent": len([m for m in platform_messages if m.status == MessageStatus.SENT]),
                "failed": len([m for m in platform_messages if m.status == MessageStatus.FAILED])
            }

        return {
            "total_messages": total_messages,
            "sent_messages": sent_messages,
            "failed_messages": failed_messages,
            "success_rate": (sent_messages / total_messages * 100) if total_messages > 0 else 0,
            "total_contacts": len(self.contacts),
            "platform_statistics": platform_stats,
            "recent_messages": [
                {
                    "id": m.id,
                    "platform": m.platform.value,
                    "recipient": m.recipient.name,
                    "content": m.content[:50] + "..." if len(m.content) > 50 else m.content,
                    "status": m.status.value,
                    "created_at": m.created_at.isoformat()
                }
                for m in sorted(self.messages, key=lambda x: x.created_at, reverse=True)[:10]
            ]
        }

# 创建全局社交媒体管理器实例
social_manager = SocialMediaManager()