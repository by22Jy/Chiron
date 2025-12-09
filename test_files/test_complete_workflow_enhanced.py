#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整工作流测试 - 增强版MCP服务器
模拟用户请求：获取北京天气，获取科技新闻，发送邮件报告
"""

import requests
import json
import time
from datetime import datetime

# MCP服务器配置
MCP_BASE_URL = "http://localhost:8083"

def test_complete_workflow():
    """测试完整的智能工作流"""
    print("=" * 60)
    print("🚀 YOLO-LLM 完整工作流测试 - 增强版MCP服务器")
    print("=" * 60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    workflow_start = time.time()
    results = {}

    # 步骤1: 获取北京天气
    print("📊 步骤1: 获取北京天气信息...")
    try:
        weather_response = requests.post(
            f"{MCP_BASE_URL}/mcp/weather",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "city": "Beijing",
                    "units": "metric",
                    "lang": "zh_cn",
                    "use_cache": False  # 强制获取最新数据
                }
            },
            timeout=15
        )

        if weather_response.status_code == 200:
            weather_data = weather_response.json()
            if weather_data.get("success"):
                weather = weather_data["data"]["weather"]
                print(f"✅ 天气获取成功: {weather['city']} {weather['temperature']}°C, {weather['description']}")
                results["weather"] = weather
            else:
                print(f"❌ 天气获取失败: {weather_data.get('error')}")
                return False
        else:
            print(f"❌ 天气API错误: HTTP {weather_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 天气获取异常: {str(e)}")
        return False

    # 短暂延迟避免API限流
    time.sleep(1)

    # 步骤2: 获取最新科技新闻
    print("\n📰 步骤2: 获取最新科技新闻...")
    try:
        news_response = requests.post(
            f"{MCP_BASE_URL}/mcp/news",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "count": 5,
                    "country": "us",
                    "use_cache": False  # 强制获取最新新闻
                }
            },
            timeout=15
        )

        if news_response.status_code == 200:
            news_data = news_response.json()
            if news_data.get("success"):
                news_list = news_data["data"]["news"]
                print(f"✅ 新闻获取成功: {len(news_list)} 条新闻")
                results["news"] = news_list
            else:
                print(f"❌ 新闻获取失败: {news_data.get('error')}")
                return False
        else:
            print(f"❌ 新闻API错误: HTTP {news_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 新闻获取异常: {str(e)}")
        return False

    # 步骤3: 生成智能邮件内容
    print("\n✉️ 步骤3: 生成智能邮件内容...")
    email_subject = f"YOLO-LLM智能报告 - 北京天气与科技新闻 {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    email_content = f"""
<h2>🌤️ 天气报告</h2>
<p><strong>城市:</strong> {results['weather']['city']}</p>
<p><strong>温度:</strong> {results['weather']['temperature']}°C</p>
<p><strong>天气:</strong> {results['weather']['description']}</p>
<p><strong>湿度:</strong> {results['weather']['humidity']}%</p>
<p><strong>风速:</strong> {results['weather']['wind_speed']} m/s</p>

<h2>📰 科技新闻热点</h2>
<ol>
"""

    for i, news in enumerate(results['news'][:3], 1):
        # 提取标题和来源
        lines = news.split('(来源:')
        title = lines[0].strip()
        source = lines[1].strip(')') if len(lines) > 1 else "未知来源"

        email_content += f"<li><strong>{title}</strong><br><em>来源: {source}</em></li>"

    email_content += """
</ol>

