#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO-LLM端到端功能测试
测试完整的业务流程
"""

import requests
import json
import time
from datetime import datetime

MCP_BASE_URL = "http://localhost:8083"

def test_news_weather_workflow():
    """测试新闻+天气工作流"""
    print("测试新闻+天气智能工作流...")

    try:
        # 1. 获取天气信息
        weather_response = requests.post(
            f"{MCP_BASE_URL}/mcp/weather",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "city": "北京",
                    "use_cache": True
                }
            },
            timeout=15
        )

        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            print(f"  天气查询成功: {weather_data['success']}")

            # 2. 获取新闻
            news_response = requests.post(
                f"{MCP_BASE_URL}/mcp/news",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {
                        "count": 3,
                        "country": "us",
                        "use_cache": True
                    }
                },
                timeout=15
            )

            if news_response.status_code == 200:
                news_data = news_response.json()
                print(f"  新闻查询成功: {news_data['success']}")

                # 3. 模拟智能分析和决策
                weather_info = weather_data.get('data', {})
                news_info = news_data.get('data', {})

                # 这里可以集成DeepSeek进行智能分析
                analysis_result = {
                    "weather_suggestion": "天气晴朗，适合外出",
                    "news_summary": f"获取到 {len(news_info.get('articles', []))} 条新闻",
                    "timestamp": datetime.now().isoformat()
                }

                print(f"  智能分析完成: {analysis_result['weather_suggestion']}")
                return True
        return False

    except Exception as e:
        print(f"  工作流测试异常: {str(e)}")
        return False

def test_computer_control_automation():
    """测试电脑控制自动化"""
    print("测试电脑控制自动化...")

    try:
        # 1. 获取屏幕信息
        screen_response = requests.post(
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

        if screen_response.status_code == 200:
            screen_data = screen_response.json()
            print(f"  屏幕信息获取成功: {screen_data['success']}")

            # 2. 测试应用启动（模拟）
            launch_response = requests.post(
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

            if launch_response.status_code == 200:
                launch_data = launch_response.json()
                print(f"  应用启动测试: {launch_data['success']}")
                return True
        return False

    except Exception as e:
        print(f"  自动化测试异常: {str(e)}")
        return False

def test_social_media_integration():
    """测试社交媒体集成"""
    print("测试社交媒体集成...")

    try:
        # 1. 添加联系人
        contact_response = requests.post(
            f"{MCP_BASE_URL}/mcp/contact_management",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "add_contact",
                    "platform": "wechat",
                    "name": "测试用户",
                    "identifier": "test_user_001"
                }
            },
            timeout=10
        )

        if contact_response.status_code == 200:
            contact_data = contact_response.json()
            print(f"  联系人添加: {contact_data['success']}")

            # 2. 获取消息统计
            stats_response = requests.post(
                f"{MCP_BASE_URL}/mcp/social_media",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {
                        "action": "get_statistics"
                    }
                },
                timeout=10
            )

            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print(f"  消息统计获取: {stats_data['success']}")
                return True
        return False

    except Exception as e:
        print(f"  社交媒体测试异常: {str(e)}")
        return False

def test_deepseek_integration():
    """测试DeepSeek集成"""
    print("测试DeepSeek LLM集成...")

    try:
        # 1. 获取可用工作流
        workflows_response = requests.post(
            f"{MCP_BASE_URL}/mcp/deepseek_llm",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "get_workflows"
                }
            },
            timeout=10
        )

        if workflows_response.status_code == 200:
            workflows_data = workflows_response.json()
            print(f"  工作流获取: {workflows_data['success']}")

            # 2. 创建智能任务
            task_response = requests.post(
                f"{MCP_BASE_URL}/mcp/deepseek_llm",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {
                        "action": "create_task",
                        "task_type": "analysis",
                        "description": "分析YOLO-LLM系统的优势",
                        "priority": 5
                    }
                },
                timeout=10
            )

            if task_response.status_code == 200:
                task_data = task_response.json()
                print(f"  智能任务创建: {task_data['success']}")
                return True
        return False

    except Exception as e:
        print(f"  DeepSeek测试异常: {str(e)}")
        return False

def test_system_health_monitoring():
    """测试系统健康监控"""
    print("测试系统健康监控...")

    try:
        # 1. 获取健康状态摘要
        health_response = requests.post(
            f"{MCP_BASE_URL}/mcp/health_monitor",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "summary"
                }
            },
            timeout=10
        )

        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"  健康监控: {health_data['success']}")

            # 2. 立即收集指标
            collect_response = requests.post(
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

            if collect_response.status_code == 200:
                collect_data = collect_response.json()
                print(f"  指标收集: {collect_data['success']}")
                return True
        return False

    except Exception as e:
        print(f"  健康监控测试异常: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("YOLO-LLM端到端功能测试")
    print("=" * 50)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 运行各种端到端测试
    test_results = []

    test_results.append(("新闻天气工作流", test_news_weather_workflow()))
    time.sleep(1)

    test_results.append(("电脑控制自动化", test_computer_control_automation()))
    time.sleep(1)

    test_results.append(("社交媒体集成", test_social_media_integration()))
    time.sleep(1)

    test_results.append(("DeepSeek集成", test_deepseek_integration()))
    time.sleep(1)

    test_results.append(("系统健康监控", test_system_health_monitoring()))

    # 统计结果
    passed = sum(1 for _, success in test_results if success)
    total = len(test_results)

    print("\n" + "=" * 50)
    print("端到端测试结果:")

    for test_name, success in test_results:
        status = "PASS" if success else "FAIL"
        print(f"  {test_name}: {status}")

    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    print("=" * 50)

if __name__ == "__main__":
    main()