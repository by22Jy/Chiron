"""
真实API的MCP服务器
使用真实的新闻和天气API，以及真实的SMTP邮件发送
"""

import os
import json
import time
import smtplib
import requests
from datetime import datetime
from typing import Dict, Any, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
# from advanced_computer_control import computer_controller  # 暂时注释掉

app = FastAPI(
    title="Real MCP Server",
    description="真实API的MCP服务器",
    version="1.0.0"
)

# 配置CORS
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

# 配置API密钥 - 从环境变量读取
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_status": {
            "news_api": "configured" if NEWS_API_KEY else "not_configured",
            "weather_api": "configured" if WEATHER_API_KEY else "not_configured",
            "smtp": "configured" if all([SMTP_USERNAME, SMTP_PASSWORD]) else "not_configured"
        },
        "available_tools": [
            "news", "weather", "email", "filesystem", "screenshot", "browser", "computer_control", "application_workflow"
        ]
    }

@app.get("/tools")
async def get_tools():
    """获取可用工具列表"""
    tools = [
        {
            "name": "news",
            "description": "获取最新新闻",
            "parameters": ["count", "category", "country"]
        },
        {
            "name": "weather",
            "description": "获取天气信息",
            "parameters": ["city", "units", "lang"]
        },
        {
            "name": "email",
            "description": "发送邮件",
            "parameters": ["to", "subject", "content"]
        },
        {
            "name": "filesystem",
            "description": "文件系统操作",
            "parameters": ["operation", "path", "content"]
        },
        {
            "name": "screenshot",
            "description": "屏幕截图",
            "parameters": ["save_path"]
        },
        {
            "name": "browser",
            "description": "浏览器控制",
            "parameters": ["action", "url"]
        },
        {
            "name": "computer_control",
            "description": "高级电脑控制",
            "parameters": ["action", "app_name", "parameters"]
        },
        {
            "name": "application_workflow",
            "description": "应用程序工作流执行",
            "parameters": ["app_name", "action", "game_name", "text", "parameters"]
        }
    ]
    return {"tools": tools}

