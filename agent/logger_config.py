#!/usr/bin/env python3
"""
日志配置管理器
为系统提供统一的日志配置，包括控制台和文件输出
"""

import logging
import os
from datetime import datetime
from pathlib import Path
import sys

# 日志目录
LOG_DIR = Path(__file__).parent / "logs"

def setup_logging(component_name: str = "agent", log_level: str = "DEBUG",
                  console_output: bool = True, file_output: bool = True):
    """
    设置日志配置

    Args:
        component_name: 组件名称，用于生成日志文件名
        log_level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        console_output: 是否输出到控制台
        file_output: 是否输出到文件

    Returns:
        logger: 配置好的logger实例
    """

    # 确保日志目录存在
    if file_output:
        LOG_DIR.mkdir(exist_ok=True)

    # 创建logger
    logger = logging.getLogger(component_name)
    logger.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))

    # 清除现有的handlers，避免重复
    logger.handlers.clear()

    # 定义日志格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s [%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 文件输出handler
    if file_output:
        # 生成带时间戳的日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"{component_name}_{timestamp}.log"
        log_filepath = LOG_DIR / log_filename

        # 创建文件handler
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8', mode='a')
        file_handler.setLevel(getattr(logging, log_level.upper(), logging.DEBUG))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # 记录日志文件创建
        logger.info(f"Log file created: {log_filepath}")

    # 控制台输出handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

def get_log_files(component_name: str = None, limit: int = 10):
    """
    获取日志文件列表

    Args:
        component_name: 组件名称，如果为None则获取所有组件的日志
        limit: 最多返回的文件数量

    Returns:
        list: 日志文件路径列表，按修改时间倒序排列
    """
    if not LOG_DIR.exists():
        return []

    pattern = f"{component_name}_*.log" if component_name else "*.log"
    log_files = list(LOG_DIR.glob(pattern))

    # 按修改时间倒序排列
    log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

    return log_files[:limit]

def read_latest_log(component_name: str = None, max_lines: int = 100):
    """
    读取最新的日志文件

    Args:
        component_name: 组件名称，如果为None则读取最新的任意日志文件
        max_lines: 最多读取的行数

    Returns:
        str: 日志内容
    """
    log_files = get_log_files(component_name, limit=1)

    if not log_files:
        return "No log files found."

    latest_log = log_files[0]

    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 返回最后max_lines行
            return ''.join(lines[-max_lines:])
    except Exception as e:
        return f"Error reading log file {latest_log}: {e}"

def clean_old_logs(days_to_keep: int = 7, component_name: str = None):
    """
    清理旧的日志文件

    Args:
        days_to_keep: 保留天数
        component_name: 组件名称，如果为None则清理所有组件的旧日志
    """
    if not LOG_DIR.exists():
        return

    import time

    current_time = time.time()
    cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)

    pattern = f"{component_name}_*.log" if component_name else "*.log"
    log_files = list(LOG_DIR.glob(pattern))

    removed_count = 0
    for log_file in log_files:
        if log_file.stat().st_mtime < cutoff_time:
            try:
                log_file.unlink()
                removed_count += 1
                print(f"Removed old log file: {log_file}")
            except Exception as e:
                print(f"Error removing log file {log_file}: {e}")

    print(f"Cleaned {removed_count} old log files (older than {days_to_keep} days)")

def get_log_summary(component_name: str = None):
    """
    获取日志文件摘要信息

    Args:
        component_name: 组件名称

    Returns:
        dict: 日志摘要信息
    """
    log_files = get_log_files(component_name)

    if not log_files:
        return {"total_files": 0, "total_size": 0, "latest": None}

    total_size = sum(f.stat().st_size for f in log_files)
    latest_file = log_files[0]

    return {
        "total_files": len(log_files),
        "total_size": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "latest": {
            "name": latest_file.name,
            "size": latest_file.stat().st_size,
            "modified": datetime.fromtimestamp(latest_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        },
        "log_directory": str(LOG_DIR)
    }

# 预定义的组件日志配置
COMPONENT_LOGGERS = {
    "agent": "agent",
    "video": "video_processor",
    "detector": "mediapipe_detector",
    "executor": "action_executor",
    "standalone": "standalone_controller"
}

def setup_component_logger(component_key: str, **kwargs):
    """
    为预定义的组件设置日志

    Args:
        component_key: 组件键名 (agent, video, detector, etc.)
        **kwargs: 传递给setup_logging的其他参数

    Returns:
        logger: 配置好的logger实例
    """
    component_name = COMPONENT_LOGGERS.get(component_key, component_key)
    return setup_logging(component_name, **kwargs)