"""
Python MCP HTTP服务器单元测试
"""

import asyncio
import json
import time
import requests
import unittest
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestMCPServerUnit(unittest.TestCase):
    """MCP服务器单元测试"""

    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.server_url = "http://localhost:8081"
        cls.test_results = []

    def log_test(self, test_name: str, success: bool, message: str, data=None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "timestamp": time.time(),
            "data": data
        }
        self.test_results.append(result)

        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")

    def test_server_health_check(self):
        """测试服务器健康检查"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.assertEqual(data.get("status"), "healthy")
                self.assertIn("services", data)
                self.assertIn("available_tools", data)
                self.log_test("服务器健康检查", True, f"状态: {data.get('status')}", data)
            else:
                self.log_test("服务器健康检查", False, f"状态码: {response.status_code}")

        except requests.exceptions.ConnectionError:
            self.log_test("服务器健康检查", False, "连接被拒绝 - 服务器未启动")
        except Exception as e:
            self.log_test("服务器健康检查", False, f"异常: {str(e)}")

    def test_get_available_tools(self):
        """测试获取可用工具列表"""
        try:
            response = requests.get(f"{self.server_url}/tools", timeout=5)

            if response.status_code == 200:
                data = response.json()
                self.assertTrue(data.get("success", False))
                tools = data.get("tools", [])
                self.assertGreater(len(tools), 0)

                tool_names = [tool.get("name") for tool in tools]
                expected_tools = ["news", "weather", "email", "filesystem", "screenshot", "browser"]

                for expected_tool in expected_tools:
                    self.assertIn(expected_tool, tool_names, f"缺少工具: {expected_tool}")

                self.log_test("获取可用工具", True, f"找到 {len(tools)} 个工具", tool_names)
            else:
                self.log_test("获取可用工具", False, f"状态码: {response.status_code}")

        except Exception as e:
            self.log_test("获取可用工具", False, f"异常: {str(e)}")

    def test_weather_tool(self):
        """测试天气工具"""
        try:
            payload = {
                "action": "execute",
                "parameters": {"city": "北京"}
            }

            response = requests.post(
                f"{self.server_url}/mcp/weather",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.assertIn("weather", data.get("data", {}))
                    self.log_test("天气工具", True, "天气工具调用成功")
                else:
                    self.log_test("天气工具", False, f"工具失败: {data.get('error')}")
            else:
                self.log_test("天气工具", False, f"HTTP错误: {response.status_code}")

        except Exception as e:
            self.log_test("天气工具", False, f"异常: {str(e)}")

    def test_news_tool(self):
        """测试新闻工具"""
        try:
            payload = {
                "action": "execute",
                "parameters": {"count": 5}
            }

            response = requests.post(
                f"{self.server_url}/mcp/news",
                json=payload,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    news_data = data.get("data", {})
                    self.assertIn("news", news_data)
                    self.log_test("新闻工具", True, f"获取到 {len(news_data.get('news', []))} 条新闻")
                else:
                    self.log_test("新闻工具", False, f"工具失败: {data.get('error')}")
            else:
                self.log_test("新闻工具", False, f"HTTP错误: {response.status_code}")

        except Exception as e:
            self.log_test("新闻工具", False, f"异常: {str(e)}")

    def test_filesystem_tool(self):
        """测试文件系统工具"""
        try:
            # 测试写文件
            test_content = "Hello MCP Test!"
            test_file = "test_mcp_output.txt"

            payload = {
                "action": "execute",
                "parameters": {
                    "operation": "write",
                    "path": test_file,
                    "content": test_content
                }
            }

            response = requests.post(
                f"{self.server_url}/mcp/filesystem",
                json=payload,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # 验证文件是否真的被创建
                    try:
                        with open(test_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        self.assertEqual(content, test_content)
                        self.log_test("文件系统工具", True, "文件读写测试成功")

                        # 清理测试文件
                        import os
                        os.remove(test_file)
                    except Exception as file_e:
                        self.log_test("文件系统工具", False, f"文件验证失败: {str(file_e)}")
                else:
                    self.log_test("文件系统工具", False, f"工具失败: {data.get('error')}")
            else:
                self.log_test("文件系统工具", False, f"HTTP错误: {response.status_code}")

        except Exception as e:
            self.log_test("文件系统工具", False, f"异常: {str(e)}")

    def test_browser_tool(self):
        """测试浏览器工具"""
        try:
            payload = {
                "action": "execute",
                "parameters": {
                    "action": "open",
                    "url": "https://www.google.com"
                }
            }

            response = requests.post(
                f"{self.server_url}/mcp/browser",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    self.log_test("浏览器工具", True, "浏览器操作成功")
                else:
                    self.log_test("浏览器工具", False, f"工具失败: {data.get('error')}")
            else:
                self.log_test("浏览器工具", False, f"HTTP错误: {response.status_code}")

        except Exception as e:
            self.log_test("浏览器工具", False, f"异常: {str(e)}")

    def test_news_weather_email_workflow(self):
        """测试新闻天气邮件工作流"""
        try:
            payload = {
                "workflow_name": "news_weather_email",
                "context": {
                    "email": "1730495747@qq.com",
                    "city": "北京"
                }
            }

            response = requests.post(
                f"{self.server_url}/workflow/execute",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    workflow_data = data.get("data", {})
                    self.assertIn("email", workflow_data)
                    self.assertIn("city", workflow_data)
                    self.log_test("新闻天气邮件工作流", True, "工作流执行成功")
                else:
                    self.log_test("新闻天气邮件工作流", False, f"工作流失败: {data.get('error')}")
            else:
                self.log_test("新闻天气邮件工作流", False, f"HTTP错误: {response.status_code}")

        except Exception as e:
            self.log_test("新闻天气邮件工作流", False, f"异常: {str(e)}")

    def test_error_handling(self):
        """测试错误处理"""
        try:
            # 测试不存在的工具
            response = requests.post(
                f"{self.server_url}/mcp/nonexistent_tool",
                json={"action": "execute"},
                timeout=5
            )

            # 应该返回404或错误状态
            self.assertIn(response.status_code, [404, 500])
            self.log_test("错误处理", True, f"正确处理不存在的工具 (状态码: {response.status_code})")

        except Exception as e:
            self.log_test("错误处理", False, f"异常: {str(e)}")

    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始MCP服务器单元测试...")
        print("=" * 60)

        # 运行各个测试
        self.test_server_health_check()
        self.test_get_available_tools()
        self.test_weather_tool()
        self.test_news_tool()
        self.test_filesystem_tool()
        self.test_browser_tool()
        self.test_news_weather_email_workflow()
        self.test_error_handling()

        # 生成测试报告
        self.generate_test_report()

    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 MCP服务器单元测试报告")
        print("=" * 60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - passed_tests

        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {passed_tests/total_tests*100:.1f}%")

        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['message']}")

        print("\n📄 详细结果:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test_name']}")

        # 保存测试报告
        report_data = {
            "test_type": "MCP服务器单元测试",
            "test_time": time.time(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests/total_tests*100,
            "results": self.test_results
        }

        try:
            with open("mcp_server_unit_test_report.json", "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n📄 测试报告已保存到: mcp_server_unit_test_report.json")
        except Exception as e:
            print(f"\n❌ 保存测试报告失败: {str(e)}")


def main():
    """主函数"""
    print("MCP服务器单元测试器")
    print("请确保MCP服务器正在运行: python mcp_http_server.py")
    print()

    tester = TestMCPServerUnit()

    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n用户取消测试")
    except Exception as e:
        print(f"\n测试过程中发生异常: {str(e)}")


if __name__ == "__main__":
    main()