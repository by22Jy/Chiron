#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整系统测试脚本
验证所有服务是否正常运行并提供功能测试
"""

import requests
import json
import time
from datetime import datetime

# 服务地址配置
SERVICES = {
    "mcp": "http://localhost:8082",
    "backend": "http://localhost:8080",
    "ai": "http://localhost:8000",
    "frontend": "http://localhost:5173"
}

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def test_service_health(service_name, url):
    """测试服务健康状态"""
    try:
        health_url = f"{url}/health"
        response = requests.get(health_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {service_name}: 健康 ({data.get('status', 'unknown')})")
            return True
        else:
            print(f"❌ {service_name}: 不健康 (HTTP {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {service_name}: 无法连接 ({str(e)[:50]}...)")
        return False
    except Exception as e:
        print(f"❌ {service_name}: 未知错误 ({str(e)[:50]}...)")
        return False

def test_mcp_functions():
    """测试MCP功能"""
    print_header("MCP 功能测试")

    mcp_url = SERVICES["mcp"]
    functions_tested = 0
    functions_passed = 0

    # 测试健康检查
    if test_service_health("MCP服务器", mcp_url):
        functions_tested += 1
        functions_passed += 1

    # 测试新闻功能
    try:
        response = requests.post(
            f"{mcp_url}/mcp/news",
            headers={"Content-Type": "application/json"},
            json={"action": "execute", "parameters": {"count": 3}},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                news_count = len(data["data"]["news"])
                print(f"✅ 新闻功能: 获取到 {news_count} 条新闻")
                functions_passed += 1
            else:
                print(f"❌ 新闻功能: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 新闻功能: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 新闻功能: {str(e)[:50]}...")
    functions_tested += 1

    # 测试天气功能
    try:
        response = requests.post(
            f"{mcp_url}/mcp/weather",
            headers={"Content-Type": "application/json"},
            json={"action": "execute", "parameters": {"city": "Beijing"}},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                weather = data["data"]["weather"]
                print(f"✅ 天气功能: {weather['city']} {weather['temperature']}°C {weather['description']}")
                functions_passed += 1
            else:
                print(f"❌ 天气功能: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 天气功能: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 天气功能: {str(e)[:50]}...")
    functions_tested += 1

    # 测试文件系统功能
    try:
        test_content = f"YOLO-LLM系统测试 - {datetime.now().isoformat()}"
        response = requests.post(
            f"{mcp_url}/mcp/filesystem",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "operation": "write",
                    "path": "test_output.txt",
                    "content": test_content
                }
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                size = data["data"]["content_length"]
                print(f"✅ 文件系统功能: 写入 {size} 字节成功")
                functions_passed += 1
            else:
                print(f"❌ 文件系统功能: {data.get('error', '未知错误')}")
        else:
            print(f"❌ 文件系统功能: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ 文件系统功能: {str(e)[:50]}...")
    functions_tested += 1

    print(f"\n📊 MCP功能测试结果: {functions_passed}/{functions_tested} ({functions_passed/functions_tested*100:.1f}%)")
    return functions_passed == functions_tested

def test_backend_functions():
    """测试Backend功能"""
    print_header("Backend 功能测试")

    backend_url = SERVICES["backend"]

    # 测试配置API
    try:
        response = requests.get(f"{backend_url}/api/config", timeout=10)
        if response.status_code == 200:
            data = response.json()
            mappings = data.get("mappings", [])
            print(f"✅ 配置API: 获取到 {len(mappings)} 个手势映射")

            # 显示前几个映射
            for i, mapping in enumerate(mappings[:3]):
                print(f"   {i+1}. {mapping['code']} → {mapping['action']['description']}")

            return True
        else:
            print(f"❌ 配置API: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 配置API: {str(e)[:50]}...")
        return False

def test_system_integration():
    """测试系统集成"""
    print_header("系统集成测试")

    integration_results = []

    # 1. 测试MCP -> Backend集成
    print("\n🔗 测试 MCP 与 Backend 集成...")
    try:
        # 这里可以测试Backend调用MCP的接口（如果已实现）
        backend_url = SERVICES["backend"]
        mcp_url = SERVICES["mcp"]

        # 首先检查两个服务都健康
        backend_healthy = test_service_health("Backend", backend_url)
        mcp_healthy = test_service_health("MCP服务器", mcp_url)

        if backend_healthy and mcp_healthy:
            print("✅ MCP-Backend 集成: 两个服务都正常运行")
            integration_results.append(True)
        else:
            print("❌ MCP-Backend 集成: 服务状态异常")
            integration_results.append(False)

    except Exception as e:
        print(f"❌ MCP-Backend 集成: {str(e)[:50]}...")
        integration_results.append(False)

    # 2. 测试完整工作流
    print("\n🔄 测试完整工作流: 获取天气信息")
    try:
        mcp_url = SERVICES["mcp"]

        # 步骤1: 获取天气
        weather_response = requests.post(
            f"{mcp_url}/mcp/weather",
            headers={"Content-Type": "application/json"},
            json={"action": "execute", "parameters": {"city": "Shanghai"}}
        )

        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            if weather_data.get("success"):
                weather = weather_data["data"]["weather"]
                print(f"✅ 工作流测试: 获取上海天气 {weather['temperature']}°C")
                integration_results.append(True)
            else:
                print(f"❌ 工作流测试: {weather_data.get('error')}")
                integration_results.append(False)
        else:
            print(f"❌ 工作流测试: HTTP {weather_response.status_code}")
            integration_results.append(False)

    except Exception as e:
        print(f"❌ 工作流测试: {str(e)[:50]}...")
        integration_results.append(False)

    success_rate = sum(integration_results) / len(integration_results) * 100
    print(f"\n📊 集成测试结果: {sum(integration_results)}/{len(integration_results)} ({success_rate:.1f}%)")
    return success_rate >= 75

def main():
    """主测试函数"""
    print_header("YOLO-LLM 完整系统测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    all_tests_passed = True

    # 1. 服务健康检查
    print_header("服务健康检查")
    health_results = []
    for service_name, url in SERVICES.items():
        healthy = test_service_health(service_name.upper(), url)
        health_results.append(healthy)

    healthy_count = sum(health_results)
    total_count = len(health_results)
    print(f"\n📊 服务健康状态: {healthy_count}/{total_count} ({healthy_count/total_count*100:.1f}%)")

    if healthy_count < 2:  # 至少需要2个核心服务运行
        print("⚠️ 警告: 核心服务数量不足，某些功能测试将被跳过")
        all_tests_passed = False

    # 2. MCP功能测试
    mcp_passed = test_mcp_functions()
    if not mcp_passed:
        all_tests_passed = False

    # 3. Backend功能测试
    backend_passed = test_backend_functions()
    if not backend_passed:
        all_tests_passed = False

    # 4. 系统集成测试
    integration_passed = test_system_integration()
    if not integration_passed:
        all_tests_passed = False

    # 5. 生成测试报告
    print_header("测试总结")

    if all_tests_passed:
        print("🎉 恭喜！所有测试都通过了！")
        print("✅ YOLO-LLM 系统运行正常，所有功能都可以正常使用")
    else:
        print("⚠️ 部分测试失败，请检查相关服务状态")
        print("💡 建议: 使用 start-all.bat 重新启动所有服务")

    print("\n📋 可用功能:")
    print("   🌐 MCP服务器: http://localhost:8082")
    print("   ⚙️  Backend API: http://localhost:8080")
    print("   🤖 AI服务: http://localhost:8000" if health_results[2] else "   🤖 AI服务: 未运行")
    print("   🖥️  前端界面: http://localhost:5173" if health_results[3] else "   🖥️  前端界面: 未运行")

    print("\n🔧 快速测试命令:")
    print("   curl http://localhost:8082/health")
    print("   curl http://localhost:8080/api/config")
    print("   curl -X POST http://localhost:8082/mcp/weather -d '{\"action\":\"execute\",\"parameters\":{\"city\":\"Beijing\"}}'")

if __name__ == "__main__":
    main()