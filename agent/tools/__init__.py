"""
YOLO-LLM Agent Tools Package

智能工作流代理工具系统
提供统一的工具接口和动态注册机制
"""

from .base_tool import BaseTool, ToolResult
from .tool_registry import ToolRegistry
from .system_tool import SystemTool
from .file_tool import FileTool
from .input_tool import InputTool

__all__ = [
    'BaseTool',
    'ToolResult',
    'ToolRegistry',
    'SystemTool',
    'FileTool',
    'InputTool'
]

# 注册所有核心工具
def register_core_tools():
    """注册所有核心工具到ToolRegistry"""
    registry = ToolRegistry()

    # 注册系统工具
    registry.register_tool(SystemTool())

    # 注册文件工具
    registry.register_tool(FileTool())

    # 注册输入工具
    registry.register_tool(InputTool())

    return registry