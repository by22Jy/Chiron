#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek LLM集成功能测试
"""

import requests
import json
import time
from datetime import datetime

# MCP服务器配置
MCP_BASE_URL = "http://localhost:8083"

def test_deepseek_llm():
    """测试DeepSeek LLM功能"""
    print("=" * 60)
    print("DeepSeek LLM集成功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 测试1: 获取可用工作流
    print("测试1: 获取可用工作流...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/deepseek_llm",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "get_workflows"
                }
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                workflows_data = data["data"]
                print(f"获取到 {workflows_data['count']} 个工作流")
                for workflow in workflows_data['workflows']:
                    print(f"  - {workflow['name']}: {workflow['description']}")
                    print(f"    预计耗时: {workflow['estimated_duration']} 秒")
            else:
                print(f"获取工作流失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"获取工作流测试异常: {str(e)}")

    time.sleep(1)

    # 测试2: 启动工作线程
    print("\n测试2: 启动DeepSeek工作线程...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/deepseek_llm",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "start_worker"
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                worker_data = data["data"]
                print(f"工作线程启动成功")
                print(f"线程状态: {'活跃' if worker_data['worker_active'] else '非活跃'}")
                print(f"消息: {worker_data['message']}")
            else:
                print(f"启动工作线程失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"启动工作线程测试异常: {str(e)}")

    time.sleep(1)

    # 测试3: 创建智能任务
    print("\n测试3: 创建智能任务...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/deepseek_llm",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "create_task",
                    "task_type": "analysis",
                    "description": "分析YOLO-LLM项目的优势和改进方向",
                    "context": {
                        "project_name": "YOLO-LLM",
                        "features": ["gesture_control", "ai_agent", "automation", "computer_vision"]
                    },
                    "priority": 5
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                task_data = data["data"]
                print(f"任务创建成功")
                print(f"任务ID: {task_data['task_id']}")
                print(f"任务类型: {task_data['task_type']}")
                print(f"优先级: {task_data['priority']}")
            else:
                print(f"创建任务失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"创建任务测试异常: {str(e)}")

    time.sleep(2)

    # 测试4: 获取任务状态
    print("\n测试4: 获取任务状态...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/task_management",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "list_tasks",
                    "limit": 5
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                tasks_data = data["data"]
                print(f"获取到 {tasks_data['count']} 个任务")

                for task in tasks_data['tasks']:
                    print(f"  任务: {task['description'][:50]}...")
                    print(f"    状态: {task['status']}, 类型: {task['task_type']}")
                    print(f"    创建时间: {task['created_at']}")
            else:
                print(f"获取任务列表失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"获取任务状态测试异常: {str(e)}")

    time.sleep(1)

    # 测试5: 获取队列状态
    print("\n测试5: 获取队列状态...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/deepseek_llm",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "get_queue_status"
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                queue_data = data["data"]
                print(f"队列状态:")
                print(f"  队列大小: {queue_data['queue_size']}")
                print(f"  等待任务: {queue_data['pending_tasks']}")
                print(f"  运行任务: {queue_data['running_tasks']}")
                print(f"  总任务数: {queue_data['total_tasks']}")
                print(f"  工作线程: {'活跃' if queue_data['worker_active'] else '非活跃'}")
            else:
                print(f"获取队列状态失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"获取队列状态测试异常: {str(e)}")

    time.sleep(1)

    # 测试6: 获取性能统计
    print("\n测试6: 获取性能统计...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/deepseek_llm",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "get_performance_stats"
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats_data = data["data"]
                print(f"性能统计:")
                print(f"  总任务数: {stats_data.get('total_tasks', 0)}")
                print(f"  已完成任务: {stats_data.get('completed_tasks', 0)}")
                print(f"  失败任务: {stats_data.get('failed_tasks', 0)}")
                print(f"  成功率: {stats_data.get('success_rate', 0):.1f}%")
                print(f"  API调用次数: {stats_data.get('api_calls', 0)}")
                print(f"  平均耗时: {stats_data.get('average_duration', 0):.2f} 秒")
            else:
                print(f"获取性能统计失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"获取性能统计测试异常: {str(e)}")

    return True

def test_task_management():
    """测试任务管理功能"""
    print("\n" + "=" * 60)
    print("任务管理功能测试")
    print("=" * 60)

    # 测试1: 批量创建任务
    print("测试1: 批量创建任务...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/task_management",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "create_batch_tasks",
                    "tasks": [
                        {
                            "task_type": "generation",
                            "description": "生成一个Python脚本来处理图像",
                            "priority": 3
                        },
                        {
                            "task_type": "planning",
                            "description": "制定系统优化计划",
                            "priority": 7
                        },
                        {
                            "task_type": "decision",
                            "description": "分析是否应该升级硬件",
                            "context": {"budget": 5000, "current_performance": "good"},
                            "priority": 5
                        }
                    ]
                }
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                batch_data = data["data"]
                print(f"批量任务创建完成")
                print(f"请求数量: {batch_data['total_requested']}")
                print(f"成功创建: {batch_data['total_created']}")
                for task in batch_data['created_tasks']:
                    if "error" not in task:
                        print(f"  成功: {task['task_id']} - {task['description'][:30]}...")
                    else:
                        print(f"  失败: {task['description']} - {task['error']}")
            else:
                print(f"批量创建任务失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"批量创建任务测试异常: {str(e)}")

    time.sleep(1)

    # 测试2: 执行工作流
    print("\n测试2: 执行工作流...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/task_management",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "execute_workflow",
                    "workflow_id": "content_analysis",
                    "parameters": {
                        "text": "YOLO-LLM是一个创新的手势控制AI平台，结合了计算机视觉和自然语言处理技术。",
                        "analysis_depth": "detailed"
                    }
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                workflow_data = data["data"]
                print(f"工作流执行任务创建成功")
                print(f"工作流: {workflow_data['workflow_name']}")
                print(f"任务ID: {workflow_data['task_id']}")
                print(f"预计耗时: {workflow_data['estimated_duration']} 秒")
            else:
                print(f"执行工作流失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"执行工作流测试异常: {str(e)}")

    time.sleep(1)

    # 测试3: 获取任务历史
    print("\n测试3: 获取任务历史...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/task_management",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "get_task_history",
                    "limit": 10
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                history_data = data["data"]
                print(f"获取到 {history_data['count']} 条历史记录")

                for record in history_data['history'][:3]:
                    print(f"  {record['task_id'][:15]}... - {record['task_type']}")
                    print(f"    状态: {record['status']}, 耗时: {record['duration']:.2f}s")
            else:
                print(f"获取任务历史失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"获取任务历史测试异常: {str(e)}")

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

        # 运行DeepSeek测试
        test_deepseek_llm()
        test_task_management()

        print("\n" + "=" * 60)
        print("DeepSeek LLM集成功能测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"测试过程中发生异常: {str(e)}")

if __name__ == "__main__":
    main()