"""
MCP 服务器主程序

提供基于 DeepSeek 大模型的智能工作流服务
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn

from config import DEEPSEEK_CONFIG, MCP_CONFIG, PROMPT_CONFIG
from tools.email_tool import EmailTool
from tools.news_tool import NewsTool
from tools.weather_tool import WeatherTool
from tools.system_tool import SystemTool
from tools.screenshot_tool import ScreenshotTool

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="YOLO-LLM MCP Server", version="1.0.0")

# 初始化工具
tools = {
    "email": EmailTool(),
    "news": NewsTool(),
    "weather": WeatherTool(),
    "system": SystemTool(),
    "screenshot": ScreenshotTool()
}


@dataclass
class MCPRequest:
    """MCP请求"""
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


@dataclass
class MCPResponse:
    """MCP响应"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None


class DeepSeekClient:
    """DeepSeek API客户端"""

    def __init__(self):
        self.api_key = DEEPSEEK_CONFIG["api_key"]
        self.base_url = DEEPSEEK_CONFIG["base_url"]
        self.model = DEEPSEEK_CONFIG["model"]

        if not self.api_key:
            logger.warning("DeepSeek API key not configured")

    async def chat_completion(self, messages: List[Dict[str, str]],
                            tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """调用DeepSeek聊天完成API"""

        if not self.api_key:
            # 模拟响应，用于测试
            return self._mock_response(messages, tools)

        import httpx

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": DEEPSEEK_CONFIG["max_tokens"],
            "temperature": DEEPSEEK_CONFIG["temperature"]
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        try:
            async with httpx.AsyncClient(timeout=DEEPSEEK_CONFIG["timeout"]) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                return response.json()

        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            return self._mock_response(messages, tools)

    def _mock_response(self, messages: List[Dict[str, str]],
                      tools: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """模拟API响应"""

        last_message = messages[-1]["content"] if messages else ""

        # 分析用户意图
        if "邮件" in last_message or "发送" in last_message:
            return {
                "choices": [{
                    "message": {
                        "content": "我将帮您发送邮件。请告诉我邮件内容和收件人。",
                        "tool_calls": [{
                            "id": "call_1",
                            "type": "function",
                            "function": {
                                "name": "email_tool",
                                "arguments": json.dumps({
                                    "action": "prepare_email",
                                    "context": last_message
                                })
                            }
                        }]
                    }
                }]
            }

        elif "新闻" in last_message:
            return {
                "choices": [{
                    "message": {
                        "content": "我将为您获取最新新闻。",
                        "tool_calls": [{
                            "id": "call_2",
                            "type": "function",
                            "function": {
                                "name": "news_tool",
                                "arguments": json.dumps({
                                    "action": "get_top_news",
                                    "count": 10
                                })
                            }
                        }]
                    }
                }]
            }

        elif "天气" in last_message:
            return {
                "choices": [{
                    "message": {
                        "content": "我将为您查询天气信息。",
                        "tool_calls": [{
                            "id": "call_3",
                            "type": "function",
                            "function": {
                                "name": "weather_tool",
                                "arguments": json.dumps({
                                    "action": "get_current_weather",
                                    "city": "北京"
                                })
                            }
                        }]
                    }
                }]
            }

        else:
            return {
                "choices": [{
                    "message": {
                        "content": "我理解您的需求。请告诉我更具体的信息，我可以帮您：发送邮件、获取新闻、查询天气、截图等。"
                    }
                }]
            }


class MCPServer:
    """MCP服务器"""

    def __init__(self):
        self.deepseek = DeepSeekClient()
        self.sessions: Dict[str, Dict[str, Any]] = {}

        # 定义可用工具
        self.available_tools = [
            {
                "type": "function",
                "function": {
                    "name": "email_tool",
                    "description": "发送邮件、管理邮件相关操作",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "description": "操作类型"},
                            "to_email": {"type": "string", "description": "收件人邮箱"},
                            "subject": {"type": "string", "description": "邮件主题"},
                            "content": {"type": "string", "description": "邮件内容"},
                            "attachments": {"type": "array", "description": "附件列表"}
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "news_tool",
                    "description": "获取新闻、分析新闻内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "description": "操作类型"},
                            "count": {"type": "integer", "description": "新闻数量"},
                            "category": {"type": "string", "description": "新闻分类"}
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "weather_tool",
                    "description": "查询天气、天气预报",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "description": "操作类型"},
                            "city": {"type": "string", "description": "城市名称"},
                            "days": {"type": "integer", "description": "预报天数"}
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "system_tool",
                    "description": "系统操作、文件管理、应用控制",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "description": "操作类型"},
                            "application": {"type": "string", "description": "应用程序名称"},
                            "parameters": {"type": "object", "description": "操作参数"}
                        },
                        "required": ["action"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "screenshot_tool",
                    "description": "截图功能、图片处理",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "description": "操作类型"},
                            "mode": {"type": "string", "description": "截图模式"},
                            "filename": {"type": "string", "description": "文件名"}
                        },
                        "required": ["action"]
                    }
                }
            }
        ]

    async def process_request(self, request: MCPRequest) -> MCPResponse:
        """处理MCP请求"""

        try:
            # 获取或创建会话
            if request.user_id not in self.sessions:
                self.sessions[request.user_id] = {
                    "messages": [
                        {"role": "system", "content": PROMPT_CONFIG["system_prompt"]}
                    ]
                }

            session = self.sessions[request.user_id]

            # 添加用户消息
            session["messages"].append({"role": "user", "content": request.message})

            # 调用DeepSeek API
            api_response = await self.deepseek.chat_completion(
                session["messages"],
                self.available_tools
            )

            # 处理响应
            choice = api_response["choices"][0]
            message = choice["message"]

            # 添加助手回复
            session["messages"].append({
                "role": "assistant",
                "content": message.get("content", "")
            })

            # 处理工具调用
            tool_calls = message.get("tool_calls", [])
            tool_results = []

            for tool_call in tool_calls:
                result = await self.execute_tool_call(tool_call)
                tool_results.append(result)

                # 添加工具结果到对话历史
                session["messages"].append({
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call["id"]
                })

            # 如果有工具调用，再次调用API获取最终回复
            if tool_results:
                followup_response = await self.deepseek.chat_completion(session["messages"])
                final_message = followup_response["choices"][0]["message"]["content"]
            else:
                final_message = message.get("content", "")

            return MCPResponse(
                success=True,
                message=final_message,
                data={"tool_results": tool_results},
                tool_calls=[tc["function"] for tc in tool_calls]
            )

        except Exception as e:
            logger.error(f"Process request error: {str(e)}")
            return MCPResponse(
                success=False,
                message="处理请求时发生错误",
                error=str(e)
            )

    async def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """执行工具调用"""

        tool_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])

        try:
            if tool_name == "email_tool":
                return await tools["email"].execute(arguments)
            elif tool_name == "news_tool":
                return await tools["news"].execute(arguments)
            elif tool_name == "weather_tool":
                return await tools["weather"].execute(arguments)
            elif tool_name == "system_tool":
                return await tools["system"].execute(arguments)
            elif tool_name == "screenshot_tool":
                return await tools["screenshot"].execute(arguments)
            else:
                return {"success": False, "error": f"Unknown tool: {tool_name}"}

        except Exception as e:
            logger.error(f"Tool execution error: {str(e)}")
            return {"success": False, "error": str(e)}


