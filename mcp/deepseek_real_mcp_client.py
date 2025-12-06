"""
DeepSeek + 真实MCP工具集成客户端

使用官方认证的MCP服务器，而非自定义实现
"""

import asyncio
import json
import subprocess
import httpx
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class RealMCPServerManager:
    """管理真实的MCP服务器"""

    def __init__(self, config_file: str = "real_mcp_config.json"):
        self.config_file = Path(__file__).parent / config_file
        self.servers_config = self._load_config()
        self.running_servers = {}
        self.server_ports = {
            "filesystem": 3001,
            "email": 3002,
            "playwright": 3003,
            "puppeteer": 3004,
            "weather": 3005,
            "brave-search": 3006,
            "github": 3007,
            "slack": 3008,
            "git": 3009,
            "memory": 3010,
            "postgres": 3011,
            "sqlite": 3012
        }

    def _load_config(self) -> Dict[str, Any]:
        """加载MCP服务器配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    async def check_mcp_availability(self) -> Dict[str, bool]:
        """检查MCP工具是否已安装"""
        availability = {}
        npm_packages = [
            "@modelcontextprotocol/server-filesystem",
            "@modelcontextprotocol/server-email",
            "@modelcontextprotocol/server-playwright",
            "@modelcontextprotocol/server-puppeteer",
            "@modelcontextprotocol/server-weather",
            "@modelcontextprotocol/server-brave-search",
            "@modelcontextprotocol/server-github",
            "@modelcontextprotocol/server-slack",
            "@modelcontextprotocol/server-git",
            "@modelcontextprotocol/server-memory",
            "@modelcontextprotocol/server-postgres",
            "@modelcontextprotocol/server-sqlite"
        ]

        for package in npm_packages:
            tool_name = package.split('/')[-1].replace('server-', '')
            try:
                result = subprocess.run(
                    f"npm list -g {package}",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                availability[tool_name] = result.returncode == 0
                status = "✅" if availability[tool_name] else "❌"
                print(f"{status} {package}")
            except subprocess.TimeoutExpired:
                availability[tool_name] = False
                print(f"❌ {package} - 检查超时")
            except Exception as e:
                availability[tool_name] = False
                print(f"❌ {package} - {str(e)}")

        return availability

    async def install_real_mcp_tools(self) -> None:
        """安装真实的MCP工具"""
        print("📦 安装官方MCP工具...")

        # 核心工具包
        core_packages = [
            "@modelcontextprotocol/server-filesystem",
            "@modelcontextprotocol/server-email",
            "@modelcontextprotocol/server-playwright",
            "@modelcontextprotocol/server-weather"
        ]

        # 开发工具包
        dev_packages = [
            "@modelcontextprotocol/server-git",
            "@modelcontextprotocol/server-github",
            "@modelcontextprotocol/server-memory"
        ]

        # 数据库工具包
        db_packages = [
            "@modelcontextprotocol/server-sqlite"
        ]

        all_packages = core_packages + dev_packages + db_packages

        for package in all_packages:
            print(f"安装 {package}...")
            try:
                result = subprocess.run(
                    f"npm install -g {package}",
                    shell=True,
                    check=True,
                    timeout=120
                )
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安装失败: {e}")
            except subprocess.TimeoutExpired:
                print(f"❌ {package} 安装超时")

    async def start_mcp_server(self, server_name: str) -> bool:
        """启动指定的MCP服务器"""
        if server_name not in self.servers_config:
            print(f"❌ 未知服务器: {server_name}")
            return False

        if server_name in self.running_servers:
            print(f"⚠️ {server_name} 已在运行")
            return True

        server_config = self.servers_config[server_name]
        port = self.server_ports.get(server_name, 3000)

        try:
            # 启动MCP服务器，指定端口
            command = f"{server_config['command']} {' '.join(server_config['args'])} --port {port}"

            # 设置环境变量
            env = os.environ.copy()
            if 'env' in server_config:
                env.update(server_config['env'])

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )

            self.running_servers[server_name] = {
                'process': process,
                'port': port,
                'config': server_config
            }

            # 等待服务器启动
            await asyncio.sleep(3)

            # 检查进程是否还在运行
            if process.poll() is None:
                print(f"✅ {server_name} 服务器启动成功 (端口: {port})")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {server_name} 启动失败: {stderr.decode()}")
                return False

        except Exception as e:
            print(f"❌ 启动 {server_name} 异常: {e}")
            return False

    async def stop_mcp_server(self, server_name: str) -> bool:
        """停止指定的MCP服务器"""
        if server_name not in self.running_servers:
            print(f"⚠️ {server_name} 未运行")
            return True

        try:
            server_info = self.running_servers[server_name]
            process = server_info['process']
            process.terminate()
            process.wait(timeout=5)
            del self.running_servers[server_name]
            print(f"✅ {server_name} 服务器已停止")
            return True
        except Exception as e:
            print(f"❌ 停止 {server_name} 失败: {e}")
            return False

    async def cleanup(self) -> None:
        """清理资源，停止所有服务器"""
        print("\n清理MCP服务器...")
        for server_name in list(self.running_servers.keys()):
            await self.stop_mcp_server(server_name)


class DeepSeekRealMCPClient:
    """DeepSeek + 真实MCP工具集成客户端"""

    def __init__(self, deepseek_api_key: str = None):
        self.deepseek_api_key = deepseek_api_key or os.getenv("DEEPSEEK_API_KEY")
        self.mcp_manager = RealMCPServerManager()
        self.session = None

    async def initialize(self) -> bool:
        """初始化MCP工具"""
        print("🚀 初始化真实MCP工具...")

        # 检查工具可用性
        availability = await self.mcp_manager.check_mcp_availability()

        print(f"\nMCP工具状态:")
        for tool_name, is_available in availability.items():
            status = "✅" if is_available else "❌"
            print(f"  {status} {tool_name}")

        missing_tools = [name for name, available in availability.items() if not available]

        if missing_tools:
            print(f"\n缺失工具: {', '.join(missing_tools)}")
            choice = input("是否安装缺失的工具? (y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                await self.mcp_manager.install_real_mcp_tools()

        # 创建HTTP会话
        self.session = httpx.AsyncClient(timeout=30.0)
        return True

    async def analyze_request_with_deepseek(self, user_request: str) -> Dict[str, Any]:
        """使用DeepSeek分析用户请求"""
        if not self.deepseek_api_key:
            return {
                "success": False,
                "error": "DeepSeek API密钥未设置"
            }

        # 构建提示词
        system_prompt = """
