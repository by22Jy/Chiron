#!/usr/bin/env python3
"""
测试MCP修复效果
"""

import requests
import json

def test_mcp_tools():
    base_url = "http://localhost:8083"

    # 测试工具列表
    tools_to_test = [
        {
            "name": "automation",
            "data": {"workflow_name": "test", "steps": []}
        },
        {
            "name": "voice_control",
            "data": {"action": "start"}
        },
        {
            "name": "system_health",
            "data": {}
        },
        {
            "name": "filesystem",
            "data": {"operation": "read", "path": "test.txt"}
        }
    ]

    print("开始测试MCP工具修复效果...")

    for tool in tools_to_test:
        try:
            print(f"测试 {tool['name']}...")
            response = requests.post(f"{base_url}/mcp/{tool['name']}", json=tool["data"], timeout=5)
            result = response.json()

            if response.status_code == 200:
                if result.get("success", False):
                    print(f"[OK] {tool['name']}: 成功")
                else:
                    print(f"[FAIL] {tool['name']}: 失败 - {result.get('message', '未知错误')}")
            else:
                print(f"[ERROR] {tool['name']}: HTTP {response.status_code}")

        except Exception as e:
            print(f"[ERROR] {tool['name']}: 异常 - {str(e)}")

    print("测试完成！")

if __name__ == "__main__":
    test_mcp_tools()