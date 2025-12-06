"""
Java MCP集成测试
测试Java Backend调用Python MCP HTTP服务器
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any

class MCPIntegrationTester:
    """MCP集成测试器"""

    def __init__(self):
        self.java_backend_url = "http://localhost:8080"
        self.python_mcp_url = "http://localhost:8081"
        self.test_results = []

    def log_test(self, test_name: str, success: bool, message: str, data: Any = None):
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

    def test_python_mcp_server(self) -> bool:
        """测试Python MCP服务器"""
        try:
            # 健康检查
            response = requests.get(f"{self.python_mcp_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                self.log_test("Python MCP健康检查", True, "MCP服务器运行正常", health_data)
                return True
            else:
                self.log_test("Python MCP健康检查", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Python MCP健康检查", False, f"连接失败: {str(e)}")
            return False

    def test_java_backend(self) -> bool:
        """测试Java Backend"""
        try:
            # 测试MCP状态接口
            response = requests.get(f"{self.java_backend_url}/api/mcp/status", timeout=5)
            if response.status_code == 200:
                status_data = response.json()
                self.log_test("Java Backend MCP状态", True, "Java Backend运行正常", status_data)
                return True
            else:
                self.log_test("Java Backend MCP状态", False, f"状态码: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Java Backend MCP状态", False, f"连接失败: {str(e)}")
            return False

    def test_direct_mcp_tool_call(self) -> bool:
        """测试直接调用MCP工具"""
        try:
            # 测试天气工具
            weather_payload = {
                "action": "execute",
                "parameters": {"city": "北京"}
            }
            response = requests.post(
                f"{self.python_mcp_url}/mcp/weather",
                json=weather_payload,
                timeout=10
            )

            if response.status_code == 200:
                weather_data = response.json()
                success = weather_data.get("success", False)
                if success:
                    self.log_test("直接MCP工具调用-天气", True, "天气工具调用成功", weather_data)
                    return True
                else:
                    self.log_test("直接MCP工具调用-天气", False, weather_data.get("error", "未知错误"))
                    return False
            else:
                self.log_test("直接MCP工具调用-天气", False, f"HTTP错误: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("直接MCP工具调用-天气", False, f"调用失败: {str(e)}")
            return False

    def test_java_enhanced_chat(self) -> bool:
        """测试Java增强对话功能"""
        try:
            chat_payload = {
                "message": "帮我查询北京的天气",
                "context": "用户想了解天气情况",
                "required_tools": ["weather"]
            }

            response = requests.post(
                f"{self.java_backend_url}/api/mcp/enhanced-chat",
                json=chat_payload,
                timeout=30
            )

            if response.status_code == 200:
                chat_data = response.json()
                success = chat_data.get("success", False)
                if success:
                    self.log_test("Java增强对话", True, "增强对话成功", chat_data)
                    return True
                else:
                    self.log_test("Java增强对话", False, chat_data.get("error", "未知错误"))
                    return False
            else:
                self.log_test("Java增强对话", False, f"HTTP错误: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("Java增强对话", False, f"调用失败: {str(e)}")
            return False

    def test_news_email_workflow(self) -> bool:
        """测试新闻邮件工作流"""
        try:
            workflow_payload = {
                "workflow_name": "news_weather_email",
                "context": {
                    "email": "1730495747@qq.com",
                    "city": "北京"
                }
            }

            response = requests.post(
                f"{self.java_backend_url}/api/mcp/execute-workflow",
                json=workflow_payload,
                timeout=60
            )

            if response.status_code == 200:
                workflow_data = response.json()
                success = workflow_data.get("success", False)
                if success:
                    self.log_test("新闻邮件工作流", True, "工作流执行成功", workflow_data)
                    return True
                else:
                    self.log_test("新闻邮件工作流", False, workflow_data.get("error", "未知错误"))
                    return False
            else:
                self.log_test("新闻邮件工作流", False, f"HTTP错误: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("新闻邮件工作流", False, f"调用失败: {str(e)}")
            return False

    def test_quick_news_email_endpoint(self) -> bool:
        """测试快速新闻邮件接口"""
        try:
            payload = {
                "email": "1730495747@qq.com",
                "city": "北京"
            }

            response = requests.post(
                f"{self.java_backend_url}/api/mcp/news-email-workflow",
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                success = data.get("success", False)
                if success:
                    self.log_test("快速新闻邮件接口", True, "快速接口成功", data)
                    return True
                else:
                    self.log_test("快速新闻邮件接口", False, data.get("error", "未知错误"))
                    return False
            else:
                self.log_test("快速新闻邮件接口", False, f"HTTP错误: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("快速新闻邮件接口", False, f"调用失败: {str(e)}")
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("🧪 开始Java MCP集成测试...")
        print("=" * 60)

        # 基础连接测试
        python_ok = self.test_python_mcp_server()
        java_ok = self.test_java_backend()

        if not python_ok:
            print("\n❌ Python MCP服务器未运行，请先启动:")
            print("cd mcp && python mcp_http_server.py")
            return

        if not java_ok:
            print("\n❌ Java Backend未运行，请先启动:")
            print("cd backend && mvn spring-boot:run")
            return

        # 功能测试
        print("\n🔧 功能测试:")
        self.test_direct_mcp_tool_call()
        self.test_java_enhanced_chat()
        self.test_news_email_workflow()
        self.test_quick_news_email_endpoint()

        # 生成测试报告
        self.generate_test_report()

    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 测试报告")
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

        # 保存测试报告到文件
        report_data = {
            "test_time": time.time(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": passed_tests/total_tests*100,
            "results": self.test_results
        }

        try:
            with open("java_mcp_integration_test_report.json", "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            print(f"\n📄 测试报告已保存到: java_mcp_integration_test_report.json")
        except Exception as e:
            print(f"\n❌ 保存测试报告失败: {str(e)}")


def main():
    """主函数"""
    print("🚀 Java MCP集成测试器")
    print("请确保以下服务正在运行:")
    print("1. Python MCP服务器: cd mcp && python mcp_http_server.py")
    print("2. Java Backend: cd backend && mvn spring-boot:run")
    print()

    tester = MCPIntegrationTester()

    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n用户取消测试")
    except Exception as e:
        print(f"\n测试过程中发生异常: {str(e)}")


if __name__ == "__main__":
    main()