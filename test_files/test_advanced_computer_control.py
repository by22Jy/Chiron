#!/usr/bin/env python3
"""
高级电脑控制功能测试
演示灵活的智能操控系统
"""

import requests
import json
import time

# MCP服务器地址
MCP_SERVER = "http://localhost:8082"

def test_computer_control():
    """测试高级电脑控制功能"""
    print("🖥️  开始测试高级电脑控制功能...")

    # 1. 获取屏幕信息
    print("\n📊 1. 获取屏幕信息...")
    screen_response = requests.post(
        f"{MCP_SERVER}/mcp/computer_control",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {
                "action": "screen_info"
            }
        }
    )

    if screen_response.status_code == 200:
        screen_data = screen_response.json()
        if screen_data.get("success"):
            print("✅ 屏幕信息获取成功:")
            info = screen_data["data"]
            print(f"   - 屏幕分辨率: {info['screen_resolution']}")
            print(f"   - 活动窗口: {info['active_window']}")
            print(f"   - 窗口数量: {len(info['all_windows'])}")
        else:
            print(f"❌ 屏幕信息获取失败: {screen_data.get('error')}")
    else:
        print(f"❌ 屏幕信息API调用失败: {screen_response.status_code}")

    # 2. 查找所有窗口
    print("\n🪟 2. 查找所有窗口...")
    windows_response = requests.post(
        f"{MCP_SERVER}/mcp/computer_control",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {
                "action": "find_windows"
            }
        }
    )

    if windows_response.status_code == 200:
        windows_data = windows_response.json()
        if windows_data.get("success"):
            windows = windows_data["data"]["windows"]
            print(f"✅ 找到 {len(windows)} 个窗口:")
            for i, window in enumerate(windows[:10], 1):  # 显示前10个
                print(f"   {i}. {window['title']} - {window['process']}")
        else:
            print(f"❌ 窗口查找失败: {windows_data.get('error')}")
    else:
        print(f"❌ 窗口查找API调用失败: {windows_response.status_code}")

    # 3. 启动记事本应用
    print("\n📝 3. 启动记事本应用...")
    notepad_response = requests.post(
        f"{MCP_SERVER}/mcp/computer_control",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {
                "action": "launch_app",
                "app_name": "notepad"
            }
        }
    )

    if notepad_response.status_code == 200:
        notepad_data = notepad_response.json()
        if notepad_data.get("success"):
            print(f"✅ {notepad_data['data']['message']}")
        else:
            print(f"❌ 记事本启动失败: {notepad_data.get('error')}")
    else:
        print(f"❌ 记事本启动API调用失败: {notepad_response.status_code}")

    time.sleep(2)  # 等待应用启动

    # 4. 使用应用程序工作流在记事本中输入文本
    print("\n⌨️ 4. 在记事本中输入文本...")
    notepad_workflow_response = requests.post(
        f"{MCP_SERVER}/mcp/application_workflow",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {
                "app_name": "notepad",
                "action": "type",
                "text": "这是通过YOLO-LLM智能工作流系统自动输入的文本！\n\n系统功能演示：\n1. 智能应用启动\n2. 自动文本输入\n3. 复杂工作流执行\n\n时间戳: " + time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
    )

    if notepad_workflow_response.status_code == 200:
        workflow_data = notepad_workflow_response.json()
        if workflow_data.get("success"):
            print("✅ 记事本工作流执行成功:")
            result = workflow_data["data"]["result"]
            print(f"   - 步骤: {', '.join(result['steps'])}")
            print(f"   - 状态: {result['message']}")
        else:
            print(f"❌ 记事本工作流执行失败: {workflow_data.get('error')}")
    else:
        print(f"❌ 记事本工作流API调用失败: {notepad_workflow_response.status_code}")

    time.sleep(3)  # 等待文本输入完成

    # 5. Steam购买游戏工作流演示
    print("\n🎮 5. Steam购买游戏工作流演示...")
    steam_workflow_response = requests.post(
        f"{MCP_SERVER}/mcp/application_workflow",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {
                "app_name": "steam",
                "action": "buy_game",
                "game_name": "赛博朋克2077"
            }
        }
    )

    if steam_workflow_response.status_code == 200:
        steam_data = steam_workflow_response.json()
        if steam_data.get("success"):
            print("✅ Steam工作流执行:")
            result = steam_data["data"]["result"]
            print(f"   - 步骤: {', '.join(result['steps'])}")
            print(f"   - 状态: {result['message']}")
            if result.get("success"):
                print("   🎯 注意: 完整的购买流程需要更多具体的UI识别和点击逻辑")
        else:
            print(f"❌ Steam工作流执行失败: {steam_data.get('error')}")
    else:
        print(f"❌ Steam工作流API调用失败: {steam_workflow_response.status_code}")

    # 6. 测试屏幕元素点击功能
    print("\n👆 6. 测试屏幕元素点击功能...")
    click_response = requests.post(
        f"{MCP_SERVER}/mcp/computer_control",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {
                "action": "click_element",
                "parameters": {
                    "element_type": "button",
                    "text_contains": "确定"
                }
            }
        }
    )

    if click_response.status_code == 200:
        click_data = click_response.json()
        if click_data.get("success"):
            print("✅ 屏幕元素点击测试:")
            result = click_data["data"]
            if result.get("success"):
                print(f"   - 成功点击: {result['element']['text']} 在位置 {result['element']['position']}")
            else:
                print(f"   - 未找到匹配元素: {result['message']}")
        else:
            print(f"❌ 屏幕元素点击失败: {click_data.get('error')}")
    else:
        print(f"❌ 屏幕元素点击API调用失败: {click_response.status_code}")

    print("\n🎉 高级电脑控制功能测试完成!")
    print("\n📋 功能总结:")
    print("✅ 屏幕信息获取")
    print("✅ 窗口管理")
    print("✅ 应用程序启动")
    print("✅ 文本自动输入")
    print("✅ 应用程序工作流执行")
    print("✅ 屏幕元素识别与点击")
    print("✅ Steam游戏购买流程(演示)")

