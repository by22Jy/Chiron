#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版MCP服务器
集成错误处理、重试机制、缓存和性能监控
"""

import os
import asyncio
import json
import requests
import time
from datetime import datetime
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# 导入我们的工具模块
from mcp_utils import (
    retry_with_backoff, timeout_handler, mcp_cache, mcp_monitor, mcp_error_handler,
    MCPRetryException, MCPTimeoutException
)

# API Keys
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
BREVO_API_KEY = os.getenv('BREVO_API_KEY')

app = FastAPI(
    title="Enhanced MCP Server",
    description="增强版MCP服务器 - 包含错误处理、重试和缓存",
    version="2.0.0"
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
    return {
        "message": "Enhanced MCP Server with Error Handling & Caching",
        "features": ["Retry with Backoff", "Caching", "Performance Monitoring", "Error Handling"]
    }

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
        "available_tools": ["news", "weather", "email", "filesystem"],
        "cache_stats": mcp_cache.get_stats(),
        "error_summary": mcp_error_handler.get_error_summary()
    }

@app.get("/tools")
async def list_tools():
    tools = [
        {
            "name": "news",
            "description": "获取最新新闻（带缓存）",
            "parameters": {
                "count": {"type": "integer", "default": 10, "description": "新闻数量"},
                "country": {"type": "string", "default": "us", "description": "国家代码"},
                "use_cache": {"type": "boolean", "default": True, "description": "是否使用缓存"}
            }
        },
        {
            "name": "weather",
            "description": "获取天气信息（带缓存）",
            "parameters": {
                "city": {"type": "string", "required": True, "description": "城市名称"},
                "units": {"type": "string", "default": "metric", "description": "单位制"},
                "lang": {"type": "string", "default": "zh_cn", "description": "语言"},
                "use_cache": {"type": "boolean", "default": True, "description": "是否使用缓存"}
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
    """处理新闻工具请求 - 增强版"""
    start_time = time.time()
    tool_name = "news"
    params = request.parameters
    count = params.get("count", 10)
    country = params.get("country", "us")
    use_cache = params.get("use_cache", True)

    try:
        print(f"执行增强版MCP工具: {tool_name}, 参数: {params}")

        # 检查缓存
        cache_data = None
        if use_cache:
            cache_data = mcp_cache.get(tool_name, params)
            if cache_data:
                duration = time.time() - start_time
                mcp_monitor.record_request(tool_name, duration, True)
                return {
                    "success": True,
                    "data": {
                        **cache_data,
                        "cache_hit": True,
                        "timestamp": datetime.now().isoformat()
                    }
                }

        # 获取新闻数据（带重试和超时）
        if NEWS_API_KEY:
            news_list = await get_real_news_enhanced(count, country)
        else:
            news_list = get_mock_news(count)

        result = {
            "success": True,
            "data": {
                "news": news_list,
                "count": len(news_list),
                "source": "real_api" if NEWS_API_KEY else "mock",
                "cache_hit": False,
                "timestamp": datetime.now().isoformat()
            }
        }

        # 设置缓存
        if use_cache:
            mcp_cache.set(tool_name, params, result["data"], ttl=600)  # 新闻缓存10分钟

        duration = time.time() - start_time
        mcp_monitor.record_request(tool_name, duration, True)
        return result

    except Exception as e:
        duration = time.time() - start_time
        mcp_monitor.record_request(tool_name, duration, False, str(e))

        error_response = mcp_error_handler.handle_error(e, tool_name, params)
        return error_response

@app.post("/mcp/weather")
async def handle_weather_tool(request: ToolRequest):
    """处理天气工具请求 - 增强版"""
    start_time = time.time()
    tool_name = "weather"
    params = request.parameters
    city = params.get("city", "Beijing")
    units = params.get("units", "metric")
    lang = params.get("lang", "zh_cn")
    use_cache = params.get("use_cache", True)

    try:
        print(f"执行增强版MCP工具: {tool_name}, 参数: {params}")

        # 检查缓存
        cache_data = None
        if use_cache:
            cache_data = mcp_cache.get(tool_name, params)
            if cache_data:
                duration = time.time() - start_time
                mcp_monitor.record_request(tool_name, duration, True)
                return {
                    "success": True,
                    "data": {
                        **cache_data,
                        "cache_hit": True,
                        "timestamp": datetime.now().isoformat()
                    }
                }

        # 获取天气数据（带重试和超时）
        if WEATHER_API_KEY:
            weather_data = await get_real_weather_enhanced(city, units, lang)
        else:
            weather_data = get_mock_weather(city)

        result = {
            "success": True,
            "data": {
                "weather": weather_data,
                "source": "real_api" if WEATHER_API_KEY else "mock",
                "cache_hit": False,
                "timestamp": datetime.now().isoformat()
            }
        }

        # 设置缓存
        if use_cache:
            mcp_cache.set(tool_name, params, result["data"], ttl=1800)  # 天气缓存30分钟

        duration = time.time() - start_time
        mcp_monitor.record_request(tool_name, duration, True)
        return result

    except Exception as e:
        duration = time.time() - start_time
        mcp_monitor.record_request(tool_name, duration, False, str(e))

        error_response = mcp_error_handler.handle_error(e, tool_name, params)
        return error_response

@app.post("/mcp/email")
async def handle_email_tool(request: ToolRequest):
    """处理邮件工具请求 - 增强版"""
    start_time = time.time()
    tool_name = "email"
    params = request.parameters
    to_email = params.get("to")
    subject = params.get("subject")
    content = params.get("content")

    try:
        print(f"执行增强版MCP工具: {tool_name}, 参数: {params}")

        if not all([to_email, subject, content]):
            raise ValueError("邮件参数不完整")

        # 发送邮件（带重试和超时）
        if BREVO_API_KEY:
            email_id = await send_real_email_enhanced(to_email, subject, content)
        else:
            email_id = f"mock_email_{hash(content)}"

        result = {
            "success": True,
            "data": {
                "email_id": email_id,
                "to": to_email,
                "subject": subject,
                "source": "real_api" if BREVO_API_KEY else "mock",
                "timestamp": datetime.now().isoformat()
            }
        }

        duration = time.time() - start_time
        mcp_monitor.record_request(tool_name, duration, True)
        return result

    except Exception as e:
        duration = time.time() - start_time
        mcp_monitor.record_request(tool_name, duration, False, str(e))

        error_response = mcp_error_handler.handle_error(e, tool_name, params)
        return error_response

@app.post("/mcp/filesystem")
async def handle_filesystem_tool(request: ToolRequest):
    """处理文件系统工具请求 - 增强版"""
    start_time = time.time()
    tool_name = "filesystem"
    params = request.parameters
    operation = params.get("operation", "read")
    path = params.get("path", "")
    content = params.get("content", "")

    try:
        print(f"执行增强版MCP工具: {tool_name}, 参数: {params}")

        if operation == "write":
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            result = {"content_length": len(content)}
        elif operation == "read":
            with open(path, 'r', encoding='utf-8') as f:
                result = {"content": f.read()}
        else:
            raise ValueError(f"不支持的操作: {operation}")

        response = {
            "success": True,
            "data": {
                "operation": operation,
                "path": path,
                **result,
                "timestamp": datetime.now().isoformat()
            }
        }

        duration = time.time() - start_time
        mcp_monitor.record_request(tool_name, duration, True)
        return response

    except Exception as e:
        duration = time.time() - start_time
        mcp_monitor.record_request(tool_name, duration, False, str(e))

        error_response = mcp_error_handler.handle_error(e, tool_name, params)
        return error_response

@app.get("/admin/stats")
async def get_performance_stats():
    """获取性能统计"""
    return {
        "performance": mcp_monitor.get_performance_report(),
        "cache": mcp_cache.get_stats(),
        "errors": mcp_error_handler.get_error_summary(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/admin/cache/clear")
async def clear_cache(tool_name: str = None):
    """清除缓存"""
    mcp_cache.clear(tool_name)
    return {
        "success": True,
        "message": f"已清除 {tool_name or '所有'} 的缓存",
        "timestamp": datetime.now().isoformat()
    }

# 增强的API函数（带重试和超时）
@retry_with_backoff(max_retries=3, backoff_factor=1.0)
@timeout_handler(seconds=15)
async def get_real_news_enhanced(count: int, country: str) -> List[str]:
    """获取真实新闻 - 增强版"""
    try:
        from newsapi import NewsApiClient
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)

        news_list = []

        print(f"[增强版] 尝试获取国家 {country} 的新闻...")

        # 策略1: 尝试获取用户指定国家的新闻
        if country == 'cn':
            # 对于中国，尝试关键词搜索中文内容
            print("[增强版] 使用中文关键词搜索...")
            response = newsapi.get_everything(
                q='科技 OR 财经 OR 国际',
                language='zh',
                page_size=min(count, 100)
            )
        else:
            # 对于其他国家，获取头条新闻
            print(f"[增强版] 获取 {country} 头条新闻...")
            response = newsapi.get_top_headlines(
                country=country,
                page_size=min(count, 100)
            )

        articles = response.get('articles', [])
        print(f"[增强版] 获取到 {len(articles)} 篇文章")

        # 如果没有结果，使用备用策略
        if len(articles) == 0:
            print("[增强版] 无结果，使用英文科技新闻作为备用")
            response = newsapi.get_top_headlines(
                category='technology',
                language='en',
                page_size=min(count, 100)
            )
            articles = response.get('articles', [])
            print(f"[增强版] 备用策略获取到 {len(articles)} 篇文章")

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

        print(f"[增强版] 成功处理 {len(news_list)} 条新闻")
        return news_list

    except Exception as e:
        print(f"[增强版] 获取新闻失败: {str(e)}")
        raise e

@retry_with_backoff(max_retries=3, backoff_factor=1.0)
@timeout_handler(seconds=10)
async def get_real_weather_enhanced(city: str, units: str, lang: str) -> Dict[str, Any]:
    """获取真实天气 - 增强版"""
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': units,
            'lang': lang
        }

        print(f"[增强版] 获取 {city} 的天气信息...")
        response = requests.get(url, params=params, timeout=8)
        response.raise_for_status()
        data = response.json()

        weather = {
            "city": data['name'],
            "temperature": data['main']['temp'],
            "description": data['weather'][0]['description'],
            "humidity": data['main']['humidity'],
            "wind_speed": data.get('wind', {}).get('speed', 0),
            "units": units
        }

        print(f"[增强版] 成功获取 {city} 天气: {weather['temperature']}°C")
        return weather

    except Exception as e:
        print(f"[增强版] 获取天气失败: {str(e)}")
        raise e

@retry_with_backoff(max_retries=3, backoff_factor=1.5)
@timeout_handler(seconds=30)
async def send_real_email_enhanced(to_email: str, subject: str, content: str) -> str:
    """发送真实邮件 - 增强版"""
    try:
        from brevo import ApiClient
        from brevo.api import TransactionalEmailsApi
        from brevo.models import SendSmtpEmail

        api_instance = TransactionalEmailsApi(ApiClient())
        api_instance.api_client.configuration.api_key['api-key'] = BREVO_API_KEY

        # 使用已验证的发送者邮箱
        sender = {"name": "YOLO-LLM 增强版系统", "email": "by2022jy@gmail.com"}
        to = [{"email": to_email}]

        send_smtp_email = SendSmtpEmail(
            sender=sender,
            to=to,
            subject=subject,
            html_content=f"<html><body>{content.replace(chr(10), '<br>')}</body></html>",
            text_content=content
        )

        print(f"[增强版] 发送邮件到: {to_email}")
        result = api_instance.send_transac_email(send_smtp_email)
        email_id = getattr(result, 'message_id', 'email_sent')

        print(f"[增强版] 邮件发送成功: {email_id} -> {to_email}")
        return email_id

    except Exception as e:
        print(f"[增强版] 发送邮件失败: {str(e)}")
        raise e

# 模拟数据函数
def get_mock_news(count: int) -> List[str]:
    """获取模拟新闻"""
    mock_news = [
        "1. GPT-5即将发布，AI能力再次突破 [增强版模拟]",
        "2. 量子计算机实现新里程碑 [增强版模拟]",
        "3. 新能源汽车市场持续增长 [增强版模拟]",
        "4. 全球气候变化会议达成新协议 [增强版模拟]",
        "5. 科技巨头推出新一代操作系统 [增强版模拟]"
    ]
    return mock_news[:count]

def get_mock_weather(city: str) -> Dict[str, Any]:
    """获取模拟天气"""
    return {
        "city": city,
        "temperature": 22,
        "description": "晴朗 [增强版模拟]",
        "humidity": 65,
        "wind_speed": 10,
        "units": "metric"
    }

if __name__ == "__main__":
    print("启动增强版MCP服务器...")
    print(f"NewsAPI配置: {'已配置' if NEWS_API_KEY else '未配置'}")
    print(f"WeatherAPI配置: {'已配置' if WEATHER_API_KEY else '未配置'}")
    print(f"邮件API配置: {'已配置' if BREVO_API_KEY else '未配置'}")
    print("特性: 错误处理 | 重试机制 | 缓存 | 性能监控")

    uvicorn.run(app, host="127.0.0.1", port=8083)  # 使用新端口避免冲突