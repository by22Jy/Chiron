#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Java MCP集成服务单元测试
测试Java Spring Boot后端的MCP集成功能
"""

import requests
import json
import time
import sys

class JavaMCPIntegrationTester:
    def __init__(self):
        self.java_base_url = "http://localhost:8080"
        self.mcp_base_url = "http://localhost:8081"
        self.test_results = []

    def test_java_backend_health(self):
        """测试Java后端健康状态"""
        print("测试Java后端健康状态...")

        try:
            response = requests.get(f"{self.java_base_url}/api/mcp/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"[PASS] Java后端健康检查: {data.get('success')}")
                self.test_results.append(("Java后端健康检查", True, str(data.get('success'))))
                return True
            else:
                print(f"[FAIL] Java后端健康检查: HTTP {response.status_code}")
                self.test_results.append(("Java后端健康检查", False, f"HTTP {response.status_code}"))
                return False
        except Exception as e:
            print(f"[FAIL] Java后端健康检查: {str(e)}")
            self.test_results.append(("Java后端健康检查", False, str(e)))
            return False

    def test_enhanced_chat(self):
        """测试增强对话接口"""
        print("测试增强对话接口...")

        try:
            payload = {
                "message": "请帮我查询北京的天气",
                "context": "测试MCP集成",
                "required_tools": ["weather"]
            }

            response = requests.post(
                f"{self.java_base_url}/api/mcp/enhanced-chat",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"[PASS] 增强对话: 成功获取响应")
                    self.test_results.append(("增强对话", True, "成功获取响应"))
                    return True
                else:
                    print(f"[FAIL] 增强对话: {data.get('error')}")
                    self.test_results.append(("增强对话", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 增强对话: HTTP {response.status_code}")
                self.test_results.append(("增强对话", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 增强对话: {str(e)}")
            self.test_results.append(("增强对话", False, str(e)))
            return False

    def test_weather_workflow(self):
        """测试天气工作流"""
        print("测试天气工作流...")

        try:
            payload = {"city": "上海"}

            response = requests.post(
                f"{self.java_base_url}/api/mcp/weather",
                json=payload,
                timeout=20
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"[PASS] 天气工作流: 成功查询天气")
                    self.test_results.append(("天气工作流", True, "成功查询天气"))
                    return True
                else:
                    print(f"[FAIL] 天气工作流: {data.get('error')}")
                    self.test_results.append(("天气工作流", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 天气工作流: HTTP {response.status_code}")
                self.test_results.append(("天气工作流", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 天气工作流: {str(e)}")
            self.test_results.append(("天气工作流", False, str(e)))
            return False

    def test_news_email_workflow(self):
        """测试新闻邮件工作流"""
        print("测试新闻邮件工作流...")

        try:
            payload = {
                "email": "test@example.com",
                "city": "北京"
            }

            response = requests.post(
                f"{self.java_base_url}/api/mcp/news-email-workflow",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"[PASS] 新闻邮件工作流: 成功执行")
                    self.test_results.append(("新闻邮件工作流", True, "成功执行"))
                    return True
                else:
                    print(f"[FAIL] 新闻邮件工作流: {data.get('error')}")
                    self.test_results.append(("新闻邮件工作流", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 新闻邮件工作流: HTTP {response.status_code}")
                self.test_results.append(("新闻邮件工作流", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 新闻邮件工作流: {str(e)}")
            self.test_results.append(("新闻邮件工作流", False, str(e)))
            return False

    def test_send_email(self):
        """测试发送邮件接口"""
        print("测试发送邮件接口...")

        try:
            payload = {
                "to": "test@example.com",
                "subject": "Java MCP测试邮件",
                "content": "这是一封来自Java MCP集成服务的测试邮件"
            }

            response = requests.post(
                f"{self.java_base_url}/api/mcp/send-email",
                json=payload,
                timeout=20
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"[PASS] 发送邮件: 成功发送")
                    self.test_results.append(("发送邮件", True, "成功发送"))
                    return True
                else:
                    print(f"[FAIL] 发送邮件: {data.get('error')}")
                    self.test_results.append(("发送邮件", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 发送邮件: HTTP {response.status_code}")
                self.test_results.append(("发送邮件", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 发送邮件: {str(e)}")
            self.test_results.append(("发送邮件", False, str(e)))
            return False

    def test_complex_workflow(self):
        """测试复杂工作流执行"""
        print("测试复杂工作流执行...")

        try:
            payload = {
                "workflow_name": "news_weather_email",
                "context": {
                    "email": "test@example.com",
                    "city": "深圳"
                }
            }

            response = requests.post(
                f"{self.java_base_url}/api/mcp/execute-workflow",
                json=payload,
                timeout=45
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"[PASS] 复杂工作流: 成功执行")
                    self.test_results.append(("复杂工作流", True, "成功执行"))
                    return True
                else:
                    print(f"[FAIL] 复杂工作流: {data.get('error')}")
                    self.test_results.append(("复杂工作流", False, data.get('error')))
                    return False
            else:
                print(f"[FAIL] 复杂工作流: HTTP {response.status_code}")
                self.test_results.append(("复杂工作流", False, f"HTTP {response.status_code}"))
                return False

        except Exception as e:
            print(f"[FAIL] 复杂工作流: {str(e)}")
            self.test_results.append(("复杂工作流", False, str(e)))
            return False

    def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("Java MCP集成服务单元测试开始")
        print("=" * 60)

        # 等待服务启动
        print("等待服务启动...")
        time.sleep(5)

        # 运行测试
        tests = [
            self.test_java_backend_health,
            self.test_enhanced_chat,
            self.test_weather_workflow,
            self.test_news_email_workflow,
            self.test_send_email,
            self.test_complex_workflow
        ]

        for test in tests:
            try:
                test()
                time.sleep(2)  # 测试间隔
            except Exception as e:
                print(f"[ERROR] 测试执行异常: {str(e)}")

        # 生成报告
        self.generate_report()

    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("Java MCP集成测试报告")
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
            with open("java_mcp_test_report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n测试报告已保存到: java_mcp_test_report.json")
        except Exception as e:
            print(f"保存报告失败: {e}")

if __name__ == "__main__":
    print("Java MCP集成服务单元测试")
    print("请确保以下服务正在运行:")
    print("1. Java Spring Boot后端 (端口8080)")
    print("2. Python MCP服务器 (端口8081)")
    print()

    tester = JavaMCPIntegrationTester()
    tester.run_all_tests()