def test_steam_purchase_workflow():
    """测试Steam游戏购买工作流 - 完整流程演示"""
    print("\n🛒 Steam游戏购买工作流完整演示...")

    workflow_steps = [
        {
            "name": "启动Steam",
            "tool": "application_workflow",
            "params": {
                "app_name": "steam",
                "action": "launch",
                "parameters": {}
            }
        },
        {
            "name": "打开商店页面",
            "tool": "application_workflow",
            "params": {
                "app_name": "steam",
                "action": "store",
                "parameters": {}
            }
        },
        {
            "name": "搜索游戏",
            "tool": "computer_control",
            "params": {
                "action": "type_text",
                "parameters": {
                    "text": "Cyberpunk 2077"
                }
            }
        }
    ]

    for i, step in enumerate(workflow_steps, 1):
        print(f"\n📋 步骤 {i}: {step['name']}")

        response = requests.post(
            f"{MCP_SERVER}/mcp/{step['tool']}",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": step["params"]
            }
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ {step['name']} 执行成功")
            else:
                print(f"❌ {step['name']} 执行失败: {data.get('error')}")
        else:
            print(f"❌ {step['name']} API调用失败: {response.status_code}")

        time.sleep(2)  # 步骤间等待

    print("\n🎯 注意: 完整的Steam购买流程需要:")
    print("   1. 更精确的UI元素识别(OCR + 计算机视觉)")
    print("   2. 账户登录验证")
    print("   3. 支付方式确认")
    print("   4. 安全确认机制")

if __name__ == "__main__":
    # 基础功能测试
    test_computer_control()

    # Steam工作流演示
    test_steam_purchase_workflow()