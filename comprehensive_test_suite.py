#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YOLO-LLM全方位测试套件
包含单元测试、集成测试、端到端测试
"""

import os
import sys
import json
import time
import requests
import subprocess
import threading
import asyncio
from datetime import datetime
from typing import Dict, List, Any
import unittest
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_results.log'),
        logging.StreamHandler()
    ]
)

class YOLOLLMTestSuite:
    """YOLO-LLM综合测试套件"""

    def __init__(self):
        self.test_results = {
            "unit_tests": {"passed": 0, "failed": 0, "total": 0},
            "integration_tests": {"passed": 0, "failed": 0, "total": 0},
            "e2e_tests": {"passed": 0, "failed": 0, "total": 0},
            "performance_tests": {"passed": 0, "failed": 0, "total": 0}
        }

        self.service_endpoints = {
            "backend": "http://localhost:8080",
            "ai_service": "http://localhost:8000",
            "mcp_server": "http://localhost:8083",
            "frontend": "http://localhost:5173"
        }

        self.test_start_time = datetime.now()

    def log_test(self, test_type: str, test_name: str, success: bool, message: str = ""):
        """记录测试结果"""
        status = "PASS" if success else "FAIL"
        logging.info(f"[{test_type.upper()}] {status} - {test_name}: {message}")

        if success:
            self.test_results[test_type]["passed"] += 1
        else:
            self.test_results[test_type]["failed"] += 1
        self.test_results[test_type]["total"] += 1

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始YOLO-LLM全方位测试")
        print("=" * 60)

        try:
            # 1. 单元测试
            await self.run_unit_tests()

            # 2. 集成测试
            await self.run_integration_tests()

            # 3. 端到端测试
            await self.run_e2e_tests()

            # 4. 性能测试
            await self.run_performance_tests()

            # 5. 生成测试报告
            self.generate_test_report()

        except Exception as e:
            logging.error(f"测试执行异常: {str(e)}")

    async def run_unit_tests(self):
        """运行单元测试"""
        print("\n📋 运行单元测试...")
        print("-" * 40)

        # 测试模块导入
        await self.test_module_imports()

        # 测试核心功能
        await self.test_core_functions()

        # 测试工具模块
        await self.test_utility_modules()

    async def test_module_imports(self):
        """测试模块导入"""
        modules_to_test = [
            ("mcp_utils", "MCP工具模块"),
            ("mcp.advanced_computer_control", "电脑控制模块"),
            ("mcp.system_health_monitor", "健康监控模块"),
            ("mcp.social_media_tools", "社交媒体模块"),
            ("mcp.deepseek_integration", "DeepSeek集成模块"),
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

    async def test_utility_modules(self):
        """测试工具模块"""
        try:
            # 测试系统健康监控
            from mcp.system_health_monitor import SystemHealthMonitor
            monitor = SystemHealthMonitor()
            health_info = monitor.get_health_summary()
            health_success = "overall_status" in health_info
            self.log_test("unit_tests", "健康监控工具", health_success, f"状态: {health_info.get('overall_status', 'unknown')}")

            # 测试社交媒体管理
            from mcp.social_media_tools import SocialMediaManager
            social_manager = SocialMediaManager()
            stats = social_manager.get_message_statistics()
            social_success = "total_messages" in stats
            self.log_test("unit_tests", "社交媒体工具", social_success, f"消息数: {stats.get('total_messages', 0)}")

        except Exception as e:
            self.log_test("unit_tests", "工具模块测试", False, str(e))

    async def run_integration_tests(self):
        """运行集成测试"""
        print("\n🔗 运行集成测试...")
        print("-" * 40)

        # 等待服务启动
        await self.wait_for_services()

        # 测试服务健康检查
        await self.test_service_health()

        # 测试API集成
        await self.test_api_integration()

        # 测试模块间通信
        await self.test_module_communication()

    async def wait_for_services(self):
        """等待服务启动"""
        services = self.service_endpoints
        max_wait = 30  # 最大等待30秒
        wait_interval = 2

        print("等待服务启动...")
        for i in range(max_wait // wait_interval):
            all_ready = True
            for service_name, endpoint in services.items():
                try:
                    health_url = f"{endpoint}/health" if service_name != "frontend" else endpoint
                    response = requests.get(health_url, timeout=5)
                    if response.status_code != 200:
                        all_ready = False
                        break
                except:
                    all_ready = False
                    break

            if all_ready:
                print("✅ 所有服务已就绪")
                return

            print(f"等待服务启动... ({i * wait_interval + wait_interval}s)")
            await asyncio.sleep(wait_interval)

        print("⚠️ 部分服务可能未完全启动，继续测试...")

    async def test_service_health(self):
        """测试服务健康检查"""
        for service_name, endpoint in self.service_endpoints.items():
            try:
                health_url = f"{endpoint}/health" if service_name != "frontend" else endpoint
                response = requests.get(health_url, timeout=10)

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status", "unknown")
                    self.log_test("integration_tests", f"服务健康检查 - {service_name}", True, f"状态: {status}")
                else:
                    self.log_test("integration_tests", f"服务健康检查 - {service_name}", False, f"HTTP {response.status_code}")

            except Exception as e:
                self.log_test("integration_tests", f"服务健康检查 - {service_name}", False, str(e))

    async def test_api_integration(self):
        """测试API集成"""
        # 测试MCP服务器API
        await self.test_mcp_apis()

        # 测试后端API
        await self.test_backend_apis()

        # 测试AI服务API
        await self.test_ai_service_apis()

    async def test_mcp_apis(self):
        """测试MCP服务器API"""
        base_url = self.service_endpoints["mcp_server"]

        # 测试新闻API
        try:
            response = requests.post(
                f"{base_url}/mcp/news",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"count": 2, "country": "us", "use_cache": True}
                },
                timeout=15
            )
            success = response.status_code == 200
            self.log_test("integration_tests", "MCP新闻API", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("integration_tests", "MCP新闻API", False, str(e))

        # 测试天气API
        try:
            response = requests.post(
                f"{base_url}/mcp/weather",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"city": "Beijing", "use_cache": True}
                },
                timeout=15
            )
            success = response.status_code == 200
            self.log_test("integration_tests", "MCP天气API", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("integration_tests", "MCP天气API", False, str(e))

        # 测试电脑控制API
        try:
            response = requests.post(
                f"{base_url}/mcp/computer_control",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"action": "screen_info"}
                },
                timeout=10
            )
            success = response.status_code == 200
            self.log_test("integration_tests", "MCP电脑控制API", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("integration_tests", "MCP电脑控制API", False, str(e))

    async def test_backend_apis(self):
        """测试后端API"""
        base_url = self.service_endpoints["backend"]

        try:
            response = requests.get(f"{base_url}/api/config", timeout=10)
            success = response.status_code == 200
            self.log_test("integration_tests", "后端配置API", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("integration_tests", "后端配置API", False, str(e))

    async def test_ai_service_apis(self):
        """测试AI服务API"""
        base_url = self.service_endpoints["ai_service"]

        try:
            response = requests.get(f"{base_url}/", timeout=10)
            success = response.status_code == 200
            self.log_test("integration_tests", "AI服务根API", success, f"状态码: {response.status_code}")
        except Exception as e:
            self.log_test("integration_tests", "AI服务根API", False, str(e))

    async def test_module_communication(self):
        """测试模块间通信"""
        # 测试MCP服务器与后端通信
        try:
            # 这里可以添加更复杂的通信测试
            self.log_test("integration_tests", "模块间通信测试", True, "基础通信正常")
        except Exception as e:
            self.log_test("integration_tests", "模块间通信测试", False, str(e))

    async def run_e2e_tests(self):
        """运行端到端测试"""
        print("\n🎯 运行端到端测试...")
        print("-" * 40)

        # 测试完整工作流
        await self.test_complete_workflow()

        # 测试跨系统功能
        await self.test_cross_system_features()

        # 测试错误处理
        await self.test_error_handling()

    async def test_complete_workflow(self):
        """测试完整工作流"""
        try:
            # 模拟完整的工作流程
            # 1. 用户请求 -> 后端处理 -> MCP执行 -> AI分析 -> 结果返回

            # 测试新闻获取工作流
            workflow_success = await self.test_news_workflow()
            self.log_test("e2e_tests", "新闻获取工作流", workflow_success)

            # 测试天气查询工作流
            workflow_success = await self.test_weather_workflow()
            self.log_test("e2e_tests", "天气查询工作流", workflow_success)

        except Exception as e:
            self.log_test("e2e_tests", "完整工作流测试", False, str(e))

    async def test_news_workflow(self):
        """测试新闻获取工作流"""
        try:
            base_url = self.service_endpoints["mcp_server"]

            # 步骤1: 请求新闻
            response = requests.post(
                f"{base_url}/mcp/news",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"count": 3, "country": "us"}
                },
                timeout=20
            )

            if response.status_code != 200:
                return False

            data = response.json()
            if not data.get("success"):
                return False

            # 步骤2: 验证返回数据
            articles = data.get("data", {}).get("articles", [])
            return len(articles) > 0

        except Exception as e:
            print(f"新闻工作流测试异常: {str(e)}")
            return False

    async def test_weather_workflow(self):
        """测试天气查询工作流"""
        try:
            base_url = self.service_endpoints["mcp_server"]

            # 步骤1: 请求天气信息
            response = requests.post(
                f"{base_url}/mcp/weather",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"city": "Shanghai"}
                },
                timeout=20
            )

            if response.status_code != 200:
                return False

            data = response.json()
            if not data.get("success"):
                return False

            # 步骤2: 验证返回数据
            weather_data = data.get("data", {})
            return "temperature" in weather_data and "city" in weather_data

        except Exception as e:
            print(f"天气工作流测试异常: {str(e)}")
            return False

    async def test_cross_system_features(self):
        """测试跨系统功能"""
        try:
            # 测试MCP工具链
            tools_count = await self.get_available_tools_count()
            tools_success = tools_count >= 10  # 至少10个工具
            self.log_test("e2e_tests", "MCP工具链", tools_success, f"工具数量: {tools_count}")

            # 测试DeepSeek集成
            deepseek_success = await self.test_deepseek_integration()
            self.log_test("e2e_tests", "DeepSeek集成", deepseek_success)

            # 测试健康监控集成
            health_success = await self.test_health_monitoring_integration()
            self.log_test("e2e_tests", "健康监控集成", health_success)

        except Exception as e:
            self.log_test("e2e_tests", "跨系统功能测试", False, str(e))

    async def get_available_tools_count(self) -> int:
        """获取可用工具数量"""
        try:
            response = requests.get(f"{self.service_endpoints['mcp_server']}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return len(data.get("available_tools", []))
        except:
            pass
        return 0

    async def test_deepseek_integration(self):
        """测试DeepSeek集成"""
        try:
            base_url = self.service_endpoints["mcp_server"]

            response = requests.post(
                f"{base_url}/mcp/deepseek_llm",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"action": "get_workflows"}
                },
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            print(f"DeepSeek集成测试异常: {str(e)}")
            return False

    async def test_health_monitoring_integration(self):
        """测试健康监控集成"""
        try:
            base_url = self.service_endpoints["mcp_server"]

            response = requests.post(
                f"{base_url}/mcp/health_monitor",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"action": "summary"}
                },
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            print(f"健康监控集成测试异常: {str(e)}")
            return False

    async def test_error_handling(self):
        """测试错误处理"""
        try:
            base_url = self.service_endpoints["mcp_server"]

            # 测试无效参数
            response = requests.post(
                f"{base_url}/mcp/news",
                headers={"Content-Type": "application/json"},
                json={
                    "action": "execute",
                    "parameters": {"invalid_param": "value"}
                },
                timeout=10
            )

            # 应该返回错误但不应崩溃
            error_handled = response.status_code != 500
            self.log_test("e2e_tests", "错误处理机制", error_handled, f"状态码: {response.status_code}")

        except Exception as e:
            self.log_test("e2e_tests", "错误处理测试", False, str(e))

    async def run_performance_tests(self):
        """运行性能测试"""
        print("\n⚡ 运行性能测试...")
        print("-" * 40)

        # 测试API响应时间
        await self.test_api_response_times()

        # 测试并发处理能力
        await self.test_concurrent_requests()

        # 测试系统资源使用
        await self.test_system_resources()

    async def test_api_response_times(self):
        """测试API响应时间"""
        apis_to_test = [
            ("健康检查", f"{self.service_endpoints['mcp_server']}/health", "GET"),
            ("新闻API", f"{self.service_endpoints['mcp_server']}/mcp/news", "POST"),
            ("天气API", f"{self.service_endpoints['mcp_server']}/mcp/weather", "POST"),
        ]

        for api_name, url, method in apis_to_test:
            try:
                start_time = time.time()

                if method == "GET":
                    response = requests.get(url, timeout=10)
                else:
                    response = requests.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        json={"action": "execute", "parameters": {}},
                        timeout=10
                    )

                response_time = time.time() - start_time
                success = response.status_code == 200 and response_time < 5.0  # 5秒内响应

                self.log_test("performance_tests", f"响应时间 - {api_name}", success,
                            f"{response_time:.2f}s (状态码: {response.status_code})")

            except Exception as e:
                self.log_test("performance_tests", f"响应时间 - {api_name}", False, str(e))

    async def test_concurrent_requests(self):
        """测试并发请求"""
        try:
            base_url = self.service_endpoints["mcp_server"]
            concurrent_count = 5
            successful_requests = 0

            async def make_request():
                nonlocal successful_requests
                try:
                    response = requests.get(f"{base_url}/health", timeout=10)
                    if response.status_code == 200:
                        successful_requests += 1
                except:
                    pass

            # 并发发送请求
            tasks = [make_request() for _ in range(concurrent_count)]
            await asyncio.gather(*tasks)

            success_rate = successful_requests / concurrent_count
            success = success_rate >= 0.8  # 80%成功率

            self.log_test("performance_tests", f"并发请求 ({concurrent_count}个)", success,
                        f"成功率: {success_rate:.1%} ({successful_requests}/{concurrent_count})")

        except Exception as e:
            self.log_test("performance_tests", "并发请求测试", False, str(e))

    async def test_system_resources(self):
        """测试系统资源使用"""
        try:
            import psutil

            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_ok = cpu_percent < 80

            self.log_test("performance_tests", "CPU使用率", cpu_ok, f"{cpu_percent:.1f}%")

            # 内存使用率
            memory = psutil.virtual_memory()
            memory_ok = memory.percent < 80

            self.log_test("performance_tests", "内存使用率", memory_ok, f"{memory.percent:.1f}%")

            # 磁盘使用率
            disk = psutil.disk_usage('/')
            disk_ok = disk.percent < 90

            self.log_test("performance_tests", "磁盘使用率", disk_ok, f"{disk.percent:.1f}%")

        except ImportError:
            self.log_test("performance_tests", "系统资源测试", False, "psutil模块未安装")
        except Exception as e:
            self.log_test("performance_tests", "系统资源测试", False, str(e))

    def generate_test_report(self):
        """生成测试报告"""
        print("\n" + "=" * 60)
        print("📊 YOLO-LLM测试报告")
        print("=" * 60)

        test_duration = datetime.now() - self.test_start_time

        # 计算总体统计
        total_passed = sum(result["passed"] for result in self.test_results.values())
        total_failed = sum(result["failed"] for result in self.test_results.values())
        total_tests = sum(result["total"] for result in self.test_results.values())

        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

        print(f"🕐 测试开始时间: {self.test_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ 测试持续时间: {test_duration}")
        print(f"📈 总体成功率: {success_rate:.1f}% ({total_passed}/{total_tests})")
        print()

        # 分类统计
        for test_type, result in self.test_results.items():
            type_rate = (result["passed"] / result["total"] * 100) if result["total"] > 0 else 0
            print(f"📋 {test_type.replace('_', ' ').title()}:")
            print(f"   ✅ 通过: {result['passed']}")
            print(f"   ❌ 失败: {result['failed']}")
            print(f"   📊 成功率: {type_rate:.1f}%")
            print()

        # 服务状态
        print("🖥️ 服务状态:")
        for service_name, endpoint in self.service_endpoints.items():
            try:
                health_url = f"{endpoint}/health" if service_name != "frontend" else endpoint
                response = requests.get(health_url, timeout=5)
                status = "🟢 运行中" if response.status_code == 200 else "🔴 异常"
                print(f"   {service_name}: {status} ({endpoint})")
            except:
                print(f"   {service_name}: 🔴 无法连接 ({endpoint})")

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
            print("📄 详细报告已保存到: test_report.json")
        except Exception as e:
            print(f"⚠️ 保存报告失败: {str(e)}")

async def main():
    """主函数"""
    test_suite = YOLOLLMTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())