你是一个智能助手，可以调用多种MCP工具来完成用户任务。

可用的MCP工具：
1. filesystem - 文件系统操作
2. email - 邮件发送
3. playwright/puppeteer - 浏览器自动化
4. weather - 天气查询
5. brave-search - 网络搜索
6. github - GitHub操作
7. git - 版本控制
8. memory - 持久化记忆
9. sqlite - 数据库操作

请分析用户请求，确定需要调用的工具和执行步骤。
返回JSON格式：
{
    "tools_needed": ["tool1", "tool2"],
    "execution_plan": [
        {"step": 1, "action": "描述", "tool": "tool_name"},
        {"step": 2, "action": "描述", "tool": "tool_name"}
    ],
    "reasoning": "分析原因"
}
"""

        try:
            # 调用DeepSeek API
            response = await self.session.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_request}
                    ],
                    "temperature": 0.1
                }
            )

            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]

                # 尝试解析JSON
                try:
                    analysis = json.loads(content)
                    return {"success": True, "analysis": analysis}
                except json.JSONDecodeError:
                    return {"success": True, "analysis": {"reasoning": content}}

            return {"success": False, "error": f"DeepSeek API错误: {response.status_code}"}

        except Exception as e:
            return {"success": False, "error": f"分析请求失败: {str(e)}"}

    async def execute_mcp_workflow(self, user_request: str) -> Dict[str, Any]:
        """执行MCP工作流"""
        print(f"\n🤖 DeepSeek分析请求: {user_request}")

        # 1. 使用DeepSeek分析请求
        analysis_result = await self.analyze_request_with_deepseek(user_request)

        if not analysis_result.get("success"):
            return analysis_result

        analysis = analysis_result.get("analysis", {})
        tools_needed = analysis.get("tools_needed", [])
        execution_plan = analysis.get("execution_plan", [])

        print(f"📋 分析结果:")
        print(f"   需要工具: {tools_needed}")
        print(f"   执行步骤: {len(execution_plan)}")

        # 2. 启动需要的MCP服务器
        results = {}
        for tool_name in tools_needed:
            print(f"🔧 启动 {tool_name} 服务器...")
            if await self.mcp_manager.start_mcp_server(tool_name):
                results[tool_name] = {"status": "started", "success": True}
            else:
                results[tool_name] = {"status": "failed", "success": False}

        # 3. 模拟执行工作流步骤
        workflow_results = []
        for step in execution_plan:
            step_result = {
                "step": step.get("step"),
                "action": step.get("action"),
                "tool": step.get("tool"),
                "status": "simulated",
                "message": f"模拟执行: {step.get('action')}"
            }
            workflow_results.append(step_result)

        return {
            "success": True,
            "analysis": analysis,
            "mcp_servers": results,
            "workflow_results": workflow_results,
            "user_request": user_request
        }

    async def test_all_mcp_tools(self) -> Dict[str, Any]:
        """测试所有MCP工具"""
        print("\n🧪 测试所有MCP工具...")

        test_results = {}

        # 测试文件系统
        print("\n测试文件系统工具...")
        if await self.mcp_manager.start_mcp_server("filesystem"):
            test_results["filesystem"] = {
                "success": True,
                "message": "文件系统服务器启动成功"
            }
        else:
            test_results["filesystem"] = {
                "success": False,
                "message": "文件系统服务器启动失败"
            }

        # 测试邮件工具
        print("\n测试邮件工具...")
        if await self.mcp_manager.start_mcp_server("email"):
            test_results["email"] = {
                "success": True,
                "message": "邮件服务器启动成功"
            }
        else:
            test_results["email"] = {
                "success": False,
                "message": "邮件服务器启动失败"
            }

        # 测试浏览器自动化
        print("\n测试Playwright工具...")
        if await self.mcp_manager.start_mcp_server("playwright"):
            test_results["playwright"] = {
                "success": True,
                "message": "Playwright服务器启动成功"
            }
        else:
            test_results["playwright"] = {
                "success": False,
                "message": "Playwright服务器启动失败"
            }

        return {
            "success": True,
            "test_results": test_results,
            "total_tests": len(test_results),
            "passed": sum(1 for r in test_results.values() if r["success"])
        }

    async def close(self):
        """关闭客户端"""
        if self.session:
            await self.session.aclose()
        await self.mcp_manager.cleanup()


async def main():
    """主函数 - 演示真实MCP工具集成"""
    print("🔗 DeepSeek + 真实MCP工具集成测试")
    print("=" * 60)

    # 创建客户端
    client = DeepSeekRealMCPClient()

    try:
        # 初始化
        if not await client.initialize():
            print("❌ 初始化失败")
            return

        # 测试所有工具
        test_result = await client.test_all_mcp_tools()
        print(f"\n📊 测试结果:")
        print(f"   总测试数: {test_result.get('total_tests', 0)}")
        print(f"   通过数: {test_result.get('passed', 0)}")

        # 示例工作流
        example_requests = [
            "获取今日新闻并发送邮件到1730495747@qq.com",
            "查询北京天气并记录到文件",
            "打开GitHub并查看项目状态"
        ]

        for request in example_requests:
            print(f"\n" + "="*60)
            result = await client.execute_mcp_workflow(request)

            if result.get("success"):
                print(f"✅ 工作流分析成功")
                tools = result.get("mcp_servers", {})
                started_tools = [name for name, info in tools.items() if info.get("success")]
                print(f"   启动的工具: {started_tools}")
            else:
                print(f"❌ 工作流失败: {result.get('error', '未知错误')}")

        # 保持运行状态
        print(f"\n按Enter键退出...")
        input()

    except KeyboardInterrupt:
        print("\n用户取消操作")
    except Exception as e:
        print(f"\n❌ 执行异常: {str(e)}")
    finally:
        # 清理资源
        await client.close()
        print("\n👋 再见！")


if __name__ == '__main__':
    asyncio.run(main())