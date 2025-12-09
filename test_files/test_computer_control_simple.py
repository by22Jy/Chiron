#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电脑控制功能简单测试
"""

import requests
import json
import time
from datetime import datetime

# MCP服务器配置
MCP_BASE_URL = "http://localhost:8083"

def test_computer_control():
    """测试电脑控制功能"""
    print("=" * 60)
    print("电脑控制功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 测试1: 获取屏幕信息
    print("测试1: 获取屏幕信息...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/computer_control",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "screen_info"
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                screen_info = data["data"]
                print(f"屏幕分辨率: {screen_info['screen_resolution']}")
                print(f"活动窗口: {screen_info['active_window']}")
                print(f"窗口数量: {len(screen_info['all_windows'])}")
            else:
                print(f"屏幕信息获取失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"屏幕信息测试异常: {str(e)}")

    time.sleep(1)

    # 测试2: 启动记事本
    print("\n测试2: 启动记事本...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/computer_control",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "launch",
                    "app_name": "notepad"
                }
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                launch_info = data["data"]
                if launch_info["success"]:
                    print("记事本启动成功")
                    time.sleep(3)
                else:
                    print("记事本启动失败")
            else:
                print(f"应用启动失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"应用启动测试异常: {str(e)}")

    time.sleep(1)

    # 测试3: 自动化工作流
    print("\n测试3: 自动化工作流...")
    try:
        workflow_steps = [
            {
                "action": "launch_app",
                "parameters": {"app_name": "notepad"},
                "description": "启动记事本",
                "wait_before": 0.5,
                "wait_after": 2.0
            },
            {
                "action": "type",
                "parameters": {"text": "YOLO-LLM自动化测试"},
                "description": "输入测试文本",
                "wait_before": 1.0,
                "wait_after": 1.0
            }
        ]

        response = requests.post(
            f"{MCP_BASE_URL}/mcp/automation",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "workflow_name": "notepad_test",
                    "steps": workflow_steps
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                workflow_result = data["data"]
                print(f"工作流执行成功")
                print(f"总步骤数: {workflow_result['total_steps']}")
                print(f"执行步骤数: {workflow_result['executed_steps']}")
                print(f"耗时: {workflow_result['duration']:.2f} 秒")
                print(f"消息: {workflow_result['message']}")
            else:
                print(f"工作流执行失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"工作流测试异常: {str(e)}")

    time.sleep(1)

    # 测试4: 系统健康检查
    print("\n测试4: 系统健康检查...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/system_health",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {}
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                health_info = data["data"]["health_info"]

                print("系统健康状态:")
                print(f"  CPU使用率: {health_info['cpu']['usage_percent']:.1f}% - {health_info['cpu']['status']}")
                print(f"  内存使用: {health_info['memory']['usage_percent']:.1f}% - {health_info['memory']['status']}")
                print(f"  磁盘使用: {health_info['disk']['usage_percent']:.1f}% - {health_info['disk']['status']}")
                print(f"  系统运行时间: {health_info['uptime_hours']:.1f} 小时")

            else:
                print(f"系统健康检查失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"系统健康检查异常: {str(e)}")

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

        # 运行测试
        test_computer_control()

        print("\n" + "=" * 60)
        print("电脑控制功能测试完成")

    except Exception as e:
        print(f"测试过程中发生异常: {str(e)}")

if __name__ == "__main__":
    main()