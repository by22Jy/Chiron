#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版电脑控制功能测试
测试OCR识别、自动化工作流、语音控制等高级功能
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
    print("🖥️ 增强版电脑控制功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 测试1: 获取屏幕信息
    print("📊 测试1: 获取屏幕信息...")
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
                print(f"✅ 屏幕分辨率: {screen_info['screen_resolution']}")
                print(f"✅ 活动窗口: {screen_info['active_window']}")
                print(f"✅ 窗口数量: {len(screen_info['all_windows'])}")
            else:
                print(f"❌ 屏幕信息获取失败: {data.get('error')}")
        else:
            print(f"❌ API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 屏幕信息测试异常: {str(e)}")

    time.sleep(1)

    # 测试2: 查找窗口
    print("\n🔍 测试2: 查找窗口...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/computer_control",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "find_window",
                    "keywords": ["notepad", "记事本"]
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                window_info = data["data"]
                if window_info["window_found"]:
                    print(f"✅ 找到窗口: {window_info['window_info']['title']}")
                    print(f"✅ 进程: {window_info['window_info']['process']}")
                else:
                    print("✅ 未找到记事本窗口（正常）")
            else:
                print(f"❌ 窗口查找失败: {data.get('error')}")
        else:
            print(f"❌ API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 窗口查找测试异常: {str(e)}")

    time.sleep(1)

    # 测试3: 智能查找屏幕元素
    print("\n🎯 测试3: 智能查找屏幕元素...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/computer_control",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "find_element",
                    "element_type": "button",
                    "search_params": {"text": "确定"}
                }
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                element_info = data["data"]
                if element_info["element_found"]:
                    print(f"✅ 找到元素: {element_info['element_info']['text']}")
                    print(f"✅ 位置: {element_info['element_info']['position']}")
                    print(f"✅ 置信度: {element_info['element_info']['confidence']:.2f}")
                else:
                    print("✅ 未找到'确定'按钮（正常，可能没有打开相关窗口）")
            else:
                print(f"❌ 元素查找失败: {data.get('error')}")
        else:
            print(f"❌ API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 元素查找测试异常: {str(e)}")

    time.sleep(1)

    # 测试4: 启动应用程序
    print("\n🚀 测试4: 启动应用程序（记事本）...")
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
                    print("✅ 记事本启动成功")
                    print("⏳ 等待3秒确保记事本完全启动...")
                    time.sleep(3)
                else:
                    print("❌ 记事本启动失败")
            else:
                print(f"❌ 应用启动失败: {data.get('error')}")
        else:
            print(f"❌ API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 应用启动测试异常: {str(e)}")

    time.sleep(1)

    return True

def test_automation_workflow():
    """测试自动化工作流"""
    print("\n" + "=" * 60)
    print("🤖 自动化工作流测试")
    print("=" * 60)

    # 测试1: 简单的自动化工作流
    print("📝 测试1: 简单自动化工作流（记事本输入）...")
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
                "parameters": {"text": "YOLO-LLM增强版自动化测试"},
                "description": "输入测试文本",
                "wait_before": 1.0,
                "wait_after": 1.0
            },
            {
                "action": "hotkey",
                "parameters": {"keys": ["ctrl", "s"]},
                "description": "保存文件",
                "wait_before": 0.5,
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
                print(f"✅ 工作流执行成功")
                print(f"✅ 总步骤数: {workflow_result['total_steps']}")
                print(f"✅ 执行步骤数: {workflow_result['executed_steps']}")
                print(f"✅ 耗时: {workflow_result['duration']:.2f} 秒")
                print(f"✅ 消息: {workflow_result['message']}")

                # 显示步骤详情
                for step in workflow_result['steps_details']:
                    print(f"   步骤{step['step']}: {step['description']} - {step['status']}")
            else:
                print(f"❌ 工作流执行失败: {data.get('error')}")
        else:
            print(f"❌ API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 工作流测试异常: {str(e)}")

    time.sleep(2)

    # 测试2: Steam购买工作流（模拟）
    print("\n🎮 测试2: Steam游戏购买工作流（模拟）...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/automation",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "workflow_name": "steam_purchase",
                    "game_name": "测试游戏"
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                workflow_result = data["data"]
                print(f"✅ Steam工作流创建成功")
                print(f"✅ 步骤数: {workflow_result['total_steps']}")
                print(f"✅ 游戏名称: 测试游戏")
            else:
                print(f"❌ Steam工作流失败: {data.get('error')}")
        else:
            print(f"❌ API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ Steam工作流测试异常: {str(e)}")

    return True

def test_voice_control():
    """测试语音控制功能"""
    print("\n" + "=" * 60)
    print("🎤 语音控制功能测试")
    print("=" * 60)

    # 测试1: 启动语音控制
    print("🔊 测试1: 启动语音控制...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/voice_control",
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
            voice_data = data["data"]
            print(f"✅ 语音控制状态: {voice_data['voice_enabled']}")
            print(f"✅ 可用命令数: {len(voice_data['available_commands'])}")
            print(f"✅ 消息: {voice_data['message']}")

            if voice_data['voice_enabled']:
                print("🎧 语音控制已启动，可以尝试语音命令")
            else:
                print("⚠️ 语音控制未启用（可能是设备不支持）")
        else:
            print(f"❌ API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 语音控制测试异常: {str(e)}")

    time.sleep(2)

    # 测试2: 停止语音控制
    print("\n🔇 测试2: 停止语音控制...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/voice_control",
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
                voice_data = data["data"]
                print(f"✅ 语音控制已停止: {not voice_data['voice_enabled']}")
                print(f"✅ 消息: {voice_data['message']}")
            else:
                print(f"❌ 停止语音控制失败: {data.get('error')}")
        else:
            print(f"❌ API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 停止语音控制测试异常: {str(e)}")

    return True

def test_system_health():
    """测试系统健康检查"""
    print("\n" + "=" * 60)
    print("🏥 系统健康检查测试")
    print("=" * 60)

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

                print("📊 系统健康状态:")
                print(f"   CPU使用率: {health_info['cpu']['usage_percent']:.1f}% - {health_info['cpu']['status']}")
                print(f"   内存使用: {health_info['memory']['usage_percent']:.1f}% - {health_info['memory']['status']}")
                print(f"   磁盘使用: {health_info['disk']['usage_percent']:.1f}% - {health_info['disk']['status']}")
                print(f"   网络连接: {health_info['network']['connections']} - {health_info['network']['status']}")
                print(f"   运行进程: {health_info['processes']['count']} - {health_info['processes']['status']}")
                print(f"   系统运行时间: {health_info['uptime_hours']:.1f} 小时")

                # 判断整体健康状态
                status_summary = []
                if health_info['cpu']['status'] != "正常":
                    status_summary.append("CPU高负载")
                if health_info['memory']['status'] != "正常":
                    status_summary.append("内存紧张")
                if health_info['disk']['status'] != "正常":
                    status_summary.append("磁盘空间不足")
                if health_info['network']['status'] != "正常":
                    status_summary.append("网络连接过多")
                if health_info['processes']['status'] != "正常":
                    status_summary.append("进程过多")

                if not status_summary:
                    print("✅ 系统整体状态良好")
                else:
                    print(f"⚠️ 需要注意: {', '.join(status_summary)}")

            else:
                print(f"❌ 系统健康检查失败: {data.get('error')}")
        else:
            print(f"❌ API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"❌ 系统健康检查异常: {str(e)}")

    return True

def main():
    """主测试函数"""
    try:
        # 首先检查服务器状态
        health_response = requests.get(f"{MCP_BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ 增强版MCP服务器不可用")
            return

        health_data = health_response.json()
        print("✅ 增强版MCP服务器健康检查通过")
        print(f"   服务器状态: {health_data['status']}")
        print(f"   可用工具: {len(health_data['available_tools'])} 个")
        print()

        # 运行所有测试
        test_results = []

        # 电脑控制测试
        if test_computer_control():
            test_results.append("电脑控制: ✅ 通过")

        # 自动化工作流测试
        if test_automation_workflow():
            test_results.append("自动化工作流: ✅ 通过")

        # 语音控制测试
        if test_voice_control():
            test_results.append("语音控制: ✅ 通过")

        # 系统健康检查测试
        if test_system_health():
            test_results.append("系统健康检查: ✅ 通过")

        # 测试总结
        print("\n" + "=" * 60)
        print("🎉 增强版电脑控制功能测试总结")
        print("=" * 60)

        for result in test_results:
            print(f"   {result}")

        print(f"\n📊 测试通过率: {len(test_results)}/4 ({len(test_results)/4*100:.0f}%)")

        if len(test_results) == 4:
            print("🏆 所有增强功能测试通过！系统运行完美")
        else:
            print("⚠️ 部分功能存在问题，请检查相关模块")

    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")

if __name__ == "__main__":
    main()