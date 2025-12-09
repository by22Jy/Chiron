#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO-LLM简化测试套件
避免Unicode编码问题
"""

import os
import sys
import json
import time
import requests
import subprocess
import asyncio
from datetime import datetime
from typing import Dict, List, Any

class YOLOLLMSimpleTestSuite:
    """YOLO-LLM简化测试套件"""

    def __init__(self):
        self.test_results = {
            "unit_tests": {"passed": 0, "failed": 0, "total": 0},
            "integration_tests": {"passed": 0, "failed": 0, "total": 0},
            "api_tests": {"passed": 0, "failed": 0, "total": 0}
        }

        self.service_endpoints = {
            "mcp_server": "http://localhost:8083",
            "backend": "http://localhost:8080",
            "ai_service": "http://localhost:8000"
        }

        self.test_start_time = datetime.now()

    def log_test(self, test_type: str, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "PASS" if success else "FAIL"
        print(f"[{test_type.upper()}] {status} - {test_name}: {message}")

        if success:
            self.test_results[test_type]["passed"] += 1
        else:
            self.test_results[test_type]["failed"] += 1
        self.test_results[test_type]["total"] += 1

    async def run_all_tests(self):
        """运行所有测试"""
        print("YOLO-LLM全方位测试开始")
        print("=" * 60)

        try:
            # 1. 单元测试
            await self.run_unit_tests()

            # 2. 集成测试
            await self.run_integration_tests()

            # 3. API测试
            await self.run_api_tests()

            # 4. 生成测试报告
            self.generate_test_report()

        except Exception as e:
            print(f"测试执行异常: {str(e)}")

    async def run_unit_tests(self):
        """运行单元测试"""
        print("\n单元测试")
        print("-" * 40)

        # 测试模块导入
        await self.test_module_imports()

        # 测试核心功能
        await self.test_core_functions()

    async def test_module_imports(self):
        """测试模块导入"""
        modules_to_test = [
            ("mcp_utils", "MCP工具模块"),
            ("mcp.system_health_monitor", "健康监控模块"),
        ]

        for module_name, display_name in modules_to_test:
            try:
                __import__(module_name)
                self.log_test("unit_tests", f"模块导入 - {display_name}", True)
            except ImportError as e:
                self.log_test("unit_tests", f"模块导入 - {display_name}", False, str(e))
            except Exception as e:
                self.log_test("unit_tests", f"模块导入 - {display_name}", False, f"其他错误: {str(e)}")

    async def test_core_functions(self):
        """测试核心功能"""
        try:
            # 测试MCP缓存功能
            from mcp_utils import mcp_cache
            mcp_cache.set("test_key", "test_value", ttl=60)
            value = mcp_cache.get("test_key")
            cache_success = value == "test_value"
            self.log_test("unit_tests", "MCP缓存功能", cache_success, f"缓存值: {value}")

            # 测试性能监控
            from mcp_utils import mcp_monitor
            mcp_monitor.record_request("test_tool", 0.1, True)
            stats = mcp_monitor.get_performance_report()
            monitor_success = "total_requests" in stats and stats["total_requests"] > 0
            self.log_test("unit_tests", "性能监控功能", monitor_success, f"总请求数: {stats.get('total_requests', 0)}")

        except Exception as e:
            self.log_test("unit_tests", "核心功能测试", False, str(e))

    async def run_integration_tests(self):
        """运行集成测试"""
        print("\n集成测试")
        print("-" * 40)

        # 测试MCP服务器健康检查
        await self.test_mcp_health()

        # 测试系统健康监控
        await self.test_health_monitoring()

    async def test_mcp_health(self):
        """测试MCP服务器健康检查"""
        try:
            response = requests.get(f"{self.service_endpoints['mcp_server']}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                tools_count = len(data.get("available_tools", []))
                self.log_test("integration_tests", "MCP服务器健康检查", True,
                            f"状态: {data.get('status')}, 工具数: {tools_count}")
            else:
                self.log_test("integration_tests", "MCP服务器健康检查", False, f"HTTP {response.status_code}")
        except Exception as e:
            self.log_test("integration_tests", "MCP服务器健康检查", False, str(e))

    async def test_health_monitoring(self):
        """测试健康监控功能"""
        try:
            from mcp.system_health_monitor import SystemHealthMonitor
            monitor = SystemHealthMonitor()
            health_info = monitor.get_health_summary()
            health_success = "overall_status" in health_info
            self.log_test("integration_tests", "健康监控功能", health_success,
                        f"状态: {health_info.get('overall_status', 'unknown')}")
        except Exception as e:
            self.log_test("integration_tests", "健康监控功能", False, str(e))

    async def run_api_tests(self):
        """运行API测试"""
        print("\nAPI测试")
        print("-" * 40)

        # 测试新闻API
        await self.test_news_api()

        # 测试天气API
        await self.test_weather_api()

        # 测试电脑控制API
        await self.test_computer_control_api()

        # 测试DeepSeek API
        await self.test_deepseek_api()

    async def test_news_api(self):
        """测试新闻API"""
        try:
            response = requests.post(
                f"{self.service_endpoints['mcp_server']}/mcp/news",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"count": 2, "country": "us", "use_cache": True}
                },
                timeout=15
            )
            success = response.status_code == 200
            self.log_test("api_tests", "新闻API", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("api_tests", "新闻API", False, str(e))

    async def test_weather_api(self):
        """测试天气API"""
        try:
            response = requests.post(
                f"{self.service_endpoints['mcp_server']}/mcp/weather",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"city": "Beijing", "use_cache": True}
                },
                timeout=15
            )
            success = response.status_code == 200
            self.log_test("api_tests", "天气API", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("api_tests", "天气API", False, str(e))

    async def test_computer_control_api(self):
        """测试电脑控制API"""
        try:
            response = requests.post(
                f"{self.service_endpoints['mcp_server']}/mcp/computer_control",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"action": "screen_info"}
                },
                timeout=10
            )
            success = response.status_code == 200
            self.log_test("api_tests", "电脑控制API", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("api_tests", "电脑控制API", False, str(e))

    async def test_deepseek_api(self):
        """测试DeepSeek API"""
        try:
            response = requests.post(
                f"{self.service_endpoints['mcp_server']}/mcp/deepseek_llm",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"action": "get_workflows"}
                },
                timeout=10
            )
            success = response.status_code == 200
            self.log_test("api_tests", "DeepSeek API", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("api_tests", "DeepSeek API", False, str(e))

    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("YOLO-LLM测试报告")
        print("=" * 60)

        test_duration = datetime.now() - self.test_start_time

        # 计算总体统计
        total_passed = sum(result["passed"] for result in self.test_results.values())
        total_failed = sum(result["failed"] for result in self.test_results.values())
        total_tests = sum(result["total"] for result in self.test_results.values())

        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        print(f"测试开始时间: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"测试持续时间: {test_duration}")
        print(f"总体成功率: {success_rate:.1f}% ({total_passed}/{total_tests})")
        print()

        # 分类统计
        for test_type, result in self.test_results.items():
            type_rate = (result["passed"] / result["total"] * 100) if result["total"] > 0 else 0
            print(f"{test_type.replace('_', ' ').title()}:")
            print(f"   通过: {result['passed']}")
            print(f"   失败: {result['failed']}")
            print(f"   成功率: {type_rate:.1f}%")
            print()

        # 服务状态
        print("服务状态:")
        for service_name, endpoint in self.service_endpoints.items():
            try:
                if service_name == "ai_service":
                    response = requests.get(f"{endpoint}/test", timeout=5)
                else:
                    response = requests.get(f"{endpoint}/health", timeout=5)

                status = "运行中" if response.status_code == 200 else "异常"
                print(f"   {service_name}: {status} ({endpoint})")
            except:
                print(f"   {service_name}: 无法连接 ({endpoint})")

        print("\n" + "=" * 60)

        # 保存报告到文件
        report_data = {
            "test_time": self.test_start_time.isoformat(),
            "duration": str(test_duration),
            "summary": {
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "success_rate": success_rate
            },
            "details": self.test_results,
            "services": self.service_endpoints
        }

        try:
            with open("test_report.json", "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            print("详细报告已保存到: test_report.json")
        except Exception as e:
            print(f"保存报告失败: {str(e)}")

async def main():
    """主函数"""
    test_suite = YOLOLLMSimpleTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())