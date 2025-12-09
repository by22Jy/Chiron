#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
社交媒体功能测试
"""

import requests
import json
import time
from datetime import datetime

# MCP服务器配置
MCP_BASE_URL = "http://localhost:8083"

def test_contact_management():
    """测试联系人管理功能"""
    print("=" * 60)
    print("联系人管理功能测试")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # 测试1: 添加联系人
    print("测试1: 添加联系人...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/contact_management",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "add_contact",
                    "platform": "wechat",
                    "name": "测试联系人",
                    "identifier": "test_user_001",
                    "group_name": "测试群组",
                    "nickname": "TestUser",
                    "notes": "这是一个测试联系人"
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                contact_data = data["data"]
                print(f"联系人添加成功: {contact_data['contact']['name']}")
                print(f"平台: {contact_data['contact']['platform']}")
                print(f"标识符: {contact_data['contact']['identifier']}")
            else:
                print(f"添加联系人失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"添加联系人测试异常: {str(e)}")

    time.sleep(1)

    # 测试2: 列出联系人
    print("\n测试2: 列出联系人...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/contact_management",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "list_contacts"
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                contacts_data = data["data"]
                print(f"获取到 {contacts_data['count']} 个联系人")

                if contacts_data['contacts']:
                    for i, contact in enumerate(contacts_data['contacts'][:3]):
                        print(f"  {i+1}. {contact['name']} ({contact['platform']})")
                        print(f"     ID: {contact['identifier']}")
                        print(f"     群组: {contact.get('group_name', 'N/A')}")
                else:
                    print("  暂无联系人")
            else:
                print(f"列出联系人失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"列出联系人测试异常: {str(e)}")

    time.sleep(1)

    # 测试3: 查找联系人
    print("\n测试3: 查找联系人...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/contact_management",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "find_contact",
                    "platform": "wechat",
                    "identifier": "test_user_001"
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                contact_data = data["data"]
                if contact_data["found"]:
                    contact = contact_data["contact"]
                    print(f"找到联系人: {contact['name']}")
                    print(f"平台: {contact['platform']}")
                    print(f"备注: {contact.get('notes', 'N/A')}")
                else:
                    print("未找到指定联系人")
            else:
                print(f"查找联系人失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"查找联系人测试异常: {str(e)}")

    time.sleep(1)

    return True

def test_social_media():
    """测试社交媒体功能"""
    print("\n" + "=" * 60)
    print("社交媒体功能测试")
    print("=" * 60)

    # 测试1: 获取消息统计
    print("测试1: 获取消息统计...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/social_media",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "get_statistics"
                }
            },
            timeout=15
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data["data"]
                print(f"总消息数: {stats['total_messages']}")
                print(f"已发送: {stats['sent_messages']}")
                print(f"失败: {stats['failed_messages']}")
                print(f"成功率: {stats['success_rate']:.1f}%")
                print(f"总联系人: {stats['total_contacts']}")

                # 显示平台统计
                print("\n平台统计:")
                for platform, platform_stats in stats['platform_statistics'].items():
                    print(f"  {platform}: {platform_stats['total']} 条消息")
            else:
                print(f"获取统计失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"获取统计测试异常: {str(e)}")

    time.sleep(1)

    # 测试2: 模拟发送单条消息
    print("\n测试2: 模拟发送单条消息...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/social_media",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "send_message",
                    "platform": "wechat",
                    "recipient_name": "测试联系人",
                    "recipient_id": "test_user_001",
                    "content": "这是一条测试消息，来自YOLO-LLM社交媒体工具。",
                    "message_type": "text"
                }
            },
            timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                msg_data = data["data"]
                print(f"消息发送状态: {msg_data['status']}")
                print(f"接收者: {msg_data['recipient']}")
                print(f"内容预览: {msg_data['content']}")
                print(f"消息ID: {msg_data['message_id']}")
            else:
                print(f"发送消息失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"发送消息测试异常: {str(e)}")

    time.sleep(2)

    # 测试3: 模拟群发消息
    print("\n测试3: 模拟群发消息...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/social_media",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "send_mass_message",
                    "platform": "wechat",
                    "recipients": [
                        {"name": "测试联系人1", "id": "test_user_001"},
                        {"name": "测试联系人2", "id": "test_user_002"},
                        {"name": "测试联系人3", "id": "test_user_003"}
                    ],
                    "content": "这是一条群发测试消息，祝您工作顺利！",
                    "message_type": "text",
                    "send_interval": 1.0,
                    "batch_size": 2
                }
            },
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                mass_data = data["data"]
                print(f"群发消息ID: {mass_data['mass_message_id']}")
                print(f"总接收者: {mass_data['total_recipients']}")
                print(f"成功发送: {mass_data['sent_count']}")
                print(f"发送失败: {mass_data['failed_count']}")
                print(f"成功率: {mass_data['success_rate']:.1f}%")
                print(f"耗时: {mass_data['duration']:.2f} 秒")
            else:
                print(f"群发消息失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"群发消息测试异常: {str(e)}")

    time.sleep(1)

    # 测试4: 获取最近消息
    print("\n测试4: 获取最近消息...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/social_media",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "action": "get_recent_messages",
                    "limit": 5
                }
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                msg_data = data["data"]
                print(f"获取到 {msg_data['count']} 条最近消息")

                if msg_data['messages']:
                    for i, msg in enumerate(msg_data['messages']):
                        print(f"  {i+1}. {msg['recipient']} ({msg['platform']})")
                        print(f"     状态: {msg['status']}")
                        print(f"     内容: {msg['content']}")
                        print(f"     时间: {msg['created_at']}")
                else:
                    print("  暂无消息记录")
            else:
                print(f"获取最近消息失败: {data.get('error')}")
        else:
            print(f"API错误: HTTP {response.status_code}")

    except Exception as e:
        print(f"获取最近消息测试异常: {str(e)}")

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

        # 运行社交媒体测试
        test_contact_management()
        test_social_media()

        print("\n" + "=" * 60)
        print("社交媒体功能测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"测试过程中发生异常: {str(e)}")

if __name__ == "__main__":
    main()