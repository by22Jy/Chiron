"""
简化的MCP HTTP服务器
用于单元测试
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(
    title="Simple MCP Server",
    description="简化版MCP服务器",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ToolRequest(BaseModel):
    action: str = "execute"
    parameters: Dict[str, Any] = {}

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "news": True,
            "weather": True,
            "email": True,
            "filesystem": True
        },
        "available_tools": [
            "news", "weather", "email", "filesystem", "screenshot", "browser"
        ]
    }

@app.get("/tools")
async def get_available_tools():
    """获取可用工具列表"""
    return {
        "success": True,
        "tools": [
            {
                "name": "news",
                "description": "获取新闻信息",
                "parameters": ["count", "category", "country"]
            },
            {
                "name": "weather",
                "description": "获取天气信息",
                "parameters": ["city", "units", "lang"]
            },
            {
                "name": "email",
                "description": "发送邮件",
                "parameters": ["to", "subject", "content", "attachments"]
            },
            {
                "name": "filesystem",
                "description": "文件系统操作",
                "parameters": ["operation", "path", "content"]
            },
            {
                "name": "screenshot",
                "description": "截图操作",
                "parameters": ["region", "save_path"]
            },
            {
                "name": "browser",
                "description": "浏览器自动化",
                "parameters": ["action", "url", "selectors"]
            }
        ]
    }

@app.post("/mcp/{tool_name}")
async def call_mcp_tool(tool_name: str, request: ToolRequest):
    """调用指定的MCP工具"""
    try:
        print(f"[INFO] 调用MCP工具: {tool_name}")

        if tool_name == "news":
            return await handle_news_tool(request)
        elif tool_name == "weather":
            return await handle_weather_tool(request)
        elif tool_name == "email":
            return await handle_email_tool(request)
        elif tool_name == "filesystem":
            return await handle_filesystem_tool(request)
        elif tool_name == "screenshot":
            return await handle_screenshot_tool(request)
        elif tool_name == "browser":
            return await handle_browser_tool(request)
        else:
            raise HTTPException(status_code=404, detail=f"未知的工具: {tool_name}")

    except Exception as e:
        print(f"[ERROR] 工具调用失败: {tool_name}, 错误: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "tool": tool_name,
            "timestamp": datetime.now().isoformat()
        }

async def handle_news_tool(request: ToolRequest) -> Dict[str, Any]:
    """处理新闻工具"""
    try:
        count = request.parameters.get("count", 10)

        # 模拟新闻数据
        news_list = [
            {"title": f"新闻标题 {i+1}", "content": f"新闻内容 {i+1}", "date": datetime.now().strftime("%Y-%m-%d")}
            for i in range(count)
        ]

        return {
            "success": True,
            "tool": "news",
            "data": {
                "news": news_list,
                "count": len(news_list),
                "source": "Mock News API"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "tool": "news",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def handle_weather_tool(request: ToolRequest) -> Dict[str, Any]:
    """处理天气工具"""
    try:
        city = request.parameters.get("city", "北京")

        # 模拟天气数据
        weather_info = {
            "city": city,
            "temperature": "18°C",
            "condition": "晴朗",
            "humidity": "45%",
            "wind_speed": "3.2 m/s",
            "date": datetime.now().strftime("%Y-%m-%d")
        }

        return {
            "success": True,
            "tool": "weather",
            "data": {
                "weather": weather_info,
                "city": city
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "tool": "weather",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def handle_email_tool(request: ToolRequest) -> Dict[str, Any]:
    """处理邮件工具"""
    try:
        to = request.parameters.get("to")
        subject = request.parameters.get("subject")
        content = request.parameters.get("content")

        if not all([to, subject, content]):
            raise ValueError("缺少必需参数: to, subject, content")

        # 模拟邮件发送
        return {
            "success": True,
            "tool": "email",
            "data": {
                "to": to,
                "subject": subject,
                "message": "邮件发送成功",
                "email_id": f"msg_{int(time.time())}"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "tool": "email",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def handle_filesystem_tool(request: ToolRequest) -> Dict[str, Any]:
    """处理文件系统工具"""
    try:
        operation = request.parameters.get("operation", "read")
        path = request.parameters.get("path")
        content = request.parameters.get("content", "")

        if operation == "read" and path:
            # 模拟读取文件
            return {
                "success": True,
                "tool": "filesystem",
                "data": {
                    "operation": operation,
                    "path": path,
                    "content": f"模拟文件内容 from {path}"
                },
                "timestamp": datetime.now().isoformat()
            }
        elif operation == "write" and path and content:
            # 模拟写入文件
            return {
                "success": True,
                "tool": "filesystem",
                "data": {
                    "operation": operation,
                    "path": path,
                    "content_length": len(content)
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise ValueError("无效的文件操作或缺少参数")
    except Exception as e:
        return {
            "success": False,
            "tool": "filesystem",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def handle_screenshot_tool(request: ToolRequest) -> Dict[str, Any]:
    """处理截图工具"""
    try:
        save_path = request.parameters.get("save_path", f"screenshot_{int(time.time())}.png")

        # 模拟截图
        return {
            "success": True,
            "tool": "screenshot",
            "data": {
                "path": save_path,
                "size": {"width": 1920, "height": 1080},
                "file_size": 1024000
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "tool": "screenshot",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def handle_browser_tool(request: ToolRequest) -> Dict[str, Any]:
    """处理浏览器工具"""
    try:
        action = request.parameters.get("action", "open")
        url = request.parameters.get("url", "https://www.google.com")

        # 模拟浏览器操作
        return {
            "success": True,
            "tool": "browser",
            "data": {
                "action": action,
                "url": url,
                "message": f"浏览器操作 {action} 执行成功"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "success": False,
            "tool": "browser",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    print("启动简化MCP HTTP服务器...")

    # 检查环境变量
    if not os.getenv("NEWS_API_KEY"):
        print("警告: NEWS_API_KEY 环境变量未设置，新闻功能使用模拟数据")

    if not os.getenv("WEATHER_API_KEY"):
        print("警告: WEATHER_API_KEY 环境变量未设置，天气功能使用模拟数据")

    # 启动服务器
    uvicorn.run(
        "simple_mcp_server:app",
        host="127.0.0.1",
        port=8081,
        reload=False,
        log_level="info"
    )