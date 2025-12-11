"""
MCP 工具包初始化文件
新架构的工具模块
"""

from .base_tool import BaseTool, ToolResponse, ToolError
from .news_tool import news_tool
from .weather_tool import weather_tool
from .email_tool import email_tool
from .filesystem_tool import filesystem_tool

__all__ = [
    'BaseTool', 'ToolResponse', 'ToolError',
    'news_tool', 'weather_tool', 'email_tool', 'filesystem_tool'
]