#!/usr/bin/env python3
"""
日志查看和分析工具
用于查看和分析系统日志文件
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from logger_config import (
    setup_logging, get_log_files, read_latest_log, get_log_summary, clean_old_logs
)

def view_logs(component_name: str = None, lines: int = 50, follow: bool = False):
    """查看日志"""
    print(f"=== 日志查看 ===")
    print(f"组件: {component_name or '所有组件'}")
    print(f"显示行数: {lines}")
    print("-" * 60)

    if follow:
        print("实时跟随模式 (按Ctrl+C退出)...")
        # 这里可以实现实时跟随功能
        # 暂时显示最新日志
        content = read_latest_log(component_name, lines)
        print(content)
    else:
        content = read_latest_log(component_name, lines)
        print(content)

def list_log_files(component_name: str = None, limit: int = 20):
    """列出日志文件"""
    print(f"=== 日志文件列表 ===")
    log_files = get_log_files(component_name, limit)

    if not log_files:
        print("没有找到日志文件。")
        return

    print(f"{'文件名':<40} {'大小':<10} {'修改时间':<20}")
    print("-" * 80)

    for log_file in log_files:
        size_kb = round(log_file.stat().st_size / 1024, 1)
        modified_time = datetime.fromtimestamp(
            log_file.stat().st_mtime
        ).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{log_file.name:<40} {size_kb:>8}KB {modified_time}")

def show_log_summary(component_name: str = None):
    """显示日志摘要"""
    print("=== 日志摘要 ===")
    summary = get_log_summary(component_name)

    print(f"日志目录: {summary['log_directory']}")
    print(f"文件总数: {summary['total_files']}")
    print(f"总大小: {summary['total_size_mb']} MB")

    if summary['latest']:
        latest = summary['latest']
        print(f"最新文件: {latest['name']}")
        print(f"最新文件大小: {round(latest['size']/1024, 1)} KB")
        print(f"最新文件修改时间: {latest['modified']}")

def search_logs(search_term: str, component_name: str = None, context_lines: int = 3):
    """搜索日志内容"""
    print(f"=== 搜索日志 ===")
    print(f"搜索词: '{search_term}'")
    print(f"组件: {component_name or '所有组件'}")
    print("-" * 60)

    log_files = get_log_files(component_name, limit=5)  # 搜索最近5个文件

    if not log_files:
        print("没有找到日志文件。")
        return

    found_lines = []
    for log_file in log_files:
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for i, line in enumerate(lines, 1):
                    if search_term.lower() in line.lower():
                        # 获取上下文
                        start_idx = max(0, i - 1 - context_lines)
                        end_idx = min(len(lines), i + context_lines)

                        context = []
                        for j in range(start_idx, end_idx):
                            prefix = ">>> " if j == i - 1 else "    "
                            context.append(f"{prefix}{j+1:4d}: {lines[j].rstrip()}")

                        found_lines.extend([
                            f"\n--- 在文件 {log_file.name} 第{i}行 ---",
                            *context
                        ])

        except Exception as e:
            print(f"读取文件 {log_file} 时出错: {e}")

    if found_lines:
        print(f"\n找到 {len([l for l in found_lines if l.startswith('>>>')])} 个匹配项:")
        print(''.join(found_lines))
    else:
        print(f"没有找到包含 '{search_term}' 的日志行。")

def cleanup_logs(days_to_keep: int = 7, component_name: str = None, dry_run: bool = True):
    """清理旧日志"""
    print(f"=== 清理旧日志 ===")
    print(f"保留天数: {days_to_keep}")
    print(f"组件: {component_name or '所有组件'}")

    if dry_run:
        print("这是预览模式，不会实际删除文件。")

    # 显示将被删除的文件
    import time
    from pathlib import Path

    LOG_DIR = Path(__file__).parent / "logs"
    if not LOG_DIR.exists():
        print("日志目录不存在。")
        return

    current_time = time.time()
    cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)

    pattern = f"{component_name}_*.log" if component_name else "*.log"
    log_files = list(LOG_DIR.glob(pattern))

    old_files = [f for f in log_files if f.stat().st_mtime < cutoff_time]

    if old_files:
        print(f"\n将删除 {len(old_files)} 个文件:")
        total_size = 0
        for log_file in old_files:
            size_kb = round(log_file.stat().st_size / 1024, 1)
            modified_time = datetime.fromtimestamp(
                log_file.stat().st_mtime
            ).strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {log_file.name:<40} {size_kb:>8}KB ({modified_time})")
            total_size += log_file.stat().st_size

        print(f"\n总共将释放: {round(total_size/(1024*1024), 1)} MB")

        if not dry_run:
            confirm = input("\n确认删除这些文件吗? (y/N): ")
            if confirm.lower() == 'y':
                clean_old_logs(days_to_keep, component_name)
            else:
                print("取消删除。")
    else:
        print("没有找到需要删除的旧日志文件。")

def main():
    parser = argparse.ArgumentParser(description='日志查看和分析工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # view命令
    view_parser = subparsers.add_parser('view', help='查看日志')
    view_parser.add_argument('-c', '--component', help='组件名称')
    view_parser.add_argument('-n', '--lines', type=int, default=50, help='显示行数')
    view_parser.add_argument('-f', '--follow', action='store_true', help='实时跟随')

    # list命令
    list_parser = subparsers.add_parser('list', help='列出日志文件')
    list_parser.add_argument('-c', '--component', help='组件名称')
    list_parser.add_argument('-n', '--limit', type=int, default=20, help='显示文件数量')

    # summary命令
    summary_parser = subparsers.add_parser('summary', help='显示日志摘要')
    summary_parser.add_argument('-c', '--component', help='组件名称')

    # search命令
    search_parser = subparsers.add_parser('search', help='搜索日志内容')
    search_parser.add_argument('term', help='搜索词')
    search_parser.add_argument('-c', '--component', help='组件名称')
    search_parser.add_argument('-C', '--context', type=int, default=3, help='上下文行数')

    # cleanup命令
    cleanup_parser = subparsers.add_parser('cleanup', help='清理旧日志')
    cleanup_parser.add_argument('-d', '--days', type=int, default=7, help='保留天数')
    cleanup_parser.add_argument('-c', '--component', help='组件名称')
    cleanup_parser.add_argument('--execute', action='store_true', help='实际执行删除')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'view':
            view_logs(args.component, args.lines, args.follow)
        elif args.command == 'list':
            list_log_files(args.component, args.limit)
        elif args.command == 'summary':
            show_log_summary(args.component)
        elif args.command == 'search':
            search_logs(args.term, args.component, args.context)
        elif args.command == 'cleanup':
            cleanup_logs(args.days, args.component, dry_run=not args.execute)

    except KeyboardInterrupt:
        print("\n操作已取消。")
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()