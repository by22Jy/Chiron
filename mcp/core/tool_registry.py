#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP工具注册器
统一管理所有MCP工具
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# 修改为绝对导入以解决相对导入问题
try:
    from ..tools.news_tool import news_tool
    from ..tools.weather_tool import weather_tool
    from ..tools.email_tool import email_tool
    from ..tools.filesystem_tool import filesystem_tool
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from tools.news_tool import news_tool
    from tools.weather_tool import weather_tool
    from tools.email_tool import email_tool
    from tools.filesystem_tool import filesystem_tool

logger = logging.getLogger(__name__)

class ToolRegistry:
    """工具注册器类"""

    def __init__(self):
        self.tools: Dict[str, Any] = {}
        self.tool_stats: Dict[str, Dict[str, Any]] = {}
        self.registered_tools: Dict[str, str] = {}  # name -> version
        self.startup_time = datetime.now()

    def register_tool(self, tool_instance: Any) -> bool:
        """注册工具"""
        try:
            tool_name = tool_instance.name
            if tool_name in self.tools:
                logger.warning(f"工具 {tool_name} 已存在，将被覆盖")

            self.tools[tool_name] = tool_instance
            self.registered_tools[tool_name] = tool_instance.version
            self.tool_stats[tool_name] = {
                "registered_time": datetime.now().isoformat(),
                "call_count": 0,
                "success_count": 0,
                "error_count": 0,
                "last_called": None
            }

            logger.info(f"工具已注册: {tool_name} v{tool_instance.version}")
            return True

        except Exception as e:
            logger.error(f"注册工具失败: {str(e)}")
            return False

    def get_tool(self, tool_name: str) -> Optional[Any]:
        """获取工具实例"""
        return self.tools.get(tool_name)

    def list_tools(self) -> List[Dict[str, Any]]:
        """列出所有已注册的工具"""
        tools_info = []
        for tool_name, tool_instance in self.tools.items():
            tools_info.append({
                "name": tool_name,
                "description": tool_instance.description,
                "version": tool_instance.version,
                "capabilities": tool_instance.get_capabilities(),
                "stats": self.tool_stats.get(tool_name, {})
            })
        return tools_info

    async def execute_tool(self, tool_name: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具操作"""
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"工具不存在: {tool_name}",
                "available_tools": list(self.tools.keys())
            }

        tool_instance = self.tools[tool_name]
        stats = self.tool_stats[tool_name]
        stats["call_count"] += 1
        stats["last_called"] = datetime.now().isoformat()

        try:
            # 使用工具的安全执行方法
            result = await tool_instance.safe_execute(action, parameters)

            if result.success:
                stats["success_count"] += 1
            else:
                stats["error_count"] += 1

            return {
                "success": True,
                "tool_name": tool_name,
                "action": action,
                "result": result.dict(),
                "execution_time": result.execution_time
            }

        except Exception as e:
            stats["error_count"] += 1
            error_msg = f"工具执行异常: {str(e)}"
            logger.error(f"{tool_name}.{action} 执行失败: {error_msg}")

            return {
                "success": False,
                "tool_name": tool_name,
                "action": action,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }

    async def health_check_all(self) -> Dict[str, Any]:
        """检查所有工具的健康状态"""
        health_results = {}
        healthy_count = 0
        unhealthy_count = 0

        for tool_name, tool_instance in self.tools.items():
            try:
                health_status = await tool_instance.health_check()
                health_results[tool_name] = health_status

                if health_status.get("status") == "healthy":
                    healthy_count += 1
                else:
                    unhealthy_count += 1

            except Exception as e:
                health_results[tool_name] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
                unhealthy_count += 1

        return {
            "total_tools": len(self.tools),
            "healthy_tools": healthy_count,
            "unhealthy_tools": unhealthy_count,
            "health_check_time": datetime.now().isoformat(),
            "results": health_results
        }

    def get_registry_stats(self) -> Dict[str, Any]:
        """获取注册器统计信息"""
        total_calls = sum(stats.get("call_count", 0) for stats in self.tool_stats.values())
        total_successes = sum(stats.get("success_count", 0) for stats in self.tool_stats.values())
        total_errors = sum(stats.get("error_count", 0) for stats in self.tool_stats.values())

        return {
            "registry_info": {
                "startup_time": self.startup_time.isoformat(),
                "total_registered_tools": len(self.tools),
                "uptime_seconds": (datetime.now() - self.startup_time).total_seconds()
            },
            "tool_stats": self.tool_stats,
            "overall_stats": {
                "total_calls": total_calls,
                "total_successes": total_successes,
                "total_errors": total_errors,
                "success_rate": (total_successes / max(total_calls, 1)) * 100
            }
        }

    def get_tool_schema(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """获取工具的模式定义"""
        tool = self.get_tool(tool_name)
        if tool:
            return tool.get_schema()
        return None

    def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """获取所有工具的模式定义"""
        schemas = {}
        for tool_name in self.tools:
            schemas[tool_name] = self.get_tool_schema(tool_name) or {}
        return schemas

# 创建全局工具注册器实例
tool_registry = ToolRegistry()

# 注册默认工具
async def initialize_default_tools():
    """初始化默认工具"""
    default_tools = [
        news_tool,
        weather_tool,
        email_tool,
        filesystem_tool
    ]

    for tool in default_tools:
        success = tool_registry.register_tool(tool)
        if not success:
            logger.error(f"初始化工具失败: {tool.name}")

    logger.info(f"工具注册器初始化完成，共注册 {len(tool_registry.tools)} 个工具")
    return len(tool_registry.tools)

# 简化版本的工具映射（用于向后兼容）
SIMPLE_TOOL_MAPPING = {
    "news": "get_news",
    "weather": "get_current_weather",
    "email": "send_email",
    "filesystem": "read_file"
}