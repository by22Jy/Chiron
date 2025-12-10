#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试日志管理系统
"""

import os
import sys
import datetime
from pathlib import Path
import json

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def test_log_system():
    """测试日志系统"""
    print("="*60)
    print("YOLO-LLM 日志管理系统测试")
    print("="*60)

    # 创建测试日志目录
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    # 创建测试会话
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = logs_dir / f"test_session_{timestamp}"
    session_dir.mkdir(exist_ok=True)

    print(f"创建测试会话目录: {session_dir}")

    # 创建各模块日志目录
    modules = ["backend", "ai_service", "mcp", "agent", "frontend"]
    for module in modules:
        module_dir = session_dir / module
        module_dir.mkdir(exist_ok=True)

    # 创建测试日志文件
    test_logs = {
        "backend": [
            "[2025-12-10 15:20:00] Spring Boot 应用启动中...",
            "[2025-12-10 15:20:05] 数据库连接成功",
            "[2025-12-10 15:20:10] 后端服务启动完成，端口: 8080"
        ],
        "mcp": [
            "[2025-12-10 15:20:15] MCP服务器启动中...",
            "[2025-12-10 15:20:20] 已加载工具: news, weather, email",
            "[2025-12-10 15:20:25] MCP服务器启动完成，端口: 8083"
        ],
        "agent": [
            "[2025-12-10 15:20:30] 语音识别模块加载中...",
            "[2025-12-10 15:20:35] 麦克风初始化成功",
            "[2025-12-10 15:20:40] 语音识别Agent启动完成"
        ]
    }

    # 写入测试日志
    for module, logs in test_logs.items():
        log_file = session_dir / module / f"{module}.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            for log in logs:
                f.write(log + "\n")
        print(f"创建 {module} 日志文件: {log_file}")

    # 创建会话信息文件
    session_info = {
        "session_id": session_dir.name,
        "start_time": datetime.datetime.now().isoformat(),
        "platform": sys.platform,
        "modules": {
            "backend": {"status": "completed", "port": 8080},
            "ai_service": {"status": "pending", "port": 8000},
            "mcp_server": {"status": "completed", "port": 8083},
            "agent": {"status": "completed", "port": None},
            "frontend": {"status": "pending", "port": 5173}
        }
    }

    info_file = session_dir / "session_info.json"
    with open(info_file, 'w', encoding='utf-8') as f:
        json.dump(session_info, f, indent=2, ensure_ascii=False)

    print(f"创建会话信息文件: {info_file}")

    # 测试读取日志
    print("\n" + "="*60)
    print("测试日志读取:")
    print("="*60)

    for module in ["backend", "mcp", "agent"]:
        log_file = session_dir / module / f"{module}.log"
        if log_file.exists():
            print(f"\n{module.upper()} 日志内容:")
            print("-" * 40)
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    print(f"  {line.strip()}")

    # 测试错误检测
    print("\n" + "="*60)
    print("测试错误检测:")
    print("="*60)

    # 添加一些错误日志
    error_logs = [
        "[2025-12-10 15:21:00] ERROR: 数据库连接失败",
        "[2025-12-10 15:21:05] Exception: 模块加载失败",
        "[2025-12-10 15:21:10] FAILED: 启动服务失败"
    ]

    backend_log = session_dir / "backend" / "backend.log"
    with open(backend_log, 'a', encoding='utf-8') as f:
        for error in error_logs:
            f.write(error + "\n")

    print("已添加测试错误日志")

    # 检测错误
    print("\n检测到的错误:")
    error_count = 0
    for module in modules:
        log_file = session_dir / module / f"{module}.log"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if any(keyword in line.lower() for keyword in ['error', 'exception', 'failed', '错误']):
                        print(f"  {module}: {line.strip()}")
                        error_count += 1

    if error_count == 0:
        print("  未发现错误")
    else:
        print(f"  共发现 {error_count} 个错误")

    print("\n" + "="*60)
    print("测试完成!")
    print("="*60)
    print(f"日志目录: {logs_dir}")
    print(f"测试会话: {session_dir}")
    print("\n使用方法:")
    print("  python log_reader.py -h  # 查看帮助")
    print("  python log_reader.py     # 查看最新日志")
    print("  python log_reader.py -e  # 查看错误信息")
    print("  view_logs.bat            # 使用交互式菜单")

if __name__ == "__main__":
    test_log_system()