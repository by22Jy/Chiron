"""
启动 MCP 系统的便捷脚本
"""

import os
import sys
import subprocess
import time
import asyncio
from pathlib import Path


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    print(f"✅ Python版本: {sys.version}")
    return True


def check_dependencies():
    """检查依赖"""
    print("检查依赖包...")

    required_packages = [
        "fastapi", "uvicorn", "websockets", "httpx",
        "requests", "psutil", "pyautogui", "Pillow"
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - 未安装")

    if missing_packages:
        print(f"\\n缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False

    print("✅ 所有依赖包已安装")
    return True


def setup_environment():
    """设置环境"""
    print("设置环境...")

    # 设置DeepSeek API密钥
    deepseek_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_key:
        print("⚠️ DEEPSEEK_API_KEY 环境变量未设置")
        print("请设置您的DeepSeek API密钥:")
        print("export DEEPSEEK_API_KEY='your-api-key-here'")
        print("或者在启动前设置环境变量")
    else:
        print("✅ DeepSeek API密钥已设置")

    # 创建截图目录
    screenshot_dir = Path("./screenshots")
    screenshot_dir.mkdir(exist_ok=True)
    print(f"✅ 截图目录: {screenshot_dir.absolute()}")

    return True


async def start_mcp_server():
    """启动MCP服务器"""
    print("\\n启动MCP服务器...")

    try:
        # 启动服务器进程
        process = subprocess.Popen([
            sys.executable, "server.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # 等待服务器启动
        print("等待服务器启动...")
        await asyncio.sleep(3)

        # 检查进程是否还在运行
        if process.poll() is None:
            print("✅ MCP服务器启动成功")
            print("🌐 服务器地址: http://localhost:8081")
            print("📡 WebSocket地址: ws://localhost:8081/ws")
            print("📊 健康检查: http://localhost:8081/health")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ MCP服务器启动失败")
            print(f"错误: {stderr.decode()}")
            return None

    except Exception as e:
        print(f"❌ 启动MCP服务器失败: {str(e)}")
        return None


async def test_mcp_connection():
    """测试MCP连接"""
    print("\\n测试MCP连接...")

    try:
        import httpx

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("http://localhost:8081/health")

        if response.status_code == 200:
            print("✅ MCP服务器连接正常")
            health_data = response.json()
            print(f"状态: {health_data.get('status', 'unknown')}")
            print(f"可用工具: {health_data.get('tools', [])}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 连接测试失败: {str(e)}")
        return False


async def start_workflow_executor():
    """启动工作流执行器"""
    print("\\n启动工作流执行器...")

    try:
        # 导入工作流执行器
        sys.path.insert(0, str(Path(__file__).parent))
        from execute_mcp_workflow import MCPWorkflowExecutor

        executor = MCPWorkflowExecutor()

        if await executor.initialize():
            print("✅ 工作流执行器初始化成功")
            print("\\n现在可以使用以下功能:")
            print("1. 执行完整工作流 (新闻+天气+邮件+截图)")
            print("2. 与DeepSeek进行智能对话")
            print("3. 使用各种MCP工具")

            # 启动交互式工作流
            await executor.execute_interactive_workflow()
        else:
            print("❌ 工作流执行器初始化失败")

    except Exception as e:
        print(f"❌ 启动工作流执行器失败: {str(e)}")


def show_usage():
    """显示使用说明"""
    print("\\n" + "="*60)
    print("YOLO-LLM MCP 系统使用说明")
    print("="*60)

    print("\\n📋 功能特性:")
    print("✅ DeepSeek大模型集成")
    print("✅ 智能邮件发送")
    print("✅ 实时新闻获取")
    print("✅ 天气信息查询")
    print("✅ 系统操作控制")
    print("✅ 智能截图功能")
    print("✅ 自然语言交互")

    print("\\n🔧 配置要求:")
    print("1. 设置DeepSeek API密钥:")
    print("   export DEEPSEEK_API_KEY='your-api-key'")
    print("\\n2. 安装依赖:")
    print("   pip install -r requirements.txt")
    print("\\n3. 启动系统:")
    print("   python start_mcp.py")

    print("\\n📞 工作流示例:")
    print("- 获取今日新闻并发送邮件")
    print("- 查询天气并给出建议")
    print("- 截图并处理图片")
    print("- 自动化系统操作")

    print("\\n🌐 API端点:")
    print("- HTTP API: http://localhost:8081/chat")
    print("- WebSocket: ws://localhost:8081/ws")
    print("- 健康检查: http://localhost:8081/health")


async def main():
    """主函数"""
    print("🚀 YOLO-LLM DeepSeek + MCP 系统启动器")
    print("="*60)

    # 检查环境
    if not check_python_version():
        return

    if not check_dependencies():
        return

    if not setup_environment():
        return

    show_usage()

    # 询问用户是否启动
    try:
        choice = input("\\n是否启动MCP系统? (y/n): ").strip().lower()

        if choice in ['y', 'yes', '是']:
            # 启动MCP服务器
            server_process = await start_mcp_server()

            if server_process:
                # 测试连接
                if await test_mcp_connection():
                    # 启动工作流执行器
                    await start_workflow_executor()

                # 关闭服务器
                print("\\n关闭MCP服务器...")
                server_process.terminate()
                server_process.wait()
            else:
                print("❌ 无法启动MCP服务器")

        else:
            print("用户取消启动")

    except KeyboardInterrupt:
        print("\\n用户取消操作")
    except Exception as e:
        print(f"❌ 启动异常: {str(e)}")


if __name__ == '__main__':
    asyncio.run(main())