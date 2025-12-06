"""
执行基于MCP的工作流

使用DeepSeek大模型和MCP工具链完成用户任务
"""

import asyncio
import sys
import os
import json
from typing import Dict, Any, List

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp.mcp_client import DeepSeekWorkflowClient, create_workflow_client


class MCPWorkflowExecutor:
    """MCP工作流执行器"""

    def __init__(self):
        self.client = None
        self.workflow_history = []

    async def initialize(self):
        """初始化MCP客户端"""
        try:
            self.client = await create_workflow_client()

            # 检查MCP服务器状态
            health = await self.client.mcp_client.check_health()
            if health.get("status") == "healthy":
                print("✅ MCP服务器连接成功")
                return True
            else:
                print("❌ MCP服务器连接失败")
                print("请先启动MCP服务器: python mcp/server.py")
                return False

        except Exception as e:
            print(f"❌ 初始化失败: {str(e)}")
            return False

    async def execute_complete_workflow(self) -> Dict[str, Any]:
        """执行完整工作流"""
        print("\\n" + "="*60)
        print("执行基于DeepSeek + MCP的智能工作流")
        print("="*60)

        workflow_request = """
        请帮我完成以下完整任务：
        1. 获取今日头条新闻Top10
        2. 获取当前天气信息（北京）
        3. 打开记事本应用程序
        4. 将新闻和天气信息记录到记事本
        5. 截取记事本窗口截图
        6. 发送邮件到1730495747@qq.com，包含所有内容

        请按步骤执行，在每个步骤完成后告诉我进度。
        如果遇到问题，请提供解决方案。
        """

        print("发送工作流请求到DeepSeek...")
        response = await self.client.execute_workflow(workflow_request)

        # 记录到历史
        self.workflow_history.append({
            "timestamp": str(asyncio.get_event_loop().time()),
            "request": workflow_request,
            "response": response
        })

        return response

    async def execute_interactive_workflow(self) -> None:
        """交互式工作流执行"""
        print("\\n" + "="*60)
        print("DeepSeek + MCP 交互式工作流")
        print("="*60)
        print("请输入您的任务需求，DeepSeek将智能执行:")
        print("- 获取新闻天气")
        print("- 发送邮件")
        print("- 截图操作")
        print("- 系统操作")
        print("- 或者任何其他任务")
        print("输入 'quit' 退出")
        print("="*60)

        while True:
            try:
                user_input = input("\\n请输入任务: ").strip()

                if user_input.lower() in ['quit', 'exit', '退出']:
                    print("感谢使用！")
                    break

                if not user_input:
                    continue

                print(f"\\n🤖 DeepSeek正在分析您的需求: {user_input}")
                print("⏳ 正在执行...")

                # 发送到DeepSeek
                response = await self.client.chat_with_deepseek(user_input)

                if response.get("success"):
                    print(f"\\n💬 DeepSeek回复:")
                    print(f"{response.get('message', '')}")

                    # 显示工具调用
                    if response.get("tool_calls"):
                        print(f"\\n🔧 调用工具: {[tool.get('name') for tool in response['tool_calls']]}")

                        # 显示工具结果
                        if response.get("data", {}).get("tool_results"):
                            print("\\n📊 工具执行结果:")
                            for result in response["data"]["tool_results"]:
                                if result.get("success"):
                                    print(f"✅ {result.get('action', '未知操作')} - 成功")
                                else:
                                    print(f"❌ {result.get('action', '未知操作')} - {result.get('error', '失败')}")
                else:
                    print(f"❌ 执行失败: {response.get('error', '未知错误')}")

                # 记录历史
                self.workflow_history.append({
                    "timestamp": str(asyncio.get_event_loop().time()),
                    "user_input": user_input,
                    "response": response
                })

            except KeyboardInterrupt:
                print("\\n用户取消操作")
                break
            except Exception as e:
                print(f"❌ 执行异常: {str(e)}")

    async def show_workflow_history(self) -> None:
        """显示工作流历史"""
        print("\\n" + "="*60)
        print("工作流执行历史")
        print("="*60)

        if not self.workflow_history:
            print("暂无工作流历史记录")
            return

        for i, record in enumerate(self.workflow_history, 1):
            print(f"\\n[{i}] 时间: {record['timestamp']}")
            print(f"请求: {record.get('request', record.get('user_input', ''))[:100]}...")
            print(f"成功: {'是' if record['response'].get('success') else '否'}")
            if record['response'].get('tool_calls'):
                tools = [tool.get('name') for tool in record['response']['tool_calls']]
                print(f"工具: {', '.join(tools)}")

    async def test_individual_tools(self) -> None:
        """测试各个工具"""
        print("\\n" + "="*60)
        print("测试MCP工具")
        print("="*60)

        tools_to_test = [
            ("新闻工具", "获取今日头条新闻Top5"),
            ("天气工具", "查询北京当前天气"),
            ("邮件工具", "准备发送邮件到test@example.com"),
            ("系统工具", "检查系统状态"),
            ("截图工具", "准备截图操作")
        ]

        for tool_name, test_request in tools_to_test:
            print(f"\\n🧪 测试 {tool_name}: {test_request}")
            print("⏳ 正在执行...")

            response = await self.client.chat_with_deepseek(test_request)

            if response.get("success"):
                print(f"✅ {tool_name} 测试通过")
                print(f"回复: {response.get('message', '')[:100]}...")
            else:
                print(f"❌ {tool_name} 测试失败: {response.get('error', '')}")

            # 短暂延迟
            await asyncio.sleep(1)

    async def generate_workflow_report(self) -> None:
        """生成工作流报告"""
        print("\\n" + "="*60)
        print("生成工作流报告")
        print("="*60)

        if not self.workflow_history:
            print("暂无数据生成报告")
            return

        # 统计信息
        total_requests = len(self.workflow_history)
        successful_requests = sum(1 for r in self.workflow_history if r['response'].get('success'))
        tool_usage = {}

        for record in self.workflow_history:
            if record['response'].get('tool_calls'):
                for tool in record['response']['tool_calls']:
                    tool_name = tool.get('name', 'unknown')
                    tool_usage[tool_name] = tool_usage.get(tool_name, 0) + 1

        report = f"""
📊 工作流执行报告
{'='*40}
总请求数: {total_requests}
成功请求数: {successful_requests}
成功率: {successful_requests/total_requests*100:.1f}%

工具使用统计:
"""

        for tool, count in sorted(tool_usage.items()):
            report += f"- {tool}: {count}次\\n"

        print(report)

        # 保存报告到文件
        report_data = {
            "generated_time": str(asyncio.get_event_loop().time()),
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": successful_requests/total_requests*100,
            "tool_usage": tool_usage,
            "history_count": len(self.workflow_history)
        }

        try:
            with open("mcp_workflow_report.json", "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print("📄 报告已保存到: mcp_workflow_report.json")
        except Exception as e:
            print(f"❌ 保存报告失败: {str(e)}")


async def main():
    """主函数"""
    print("🚀 YOLO-LLM DeepSeek + MCP 工作流系统")
    print("="*60)

    # 初始化
    executor = MCPWorkflowExecutor()

    if not await executor.initialize():
        print("请先启动MCP服务器:")
        print("cd mcp && python server.py")
        return

    # 显示菜单
    while True:
        print("\\n" + "="*40)
        print("请选择操作:")
        print("1. 执行完整工作流 (新闻+天气+邮件+截图)")
        print("2. 交互式工作流 (自由对话)")
        print("3. 测试各个工具")
        print("4. 查看工作流历史")
        print("5. 生成工作流报告")
        print("6. 退出")
        print("="*40)

        try:
            choice = input("\\n请输入选择 (1-6): ").strip()

            if choice == "1":
                response = await executor.execute_complete_workflow()
                print(f"\\n工作流执行结果: {'成功' if response.get('success') else '失败'}")
                if response.get("message"):
                    print(f"DeepSeek回复: {response['message']}")

            elif choice == "2":
                await executor.execute_interactive_workflow()

            elif choice == "3":
                await executor.test_individual_tools()

            elif choice == "4":
                await executor.show_workflow_history()

            elif choice == "5":
                await executor.generate_workflow_report()

            elif choice == "6":
                print("感谢使用YOLO-LLM MCP工作流系统！")
                break

            else:
                print("无效选择，请重新输入")

        except KeyboardInterrupt:
            print("\\n用户取消操作")
            break
        except Exception as e:
            print(f"❌ 操作异常: {str(e)}")


if __name__ == '__main__':
    asyncio.run(main())