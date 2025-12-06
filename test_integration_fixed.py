#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP端到端集成测试 - 修复版
测试完整的多模态智能代理工作流程
"""

import requests
import json
import time
import uuid
from datetime import datetime

class FixedEndToEndIntegrationTester:
    def __init__(self):
        self.java_base_url = "http://localhost:8080"
        self.mcp_base_url = "http://localhost:8081"
        self.test_results = []
        self.session_id = str(uuid.uuid4())[:8]

    def test_complete_news_weather_workflow(self):
        """测试完整的新闻-天气-邮件工作流"""
        print("测试完整的新闻-天气-邮件工作流...")

        try:
            # 步骤1: 获取天气信息
            print("  步骤1: 获取天气信息...")
            weather_payload = {"city": "杭州"}
            weather_response = requests.post(
                f"{self.java_base_url}/api/mcp/weather",
                json=weather_payload,
                timeout=20
            )

            if weather_response.status_code != 200:
                raise Exception(f"天气查询失败: HTTP {weather_response.status_code}")

            weather_data = weather_response.json()
            if not weather_data.get("success"):
                raise Exception(f"天气查询失败: {weather_data.get('error')}")

            print("    [OK] 天气查询成功")

            # 步骤2: 执行新闻邮件工作流
            print("  步骤2: 执行新闻邮件工作流...")
            workflow_payload = {
                "email": "test-integration@example.com",
                "city": "杭州"
            }

            workflow_response = requests.post(
                f"{self.java_base_url}/api/mcp/news-email-workflow",
                json=workflow_payload,
                timeout=45
            )

            if workflow_response.status_code != 200:
                raise Exception(f"工作流执行失败: HTTP {workflow_response.status_code}")

            workflow_data = workflow_response.json()
            if not workflow_data.get("success"):
                raise Exception(f"工作流执行失败: {workflow_data.get('error')}")

            print("    [OK] 工作流执行成功")
            print(f"[PASS] 完整工作流: 新闻-天气-邮件流程完成")
            self.test_results.append(("完整工作流", True, "新闻-天气-邮件流程完成"))
            return True

        except Exception as e:
            print(f"[FAIL] 完整工作流: {str(e)}")
            self.test_results.append(("完整工作流", False, str(e)))
            return False

    def test_system_connectivity(self):
        """测试系统连通性"""
        print("测试系统连通性...")

        try:
            connectivity_results = []

            # 测试Java后端连接
            java_health = requests.get(f"{self.java_base_url}/api/mcp/status", timeout=10)
            if java_health.status_code == 200:
                connectivity_results.append("Java后端: 连通")
                print("    [OK] Java后端连通")
            else:
                connectivity_results.append(f"Java后端: HTTP{java_health.status_code}")

            # 测试MCP服务器连接
            mcp_health = requests.get(f"{self.mcp_base_url}/health", timeout=10)
            if mcp_health.status_code == 200:
                connectivity_results.append("MCP服务器: 连通")
                print("    [OK] MCP服务器连通")
            else:
                connectivity_results.append(f"MCP服务器: HTTP{mcp_health.status_code}")

            # 测试工具可用性
            tools_response = requests.get(f"{self.mcp_base_url}/tools", timeout=10)
            if tools_response.status_code == 200:
                tools_data = tools_response.json()
                tool_count = len(tools_data.get("tools", []))
                connectivity_results.append(f"可用工具: {tool_count}个")
                print(f"    [OK] 可用工具: {tool_count}个")
            else:
                connectivity_results.append("工具列表: 获取失败")

            # 检查所有连接是否正常
            all_connected = all("连通" in result or "个" in result for result in connectivity_results)

            if all_connected:
                print(f"[PASS] 系统连通性: 所有组件正常")
                self.test_results.append(("系统连通性", True, "所有组件正常"))
                return True
            else:
                print(f"[FAIL] 系统连通性: {connectivity_results}")
                self.test_results.append(("系统连通性", False, str(connectivity_results)))
                return False

        except Exception as e:
            print(f"[FAIL] 系统连通性: {str(e)}")
            self.test_results.append(("系统连通性", False, str(e)))
            return False

    def test_simple_workflow(self):
        """测试简单工作流"""
        print("测试简单工作流...")

        try:
            # 测试天气查询
            print("  测试天气查询...")
            response = requests.post(
                f"{self.java_base_url}/api/mcp/weather",
                json={"city": "深圳"},
                timeout=20
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("    [OK] 天气查询成功")

                    # 测试邮件发送
                    print("  测试邮件发送...")
                    email_response = requests.post(
                        f"{self.java_base_url}/api/mcp/send-email",
                        json={
                            "to": "test@example.com",
                            "subject": "集成测试邮件",
                            "content": "这是端到端集成测试邮件"
                        },
                        timeout=20
                    )

                    if email_response.status_code == 200:
                        email_data = email_response.json()
                        if email_data.get("success"):
                            print("    [OK] 邮件发送成功")
                            print("[PASS] 简单工作流: 天气查询+邮件发送完成")
                            self.test_results.append(("简单工作流", True, "天气+邮件完成"))
                            return True
                        else:
                            print(f"[FAIL] 邮件发送失败: {email_data.get('error')}")
                    else:
                        print(f"[FAIL] 邮件HTTP错误: {email_response.status_code}")
                else:
                    print(f"[FAIL] 天气查询失败: {data.get('error')}")
            else:
                print(f"[FAIL] 天气HTTP错误: {response.status_code}")

            self.test_results.append(("简单工作流", False, "部分失败"))
            return False

        except Exception as e:
            print(f"[FAIL] 简单工作流: {str(e)}")
            self.test_results.append(("简单工作流", False, str(e)))
            return False

    def test_performance(self):
        """测试性能"""
        print("测试性能...")

        try:
            latencies = []

            # 测试天气查询延迟
            print("  测试天气查询延迟...")
            start_time = time.time()
            response = requests.post(
                f"{self.java_base_url}/api/mcp/weather",
                json={"city": "广州"},
                timeout=30
            )
            weather_latency = (time.time() - start_time) * 1000
            latencies.append(("天气查询", weather_latency))
            print(f"    天气查询: {weather_latency:.0f}ms")

            # 测试MCP工具延迟
            print("  测试MCP工具延迟...")
            start_time = time.time()
            response = requests.post(
                f"{self.mcp_base_url}/mcp/news",
                json={"action": "execute", "parameters": {"count": 3}},
                timeout=20
            )
            tool_latency = (time.time() - start_time) * 1000
            latencies.append(("新闻工具", tool_latency))
            print(f"    新闻工具: {tool_latency:.0f}ms")

            # 评估性能
            avg_latency = sum(lat[1] for lat in latencies) / len(latencies)
            max_latency = max(lat[1] for lat in latencies)

            # 性能标准
            performance_good = (
                avg_latency < 10000 and  # 平均延迟小于10秒
                max_latency < 30000     # 最大延迟小于30秒
            )

            if performance_good:
                print(f"[PASS] 性能测试: 平均延迟 {avg_latency:.0f}ms，最大延迟 {max_latency:.0f}ms")
                self.test_results.append(("性能测试", True, f"平均{avg_latency:.0f}ms"))
                return True
            else:
                print(f"[FAIL] 性能测试: 平均延迟 {avg_latency:.0f}ms，最大延迟 {max_latency:.0f}ms")
                self.test_results.append(("性能测试", False, f"平均{avg_latency:.0f}ms"))
                return False

        except Exception as e:
            print(f"[FAIL] 性能测试: {str(e)}")
            self.test_results.append(("性能测试", False, str(e)))
            return False

    def run_all_tests(self):
        """运行所有集成测试"""
        print("=" * 60)
        print("MCP端到端集成测试开始 - 修复版")
        print(f"测试会话ID: {self.session_id}")
        print("=" * 60)

        # 等待系统准备就绪
        print("等待系统准备就绪...")
        time.sleep(5)

        # 运行测试
        tests = [
            self.test_system_connectivity,
            self.test_simple_workflow,
            self.test_complete_news_weather_workflow,
            self.test_performance
        ]

        for test in tests:
            try:
                test()
                print("\n" + "-" * 40)
                time.sleep(3)  # 测试间隔
            except Exception as e:
                print(f"[ERROR] 测试执行异常: {str(e)}")

        # 生成报告
        self.generate_report()

    def generate_report(self):
        """生成集成测试报告"""
        print("\n" + "=" * 60)
        print("MCP端到端集成测试报告")
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
            "session_id": self.session_id,
            "test_time": time.time(),
            "total": total,
            "passed": passed,
            "failed": failed,
            "success_rate": passed/total*100,
            "results": [{"name": name, "success": success, "details": details} for name, success, details in self.test_results]
        }

        try:
            with open("fixed_integration_report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"\n集成测试报告已保存到: fixed_integration_report.json")
        except Exception as e:
            print(f"保存报告失败: {e}")

if __name__ == "__main__":
    print("MCP端到端集成测试 - 修复版")
    print("请确保以下服务正在运行:")
    print("1. Java Spring Boot后端 (端口8080)")
    print("2. Python MCP服务器 (端口8081)")
    print()

    tester = FixedEndToEndIntegrationTester()
    tester.run_all_tests()