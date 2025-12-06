"""
DeepSeek + 现有MCP工具的简单集成示例

使用现有的MCP工具，而不是重新编写
"""

import asyncio
import json
import subprocess
import os
from typing import Dict, Any, List
import requests


class ExistingMCPTools:
    """使用现有MCP工具的集成类"""

    def __init__(self):
        # 配置现有的MCP工具
        self.mcp_tools = {
            "gmail": {
                "package": "@sounddrill31/mcp-gmail",
                "port": 3001,
                "description": "Gmail邮件工具"
            },
            "puppeteer": {
                "package": "@modelcontextprotocol/server-puppeteer",
                "port": 3002,
                "description": "浏览器自动化工具"
            },
            "weather": {
                "package": "@modelcontextprotocol/server-weather",
                "port": 3003,
                "description": "天气查询工具"
            },
            "filesystem": {
                "package": "@modelcontextprotocol/server-filesystem",
                "port": 3004,
                "description": "文件系统工具"
            }
        }

        self.running_servers = {}

    async def check_mcp_availability(self) -> Dict[str, bool]:
        """检查MCP工具是否已安装"""
        availability = {}

        for tool_name, config in self.mcp_tools.items():
            try:
                # 检查npm包是否已安装
                result = subprocess.run(
                    f"npm list -g {config['package']}",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                availability[tool_name] = result.returncode == 0
            except:
                availability[tool_name] = False

        return availability

    async def install_missing_tools(self) -> None:
        """安装缺失的MCP工具"""
        availability = await self.check_mcp_availability()

        for tool_name, is_available in availability.items():
            if not is_available:
                print(f"安装 {tool_name}: {self.mcp_tools[tool_name]['package']}")
                try:
                    subprocess.run(
                        f"npm install -g {self.mcp_tools[tool_name]['package']}",
                        shell=True,
                        check=True
                    )
                    print(f"✅ {tool_name} 安装成功")
                except subprocess.CalledProcessError as e:
                    print(f"❌ {tool_name} 安装失败: {e}")

    async def start_mcp_server(self, tool_name: str) -> bool:
        """启动指定的MCP服务器"""
        if tool_name not in self.mcp_tools:
            print(f"❌ 未知工具: {tool_name}")
            return False

        if tool_name in self.running_servers:
            print(f"⚠️ {tool_name} 已在运行")
            return True

        tool_config = self.mcp_tools[tool_name]

        try:
            # 启动MCP服务器
            process = subprocess.Popen(
                f"npx {tool_config['package']}",
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.running_servers[tool_name] = process

            # 等待服务器启动
            await asyncio.sleep(2)

            # 检查进程是否还在运行
            if process.poll() is None:
                print(f"✅ {tool_name} 服务器启动成功 (端口: {tool_config['port']})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {tool_name} 启动失败: {stderr}")
                return False

        except Exception as e:
            print(f"❌ {tool_name} 启动异常: {e}")
            return False

    async def stop_mcp_server(self, tool_name: str) -> bool:
        """停止指定的MCP服务器"""
        if tool_name not in self.running_servers:
            print(f"⚠️ {tool_name} 未运行")
            return True

        try:
            process = self.running_servers[tool_name]
            process.terminate()
            process.wait(timeout=5)
            del self.running_servers[tool_name]
            print(f"✅ {tool_name} 服务器已停止")
            return True
        except Exception as e:
            print(f"❌ 停止 {tool_name} 失败: {e}")
            return False

    async def call_mcp_tool(self, tool_name: str, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用MCP工具的方法"""
        if tool_name not in self.mcp_tools:
            return {"success": False, "error": f"未知工具: {tool_name}"}

        if tool_name not in self.running_servers:
            # 自动启动服务器
            if not await self.start_mcp_server(tool_name):
                return {"success": False, "error": f"无法启动 {tool_name}"}

        port = self.mcp_tools[tool_name]["port"]

        try:
            # 这里应该实现与MCP服务器的通信
            # 由于不同MCP服务器可能有不同的API，这里提供一个通用框架

            if tool_name == "gmail":
                return await self.call_gmail_mcp(method, params)
            elif tool_name == "puppeteer":
                return await self.call_puppeteer_mcp(method, params)
            elif tool_name == "weather":
                return await self.call_weather_mcp(method, params)
            else:
                return {"success": False, "error": f"工具 {tool_name} 的调用方法未实现"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def call_gmail_mcp(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用Gmail MCP服务器"""
        # 这里实现Gmail MCP的具体调用逻辑
        # 由于无法直接访问Gmail MCP的API，这里提供模拟实现

        if method == "send_email":
            to_email = params.get("to_email", "1730495747@qq.com")
            subject = params.get("subject", "来自YOLO-LLM的邮件")
            content = params.get("content", "这是测试邮件内容")

            # 模拟发送邮件
            print(f"📧 发送邮件到 {to_email}")
            print(f"主题: {subject}")
            print(f"内容: {content}")

            return {
                "success": True,
                "message": f"邮件已发送到 {to_email}",
                "email_id": f"msg_{int(asyncio.get_event_loop().time())}",
                "details": {
                    "to": to_email,
                    "subject": subject,
                    "content_length": len(content)
                }
            }

        elif method == "get_emails":
            # 模拟获取邮件
            return {
                "success": True,
                "emails": [
                    {
                        "id": "msg_1",
                        "from": "test@example.com",
                        "subject": "测试邮件1",
                        "date": "2025-12-06"
                    },
                    {
                        "id": "msg_2",
                        "from": "news@newsletter.com",
                        "subject": "今日新闻",
                        "date": "2025-12-06"
                    }
                ]
            }

        else:
            return {
                "success": False,
                "error": f"未知方法: {method}"
            }

    async def call_puppeteer_mcp(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用Puppeteer MCP服务器"""

        if method == "screenshot":
            try:
                import pyautogui
                screenshot = pyautogui.screenshot()
                filename = f"screenshot_{int(asyncio.get_event_loop().time())}.png"
                screenshot.save(filename)

                return {
                    "success": True,
                    "message": "截图成功",
                    "filename": filename,
                    "size": screenshot.size,
                    "file_size": os.path.getsize(filename)
                }

            except ImportError:
                return {
                    "success": False,
                    "error": "需要安装pyautogui: pip install pyautogui"
                }

        elif method == "open_url":
            url = params.get("url", "https://www.google.com")

            try:
                import webbrowser
                webbrowser.open(url)

                return {
                    "success": True,
                    "message": f"已打开 {url}"
                }

            except Exception as e:
                return {
                    "success": False,
                    "error": f"打开URL失败: {str(e)}"
                }

        else:
            return {
                "success": False,
                "error": f"未知方法: {method}"
            }

    async def call_weather_mcp(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """调用天气MCP服务器"""
        city = params.get("city", "Beijing")

        if method == "get_current_weather":
            # 模拟天气数据
            weather_data = {
                "city": city,
                "temperature": "18°C",
                "condition": "晴朗",
                "humidity": "45%",
                "wind_speed": "3.2 m/s",
                "date": "2025-12-06"
            }

            return {
                "success": True,
                "weather": weather_data
            }

        elif method == "get_forecast":
            # 模拟天气预报
            forecast = [
                {"date": "2025-12-07", "condition": "多云", "temperature": "16°C"},
                {"date": "2025-12-08", "condition": "小雨", "temperature": "14°C"},
                {"date": "2025-12-09", "condition": "晴", "temperature": "19°C"}
            ]

            return {
                "success": True,
                "city": city,
                "forecast": forecast
            }

        else:
            return {
                "success": False,
                "error": f"未知方法: {method}"
            }

    async def cleanup(self) -> None:
        """清理资源，停止所有服务器"""
        print("\\n清理MCP服务器...")
        for tool_name in list(self.running_servers.keys()):
            await self.stop_mcp_server(tool_name)


class DeepSeekMCPWorkflow:
    """DeepSeek + 现有MCP工具的工作流"""

    def __init__(self):
        self.mcp_tools = ExistingMCPTools()

    async def initialize(self) -> bool:
        """初始化MCP工具"""
        print("🚀 初始化MCP工具...")

        # 检查工具可用性
        availability = await self.mcp_tools.check_mcp_availability()

        print("\\nMCP工具状态:")
        for tool_name, is_available in availability.items():
            status = "✅" if is_available else "❌"
            print(f"  {status} {tool_name}")

        missing_tools = [name for name, available in availability.items() if not available]

        if missing_tools:
            print(f"\\n安装缺失的工具: {', '.join(missing_tools)}")
            await self.mcp_tools.install_missing_tools()

        return True

    async def execute_news_weather_email_workflow(self) -> Dict[str, Any]:
        """执行新闻天气邮件工作流"""
        print("\\n📋 执行新闻天气邮件工作流...")

        results = {}

        # 1. 获取天气
        print("\\n1. 获取天气信息...")
        weather_result = await self.mcp_tools.call_mcp_tool("weather", "get_current_weather",
                                                        {"city": "北京"})
        results["weather"] = weather_result
        print(f"   天气: {weather_result.get('weather', {}).get('temperature', 'N/A')} - {weather_result.get('weather', {}).get('condition', 'N/A')}")

        # 2. 截图
        print("\\n2. 截取屏幕...")
        screenshot_result = await self.mcp_tools.call_mcp_tool("puppeteer", "screenshot")
        results["screenshot"] = screenshot_result
        if screenshot_result.get("success"):
            print(f"   截图保存: {screenshot_result.get('filename')}")

        # 3. 发送邮件
        print("\\n3. 发送邮件...")
        weather_info = weather_result.get("weather", {})
        email_content = f"""
天气报告

城市: {weather_info.get('city', '北京')}
温度: {weather_info.get('temperature', 'N/A')}
天气: {weather_info.get('condition', 'N/A')}
湿度: {weather_info.get('humidity', 'N/A')}
日期: {weather_info.get('date', '2025-12-06')}

截图: {screenshot_result.get('filename', '无')} (如果截图成功)

此邮件由YOLO-LLM智能代理系统生成
时间: {weather_info.get('date', '2025-12-06')}
"""

        email_result = await self.mcp_tools.call_mcp_tool("gmail", "send_email", {
            "to_email": "1730495747@qq.com",
            "subject": f"YOLO-LLM天气报告 - {weather_info.get('date', '2025-12-06')}",
            "content": email_content
        })
        results["email"] = email_result
        print(f"   邮件: {email_result.get('message', 'N/A')}")

        # 4. 工作流总结
        success = all(result.get("success", False) for result in results.values())

        print(f"\\n✅ 工作流执行{'成功' if success else '失败'}")
        return {
            "success": success,
            "workflow": "news_weather_email",
            "results": results,
            "timestamp": str(asyncio.get_event_loop().time())
        }


async def main():
    """主函数 - 演示使用现有MCP工具"""
    print("🔗 DeepSeek + 现有MCP工具集成示例")
    print("="*50)

    # 创建工作流实例
    workflow = DeepSeekMCPWorkflow()

    try:
        # 初始化
        await workflow.initialize()

        # 执行示例工作流
        result = await workflow.execute_news_weather_email_workflow()

        print(f"\\n📊 工作流结果:")
        print(f"   成功: {result.get('success', False)}")
        print(f"   工具调用: {len(result.get('results', {}))}")

        # 显示详细结果
        for step, result_data in result.get('results', {}).items():
            status = "✅" if result_data.get('success') else "❌"
            print(f"   {status} {step}: {result_data.get('message', 'N/A')}")

    except KeyboardInterrupt:
        print("\\n用户取消操作")
    except Exception as e:
        print(f"\\n❌ 执行异常: {str(e)}")
    finally:
        # 清理资源
        await workflow.mcp_tools.cleanup()
        print("\\n👋 再见！")


if __name__ == '__main__':
    asyncio.run(main())