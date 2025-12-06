"""
MCP 工具包初始化文件
"""

from .email_tool import EmailTool
from .news_tool import NewsTool
from .weather_tool import WeatherTool
from .system_tool import SystemTool
from .screenshot_tool import ScreenshotTool

__all__ = [
    "EmailTool",
    "NewsTool",
    "WeatherTool",
    "SystemTool",
    "ScreenshotTool"
]