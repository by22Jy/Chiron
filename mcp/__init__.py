#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP (Model Context Protocol) Server Package

YOLO-LLM MCP工具服务器
提供邮件、天气、新闻等外部工具集成
"""

__version__ = "1.0.0"
__author__ = "YOLO-LLM Team"
__description__ = "MCP工具服务器 - 为YOLO-LLM提供外部工具集成能力"

# 导出主要组件
from .core.mcp_server import run_server
from .core.tool_registry import tool_registry

__all__ = [
    "run_server",
    "tool_registry",
    "__version__",
    "__author__",
    "__description__"
]