#!/usr/bin/env python3
"""
完整工作流测试
1. 获取北京天气
2. 获取新闻
3. 发送邮件到 1730495747@qq.com
"""

import requests
import json
from datetime import datetime

# MCP服务器地址
MCP_SERVER = "http://localhost:8082"

def test_complete_workflow():
    """测试完整工作流"""
    print("🚀 开始测试完整工作流...")

    # 1. 获取北京天气
    print("\n📡 1. 获取北京天气...")
    weather_response = requests.post(
        f"{MCP_SERVER}/mcp/weather",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {
                "city": "Beijing",
                "units": "metric",
                "lang": "zh_cn"
            }
        }
    )

    if weather_response.status_code == 200:
        weather_data = weather_response.json()
        if weather_data.get("success"):
            weather = weather_data["data"]["weather"]
            print(f"✅ 天气获取成功: {weather['city']} {weather['temperature']}°C {weather['description']}")
        else:
            print(f"❌ 天气获取失败: {weather_data.get('error')}")
            return
    else:
        print(f"❌ 天气API调用失败: {weather_response.status_code}")
        return

    # 2. 获取新闻
    print("\n📰 2. 获取新闻...")
    news_response = requests.post(
        f"{MCP_SERVER}/mcp/news",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {
                "count": 10,
                "country": "cn"
            }
        }
    )

    if news_response.status_code == 200:
        news_data = news_response.json()
        if news_data.get("success"):
            news_list = news_data["data"]["news"]
            print(f"✅ 新闻获取成功: {len(news_list)} 条")
        else:
            print(f"❌ 新闻获取失败: {news_data.get('error')}")
            return
    else:
        print(f"❌ 新闻API调用失败: {news_response.status_code}")
        return

    # 3. 构建邮件内容
    print("\n📧 3. 构建邮件内容...")
    email_subject = f"YOLO-LLM智能工作流报告 - 北京天气与新闻 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    email_content = f"""
YOLO-LLM智能工作流报告
生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

🌤️ 北京天气信息:
城市: {weather['city']}
温度: {weather['temperature']}°C (体感: {weather['feels_like']}°C)
天气: {weather['description']}
湿度: {weather['humidity']}%
风速: {weather['wind_speed']} m/s
气压: {weather['pressure']} hPa
数据源: OpenWeatherMap真实API

📰 今日新闻 (前10条):
"""

    if news_list:
        for i, news in enumerate(news_list[:10], 1):
            email_content += f"\n{i}. {news}"
    else:
        email_content += "\n暂无新闻数据"

    email_content += f"\n\n数据源: NewsAPI.org真实API\n\n此邮件由YOLO-LLM智能代理系统自动生成"

    print(f"邮件主题: {email_subject}")
    print(f"邮件内容长度: {len(email_content)} 字符")

    # 4. 发送邮件
    print("\n📮 4. 发送邮件...")
    email_response = requests.post(
        f"{MCP_SERVER}/mcp/email",
        headers={"Content-Type": "application/json"},
        json={
            "action": "execute",
            "parameters": {
                "to": "1730495747@qq.com",
                "subject": email_subject,
                "content": email_content
            }
        }
    )

    if email_response.status_code == 200:
        email_data = email_response.json()
        if email_data.get("success"):
            print(f"✅ 邮件发送成功!")
            print(f"   邮件ID: {email_data['data']['email_id']}")
            print(f"   收件人: {email_data['data']['to']}")
            print(f"   数据源: {email_data['data']['source']}")
        else:
            print(f"❌ 邮件发送失败: {email_data.get('error')}")
    else:
        print(f"❌ 邮件API调用失败: {email_response.status_code}")
        print(f"响应内容: {email_response.text}")

    print("\n🎉 工作流测试完成!")

if __name__ == "__main__":
    test_complete_workflow()