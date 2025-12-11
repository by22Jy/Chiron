#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务器主启动脚本
"""

import sys
import os
import asyncio
import argparse
from pathlib import Path

# 添加mcp目录到Python路径
mcp_dir = Path(__file__).parent
sys.path.insert(0, str(mcp_dir))

from core.mcp_server import run_server
from core.tool_registry import tool_registry

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="模块化MCP服务器")
    parser.add_argument("--host", default="127.0.0.1", help="服务器主机地址")
    parser.add_argument("--port", type=int, default=8083, help="服务器端口")
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    parser.add_argument("--list-tools", action="store_true", help="列出所有可用工具")
    parser.add_argument("--health-check", action="store_true", help="执行健康检查")

    args = parser.parse_args()

    if args.list_tools:
        print("可用工具:")
        for tool in tool_registry.list_tools():
            print(f"  - {tool['name']} v{tool['version']}: {tool['description']}")
            print(f"    能力: {', '.join(tool['capabilities'])}")
        return

    if args.health_check:
        print("执行健康检查...")
        health = await tool_registry.health_check_all()
        print(f"总工具数: {health['total_tools']}")
        print(f"健康工具: {health['healthy_tools']}")
        print(f"异常工具: {health['unhealthy_tools']}")
        return

    print(f"启动模块化MCP服务器...")
    print(f"地址: http://{args.host}:{args.port}")
    print(f"调试模式: {args.debug}")

    # 启动服务器
    run_server(host=args.host, port=args.port, debug=args.debug)

if __name__ == "__main__":
    asyncio.run(main())