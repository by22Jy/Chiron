#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP核心模块

包含MCP服务器核心功能：
- mcp_server: FastAPI服务器实现
- tool_registry: 工具注册和管理系统
"""

from .mcp_server import run_server
from .tool_registry import tool_registry

__all__ = [
    "run_server",
    "tool_registry"
]