#!/usr/bin/env python3
"""
测试新的日志系统
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from logger_config import setup_component_logger, get_log_files, get_log_summary

def test_logging_system():
    """测试日志系统"""
    print("=== 测试新的日志系统 ===")

    # 测试不同组件的日志
    components = ["agent", "video", "detector", "standalone"]

    for component in components:
        print(f"\n测试组件: {component}")
        logger = setup_component_logger(component, console_output=False, file_output=True)

        # 写入一些测试日志
        logger.info(f"这是 {component} 组件的信息日志")
        logger.debug(f"这是 {component} 组件的调试日志")
        logger.warning(f"这是 {component} 组件的警告日志")
        logger.error(f"这是 {component} 组件的错误日志")

        print(f"[OK] {component} component log written successfully")

    # 等待一下确保文件写入
    time.sleep(1)

    # 显示日志文件列表
    print("\n=== 日志文件列表 ===")
    log_files = get_log_files()
    for log_file in log_files[:10]:  # 只显示前10个
        size_kb = round(log_file.stat().st_size / 1024, 1)
        print(f"  {log_file.name:<40} {size_kb:>6}KB")

    # 显示日志摘要
    print("\n=== 日志摘要 ===")
    summary = get_log_summary()
    print(f"总文件数: {summary['total_files']}")
    print(f"总大小: {summary['total_size_mb']} MB")
    if summary['latest']:
        print(f"最新文件: {summary['latest']['name']}")
        print(f"修改时间: {summary['latest']['modified']}")

    print(f"\n[SUCCESS] Logging system test completed!")
    print(f"日志保存在: {Path(__file__).parent / 'logs'}")

if __name__ == '__main__':
    test_logging_system()