# 创建MCP服务器实例
mcp_server = MCPServer()


@app.post("/chat")
async def chat(request: MCPRequest):
    """聊天接口"""
    response = await mcp_server.process_request(request)
    return response


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket接口"""
    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            request = MCPRequest(
                user_id=message_data.get("user_id", "default"),
                message=message_data.get("message", ""),
                context=message_data.get("context")
            )

            response = await mcp_server.process_request(request)

            await websocket.send_text(json.dumps({
                "success": response.success,
                "message": response.message,
                "data": response.data,
                "tool_calls": response.tool_calls,
                "error": response.error
            }))

    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close()


@app.get("/")
async def get():
    """主页"""
    return HTMLResponse("""
    <html>
        <head>
            <title>YOLO-LLM MCP Server</title>
        </head>
        <body>
            <h1>YOLO-LLM MCP Server</h1>
            <p>基于 DeepSeek 大模型的智能工作流服务</p>
            <p>端点:</p>
            <ul>
                <li>POST /chat - HTTP聊天接口</li>
                <li>WS /ws - WebSocket实时通信</li>
            </ul>
        </body>
    </html>
    """)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "tools": list(tools.keys())}


if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host=MCP_CONFIG["host"],
        port=MCP_CONFIG["port"],
        reload=MCP_CONFIG["debug"]
    )