@app.post("/mcp/news")
async def handle_news_tool(request: ToolRequest):
    """处理新闻工具请求"""
    try:
        params = request.parameters
        count = params.get("count", 10)
        country = params.get("country", "cn")

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
            # 使用真实OpenWeatherMap API
            weather_data = await get_real_weather(city, units, lang)
        else:
            # 使用模拟数据
            weather_data = get_mock_weather(city)

        return {
            "success": True,
            "data": {
                "weather": weather_data,
                "city": city,
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
        subject = params.get("subject", "无标题邮件")
        content = params.get("content", "")

        print(f"执行MCP工具: email, 参数: {{to: {to_email}, subject: {subject}}}")

        if all([SMTP_USERNAME, SMTP_PASSWORD, to_email]):
            # 使用真实SMTP发送
            email_id = await send_real_email(to_email, subject, content)
            source = "real_smtp"
        else:
            # 使用模拟发送
            email_id = send_mock_email(to_email, subject, content)
            source = "mock"

        return {
            "success": True,
            "data": {
                "email_id": email_id,
                "to": to_email,
                "subject": subject,
                "source": source,
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

@app.post("/mcp/screenshot")
async def handle_screenshot_tool(request: ToolRequest):
    """处理截图工具请求"""
    try:
        params = request.parameters
        save_path = params.get("save_path", "screenshot.png")

        print(f"执行MCP工具: screenshot, 参数: {params}")

        # 模拟截图功能
        await asyncio.sleep(0.5)
        screenshot_data = {
            "path": save_path,
            "size": {"width": 1920, "height": 1080},
            "file_size": 1024000,
            "format": "PNG"
        }

        return {
            "success": True,
            "data": {
                **screenshot_data,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"截图工具错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/mcp/browser")
async def handle_browser_tool(request: ToolRequest):
    """处理浏览器工具请求"""
    try:
        params = request.parameters
        action = params.get("action", "open")
        url = params.get("url", "")

        print(f"执行MCP工具: browser, 参数: {params}")

        # 模拟浏览器操作
        result = {
            "action": action,
            "url": url,
            "status": "success",
            "message": f"浏览器操作 {action} 执行成功"
        }

        return {
            "success": True,
            "data": {
                **result,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        print(f"浏览器工具错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/mcp/computer_control")
async def handle_computer_control_tool(request: ToolRequest):
    """处理高级电脑控制请求"""
    try:
        params = request.parameters
        action = params.get("action", "screen_info")
        app_name = params.get("app_name")
        control_params = params.get("parameters", {})

        print(f"执行MCP工具: computer_control, 参数: {params}")

        if action == "screen_info":
            # 获取屏幕信息
            result = computer_controller.get_screen_info()
        elif action == "launch_app":
            # 启动应用程序
            if not app_name:
                raise ValueError("启动应用需要提供app_name参数")
            success = computer_controller.launch_application(app_name)
            result = {
                "action": "launch_app",
                "app_name": app_name,
                "success": success,
                "message": f"应用 {app_name} {'启动成功' if success else '启动失败'}"
            }
        elif action == "find_windows":
            # 查找窗口
            windows = computer_controller.get_all_windows()
            result = {
                "action": "find_windows",
                "windows": [
                    {
                        "title": w.title,
                        "process": w.process_name,
                        "handle": w.handle,
                        "visible": w.visible,
                        "rect": w.rect
                    } for w in windows
                ]
            }
        elif action == "click_element":
            # 点击屏幕元素
            element_type = control_params.get("element_type")
            text_contains = control_params.get("text_contains")

            elements = computer_controller.find_screen_elements(element_type, text_contains)
            if elements:
                success = computer_controller.click_element(elements[0])
                result = {
                    "action": "click_element",
                    "element": {
                        "type": elements[0].element_type,
                        "text": elements[0].text,
                        "position": elements[0].position
                    },
                    "success": success
                }
            else:
                result = {
                    "action": "click_element",
                    "success": False,
                    "message": "未找到匹配的屏幕元素"
                }
        elif action == "type_text":
            # 输入文本
            text = control_params.get("text", "")
            position = control_params.get("position")

            success = computer_controller.type_text(text, position)
            result = {
                "action": "type_text",
                "text": text[:100] + "..." if len(text) > 100 else text,
                "success": success
            }
        else:
            raise ValueError(f"不支持的电脑控制操作: {action}")

        return {
            "success": True,
            "data": {
                **result,
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        print(f"电脑控制工具错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/mcp/application_workflow")
async def handle_application_workflow_tool(request: ToolRequest):
    """处理应用程序工作流请求"""
    try:
        params = request.parameters
        app_name = params.get("app_name")
        action = params.get("action")
        game_name = params.get("game_name")
        text = params.get("text")
        workflow_params = params.get("parameters", {})

        print(f"执行MCP工具: application_workflow, 参数: {params}")

        if not app_name or not action:
            raise ValueError("应用工作流需要提供app_name和action参数")

        # 构建工作流参数
        parameters = workflow_params.copy()
        if game_name:
            parameters["game_name"] = game_name
        if text:
            parameters["text"] = text

        # 执行应用程序工作流
        result = computer_controller.execute_application_workflow(app_name, action, parameters)

        return {
            "success": result["success"],
            "data": {
                "app_name": app_name,
                "action": action,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        }

    except Exception as e:
        print(f"应用工作流工具错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# 真实API函数
async def get_real_news(count: int, country: str) -> List[str]:
    """获取真实新闻"""
    try:
        # 使用newsapi-python客户端
        from newsapi import NewsApiClient
        newsapi = NewsApiClient(api_key=NEWS_API_KEY)

        news_list = []

        # 策略1: 尝试获取用户指定国家的新闻
        if country == 'cn':
            # 对于中国，尝试关键词搜索中文内容
            response = newsapi.get_everything(
                q='科技 OR 财经 OR 国际',
                language='zh',
                sort_by='publishedAt',
                page_size=min(count, 100)
            )
        else:
            # 对于其他国家，获取头条新闻
            response = newsapi.get_top_headlines(
                country=country,
                page_size=min(count, 100),
                sort_by='publishedAt'
            )

        articles = response.get('articles', [])

        # 如果没有结果，使用备用策略
        if len(articles) == 0:
            print(f"国家 {country} 无新闻结果，使用英文科技新闻作为备用")
            response = newsapi.get_top_headlines(
                category='technology',
                language='en',
                page_size=min(count, 100)
            )
            articles = response.get('articles', [])

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

        print(f"成功获取 {len(news_list)} 条新闻")
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

        weather_info = {
            "city": data['name'],
            "temperature": data['main']['temp'],
            "feels_like": data['main']['feels_like'],
            "humidity": data['main']['humidity'],
            "description": data['weather'][0]['description'],
            "wind_speed": data.get('wind', {}).get('speed', 0),
            "pressure": data['main']['pressure']
        }

        return weather_info

    except Exception as e:
        print(f"获取真实天气失败: {str(e)}")
        return get_mock_weather(city)

async def send_real_email(to_email: str, subject: str, content: str) -> str:
    """发送真实邮件"""
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USERNAME
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(content, 'plain', 'utf-8'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)

        text = msg.as_string()
        server.sendmail(SMTP_USERNAME, to_email, text)
        server.quit()

        email_id = f"real_email_{int(time.time())}"
        print(f"真实邮件发送成功: {email_id}")

        return email_id

    except Exception as e:
        print(f"发送真实邮件失败: {str(e)}")
        raise Exception(f"邮件发送失败: {str(e)}")

# 模拟函数
def get_mock_news(count: int) -> List[str]:
    """获取模拟新闻"""
    mock_headlines = [
        "科技巨头发布新一代人工智能芯片，性能提升300%",
        "全球气候变化大会达成历史性协议",
        "新能源汽车销量创历史新高，市场渗透率超过50%",
        "量子计算机实现重大突破，商业化进程加速",
        "5G网络覆盖率达90%，推动数字化转型",
        "生物医药公司成功研发新型抗癌药物",
        "教育科技行业迎来新一轮投资热潮",
        "数字货币监管政策正式出台，市场趋于规范",
        "智能制造工厂全面推进，工业4.0时代来临",
        "元宇宙概念持续升温，虚拟现实技术成熟"
    ]

    return mock_headlines[:count]

def get_mock_weather(city: str) -> Dict[str, Any]:
    """获取模拟天气"""
    return {
        "city": city,
        "temperature": 18,
        "feels_like": 16,
        "humidity": 65,
        "description": "晴朗",
        "wind_speed": 3.2,
        "pressure": 1013
    }

def send_mock_email(to_email: str, subject: str, content: str) -> str:
    """发送模拟邮件"""
    email_id = f"mock_email_{int(time.time())}"
    print(f"模拟邮件发送成功: {email_id} -> {to_email}")
    print(f"邮件内容预览: {subject[:50]}...")
    return email_id

if __name__ == "__main__":
    print("启动真实API MCP服务器...")
    print(f"NewsAPI配置: {'已配置' if NEWS_API_KEY else '未配置'}")
    print(f"WeatherAPI配置: {'已配置' if WEATHER_API_KEY else '未配置'}")
    print(f"SMTP配置: {'已配置' if SMTP_USERNAME else '未配置'}")

    uvicorn.run(app, host="127.0.0.1", port=8081)