#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO-LLM 系统真实启动器
实际启动服务并集成日志管理
"""

import os
import sys
import time
import subprocess
import signal
import threading
import requests
from pathlib import Path
from datetime import datetime

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from log_manager import LogManager

class RealSystemLauncher:
    """真实系统启动器"""

    def __init__(self):
        self.log_manager = LogManager()
        self.processes = {}
        self.running = True
        self.start_time = datetime.now()

        # 注册信号处理器
        if hasattr(signal, 'SIGINT'):
            signal.signal(signal.SIGINT, self._signal_handler)
        if hasattr(signal, 'SIGTERM'):
            signal.signal(signal.SIGTERM, self._signal_handler)

        print(f"[SYSTEM] YOLO-LLM 系统启动器初始化完成")
        print(f"[SYSTEM] 本次会话日志目录: {self.log_manager.session_dir}")

    def _signal_handler(self, signum, frame):
        """信号处理器，用于优雅关闭"""
        print(f"\n[SYSTEM] 收到关闭信号，正在关闭系统...")
        self.running = False
        self.shutdown_all()

    def _start_process_with_logging(self, name: str, cmd: list, cwd: str = None):
        """启动进程并记录日志"""
        try:
            self.log_manager.append_log(name, f"启动命令: {' '.join(cmd)}")
            if cwd:
                self.log_manager.append_log(name, f"工作目录: {cwd}")

            # 启动进程
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )

            # 启动日志收集线程
            def collect_logs():
                for line in process.stdout:
                    if line.strip():
                        self.log_manager.append_log(name, line.strip())

            log_thread = threading.Thread(target=collect_logs, daemon=True)
            log_thread.start()

            self.processes[name] = process
            self.log_manager.append_log(name, f"✅ 进程已启动，PID: {process.pid}")
            return True

        except Exception as e:
            self.log_manager.append_log(name, f"❌ 启动失败: {str(e)}")
            return False

    def start_mcp_server(self):
        """启动MCP服务器"""
        print("[SYSTEM] 启动MCP服务器...")
        self.log_manager.start_mcp_logging()

        mcp_dir = Path(__file__).parent / "mcp"
        venv_python = mcp_dir / ".venv" / "Scripts" / "python.exe"

        if not venv_python.exists():
            self.log_manager.append_log("mcp", f"❌ MCP虚拟环境Python不存在: {venv_python}")
            print("[SYSTEM] ❌ MCP虚拟环境不存在，请先运行: cd mcp && python -m venv .venv")
            return False

        # 检查是否已经在运行
        try:
            response = requests.get("http://localhost:8083/health", timeout=5)
            if response.status_code == 200:
                self.log_manager.append_log("mcp", "✅ MCP服务器已在运行")
                print("[SYSTEM] ✅ MCP服务器已在运行")
                return True
        except:
            pass

        cmd = [str(venv_python), "enhanced_mcp_server.py"]
        return self._start_process_with_logging("mcp", cmd, str(mcp_dir))

    def start_ai_service(self):
        """启动AI服务"""
        print("[SYSTEM] 启动AI服务...")
        self.log_manager.start_ai_service_logging()

        ai_dir = Path(__file__).parent / "ai"
        if not (ai_dir / "main.py").exists():
            self.log_manager.append_log("ai_service", "❌ ai目录或main.py文件不存在")
            return False

        cmd = [sys.executable, "-m", "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000"]
        return self._start_process_with_logging("ai_service", cmd, str(ai_dir))

    def start_agent(self):
        """启动Agent"""
        print("[SYSTEM] 启动语音识别Agent...")
        self.log_manager.start_agent_logging()

        agent_dir = Path(__file__).parent / "agent"
        if not (agent_dir / "main.py").exists():
            self.log_manager.append_log("agent", "❌ agent目录或main.py文件不存在")
            return False

        cmd = [sys.executable, "main.py"]
        return self._start_process_with_logging("agent", cmd, str(agent_dir))

    def start_frontend(self):
        """启动前端服务"""
        print("[SYSTEM] 启动前端服务...")
        self.log_manager.start_frontend_logging()

        frontend_dir = Path(__file__).parent / "frontend"
        if not (frontend_dir / "package.json").exists():
            self.log_manager.append_log("frontend", "❌ frontend目录或package.json文件不存在")
            return False

        # 检查node_modules是否存在
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists():
            self.log_manager.append_log("frontend", "安装依赖中...")
            install_cmd = ["npm", "install"]
            install_process = subprocess.run(install_cmd, cwd=str(frontend_dir), capture_output=True, text=True)
            if install_process.returncode != 0:
                self.log_manager.append_log("frontend", f"❌ 依赖安装失败: {install_process.stderr}")
                return False
            self.log_manager.append_log("frontend", "✅ 依赖安装完成")

        cmd = ["npm", "run", "dev"]
        return self._start_process_with_logging("frontend", cmd, str(frontend_dir))

    def wait_for_service(self, name: str, url: str, timeout: int = 30):
        """等待服务启动"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    self.log_manager.append_log(name, f"✅ 服务就绪: {url}")
                    return True
            except:
                pass
            time.sleep(2)

        self.log_manager.append_log(name, f" 服务启动超时: {url}")
        return False

    def monitor_system(self):
        """监控系统状态"""
        while self.running:
            try:
                # 检查进程状态
                for name, process in list(self.processes.items()):
                    if process and process.poll() is not None:
                        self.log_manager.append_log(name, f"❌ 进程意外退出，返回码: {process.returncode}")
                        del self.processes[name]

                time.sleep(10)  # 每10秒检查一次

            except Exception as e:
                self.log_manager.append_log("system", f"监控出错: {str(e)}")
                time.sleep(5)

    def shutdown_all(self):
        """关闭所有服务"""
        print("[SYSTEM] 正在关闭所有服务...")

        for name, process in self.processes.items():
            if process and process.poll() is None:
                print(f"[SYSTEM] 关闭 {name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()

        # 保存最终状态
        self.log_manager.save_system_state()
        uptime = datetime.now() - self.start_time
        self.log_manager.append_log("system", f"系统已关闭，运行时长: {uptime}")

        print(f"[SYSTEM] 系统已关闭，日志保存在: {self.log_manager.session_dir}")

    def run(self):
        """运行完整启动流程"""
        try:
            print("\n" + "="*60)
            print("YOLO-LLM 系统启动中...")
            print("="*60)

            # 按顺序启动各个服务
            services = [
                ("mcp", self.start_mcp_server),
                ("ai_service", self.start_ai_service),
                ("agent", self.start_agent),
                ("frontend", self.start_frontend)
            ]

            failed_services = []
            for service_name, start_func in services:
                print(f"\n[SYSTEM] 启动 {service_name}...")
                if not start_func():
                    failed_services.append(service_name)
                    print(f"[SYSTEM] ❌ {service_name} 启动失败")
                else:
                    print(f"[SYSTEM] ✅ {service_name} 启动成功")
                    time.sleep(2)  # 给服务一些启动时间

            # 启动监控线程
            monitor_thread = threading.Thread(target=self.monitor_system, daemon=True)
            monitor_thread.start()

            # 等待服务就绪
            print("\n[SYSTEM] 等待服务就绪...")
            self.wait_for_service("mcp", "http://localhost:8083/health")
            self.wait_for_service("ai_service", "http://localhost:8000/")

            print("\n" + "="*60)
            if failed_services:
                print(f"[SYSTEM]  部分服务启动失败: {', '.join(failed_services)}")
            else:
                print("[SYSTEM] 🎉 所有服务启动成功！")

            print(f"[SYSTEM] 📁 日志目录: {self.log_manager.session_dir}")
            print(f"[SYSTEM] 🌐 前端访问: http://localhost:5173")
            print(f"[SYSTEM] 🤖 AI服务: http://localhost:8000")
            print(f"[SYSTEM] 🔌 MCP服务: http://localhost:8083")
            print("="*60)

            # 显示错误摘要
            error_summary = self.log_manager.create_error_summary()
            print(f"\n[SYSTEM] 📊 错误摘要:")
            print(error_summary)

            print(f"\n[SYSTEM] 💡 提示:")
            print(f"[SYSTEM] - 使用 'python log_reader.py' 查看最新日志")
            print(f"[SYSTEM] - 使用 'python log_reader.py -e' 查看错误信息")
            print(f"[SYSTEM] - 按 Ctrl+C 优雅关闭系统")

            # 保持运行
            while self.running:
                time.sleep(1)

        except KeyboardInterrupt:
            pass
        finally:
            self.shutdown_all()

def main():
    """主函数"""
    launcher = RealSystemLauncher()
    launcher.run()

if __name__ == "__main__":
    main()