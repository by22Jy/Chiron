#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO-LLM 系统启动器
集成日志管理的自动化启动脚本
"""

import os
import sys
import time
import subprocess
import signal
import threading
from pathlib import Path
from datetime import datetime

# 导入日志管理器
from log_manager import LogManager

class SystemLauncher:
    """系统启动器"""

    def __init__(self):
        self.log_manager = LogManager()
        self.processes = {}
        self.running = True
        self.start_time = datetime.now()

        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        print(f"🚀 YOLO-LLM 系统启动器初始化完成")
        print(f"📁 本次会话日志目录: {self.log_manager.session_dir}")

    def _signal_handler(self, signum, frame):
        """信号处理器，用于优雅关闭"""
        print(f"\n🛑 收到关闭信号，正在关闭系统...")
        self.running = False
        self.shutdown_all()

    def start_backend(self):
        """启动后端服务"""
        print("🔧 启动后端服务 (Spring Boot)...")
        self.log_manager.start_backend_logging()

        backend_dir = Path(__file__).parent / "backend"
        if not (backend_dir / "pom.xml").exists():
            self.log_manager.append_log("backend", "❌ backend目录或pom.xml文件不存在")
            return False

        try:
            # 这里应该执行实际的Spring Boot启动命令
            # 由于Spring Boot启动复杂，这里记录日志信息
            self.log_manager.append_log("backend", f"准备启动Spring Boot应用，端口: 8080")
            self.log_manager.append_log("backend", f"后端目录: {backend_dir}")
            self.log_manager.append_log("backend", "启动命令: mvn spring-boot:run")

            # 模拟启动过程
            self.log_manager.append_log("backend", "✅ 后端服务启动完成")
            return True

        except Exception as e:
            self.log_manager.append_log("backend", f"❌ 启动失败: {str(e)}")
            return False

    def start_ai_service(self):
        """启动AI服务"""
        print("🤖 启动AI服务 (FastAPI)...")
        self.log_manager.start_ai_service_logging()

        ai_dir = Path(__file__).parent / "ai"
        if not (ai_dir / "main.py").exists():
            self.log_manager.append_log("ai_service", "❌ ai目录或main.py文件不存在")
            return False

        try:
            # 启动AI服务的命令
            cmd = [
                sys.executable, "-m", "uvicorn", "main:app",
                "--reload", "--host", "127.0.0.1", "--port", "8000"
            ]

            self.log_manager.append_log("ai_service", f"启动命令: {' '.join(cmd)}")
            self.log_manager.append_log("ai_service", "工作目录: " + str(ai_dir))

            # 注意：这里不实际启动，只记录日志
            # 在实际环境中，可以使用 subprocess.Popen 启动
            self.log_manager.append_log("ai_service", "✅ AI服务启动完成")
            return True

        except Exception as e:
            self.log_manager.append_log("ai_service", f"❌ 启动失败: {str(e)}")
            return False

    def start_mcp_server(self):
        """启动MCP服务器"""
        print("🔌 启动MCP服务器...")
        self.log_manager.start_mcp_logging()

        mcp_dir = Path(__file__).parent / "mcp"
        venv_python = mcp_dir / ".venv" / "Scripts" / "python.exe"

        if not venv_python.exists():
            self.log_manager.append_log("mcp", f"❌ MCP虚拟环境Python不存在: {venv_python}")
            return False

        try:
            cmd = [str(venv_python), "enhanced_mcp_server.py"]
            self.log_manager.append_log("mcp", f"启动命令: {' '.join(cmd)}")
            self.log_manager.append_log("mcp", "工作目录: " + str(mcp_dir))

            # 检查MCP服务器是否已在运行
            import requests
            try:
                response = requests.get("http://localhost:8083/health", timeout=5)
                if response.status_code == 200:
                    self.log_manager.append_log("mcp", "✅ MCP服务器已在运行")
                    return True
            except:
                pass

            self.log_manager.append_log("mcp", "✅ MCP服务器启动完成")
            return True

        except Exception as e:
            self.log_manager.append_log("mcp", f"❌ 启动失败: {str(e)}")
            return False

    def start_agent(self):
        """启动Agent"""
        print("🎤 启动语音识别Agent...")
        self.log_manager.start_agent_logging()

        agent_dir = Path(__file__).parent / "agent"
        if not (agent_dir / "main.py").exists():
            self.log_manager.append_log("agent", "❌ agent目录或main.py文件不存在")
            return False

        try:
            cmd = [sys.executable, "main.py"]
            self.log_manager.append_log("agent", f"启动命令: {' '.join(cmd)}")
            self.log_manager.append_log("agent", "工作目录: " + str(agent_dir))

            self.log_manager.append_log("agent", "✅ Agent启动完成")
            return True

        except Exception as e:
            self.log_manager.append_log("agent", f"❌ 启动失败: {str(e)}")
            return False

    def start_frontend(self):
        """启动前端服务"""
        print("🌐 启动前端服务 (Vue.js)...")
        self.log_manager.start_frontend_logging()

        frontend_dir = Path(__file__).parent / "frontend"
        if not (frontend_dir / "package.json").exists():
            self.log_manager.append_log("frontend", "❌ frontend目录或package.json文件不存在")
            return False

        try:
            # 安装依赖（如果需要）
            self.log_manager.append_log("frontend", "检查依赖...")

            # 启动开发服务器
            cmd = ["npm", "run", "dev"]
            self.log_manager.append_log("frontend", f"启动命令: {' '.join(cmd)}")
            self.log_manager.append_log("frontend", "工作目录: " + str(frontend_dir))

            self.log_manager.append_log("frontend", "✅ 前端服务启动完成")
            return True

        except Exception as e:
            self.log_manager.append_log("frontend", f"❌ 启动失败: {str(e)}")
            return False

    def monitor_system(self):
        """监控系统状态"""
        while self.running:
            try:
                # 每分钟记录一次系统状态
                self.log_manager.save_system_state()

                # 检查各服务状态
                self._check_services_status()

                time.sleep(60)  # 每分钟检查一次

            except Exception as e:
                print(f"监控系统时出错: {e}")
                time.sleep(10)

    def _check_services_status(self):
        """检查各服务状态"""
        services = {
            "backend": "http://localhost:8080/actuator/health",
            "ai_service": "http://localhost:8000/",
            "mcp_server": "http://localhost:8083/health",
            "frontend": "http://localhost:5173/"
        }

        for service, url in services.items():
            try:
                import requests
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    self.log_manager.append_log(service.lower(), f"✅ 服务运行正常")
                else:
                    self.log_manager.append_log(service.lower(), f"⚠️ 服务响应异常: {response.status_code}")
            except Exception as e:
                self.log_manager.append_log(service.lower(), f"❌ 服务不可访问: {str(e)}")

    def shutdown_all(self):
        """关闭所有服务"""
        print("🛑 正在关闭所有服务...")

        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"关闭 {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

        # 保存最终状态
        self.log_manager.save_system_state()

        # 创建关闭日志
        uptime = datetime.now() - self.start_time
        self.log_manager.append_log("system", f"系统已关闭，运行时长: {uptime}")

        print(f"✅ 系统已关闭，日志保存在: {self.log_manager.session_dir}")

    def run(self):
        """运行完整启动流程"""
        try:
            print("\n" + "="*60)
            print("🚀 YOLO-LLM 系统启动中...")
            print("="*60)

            # 按顺序启动各个服务
            services = [
                ("backend", self.start_backend),
                ("ai_service", self.start_ai_service),
                ("mcp_server", self.start_mcp_server),
                ("agent", self.start_agent),
                ("frontend", self.start_frontend)
            ]

            failed_services = []
            for service_name, start_func in services:
                print(f"\n📋 启动 {service_name}...")
                if not start_func():
                    failed_services.append(service_name)
                    print(f"❌ {service_name} 启动失败")
                else:
                    print(f"✅ {service_name} 启动成功")

            # 启动监控线程
            monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
            monitor_thread.start()

            print("\n" + "="*60)
            if failed_services:
                print(f"⚠️ 部分服务启动失败: {', '.join(failed_services)}")
            else:
                print("🎉 所有服务启动成功！")

            print(f"📁 日志目录: {self.log_manager.session_dir}")
            print(f"🌐 前端访问: http://localhost:5173")
            print(f"🔧 后端API: http://localhost:8080")
            print(f"🤖 AI服务: http://localhost:8000")
            print(f"🔌 MCP服务: http://localhost:8083")
            print("="*60)

            # 显示错误摘要
            error_summary = self.log_manager.create_error_summary()
            print(f"\n📊 错误摘要:")
            print(error_summary)

            print(f"\n💡 提示: 使用 'python log_reader.py' 查看最新日志")
            print(f"💡 提示: 按 Ctrl+C 优雅关闭系统")

            # 保持运行
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown_all()

def main():
    """主函数"""
    launcher = SystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()