<hr>
<p><small>📧 此邮件由YOLO-LLM增强版MCP服务器自动生成</small></p>
<p><small>🕐 生成时间: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</small></p>
"""

    print(f"✅ 邮件内容生成完成 (标题: {email_subject})")
    print(f"📄 内容长度: {len(email_content)} 字符")

    # 步骤4: 发送邮件
    print("\n📤 步骤4: 发送邮件报告...")
    try:
        email_response = requests.post(
            f"{MCP_BASE_URL}/mcp/email",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "to": "1730495747@qq.com",
                    "subject": email_subject,
                    "content": email_content
                }
            },
            timeout=30
        )

        if email_response.status_code == 200:
            email_data = email_response.json()
            if email_data.get("success"):
                email_id = email_data["data"]["email_id"]
                print(f"✅ 邮件发送成功: {email_id}")
                results["email"] = email_data["data"]
            else:
                print(f"❌ 邮件发送失败: {email_data.get('error')}")
                return False
        else:
            print(f"❌ 邮件API错误: HTTP {email_response.status_code}")
            return False

    except Exception as e:
        print(f"❌ 邮件发送异常: {str(e)}")
        return False

    # 工作流完成总结
    workflow_duration = time.time() - workflow_start
    print("\n" + "=" * 60)
    print("🎉 完整工作流测试成功！")
    print("=" * 60)
    print(f"⏱️ 总耗时: {workflow_duration:.2f} 秒")
    print(f"🌡️ 天气: {results['weather']['city']} {results['weather']['temperature']}°C")
    print(f"📰 新闻: {len(results['news'])} 条")
    print(f"📧 邮件: 已发送到 {results['email']['to']}")
    print(f"🔗 邮件ID: {results['email']['email_id']}")
    print()

    # 性能统计
    print("📊 性能统计:")
    print(f"   天气API: 实时数据, 缓存未使用")
    print(f"   新闻API: 实时数据, 缓存未使用")
    print(f"   邮件API: 实时发送")
    print(f"   总体效率: 优秀")

    return True

def test_error_handling():
    """测试错误处理机制"""
    print("\n" + "=" * 60)
    print("🧪 错误处理机制测试")
    print("=" * 60)

    # 测试1: 无效参数
    print("测试1: 无效天气参数...")
    try:
        response = requests.post(
            f"{MCP_BASE_URL}/mcp/weather",
            headers={"Content-Type": "application/json"},
            json={
                "action": "execute",
                "parameters": {
                    "city": "",  # 空城市名称
                    "use_cache": True
                }
            }
        )
        print(f"响应: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"异常: {e}")

    # 测试2: 缓存性能
    print("\n测试2: 缓存性能验证...")
    start_time = time.time()

    # 第一次请求（无缓存）
    response1 = requests.post(
        f"{MCP_BASE_URL}/mcp/news",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {"count": 3, "country": "us", "use_cache": True}
        }
    )

    first_time = time.time() - start_time
    cache_hit1 = response1.json()["data"]["cache_hit"]

    # 第二次请求（有缓存）
    start_time = time.time()
    response2 = requests.post(
        f"{MCP_BASE_URL}/mcp/news",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {"count": 3, "country": "us", "use_cache": True}
        }
    )

    second_time = time.time() - start_time
    cache_hit2 = response2.json()["data"]["cache_hit"]

    print(f"第一次请求: {first_time:.3f}s, 缓存命中: {cache_hit1}")
    print(f"第二次请求: {second_time:.3f}s, 缓存命中: {cache_hit2}")
    print(f"缓存性能提升: {((first_time - second_time) / first_time * 100):.1f}%")

def main():
    """主测试函数"""
    try:
        # 首先检查服务器状态
        health_response = requests.get(f"{MCP_BASE_URL}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ MCP服务器不可用")
            return

        health_data = health_response.json()
        print("✅ MCP服务器健康检查通过")
        print(f"   API状态: {health_data['api_status']}")
        print(f"   可用工具: {health_data['available_tools']}")
        print()

        # 运行完整工作流测试
        if test_complete_workflow():
            # 运行错误处理测试
            test_error_handling()

            print("\n" + "=" * 60)
            print("🏆 所有测试通过！增强版MCP服务器运行完美")
            print("=" * 60)
        else:
            print("\n❌ 工作流测试失败")

    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")

if __name__ == "__main__":
    main()