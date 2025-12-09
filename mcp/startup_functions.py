#!/usr/bin/env python3
# 真实API启动函数

import os
from newsapi import NewsApiClient
from sib_api_v3_sdk import Configuration, ApiClient

def initialize_real_apis():
    """初始化真实的API客户端"""
    global newsapi_client, weather_api_key, brevo_config
    
    print("初始化真实API客户端...")
    
    # 初始化NewsAPI
    try:
        news_api_key = os.getenv("NEWS_API_KEY")
        if news_api_key:
            newsapi_client = NewsApiClient(api_key=news_api_key)
            print("✅ NewsAPI初始化成功")
        else:
            print("❌ NewsAPI密钥未配置")
    except Exception as e:
        print(f"❌ NewsAPI初始化失败: {e}")
        newsapi_client = None
    
    # 初始化天气API密钥
    try:
        weather_api_key = os.getenv("WEATHER_API_KEY")
        if weather_api_key:
            print(f"✅ WeatherAPI密钥已配置: {weather_api_key[:8]}...")
        else:
            print("❌ WeatherAPI密钥未配置")
    except Exception as e:
        print(f"❌ WeatherAPI配置失败: {e}")
        weather_api_key = None
    
    # 初始化Brevo配置
    try:
        brevo_api_key = os.getenv("BREVO_API_KEY")
        if brevo_api_key:
            brevo_config = Configuration()
            brevo_config.api_key['api-key'] = brevo_api_key
            print(f"✅ Brevo API配置成功: {brevo_api_key[:8]}...")
        else:
            print("❌ Brevo API密钥未配置")
    except Exception as e:
        print(f"❌ Brevo API配置失败: {e}")
        brevo_config = None

def fetch_real_news(count=10, country='cn'):
    """使用真实NewsAPI获取新闻"""
    if not newsapi_client:
        return {"error": "NewsAPI未初始化"}
    
    try:
        response = newsapi_client.get_top_headlines(
            country=country,
            pageSize=count,
            language='zh'
        )
        
        if response['status'] == 'ok':
            articles = response['articles']
            news_list = []
            for article in articles[:count]:
                title = article.get('title', '').strip()
                description = article.get('description', '').strip()
                news_item = f"{title}"
                if description and description != title:
                    news_item += f" - {description[:100]}..."
                news_list.append(news_item)
            
            return {
                "success": True,
                "news": news_list,
                "count": len(news_list),
                "source": "NewsAPI.org - 真实数据"
            }
        else:
            return {"error": f"NewsAPI调用失败: {response.get('message')}"}
            
    except Exception as e:
        return {"error": f"获取新闻失败: {str(e)}"}

def fetch_real_weather(city="Beijing"):
    """使用真实天气API获取天气"""
    if not weather_api_key:
        return {"error": "WeatherAPI密钥未配置"}
    
    try:
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': weather_api_key,
            'units': 'metric',
            'lang': 'zh_cn'
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
        
        return {
            "success": True,
            "weather": weather_info,
            "source": "OpenWeatherMap - 真实数据"
        }
        
    except Exception as e:
        return {"error": f"获取天气失败: {str(e)}"}

def send_real_email(to_email, subject, content):
    """使用真实Brevo API发送邮件"""
    if not brevo_config:
        return {"error": "Brevo API未配置"}
    
    try:
        api_instance = TransactionalEmailsApi(ApiClient(brevo_config))
        
        smtp_email = SendSmtpEmail(
            sender={"name": "YOLO-LLM", "email": "noreply@yolo-llm.com"},
            to=[{"email": to_email}],
            subject=subject,
            html_content=f"<html><body>{content.replace(chr(10), '<br>')}</body></html>",
            text_content=content
        )
        
        response = api_instance.send_transac_email(smtp_email)
        
        return {
            "success": True,
            "message_id": response.message_id,
            "to_email": to_email,
            "subject": subject,
            "source": "Brevo API - 真实发送"
        }
        
    except Exception as e:
        return {"error": f"邮件发送失败: {str(e)}"}
