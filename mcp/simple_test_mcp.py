"""
简化版MCP服务器测试
"""

import requests
import json
import time

def test_mcp_server():
    """测试MCP服务器"""
    server_url = "http://localhost:8081"

    print("开始MCP服务器测试...")
    print("=" * 50)

    tests = []

    # 1. 健康检查
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] 健康检查: 状态={data.get('status')}")
            tests.append(("健康检查", True, data.get('status')))
        else:
            print(f"[FAIL] 健康检查: 状态码={response.status_code}")
            tests.append(("健康检查", False, str(response.status_code)))
    except Exception as e:
        print(f"[FAIL] 健康检查: {str(e)}")
        tests.append(("健康检查", False, str(e)))
        return  # 服务器未启动，无需继续测试

    # 2. 获取工具列表
    try:
        response = requests.get(f"{server_url}/tools", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tools = data.get('tools', [])
            print(f"[PASS] 获取工具列表: 找到 {len(tools)} 个工具")
            tests.append(("获取工具列表", True, f"找到{len(tools)}个工具"))
        else:
            print(f"[FAIL] 获取工具列表: 状态码={response.status_code}")
            tests.append(("获取工具列表", False, str(response.status_code)))
    except Exception as e:
        print(f"[FAIL] 获取工具列表: {str(e)}")
        tests.append(("获取工具列表", False, str(e)))

    # 3. 测试天气工具
    try:
        payload = {"action": "execute", "parameters": {"city": "北京"}}
        response = requests.post(f"{server_url}/mcp/weather", json=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("[PASS] 天气工具: 调用成功")
                tests.append(("天气工具", True, "调用成功"))
            else:
                print(f"[FAIL] 天气工具: {data.get('error')}")
                tests.append(("天气工具", False, data.get('error')))
        else:
            print(f"[FAIL] 天气工具: HTTP错误 {response.status_code}")
            tests.append(("天气工具", False, f"HTTP{response.status_code}"))
    except Exception as e:
        print(f"[FAIL] 天气工具: {str(e)}")
        tests.append(("天气工具", False, str(e)))

    # 4. 测试新闻工具
    try:
        payload = {"action": "execute", "parameters": {"count": 3}}
        response = requests.post(f"{server_url}/mcp/news", json=payload, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                news_count = len(data.get("data", {}).get("news", []))
                print(f"[PASS] 新闻工具: 获取到 {news_count} 条新闻")
                tests.append(("新闻工具", True, f"获取{news_count}条新闻"))
            else:
                print(f"[FAIL] 新闻工具: {data.get('error')}")
                tests.append(("新闻工具", False, data.get('error')))
        else:
            print(f"[FAIL] 新闻工具: HTTP错误 {response.status_code}")
            tests.append(("新闻工具", False, f"HTTP{response.status_code}"))
    except Exception as e:
        print(f"[FAIL] 新闻工具: {str(e)}")
        tests.append(("新闻工具", False, str(e)))

    # 5. 测试文件系统工具
    try:
        test_content = "Hello MCP Test!"
        payload = {
            "action": "execute",
            "parameters": {
                "operation": "write",
                "path": "test_file.txt",
                "content": test_content
            }
        }
        response = requests.post(f"{server_url}/mcp/filesystem", json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print("[PASS] 文件系统工具: 文件写入成功")
                tests.append(("文件系统工具", True, "写入成功"))

                # 清理文件
                import os
                try:
                    os.remove("test_file.txt")
                except:
                    pass
            else:
                print(f"[FAIL] 文件系统工具: {data.get('error')}")
                tests.append(("文件系统工具", False, data.get('error')))
        else:
            print(f"[FAIL] 文件系统工具: HTTP错误 {response.status_code}")
            tests.append(("文件系统工具", False, f"HTTP{response.status_code}"))
    except Exception as e:
        print(f"[FAIL] 文件系统工具: {str(e)}")
        tests.append(("文件系统工具", False, str(e)))

    # 生成报告
    print("\n" + "=" * 50)
    print("测试报告")
    print("=" * 50)

    total = len(tests)
    passed = sum(1 for _, success, _ in tests if success)
    failed = total - passed

    print(f"总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    print(f"成功率: {passed/total*100:.1f}%")

    print("\n详细结果:")
    for name, success, details in tests:
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {status} {name}: {details}")

    # 保存报告
    report = {
        "test_time": time.time(),
        "total": total,
        "passed": passed,
        "failed": failed,
        "success_rate": passed/total*100,
        "results": [{"name": name, "success": success, "details": details} for name, success, details in tests]
    }

    try:
        with open("mcp_test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n测试报告已保存到: mcp_test_report.json")
    except Exception as e:
        print(f"保存报告失败: {e}")

if __name__ == "__main__":
    print("MCP服务器简化测试")
    print("请确保MCP服务器正在运行: python mcp_http_server.py")
    print()

    test_mcp_server()