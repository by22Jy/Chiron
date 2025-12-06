"""
MCP 客户端

用于与 DeepSeek MCP 服务器通信的客户端
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
import requests
import websockets
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MCPMessage:
    """MCP消息"""
    user_id: str
    message: str
    context: Optional[Dict[str, Any]] = None


class MCPClient:
    """MCP客户端"""

    def __init__(self, server_url: str = "http://localhost:8081"):
        self.server_url = server_url
        self.ws_url = server_url.replace("http://", "ws://") + "/ws"

    async def send_message(self, user_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """发送消息到MCP服务器"""

        try:
            # 使用HTTP接口
            response = requests.post(
                f"{self.server_url}/chat",
                json={
                    "user_id": user_id,
                    "message": message,
                    "context": context
                },
                timeout=30
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"MCP请求失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "MCP服务器通信失败"
            }

    async def send_websocket_message(self, user_id: str, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """通过WebSocket发送消息"""

        try:
            async with websockets.connect(self.ws_url) as websocket:
                message_data = {
                    "user_id": user_id,
                    "message": message,
                    "context": context
                }

                await websocket.send(json.dumps(message_data))
                response = await websocket.recv()

                return json.loads(response)

        except Exception as e:
            logger.error(f"WebSocket请求失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "WebSocket连接失败"
            }

    async def check_health(self) -> Dict[str, Any]:
        """检查MCP服务器健康状态"""

        try:
            response = requests.get(f"{self.server_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()

        except Exception as e:
            logger.error(f"健康检查失败: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }


class DeepSeekWorkflowClient:
    """基于DeepSeek的工作流客户端"""

    def __init__(self, mcp_client: MCPClient = None):
        self.mcp_client = mcp_client or MCPClient()
        self.user_id = "yolo_llm_user"

    async def execute_workflow(self, workflow_request: str) -> Dict[str, Any]:
        """执行工作流请求"""

        try:
            # 构建工作流上下文
            context = {
                "workflow_type": "intelligent",
                "timestamp": str(asyncio.get_event_loop().time()),
                "tools_available": ["email", "news", "weather", "system", "screenshot"]
            }

            # 发送到MCP服务器
            response = await self.mcp_client.send_message(
                user_id=self.user_id,
                message=workflow_request,
                context=context
            )

            return response

        except Exception as e:
            logger.error(f"工作流执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "workflow_request": workflow_request
            }

    async def execute_news_weather_workflow(self) -> Dict[str, Any]:
        """执行新闻天气工作流"""

        workflow_request = """
        请帮我完成以下任务：
        1. 获取今日头条新闻Top10
        2. 获取当前天气信息
        3. 打开记事本并记录这些信息
        4. 截取记事本窗口
        5. 发送邮件到1730495747@qq.com，包含新闻、天气信息和截图

        请按步骤执行，并在每个步骤完成后告知我进度。
        """

        return await self.execute_workflow(workflow_request)

    async def execute_email_workflow(self, recipient: str, content: str = None) -> Dict[str, Any]:
        """执行邮件发送工作流"""

        if not content:
            content = "这是由YOLO-LLM智能代理自动生成的测试邮件。"

        workflow_request = f"""
        请帮我发送邮件到 {recipient}，内容如下：
        {content}

        如果需要额外的信息或确认，请告诉我。
        """

        return await self.execute_workflow(workflow_request)

    async def execute_news_workflow(self, count: int = 10) -> Dict[str, Any]:
        """执行新闻获取工作流"""

        workflow_request = f"""
        请帮我获取今日头条新闻Top{count}，并进行以下操作：
        1. 获取新闻
        2. 分析新闻内容
        3. 生成新闻摘要
        4. 如果有重要新闻，建议是否需要发送通知
        """

        return await self.execute_workflow(workflow_request)

    async def execute_weather_workflow(self, city: str = "北京") -> Dict[str, Any]:
        """执行天气查询工作流"""

        workflow_request = f"""
        请帮我查询{city}的天气信息，包括：
        1. 当前天气状况
        2. 天气分析和建议
        3. 3天天气预报
        4. 根据天气给出活动建议
        """

        return await self.execute_workflow(workflow_request)

    async def chat_with_deepseek(self, message: str) -> Dict[str, Any]:
        """与DeepSeek进行对话"""

        return await self.execute_workflow(message)


# 便捷函数
async def create_workflow_client() -> DeepSeekWorkflowClient:
    """创建工作流客户端"""
    return DeepSeekWorkflowClient()


async def quick_workflow_test() -> Dict[str, Any]:
    """快速工作流测试"""

    client = await create_workflow_client()

    # 测试健康检查
    health = await client.mcp_client.check_health()
    print(f"MCP服务器状态: {health}")

    # 测试简单对话
    response = await client.chat_with_deepseek("你好，请介绍一下你的功能")
    print(f"DeepSeek回复: {response}")

    return response


if __name__ == '__main__':
    async def main():
        """主函数 - 测试MCP客户端"""
        print("测试MCP客户端...")
        print("="*50)

        # 创建客户端
        client = DeepSeekWorkflowClient()

        # 测试健康检查
        print("检查MCP服务器状态...")
        health = await client.mcp_client.check_health()
        print(f"服务器状态: {health}")

        # 测试简单对话
        print("\\n测试对话功能...")
        response = await client.chat_with_deepseek("你好，请介绍一下你的功能")
        print(f"DeepSeek回复: {response.get('message', '无回复')}")

        # 测试新闻天气工作流
        print("\\n测试新闻天气工作流...")
        workflow_response = await client.execute_news_weather_workflow()
        print(f"工作流结果: {workflow_response.get('success', False)}")
        if workflow_response.get('tool_calls'):
            print(f"调用工具: {[tool.get('name') for tool in workflow_response['tool_calls']]}")

    # 运行测试
    asyncio.run(main())