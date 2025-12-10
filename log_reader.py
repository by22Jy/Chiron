#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO-LLM 日志读取和分析工具
快速查看和分析系统日志
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import json
from log_manager import LogManager

class LogReader:
    """日志读取器"""

    def __init__(self):
        self.log_manager = LogManager()

    def show_latest_logs(self, module: str = None, lines: int = 50):
        """显示最新的日志"""
        latest_session = self.log_manager.get_latest_session_dir()
        if not latest_session:
            print("❌ 没有找到日志会话")
            return

        print(f"📁 最新会话日志: {latest_session}")
        print("=" * 80)

        if module:
            self._show_module_logs(latest_session, module, lines)
        else:
            self._show_all_logs(latest_session, lines)

    def _show_module_logs(self, session_dir: Path, module: str, lines: int):
        """显示指定模块的日志"""
        module_dir = session_dir / module
        if not module_dir.exists():
            print(f"❌ 模块 {module} 的日志目录不存在")
            return

        log_files = list(module_dir.glob("*.log"))
        if not log_files:
            print(f"❌ 模块 {module} 没有日志文件")
            return

        print(f"\n🔍 {module.upper()} 模块最新日志 (最后 {lines} 行):")
        print("-" * 60)

        for log_file in log_files:
            print(f"\n📄 文件: {log_file.name}")
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    all_lines = f.readlines()
                    recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

                    for line in recent_lines:
                        print(line.rstrip())

            except Exception as e:
                print(f"❌ 读取日志文件失败: {e}")

    def _show_all_logs(self, session_dir: Path, lines: int):
        """显示所有模块的日志摘要"""
        modules = ["backend", "ai_service", "mcp", "agent", "frontend"]

        for module in modules:
            module_dir = session_dir / module
            if not module_dir.exists():
                continue

            log_files = list(module_dir.glob("*.log"))
            if not log_files:
                continue

            print(f"\n🔍 {module.upper()} 模块日志摘要:")
            print("-" * 40)

            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        all_lines = f.readlines()
                        recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines

                        # 显示关键信息
                        for line in recent_lines:
                            line = line.strip()
                            if any(keyword in line.lower() for keyword in
                                  ['error', 'failed', 'exception', '启动', '完成', '成功']):
                                print(f"  {line}")

                except Exception as e:
                    print(f"  ❌ 读取失败: {e}")

    def show_errors_only(self, session_name: str = None):
        """只显示错误信息"""
        if session_name:
            session_dir = self.log_manager.base_dir / session_name
        else:
            session_dir = self.log_manager.get_latest_session_dir()

        if not session_dir or not session_dir.exists():
            print("❌ 没有找到日志会话")
            return

        print(f"🔍 错误日志分析: {session_dir.name}")
        print("=" * 80)

        modules = ["backend", "ai_service", "mcp", "agent", "frontend"]
        found_errors = False

        for module in modules:
            module_dir = session_dir / module
            if not module_dir.exists():
                continue

            log_files = list(module_dir.glob("*.log"))
            if not log_files:
                continue

            module_errors = []
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for line in lines:
                            if any(keyword in line.lower() for keyword in
                                  ['error', 'exception', 'failed', '错误', '失败', '异常']):
                                module_errors.append(line.strip())
                except Exception:
                    continue

            if module_errors:
                found_errors = True
                print(f"\n🔴 {module.upper()} 模块错误:")
                for i, error in enumerate(module_errors[-10:], 1):  # 只显示最后10个错误
                    print(f"  {i}. {error}")

        if not found_errors:
            print("🟢 未发现错误信息")

    def show_session_info(self, session_name: str = None):
        """显示会话信息"""
        if session_name:
            session_dir = self.log_manager.base_dir / session_name
        else:
            session_dir = self.log_manager.get_latest_session_dir()

        if not session_dir or not session_dir.exists():
            print("❌ 没有找到日志会话")
            return

        info_file = session_dir / "session_info.json"
        if not info_file.exists():
            print("❌ 会话信息文件不存在")
            return

        try:
            with open(info_file, 'r', encoding='utf-8') as f:
                info = json.load(f)

            print(f"📊 会话信息: {session_dir.name}")
            print("=" * 50)
            print(f"开始时间: {info['start_time']}")
            print(f"平台: {info['platform']}")
            print(f"Python版本: {info['python_version']}")

            print(f"\n🔧 模块状态:")
            for module, details in info['modules'].items():
                status_icon = "🟢" if details['status'] in ['completed', 'logging'] else "🟡"
                print(f"  {status_icon} {module}: {details['status']} (端口: {details.get('port', 'N/A')})")

        except Exception as e:
            print(f"❌ 读取会话信息失败: {e}")

    def list_sessions(self):
        """列出所有会话"""
        sessions = [d for d in self.log_manager.base_dir.iterdir()
                   if d.is_dir() and d.name.startswith("session_")]

        if not sessions:
            print("❌ 没有找到日志会话")
            return

        sessions.sort(key=lambda x: x.name, reverse=True)

        print("📁 所有日志会话:")
        print("=" * 60)

        for session in sessions:
            info_file = session / "session_info.json"
            try:
                with open(info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)

                start_time = info['start_time']
                print(f"📂 {session.name}")
                print(f"   开始时间: {start_time}")

                # 显示模块状态
                modules = info.get('modules', {})
                completed = sum(1 for m in modules.values() if m['status'] in ['completed', 'logging'])
                total = len(modules)
                print(f"   模块状态: {completed}/{total} 完成")

            except Exception:
                print(f"📂 {session.name} (信息不可读取)")

            print()

    def watch_logs(self, module: str = None):
        """实时监控日志"""
        print(f"👀 实时监控日志 (Ctrl+C 退出)")
        if module:
            print(f"📝 模块: {module}")
        else:
            print("📝 所有模块")

        try:
            import time
            last_content = {}

            while True:
                latest_session = self.log_manager.get_latest_session_dir()
                if not latest_session:
                    print("❌ 没有找到日志会话")
                    time.sleep(2)
                    continue

                # 检查新日志内容
                if module:
                    modules = [module]
                else:
                    modules = ["backend", "ai_service", "mcp", "agent", "frontend"]

                new_content_found = False
                for mod in modules:
                    module_dir = latest_session / mod
                    if not module_dir.exists():
                        continue

                    for log_file in module_dir.glob("*.log"):
                        try:
                            with open(log_file, 'r', encoding='utf-8') as f:
                                content = f.read()

                            key = str(log_file)
                            if key not in last_content:
                                last_content[key] = ""

                            new_content = content[len(last_content[key]):]
                            if new_content.strip():
                                for line in new_content.strip().split('\n'):
                                    if line.strip():
                                        timestamp = datetime.now().strftime("%H:%M:%S")
                                        print(f"[{timestamp}] {mod}: {line}")
                                        new_content_found = True

                            last_content[key] = content

                        except Exception:
                            continue

                if not new_content_found:
                    time.sleep(1)

        except KeyboardInterrupt:
            print(f"\n👋 停止监控")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="YOLO-LLM 日志读取和分析工具")
    parser.add_argument("--module", "-m", help="指定模块 (backend/ai_service/mcp/agent/frontend)")
    parser.add_argument("--lines", "-l", type=int, default=50, help="显示的行数 (默认: 50)")
    parser.add_argument("--errors", "-e", action="store_true", help="只显示错误信息")
    parser.add_argument("--session", "-s", help="指定会话名称")
    parser.add_argument("--info", "-i", action="store_true", help="显示会话信息")
    parser.add_argument("--list", action="store_true", help="列出所有会话")
    parser.add_argument("--watch", "-w", action="store_true", help="实时监控日志")

    args = parser.parse_args()

    reader = LogReader()

    try:
        if args.list:
            reader.list_sessions()
        elif args.errors:
            reader.show_errors_only(args.session)
        elif args.info:
            reader.show_session_info(args.session)
        elif args.watch:
            reader.watch_logs(args.module)
        else:
            reader.show_latest_logs(args.module, args.lines)

    except KeyboardInterrupt:
        print(f"\n👋 退出")
    except Exception as e:
        print(f"❌ 执行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()