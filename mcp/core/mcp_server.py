#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块化MCP服务器
使用新的工具架构
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import logging

# 导入工具注册器
from .tool_registry import tool_registry, initialize_default_tools, SIMPLE_TOOL_MAPPING

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 请求模型
class ToolRequest(BaseModel):
    tool_name: str
    action: str = "default"
    parameters: Dict[str, Any] = {}

class ToolListResponse(BaseModel):
    success: bool
    tools: List[Dict[str, Any]]
    count: int

# 创建FastAPI应用
app = FastAPI(
    title="模块化MCP服务器",
    description="使用新架构的MCP工具服务器",
    version="2.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """服务器启动事件"""
    logger.info("启动模块化MCP服务器...")

    # 初始化默认工具
    tool_count = await initialize_default_tools()
    logger.info(f"服务器启动完成，已加载 {tool_count} 个工具")

@app.get("/", response_model=Dict[str, Any])
async def root():
    """根路径"""
    return {
        "message": "模块化MCP服务器",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "tools": "/tools",
            "execute": "/execute",
            "health": "/health",
            "stats": "/stats"
        }
    }

@app.get("/tools", response_model=ToolListResponse)
async def list_tools():
    """列出所有可用工具"""
    try:
        tools = tool_registry.list_tools()
        return ToolListResponse(
            success=True,
            tools=tools,
            count=len(tools)
        )
    except Exception as e:
        logger.error(f"获取工具列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
async def execute_tool(request: ToolRequest):
    """执行工具操作"""
    try:
        start_time = time.time()

        # 对于简化的工具调用，使用默认action
        if request.tool_name in SIMPLE_TOOL_MAPPING:
            action = SIMPLE_TOOL_MAPPING[request.tool_name]
        else:
            action = request.action

        logger.info(f"执行工具: {request.tool_name}.{action}")

        result = await tool_registry.execute_tool(
            request.tool_name,
            action,
            request.parameters
        )

        execution_time = time.time() - start_time

        # 构建响应
        response_data = {
            "success": result.get("success", False),
            "tool_name": request.tool_name,
            "action": action,
            "execution_time": round(execution_time, 3),
            "timestamp": datetime.now().isoformat()
        }

        if result.get("success"):
            response_data["data"] = result.get("result", {}).get("data", {})
        else:
            response_data["error"] = result.get("error", "未知错误")

        return response_data

    except Exception as e:
        logger.error(f"执行工具失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# 为每个工具创建独立的端点（向后兼容）
@app.post("/mcp/{tool_name}")
async def legacy_tool_endpoint(tool_name: str, request: dict):
    """兼容旧版本的工具端点"""
    try:
        # 转换为新格式的请求
        tool_request = ToolRequest(
            tool_name=tool_name,
            action=request.get("action", "default"),
            parameters=request.get("parameters", request)
        )

        return await execute_tool(tool_request)

    except Exception as e:
        logger.error(f"旧版工具端点执行失败: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "tool_name": tool_name
        }

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        # 检查所有工具的健康状态
        tool_health = await tool_registry.health_check_all()

        return {
            "status": "healthy" if tool_health["unhealthy_tools"] == 0 else "degraded",
            "server": "模块化MCP服务器",
            "version": "2.0.0",
            "uptime": tool_registry.get_registry_stats()["registry_info"]["uptime_seconds"],
            "tools": tool_health,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/stats")
async def get_stats():
    """获取统计信息"""
    try:
        stats = tool_registry.get_registry_stats()

        return {
            "success": True,
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schema/{tool_name}")
async def get_tool_schema(tool_name: str):
    """获取工具模式"""
    try:
        schema = tool_registry.get_tool_schema(tool_name)
        if not schema:
            raise HTTPException(status_code=404, detail=f"工具不存在: {tool_name}")

        return {
            "success": True,
            "tool_name": tool_name,
            "schema": schema
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取工具模式失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/schemas")
async def get_all_schemas():
    """获取所有工具模式"""
    try:
        schemas = tool_registry.get_all_schemas()

        return {
            "success": True,
            "schemas": schemas,
            "count": len(schemas)
        }

    except Exception as e:
        logger.error(f"获取所有工具模式失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def run_server(host: str = "127.0.0.1", port: int = 8083, debug: bool = False):
    """运行服务器"""
    logger.info(f"启动模块化MCP服务器: http://{host}:{port}")
    uvicorn.run(
        "mcp.core.mcp_server:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info" if debug else "warning"
    )

if __name__ == "__main__":
    run_server(debug=True)