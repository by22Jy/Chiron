#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO-LLM 日志管理系统
自动收集、整理和管理各模块日志
"""

import os
import sys
import time
import datetime
import subprocess
import threading
import shutil
from pathlib import Path
from typing import Dict, List, Optional
import json

class LogManager:
    """日志管理器"""

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent / "logs"
        self.base_dir.mkdir(exist_ok=True)

        # 创建当前会话的日志目录
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_dir = self.base_dir / f"session_{timestamp}"
        self.session_dir.mkdir(exist_ok=True)

        # 子模块日志目录
        self.backend_dir = self.session_dir / "backend"
        self.ai_service_dir = self.session_dir / "ai_service"
        self.agent_dir = self.session_dir / "agent"
        self.mcp_dir = self.session_dir / "mcp"
        self.frontend_dir = self.session_dir / "frontend"

        for dir_path in [self.backend_dir, self.ai_service_dir, self.agent_dir, self.mcp_dir, self.frontend_dir]:
            dir_path.mkdir(exist_ok=True)

        # 日志进程记录
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self.log_files: Dict[str, str] = {}

        # 创建会话信息文件
        self._create_session_info()

        print(f"📁 日志管理器启动，会话目录: {self.session_dir}")

    def _create_session_info(self):
        """创建会话信息文件"""
        session_info = {
            "session_id": self.session_dir.name,
            "start_time": datetime.datetime.now().isoformat(),
            "platform": sys.platform,
            "python_version": sys.version,
            "working_directory": os.getcwd(),
            "modules": {
                "backend": {"status": "pending", "port": 8080},
                "ai_service": {"status": "pending", "port": 8000},
                "mcp_server": {"status": "pending", "port": 8083},
                "agent": {"status": "pending"},
                "frontend": {"status": "pending", "port": 5173}
            }
        }

        info_file = self.session_dir / "session_info.json"
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(session_info, f, indent=2, ensure_ascii=False)

    def start_backend_logging(self):
        """启动后端日志记录"""
        log_file = self.backend_dir / "spring-boot.log"
        self.log_files["backend"] = str(log_file)

        # 这里应该与实际的Spring Boot启动集成
        print(f"📝 后端日志将记录到: {log_file}")
        self._update_module_status("backend", "logging")

    def start_ai_service_logging(self):
        """启动AI服务日志记录"""
        log_file = self.ai_service_dir / "fastapi.log"
        self.log_files["ai_service"] = str(log_file)
        print(f"📝 AI服务日志将记录到: {log_file}")
        self._update_module_status("ai_service", "logging")

    def start_mcp_logging(self):
        """启动MCP服务器日志记录"""
        log_file = self.mcp_dir / "mcp_server.log"
        self.log_files["mcp"] = str(log_file)
        print(f"📝 MCP服务器日志将记录到: {log_file}")
        self._update_module_status("mcp_server", "logging")

        # 如果MCP服务器已在运行，开始收集其日志
        self._collect_existing_mcp_logs()

    def start_agent_logging(self):
        """启动Agent日志记录"""
        log_file = self.agent_dir / "agent.log"
        self.log_files["agent"] = str(log_file)
        print(f"📝 Agent日志将记录到: {log_file}")
        self._update_module_status("agent", "logging")

    def start_frontend_logging(self):
        """启动前端日志记录"""
        log_file = self.frontend_dir / "frontend.log"
        self.log_files["frontend"] = str(log_file)
        print(f"📝 前端日志将记录到: {log_file}")
        self._update_module_status("frontend", "logging")

    def _collect_existing_mcp_logs(self):
        """收集已存在的MCP服务器日志"""
        try:
            # 这里可以连接到正在运行的MCP服务器获取日志
            # 或者从MCP服务器的输出流中读取
            pass
        except Exception as e:
            print(f"收集MCP日志时出错: {e}")

    def _update_module_status(self, module: str, status: str):
        """更新模块状态"""
        info_file = self.session_dir / "session_info.json"
        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if module in data["modules"]:
                data["modules"][module]["status"] = status
                data["modules"][module]["last_update"] = datetime.datetime.now().isoformat()

            with open(info_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"更新模块状态时出错: {e}")

    def append_log(self, module: str, content: str):
        """向指定模块的日志文件追加内容"""
        if module in self.log_files:
            try:
                with open(self.log_files[module], 'a', encoding='utf-8') as f:
                    timestamp = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")
                    f.write(timestamp + content + "\n")
            except Exception as e:
                print(f"写入{module}日志时出错: {e}")

    def get_latest_session_dir(self) -> Optional[Path]:
        """获取最新的会话日志目录"""
        sessions = [d for d in self.base_dir.iterdir() if d.is_dir() and d.name.startswith("session_")]
        if not sessions:
            return None

        # 按时间戳排序，返回最新的
        latest_session = max(sessions, key=lambda x: x.name)
        return latest_session

    def get_session_logs(self, session_name: str = None) -> Dict[str, List[str]]:
        """获取指定会话的所有日志内容"""
        if session_name:
            session_dir = self.base_dir / session_name
        else:
            session_dir = self.get_latest_session_dir()

        if not session_dir or not session_dir.exists():
            return {}

        logs = {}
        for module_dir in session_dir.iterdir():
            if module_dir.is_dir():
                logs[module_dir.name] = []
                for log_file in module_dir.glob("*.log"):
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            logs[module_dir.name].extend(f.readlines())
                    except Exception as e:
                        print(f"读取日志文件{log_file}时出错: {e}")

        return logs

    def create_error_summary(self) -> str:
        """创建错误摘要"""
        logs = self.get_session_logs()
        error_summary = []

        for module, log_lines in logs.items():
            errors = [line for line in log_lines if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', '错误'])]
            if errors:
                error_summary.append(f"\n🔴 {module.upper()} 模块错误:")
                for i, error in enumerate(errors[-5:], 1):  # 只显示最后5个错误
                    error_summary.append(f"  {i}. {error.strip()}")

        if not error_summary:
            return "🟢 未发现错误"

        return "\n".join(error_summary)

    def save_system_state(self):
        """保存当前系统状态快照"""
        state_file = self.session_dir / f"system_state_{datetime.datetime.now().strftime('%H%M%S')}.json"

        try:
            # 收集系统状态信息
            state = {
                "timestamp": datetime.datetime.now().isoformat(),
                "active_processes": len(self.active_processes),
                "log_files": {k: v for k, v in self.log_files.items()},
                "disk_usage": {
                    "total": shutil.disk_usage('/').total if os.name != 'nt' else shutil.disk_usage('C:').total,
                    "free": shutil.disk_usage('/').free if os.name != 'nt' else shutil.disk_usage('C:').free
                }
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)

            print(f"💾 系统状态已保存到: {state_file}")

        except Exception as e:
            print(f"保存系统状态时出错: {e}")

    def cleanup_old_sessions(self, keep_count: int = 10):
        """清理旧的会话日志，只保留最新的几个"""
        sessions = [d for d in self.base_dir.iterdir() if d.is_dir() and d.name.startswith("session_")]
        sessions.sort(key=lambda x: x.name, reverse=True)

        for old_session in sessions[keep_count:]:
            try:
                shutil.rmtree(old_session)
                print(f"🗑️ 已清理旧会话: {old_session.name}")
            except Exception as e:
                print(f"清理会话{old_session.name}时出错: {e}")

# 全局日志管理器实例
log_manager = LogManager()

def get_log_manager() -> LogManager:
    """获取全局日志管理器实例"""
    return log_manager

if __name__ == "__main__":
    # 测试日志管理器
    lm = LogManager()

    # 启动各模块日志记录
    lm.start_backend_logging()
    lm.start_ai_service_logging()
    lm.start_mcp_logging()
    lm.start_agent_logging()
    lm.start_frontend_logging()

    # 测试日志写入
    lm.append_log("backend", "后端服务启动中...")
    lm.append_log("mcp", "MCP服务器已在端口8083启动")
    lm.append_log("agent", "语音识别模块加载完成")

    # 显示错误摘要
    print("\n" + "="*50)
    print(lm.create_error_summary())

    print(f"\n✅ 日志管理系统已启动，会话目录: {lm.session_dir}")
    print(f"📁 最新日志目录: {lm.get_latest_session_dir()}")