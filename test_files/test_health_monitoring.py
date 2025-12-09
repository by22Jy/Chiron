#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统健康监控功能测试
"""

import requests
import json
import time
from datetime import datetime

# MCP服务器配置
MCP_BASE_URL = "http://localhost:8083"

def test_health_monitoring():
    """测试健康监控功能"""
    print("=" * 60)
    print("系统健康监控功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 测试1: 获取健康状态摘要
    print("测试1: 获取健康状态摘要...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/health_monitor",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "summary"
                }
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                summary = data["data"]
                print(f"整体状态: {summary['overall_status']}")
                print(f"监控状态: {'运行中' if summary['monitoring_active'] else '已停止'}")
                print(f"指标数量: {summary['metrics_count']}")
                print(f"活跃告警: {summary['active_alerts_count']}")
                print(f"自动恢复: {'启用' if summary['auto_recovery_enabled'] else '禁用'}")

                # 显示主要指标
                print("\n主要系统指标:")
                for metric_name, metric in summary['metrics'].items():
                    print(f"  {metric['name']}: {metric['value']}{metric['unit']} - {metric['status']}")
            else:
                print(f"健康状态摘要获取失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"健康状态摘要测试异常: {str(e)}")

    time.sleep(1)

    # 测试2: 启动健康监控
    print("\n测试2: 启动健康监控...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/health_monitor",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "start"
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                monitor_data = data["data"]
                print(f"健康监控启动成功")
                print(f"监控状态: {'运行中' if monitor_data['monitoring_active'] else '已停止'}")
                print(f"消息: {monitor_data['message']}")
            else:
                print(f"启动健康监控失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"启动健康监控测试异常: {str(e)}")

    time.sleep(3)  # 等待监控收集一些数据

    # 测试3: 立即收集指标
    print("\n测试3: 立即收集指标...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/health_monitor",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "collect_now"
                }
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                collect_data = data["data"]
                print(f"指标收集完成")
                print(f"消息: {collect_data['message']}")

                # 显示最新摘要中的关键指标
                latest = collect_data['latest_summary']
                print(f"当前状态: {latest['overall_status']}")
                print(f"活跃告警数: {latest['active_alerts_count']}")
            else:
                print(f"立即收集指标失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"立即收集指标测试异常: {str(e)}")

    time.sleep(1)

    # 测试4: 获取详细指标
    print("\n测试4: 获取详细指标...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/health_monitor",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "detailed_metrics"
                }
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                metrics_data = data["data"]
                print(f"获取到 {metrics_data['metrics_count']} 个详细指标")

                # 显示前5个指标的详细信息
                for i, metric in enumerate(metrics_data['metrics'][:5]):
                    print(f"  {i+1}. {metric['name']}: {metric['value']}{metric['unit']}")
                    print(f"     状态: {metric['status']}, 描述: {metric['description']}")
                    print(f"     时间: {metric['timestamp']}")
            else:
                print(f"获取详细指标失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"获取详细指标测试异常: {str(e)}")

    time.sleep(1)

    # 测试5: 获取告警历史
    print("\n测试5: 获取告警历史...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/health_monitor",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "alert_history",
                    "limit": 10
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                alert_data = data["data"]
                print(f"获取到 {alert_data['count']} 条告警记录")

                if alert_data['alert_history']:
                    for i, alert in enumerate(alert_data['alert_history'][:3]):
                        print(f"  {i+1}. 告警: {alert['metric_name']}")
                        print(f"     级别: {alert['level']}, 状态: {'已解决' if alert['resolved'] else '活跃'}")
                        print(f"     消息: {alert['message']}")
                        print(f"     时间: {alert['timestamp']}")
                        if alert['actions_taken']:
                            print(f"     已执行操作: {', '.join(alert['actions_taken'])}")
                else:
                    print("  暂无告警记录")
            else:
                print(f"获取告警历史失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"获取告警历史测试异常: {str(e)}")

    time.sleep(1)

    # 测试6: 停止健康监控
    print("\n测试6: 停止健康监控...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/health_monitor",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "stop"
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                monitor_data = data["data"]
                print(f"健康监控停止成功")
                print(f"监控状态: {'运行中' if monitor_data['monitoring_active'] else '已停止'}")
                print(f"消息: {monitor_data['message']}")
            else:
                print(f"停止健康监控失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"停止健康监控测试异常: {str(e)}")

    return True

def main():
    """主测试函数"""
    try:
        # 检查服务器状态
        health_response = requests.get(f"{MCP_BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("增强版MCP服务器不可用")
            return

        health_data = health_response.json()
        print("增强版MCP服务器健康检查通过")
        print(f"服务器状态: {health_data['status']}")
        print(f"可用工具: {len(health_data['available_tools'])} 个")
        print()

        # 运行健康监控测试
        test_health_monitoring()

        print("\n" + "=" * 60)
        print("系统健康监控功能测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"测试过程中发生异常: {str(e)}")

if __name__ == "__main__":
    main()