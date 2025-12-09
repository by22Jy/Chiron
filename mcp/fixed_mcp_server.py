#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化修复版MCP服务器
专注于新闻、天气、邮件功能
"""

import os
import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
BREVO_API_KEY = os.getenv('BREVO_API_KEY')

app = FastAPI(
    title="Fixed MCP Server",
    description="修复版MCP服务器 - 专注核心功能",
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ToolRequest(BaseModel):
    action: str = "execute"
    parameters: Dict[str, Any] = {}

@app.get("/")
async def root():
    return {"message": "Fixed MCP Server - News, Weather, Email"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_status": {
            "news_api": "configured" if NEWS_API_KEY else "not_configured",
            "weather_api": "configured" if WEATHER_API_KEY else "not_configured",
            "smtp": "configured" if BREVO_API_KEY else "not_configured"
        },
        "available_tools": ["news", "weather", "email", "filesystem"]
    }

@app.get("/tools")
async def list_tools():
    tools = [
        {
            "name": "news",
            "description": "获取最新新闻",
            "parameters": {
                "count": {"type": "integer", "default": 10, "description": "新闻数量"},
                "country": {"type": "string", "default": "us", "description": "国家代码"}
            }
        },
        {
            "name": "weather",
            "description": "获取天气信息",
            "parameters": {
                "city": {"type": "string", "required": True, "description": "城市名称"},
                "units": {"type": "string", "default": "metric", "description": "单位制"},
                "lang": {"type": "string", "default": "zh_cn", "description": "语言"}
            }
        },
        {
            "name": "email",
            "description": "发送邮件",
            "parameters": {
                "to": {"type": "string", "required": True, "description": "收件人邮箱"},
                "subject": {"type": "string", "required": True, "description": "邮件主题"},
                "content": {"type": "string", "required": True, "description": "邮件内容"}
            }
        }
    ]
    return {"tools": tools}

@app.post("/mcp/news")
async def handle_news_tool(request: ToolRequest):
    """处理新闻工具请求"""
    try:
        params = request.parameters
        count = params.get("count", 10)
        country = params.get("country", "us")

        print(f"执行MCP工具: news, 参数: {params}")

        if NEWS_API_KEY:
            # 使用真实NewsAPI
            news_list = await get_real_news(count, country)
        else:
            # 使用模拟数据
            news_list = get_mock_news(count)

        return {
            "success": True,
            "data": {
                "news": news_list,
                "count": len(news_list),
                "source": "real_api" if NEWS_API_KEY else "mock",
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"新闻工具错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/mcp/weather")
async def handle_weather_tool(request: ToolRequest):
    """处理天气工具请求"""
    try:
        params = request.parameters
        city = params.get("city", "Beijing")
        units = params.get("units", "metric")
        lang = params.get("lang", "zh_cn")

        print(f"执行MCP工具: weather, 参数: {params}")

        if WEATHER_API_KEY:
            # 使用真实天气API
            weather_data = await get_real_weather(city, units, lang)
        else:
            # 使用模拟数据
            weather_data = get_mock_weather(city)

        return {
            "success": True,
            "data": {
                "weather": weather_data,
                "source": "real_api" if WEATHER_API_KEY else "mock",
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"天气工具错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/mcp/email")
async def handle_email_tool(request: ToolRequest):
    """处理邮件工具请求"""
    try:
        params = request.parameters
        to_email = params.get("to")
        subject = params.get("subject")
        content = params.get("content")

        print(f"执行MCP工具: email, 参数: {params}")

        if not all([to_email, subject, content]):
            raise ValueError("邮件参数不完整")

        if BREVO_API_KEY:
            # 使用真实Brevo API
            email_id = await send_real_email(to_email, subject, content)
        else:
            # 使用模拟发送
            email_id = f"mock_email_{hash(content)}"

        return {
            "success": True,
            "data": {
                "email_id": email_id,
                "to": to_email,
                "subject": subject,
                "source": "real_api" if BREVO_API_KEY else "mock",
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"邮件工具错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/mcp/filesystem")
async def handle_filesystem_tool(request: ToolRequest):
    """处理文件系统工具请求"""
    try:
        params = request.parameters
        operation = params.get("operation", "read")
        path = params.get("path", "")
        content = params.get("content", "")

        print(f"执行MCP工具: filesystem, 参数: {params}")

        if operation == "write":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            result = {"content_length": len(content)}
        elif operation == "read":
            with open(path, 'r', encoding='utf-8') as f:
                result = {"content": f.read()}
        else:
            raise ValueError(f"不支持的操作: {operation}")

        return {
            "success": True,
            "data": {
                "operation": operation,
                "path": path,
                **result,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"文件系统工具错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# 真实API函数
async def get_real_news(count: int, country: str) -> List[str]:
    """获取真实新闻 - 修复版"""
    try:
        from newsapi import NewsApiClient
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)

        news_list = []

        print(f"尝试获取国家 {country} 的新闻...")

        # 策略1: 尝试获取用户指定国家的新闻
        if country == 'cn':
            # 对于中国，尝试关键词搜索中文内容
            print("使用中文关键词搜索...")
            response = newsapi.get_everything(
                q='科技 OR 财经 OR 国际',
                language='zh',
                sort_by='publishedAt',
                page_size=min(count, 100)
            )
        else:
            # 对于其他国家，获取头条新闻
            print(f"获取 {country} 头条新闻...")
            response = newsapi.get_top_headlines(
                country=country,
                page_size=min(count, 100)
            )

        articles = response.get('articles', [])
        print(f"获取到 {len(articles)} 篇文章")

        # 如果没有结果，使用备用策略
        if len(articles) == 0:
            print("无结果，使用英文科技新闻作为备用")
            response = newsapi.get_top_headlines(
                category='technology',
                language='en',
                page_size=min(count, 100)
            )
            articles = response.get('articles', [])
            print(f"备用策略获取到 {len(articles)} 篇文章")

        for i, article in enumerate(articles[:count], 1):
            title = article.get('title', '').strip()
            description = article.get('description', '').strip()
            source = article.get('source', {}).get('name', 'Unknown Source')

            # 过滤掉None值和空字符串
            if not title:
                continue

            news_item = f"{i}. {title}"
            if description and description != title and len(description) > 10:
                news_item += f" - {description[:200]}..."
            news_item += f" (来源: {source})"

            news_list.append(news_item)

        print(f"成功处理 {len(news_list)} 条新闻")
        return news_list

    except Exception as e:
        print(f"获取新闻失败: {str(e)}")
        return get_mock_news(count)

async def get_real_weather(city: str, units: str, lang: str) -> Dict[str, Any]:
    """获取真实天气"""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': units,
            'lang': lang
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        return {
            "city": data['name'],
            "temperature": data['main']['temp'],
            "description": data['weather'][0]['description'],
            "humidity": data['main']['humidity'],
            "wind_speed": data.get('wind', {}).get('speed', 0),
            "units": units
        }

    except Exception as e:
        print(f"获取真实天气失败: {str(e)}")
        return get_mock_weather(city)

async def send_real_email(to_email: str, subject: str, content: str) -> str:
    """发送真实邮件"""
    try:
        from brevo import ApiClient
        from brevo.api import TransactionalEmailsApi
        from brevo.models import SendSmtpEmail

        api_instance = TransactionalEmailsApi(ApiClient())
        api_instance.api_client.configuration.api_key['api-key'] = BREVO_API_KEY

        # 使用已验证的发送者邮箱
        sender = {"name": "YOLO-LLM 系统", "email": "by2022jy@gmail.com"}

        to = [{"email": to_email}]

        send_smtp_email = SendSmtpEmail(
            sender=sender,
            to=to,
            subject=subject,
            html_content=f"<html><body>{content.replace(chr(10), '<br>')}</body></html>",
            text_content=content
        )

        result = api_instance.send_transac_email(send_smtp_email)
        email_id = getattr(result, 'message_id', 'email_sent')

        print(f"真实邮件发送成功: {email_id} -> {to_email}")
        return email_id

    except Exception as e:
        print(f"发送真实邮件失败: {str(e)}")
        raise e

# 模拟数据函数
def get_mock_news(count: int) -> List[str]:
    """获取模拟新闻"""
    mock_news = [
        "1. GPT-5即将发布，AI能力再次突破",
        "2. 量子计算机实现新里程碑",
        "3. 新能源汽车市场持续增长",
        "4. 全球气候变化会议达成新协议",
        "5. 科技巨头推出新一代操作系统"
    ]
    return mock_news[:count]

def get_mock_weather(city: str) -> Dict[str, Any]:
    """获取模拟天气"""
    return {
        "city": city,
        "temperature": 22,
        "description": "晴朗",
        "humidity": 65,
        "wind_speed": 10,
        "units": "metric"
    }

if __name__ == "__main__":
    print("启动修复版MCP服务器...")
    print(f"NewsAPI配置: {'已配置' if NEWS_API_KEY else '未配置'}")
    print(f"WeatherAPI配置: {'已配置' if WEATHER_API_KEY else '未配置'}")
    print(f"邮件API配置: {'已配置' if BREVO_API_KEY else '未配置'}")

    uvicorn.run(app, host="127.0.0.1", port=8082)