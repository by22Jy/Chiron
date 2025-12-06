"""
工作流执行器模块

支持复杂的多步骤工作流，包括邮件发送和截图功能
"""

import os
import sys
import time
import pyautogui
import requests
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import logging

from email_client import EmailClient, EmailConfig, EmailMessage, EmailTemplate
from real_news_weather import RealNewsWeatherService, create_news_weather_service

# 设置工作流日志
logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """工作流步骤"""
    name: str
    action: str
    params: Dict[str, Any]
    requires_confirmation: bool = False
    timeout: float = 30.0


@dataclass
class ScreenshotConfig:
    """截图配置"""
    save_dir: str = "./screenshots"
    file_format: str = "png"
    quality: int = 95


class ScreenshotManager:
    """截图管理器"""

    def __init__(self, config: ScreenshotConfig = None):
        self.config = config or ScreenshotConfig()
        self._ensure_save_directory()

    def _ensure_save_directory(self):
        """确保保存目录存在"""
        os.makedirs(self.config.save_dir, exist_ok=True)

    def capture_screenshot(self, name: str = None) -> str:
        """截图并返回文件路径"""
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"{name or 'screenshot'}_{timestamp}.{self.config.file_format}"
            filepath = os.path.join(self.config.save_dir, filename)

            # 截图
            screenshot = pyautogui.screenshot()
            screenshot.save(filepath, quality=self.config.quality, optimize=True)

            logger.info(f"截图保存成功: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            return ""

    def capture_active_window(self, name: str = None) -> str:
        """截图活动窗口"""
        try:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f"{name or 'window'}_{timestamp}.{self.config.file_format}"
            filepath = os.path.join(self.config.save_dir, filename)

            # 获取活动窗口截图
            window = pyautogui.getActiveWindow()
            if window:
                screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
            else:
                screenshot = pyautogui.screenshot()

            screenshot.save(filepath, quality=self.config.quality, optimize=True)

            logger.info(f"窗口截图保存成功: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"窗口截图失败: {str(e)}")
            return ""


# 使用真实的新闻天气服务
# NewsWeatherService 已被 RealNewsWeatherService 替代


class WorkflowExecutor:
    """工作流执行器"""

    def __init__(self, email_config: EmailConfig = None, screenshot_config: ScreenshotConfig = None):
        self.email_client = EmailClient(email_config) if email_config else None
        self.screenshot_manager = ScreenshotManager(screenshot_config)
        self.news_weather_service = create_news_weather_service()  # 使用真实的API服务
        self.workflow_steps = []
        self.screenshots = []
        self.start_time = 0

    def execute_complex_workflow(self) -> Tuple[bool, str]:
        """执行复杂工作流：记事本+新闻天气+邮件发送"""
        self.start_time = time.time()
        self.workflow_steps = []
        self.screenshots = []

        try:
            logger.info("开始执行复杂工作流...")

            # 步骤1：打开记事本
            success = self._step1_open_notepad()
            if not success:
                return False, "打开记事本失败"

            # 步骤2：获取新闻和天气信息
            news_list, weather_info = self._step2_get_news_weather()

            # 步骤3：记录信息到记事本
            success = self._step3_record_to_notepad(news_list, weather_info)
            if not success:
                return False, "记录信息到记事本失败"

            # 步骤4：截图记录
            screenshot_path = self._step4_capture_screenshot()

            # 步骤5：发送邮件
            success = self._step5_send_email(news_list, weather_info, screenshot_path)
            if not success:
                return False, "发送邮件失败"

            total_time = time.time() - self.start_time
            logger.info(f"复杂工作流执行成功，总耗时: {total_time:.2f}秒")

            return True, f"工作流执行成功，总耗时: {total_time:.2f}秒"

        except Exception as e:
            error_msg = f"工作流执行异常: {str(e)}"
            logger.error(error_msg)
            return False, error_msg

    def _step1_open_notepad(self) -> bool:
        """步骤1：打开记事本"""
        try:
            logger.info("步骤1：打开记事本...")
            self.workflow_steps.append("打开记事本")

            # 截图前状态
            self.screenshot_manager.capture_screenshot("before_open_notepad")

            # 打开记事本
            pyautogui.hotkey('win', 'r')
            time.sleep(1)
            pyautogui.write('notepad')
            time.sleep(1)
            pyautogui.press('enter')
            time.sleep(2)

            # 截图后状态
            screenshot_path = self.screenshot_manager.capture_screenshot("after_open_notepad")
            if screenshot_path:
                self.screenshots.append({
                    "timestamp": time.strftime('%H:%M:%S'),
                    "step": "记事本已打开",
                    "path": screenshot_path
                })

            logger.info("记事本打开成功")
            return True

        except Exception as e:
            logger.error(f"打开记事本失败: {str(e)}")
            return False

    def _step2_get_news_weather(self) -> Tuple[List[str], Dict[str, Any]]:
        """步骤2：获取新闻和天气信息"""
        try:
            logger.info("步骤2：获取新闻和天气信息...")
            self.workflow_steps.append("获取新闻天气信息")

            # 获取新闻
            news_list = self.news_weather_service.get_top_news(10)

            # 获取天气
            weather_info = self.news_weather_service.get_weather_info()

            logger.info(f"获取到{len(news_list)}条新闻，天气信息: {weather_info['condition']}")
            return news_list, weather_info

        except Exception as e:
            logger.error(f"获取新闻天气失败: {str(e)}")
            return [], {}

    def _step3_record_to_notepad(self, news_list: List[str], weather_info: Dict[str, Any]) -> bool:
        """步骤3：记录信息到记事本"""
        try:
            logger.info("步骤3：记录信息到记事本...")
            self.workflow_steps.append("信息记录到记事本")

            # 构建记录内容
            content_lines = [
                "=" * 50,
                f"日期：{weather_info.get('date', time.strftime('%Y年%m月%d日'))}",
                "=" * 50,
                "",
                "📰 今日头条新闻 Top10：",
                ""
            ]

            # 添加新闻
            for news in news_list:
                content_lines.append(news)

            content_lines.extend([
                "",
                "🌤️ 今日天气情况：",
                f"温度：{weather_info.get('temperature', '未知')}",
                f"天气：{weather_info.get('condition', '未知')}",
                f"湿度：{weather_info.get('humidity', '未知')}",
                f"风力：{weather_info.get('wind', '未知')}",
                "",
                "=" * 50,
                f"记录时间：{time.strftime('%H:%M:%S')}"
            ])

            # 输入到记事本
            content = "\n".join(content_lines)
            pyautogui.write(content, interval=0.01)

            # 截图记录
            screenshot_path = self.screenshot_manager.capture_screenshot("after_record_info")
            if screenshot_path:
                self.screenshots.append({
                    "timestamp": time.strftime('%H:%M:%S'),
                    "step": "信息记录完成",
                    "path": screenshot_path
                })

            logger.info("信息记录成功")
            return True

        except Exception as e:
            logger.error(f"记录信息失败: {str(e)}")
            return False

    def _step4_capture_screenshot(self) -> str:
        """步骤4：截图记录"""
        try:
            logger.info("步骤4：截图记录...")
            self.workflow_steps.append("工作流截图")

            # 截取活动窗口
            screenshot_path = self.screenshot_manager.capture_active_window("workflow_complete")

            if screenshot_path:
                self.screenshots.append({
                    "timestamp": time.strftime('%H:%M:%S'),
                    "step": "工作流截图完成",
                    "path": screenshot_path
                })

            return screenshot_path

        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            return ""

    def _step5_send_email(self, news_list: List[str], weather_info: Dict[str, Any], screenshot_path: str) -> bool:
        """步骤5：发送邮件"""
        try:
            logger.info("步骤5：发送邮件...")
            self.workflow_steps.append("发送邮件")

            if not self.email_client:
                logger.error("邮件客户端未配置")
                return False

            # 使用邮件模板创建邮件
            email_message = EmailTemplate.create_news_weather_email(
                news_list=news_list,
                weather_info=weather_info,
                screenshots=self.screenshots
            )

            # 添加截图附件
            if screenshot_path and os.path.exists(screenshot_path):
                email_message.attachments.append(screenshot_path)

            # 发送邮件
            success, message = self.email_client.send_email(email_message)

            if success:
                logger.info(f"邮件发送成功: {message}")
                return True
            else:
                logger.error(f"邮件发送失败: {message}")
                return False

        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return False

    def get_workflow_summary(self) -> Dict[str, Any]:
        """获取工作流摘要"""
        return {
            "total_steps": len(self.workflow_steps),
            "execution_time": time.time() - self.start_time,
            "screenshots_count": len(self.screenshots),
            "steps": self.workflow_steps,
            "screenshots": self.screenshots
        }


# 便捷函数
def create_workflow_executor(email_config: EmailConfig = None) -> WorkflowExecutor:
    """创建工作流执行器"""
    return WorkflowExecutor(email_config)


if __name__ == '__main__':
    # 测试工作流执行器
    print("测试工作流执行器...")

    # 配置邮件（需要用户配置实际的邮件服务器信息）
    email_config = EmailConfig(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        sender_email="your_email@gmail.com",  # 需要配置
        sender_password="your_password",      # 需要配置
        use_tls=True
    )

    executor = WorkflowExecutor(email_config)

    # 执行工作流
    success, message = executor.execute_complex_workflow()

    print(f"工作流执行结果: {success} - {message}")

    # 打印摘要
    summary = executor.get_workflow_summary()
    print("工作流摘要:")
    print(f"  总步骤数: {summary['total_steps']}")
    print(f"  执行时间: {summary['execution_time']:.2f}秒")
    print(f"  截图数量: {summary['screenshots_count']}")
    print("  执行步骤:")
    for step in summary['steps']:
        print(f"    - {step}")