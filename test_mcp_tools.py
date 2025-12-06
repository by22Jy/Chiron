#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP各个工具模块单元测试
分别测试每个MCP工具的具体功能
"""

import requests
import json
import time
import os
import tempfile
from datetime import datetime

class MCPToolsModuleTester:
    def __init__(self):
        self.mcp_base_url = "http://localhost:8081"
        self.java_base_url = "http://localhost:8080"
        self.test_results = []
        self.test_files = []  # 记录测试期间创建的文件，用于清理

    def cleanup_test_files(self):
        """清理测试文件"""
        for file_path in self.test_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"清理测试文件: {file_path}")
            except Exception as e:
                print(f"清理文件失败 {file_path}: {e}")

    def test_news_tool_direct(self):
        """直接测试新闻工具"""
        print("直接测试新闻工具...")

        try:
            payload = {
                "action": "execute",
                "parameters": {
                    "count": 5,
                    "category": "technology",
                    "country": "cn"
                }
            }

            response = requests.post(
                f"{self.mcp_base_url}/mcp/news",
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    news_list = data.get("data", {}).get("news", [])
                    print(f"[PASS] 新闻工具(直接): 获取到 {len(news_list)} 条新闻")
                    self.test_results.append(("新闻工具(直接)", True, f"获取{len(news_list)}条新闻"))
                    return True
                else:
                    print(f"[FAIL] 新闻工具(直接): {data.get('error')}")
                    self.test_results.append(("新闻工具(直接)", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 新闻工具(直接): HTTP {response.status_code}")
                self.test_results.append(("新闻工具(直接)", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 新闻工具(直接): {str(e)}")
            self.test_results.append(("新闻工具(直接)", False, str(e)))
            return False

    def test_weather_tool_direct(self):
        """直接测试天气工具"""
        print("直接测试天气工具...")

        try:
            payload = {
                "action": "execute",
                "parameters": {
                    "city": "上海",
                    "units": "metric",
                    "lang": "zh_cn"
                }
            }

            response = requests.post(
                f"{self.mcp_base_url}/mcp/weather",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    weather_info = data.get("data", {}).get("weather", {})
                    city = weather_info.get("city")
                    temperature = weather_info.get("temperature")
                    print(f"[PASS] 天气工具(直接): {city} {temperature}")
                    self.test_results.append(("天气工具(直接)", True, f"{city} {temperature}"))
                    return True
                else:
                    print(f"[FAIL] 天气工具(直接): {data.get('error')}")
                    self.test_results.append(("天气工具(直接)", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 天气工具(直接): HTTP {response.status_code}")
                self.test_results.append(("天气工具(直接)", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 天气工具(直接): {str(e)}")
            self.test_results.append(("天气工具(直接)", False, str(e)))
            return False

    def test_email_tool_direct(self):
        """直接测试邮件工具"""
        print("直接测试邮件工具...")

        try:
            payload = {
                "action": "execute",
                "parameters": {
                    "to": "test@example.com",
                    "subject": "MCP工具模块测试",
                    "content": "这是来自MCP工具单元测试的邮件"
                }
            }

            response = requests.post(
                f"{self.mcp_base_url}/mcp/email",
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    email_id = data.get("data", {}).get("email_id")
                    print(f"[PASS] 邮件工具(直接): 邮件发送成功 {email_id}")
                    self.test_results.append(("邮件工具(直接)", True, f"发送成功 {email_id}"))
                    return True
                else:
                    print(f"[FAIL] 邮件工具(直接): {data.get('error')}")
                    self.test_results.append(("邮件工具(直接)", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 邮件工具(直接): HTTP {response.status_code}")
                self.test_results.append(("邮件工具(直接)", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 邮件工具(直接): {str(e)}")
            self.test_results.append(("邮件工具(直接)", False, str(e)))
            return False

    def test_filesystem_tool_read(self):
        """测试文件系统工具-读取"""
        print("测试文件系统工具-读取...")

        try:
            # 创建测试文件
            test_content = f"MCP文件系统测试内容 - {datetime.now()}"
            test_file = "test_mcp_fs_read.txt"

            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_content)

            self.test_files.append(test_file)

            payload = {
                "action": "execute",
                "parameters": {
                    "operation": "read",
                    "path": test_file
                }
            }

            response = requests.post(
                f"{self.mcp_base_url}/mcp/filesystem",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    content = data.get("data", {}).get("content", "")
                    if "MCP文件系统测试" in content:
                        print(f"[PASS] 文件系统工具(读取): 成功读取文件内容")
                        self.test_results.append(("文件系统工具(读取)", True, "成功读取"))
                        return True
                    else:
                        print(f"[FAIL] 文件系统工具(读取): 内容不匹配")
                        self.test_results.append(("文件系统工具(读取)", False, "内容不匹配"))
                        return False
                else:
                    print(f"[FAIL] 文件系统工具(读取): {data.get('error')}")
                    self.test_results.append(("文件系统工具(读取)", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 文件系统工具(读取): HTTP {response.status_code}")
                self.test_results.append(("文件系统工具(读取)", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 文件系统工具(读取): {str(e)}")
            self.test_results.append(("文件系统工具(读取)", False, str(e)))
            return False

    def test_filesystem_tool_write(self):
        """测试文件系统工具-写入"""
        print("测试文件系统工具-写入...")

        try:
            test_content = f"MCP写入测试内容 - {datetime.now()}"
            test_file = "test_mcp_fs_write.txt"
            self.test_files.append(test_file)

            payload = {
                "action": "execute",
                "parameters": {
                    "operation": "write",
                    "path": test_file,
                    "content": test_content
                }
            }

            response = requests.post(
                f"{self.mcp_base_url}/mcp/filesystem",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    content_length = data.get("data", {}).get("content_length", 0)
                    if content_length > 0:
                        print(f"[PASS] 文件系统工具(写入): 成功写入 {content_length} 字节")
                        self.test_results.append(("文件系统工具(写入)", True, f"写入{content_length}字节"))
                        return True
                    else:
                        print(f"[FAIL] 文件系统工具(写入): 写入字节数为0")
                        self.test_results.append(("文件系统工具(写入)", False, "写入字节数为0"))
                        return False
                else:
                    print(f"[FAIL] 文件系统工具(写入): {data.get('error')}")
                    self.test_results.append(("文件系统工具(写入)", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 文件系统工具(写入): HTTP {response.status_code}")
                self.test_results.append(("文件系统工具(写入)", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 文件系统工具(写入): {str(e)}")
            self.test_results.append(("文件系统工具(写入)", False, str(e)))
            return False

    def test_screenshot_tool(self):
        """测试截图工具"""
        print("测试截图工具...")

        try:
            # 创建临时文件路径
            temp_dir = tempfile.gettempdir()
            screenshot_path = os.path.join(temp_dir, "test_mcp_screenshot.png")

            payload = {
                "action": "execute",
                "parameters": {
                    "save_path": screenshot_path
                }
            }

            response = requests.post(
                f"{self.mcp_base_url}/mcp/screenshot",
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    size_info = data.get("data", {}).get("size", {})
                    file_size = data.get("data", {}).get("file_size", 0)
                    print(f"[PASS] 截图工具: 成功截图 {size_info.get('width')}x{size_info.get('height')}")
                    self.test_results.append(("截图工具", True, f"截图成功 {file_size} 字节"))
                    return True
                else:
                    print(f"[FAIL] 截图工具: {data.get('error')}")
                    self.test_results.append(("截图工具", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 截图工具: HTTP {response.status_code}")
                self.test_results.append(("截图工具", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 截图工具: {str(e)}")
            self.test_results.append(("截图工具", False, str(e)))
            return False

    def test_browser_tool(self):
        """测试浏览器工具"""
        print("测试浏览器工具...")

        try:
            payload = {
                "action": "execute",
                "parameters": {
                    "action": "open",
                    "url": "https://www.example.com"
                }
            }

            response = requests.post(
                f"{self.mcp_base_url}/mcp/browser",
                json=payload,
                timeout=20
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    action_info = data.get("data", {})
                    message = action_info.get("message", "")
                    print(f"[PASS] 浏览器工具: {message}")
                    self.test_results.append(("浏览器工具", True, message))
                    return True
                else:
                    print(f"[FAIL] 浏览器工具: {data.get('error')}")
                    self.test_results.append(("浏览器工具", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 浏览器工具: HTTP {response.status_code}")
                self.test_results.append(("浏览器工具", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 浏览器工具: {str(e)}")
            self.test_results.append(("浏览器工具", False, str(e)))
            return False

    def test_tools_availability(self):
        """测试工具可用性"""
        print("测试工具可用性...")

        try:
            response = requests.get(f"{self.mcp_base_url}/tools", timeout=10)

            if response.status_code == 200:
                data = response.json()
                tools = data.get("tools", [])
                tool_names = [tool.get("name") for tool in tools]

                expected_tools = ["news", "weather", "email", "filesystem", "screenshot", "browser"]
                missing_tools = [tool for tool in expected_tools if tool not in tool_names]

                if not missing_tools:
                    print(f"[PASS] 工具可用性: 所有 {len(expected_tools)} 个工具都可用")
                    self.test_results.append(("工具可用性", True, f"所有{len(expected_tools)}个工具可用"))
                    return True
                else:
                    print(f"[FAIL] 工具可用性: 缺少工具 {missing_tools}")
                    self.test_results.append(("工具可用性", False, f"缺少{missing_tools}"))
                    return False
            else:
                print(f"[FAIL] 工具可用性: HTTP {response.status_code}")
                self.test_results.append(("工具可用性", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 工具可用性: {str(e)}")
            self.test_results.append(("工具可用性", False, str(e)))
            return False

    def run_all_tests(self):
        """运行所有工具模块测试"""
        print("=" * 60)
        print("MCP各个工具模块单元测试开始")
        print("=" * 60)

        # 等待服务准备就绪
        print("等待服务准备就绪...")
        time.sleep(3)

        # 运行测试
        tests = [
            self.test_tools_availability,
            self.test_news_tool_direct,
            self.test_weather_tool_direct,
            self.test_email_tool_direct,
            self.test_filesystem_tool_read,
            self.test_filesystem_tool_write,
            self.test_screenshot_tool,
            self.test_browser_tool
        ]

        for test in tests:
            try:
                test()
                time.sleep(2)  # 测试间隔
            except Exception as e:
                print(f"[ERROR] 测试执行异常: {str(e)}")

        # 清理测试文件
        print("\n清理测试文件...")
        self.cleanup_test_files()

        # 生成报告
        self.generate_report()

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("MCP工具模块测试报告")
        print("=" * 60)

        total = len(self.test_results)
        passed = sum(1 for _, success, _ in self.test_results if success)
        failed = total - passed

        print(f"总测试数: {total}")
        print(f"通过: {passed}")
        print(f"失败: {failed}")
        print(f"成功率: {passed/total*100:.1f}%")

        print("\n详细结果:")
        for name, success, details in self.test_results:
            status = "[PASS]" if success else "[FAIL]"
            print(f"  {status} {name}: {details}")

        # 保存报告
        report = {
            "test_time": time.time(),
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed/total*100,
            "results": [{"name": name, "success": success, "details": details} for name, success, details in self.test_results]
        }

        try:
            with open("mcp_tools_test_report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n测试报告已保存到: mcp_tools_test_report.json")
        except Exception as e:
            print(f"保存报告失败: {e}")

if __name__ == "__main__":
    print("MCP各个工具模块单元测试")
    print("请确保以下服务正在运行:")
    print("1. Python MCP服务器 (端口8081)")
    print()

    tester = MCPToolsModuleTester()
    tester.run_all_tests()