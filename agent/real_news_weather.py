"""
真实的新闻和天气API服务

使用真实的API获取新闻和天气信息
"""

import requests
import json
import time
import os
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass

# 设置API日志
logger = logging.getLogger(__name__)


@dataclass
class NewsConfig:
    """新闻API配置"""
    news_api_key: str = ""  # NewsAPI.org的API密钥
    news_source: str = "google-news-cn"  # 中文新闻源
    max_articles: int = 10
    country: str = "cn"  # 国家代码


@dataclass
class WeatherConfig:
    """天气API配置"""
    weather_api_key: str = ""  # OpenWeatherMap的API密钥
    city: str = "Beijing"  # 默认城市
    units: str = "metric"  # 单位制
    lang: str = "zh_cn"  # 语言


class RealNewsService:
    """真实新闻服务"""

    def __init__(self, config: NewsConfig = None):
        self.config = config or NewsConfig()
        self.base_url = "https://newsapi.org/v2"
        self.last_fetch_time = 0
        self.cache_timeout = 3600  # 缓存1小时
        self.cached_news = []

    def fetch_top_headlines(self, count: int = 10) -> List[str]:
        """获取头条新闻"""
        try:
            # 检查缓存
            current_time = time.time()
            if (current_time - self.last_fetch_time < self.cache_timeout and
                self.cached_news):
                logger.info("使用缓存新闻数据")
                return self.cached_news[:count]

            if not self.config.news_api_key:
                logger.warning("新闻API密钥未配置，使用模拟数据")
                return self._get_mock_news(count)

            # 构建请求参数
            params = {
                'apiKey': self.config.news_api_key,
                'country': self.config.country,
                'pageSize': min(count, 100),  # NewsAPI限制
                'sortBy': 'publishedAt',
                'language': 'zh'
            }

            # 如果指定了新闻源，使用新闻源而不是国家
            if self.config.news_source:
                params['sources'] = self.config.news_source
                del params['country']

            logger.info(f"正在获取新闻，参数: {params}")

            # 发送请求
            response = requests.get(
                f"{self.base_url}/top-headlines",
                params=params,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            # 解析新闻数据
            articles = data.get('articles', [])
            news_list = []

            for i, article in enumerate(articles[:count], 1):
                title = article.get('title', '').strip()
                description = article.get('description', '').strip()
                source = article.get('source', {}).get('name', '未知来源')
                published_at = article.get('publishedAt', '')

                # 格式化新闻条目
                news_item = f"{i}. {title}"
                if description and description != title:
                    news_item += f" - {description}"

                news_item += f" ({source})"
                news_list.append(news_item)

            # 更新缓存
            self.cached_news = news_list
            self.last_fetch_time = current_time

            logger.info(f"成功获取 {len(news_list)} 条新闻")
            return news_list

        except requests.exceptions.RequestException as e:
            logger.error(f"新闻API请求失败: {str(e)}")
            return self._get_mock_news(count)
        except Exception as e:
            logger.error(f"获取新闻失败: {str(e)}")
            return self._get_mock_news(count)

    def _get_mock_news(self, count: int) -> List[str]:
        """获取模拟新闻（当API失败时使用）"""
        mock_news = [
            "1. 全球AI技术突破：新型大模型发布，性能提升显著",
            "2. 科技股大涨：多家AI公司股价创新高，市场乐观",
            "3. 新能源汽车销量创新纪录：电动汽车普及加速",
            "4. 医疗领域重大发现：新基因疗法获批，前景广阔",
            "5. 航天事业：新一代火箭成功发射，载人任务即将启动",
            "6. 环境保护：碳中和目标进展顺利，绿色能源投资增加",
            "7. 教育改革：在线教育新政策发布，数字化转型加速",
            "8. 体育盛事：重要国际赛事即将开始，备受关注",
            "9. 经济数据：GDP增长超预期，经济复苏势头强劲",
            "10. 国际合作：多项重要协议签署，全球治理改善"
        ]
        return mock_news[:count]


class RealWeatherService:
    """真实天气服务"""

    def __init__(self, config: WeatherConfig = None):
        self.config = config or WeatherConfig()
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.last_fetch_time = 0
        self.cache_timeout = 1800  # 缓存30分钟
        self.cached_weather = {}

    def fetch_current_weather(self, city: str = None) -> Dict[str, Any]:
        """获取当前天气"""
        try:
            # 检查缓存
            current_time = time.time()
            target_city = city or self.config.city

            if (current_time - self.last_fetch_time < self.cache_timeout and
                self.cached_weather.get('city') == target_city):
                logger.info("使用缓存天气数据")
                return self.cached_weather

            if not self.config.weather_api_key:
                logger.warning("天气API密钥未配置，使用模拟数据")
                return self._get_mock_weather()

            # 构建请求参数
            params = {
                'q': target_city,
                'appid': self.config.weather_api_key,
                'units': self.config.units,
                'lang': self.config.lang
            }

            logger.info(f"正在获取天气，参数: {params}")

            # 发送请求
            response = requests.get(
                f"{self.base_url}/weather",
                params=params,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            # 解析天气数据
            weather_info = {
                'city': target_city,
                'date': time.strftime('%Y年%m月%d日'),
                'temperature': f"{round(data['main']['temp'])}°C",
                'condition': data['weather'][0]['description'].capitalize(),
                'humidity': f"{data['main']['humidity']}%",
                'wind': f"{data['wind'].get('speed', 0)} m/s",
                'pressure': f"{data['main']['pressure']} hPa",
                'visibility': f"{data.get('visibility', 0) / 1000:.1f} km",
                'sunrise': time.strftime('%H:%M', time.localtime(data['sys']['sunrise'])),
                'sunset': time.strftime('%H:%M', time.localtime(data['sys']['sunset'])),
                'feels_like': f"{round(data['main']['feels_like'])}°C"
            }

            # 更新缓存
            self.cached_weather = weather_info
            self.last_fetch_time = current_time

            logger.info(f"成功获取 {target_city} 的天气信息")
            return weather_info

        except requests.exceptions.RequestException as e:
            logger.error(f"天气API请求失败: {str(e)}")
            return self._get_mock_weather()
        except Exception as e:
            logger.error(f"获取天气失败: {str(e)}")
            return self._get_mock_weather()

    def _get_mock_weather(self) -> Dict[str, Any]:
        """获取模拟天气（当API失败时使用）"""
        return {
            'city': self.config.city,
            'date': time.strftime('%Y年%m月%d日'),
            'temperature': '18°C',
            'condition': '晴朗',
            'humidity': '65%',
            'wind': '东南风 3级',
            'pressure': '1013 hPa',
            'visibility': '10 km',
            'sunrise': '06:30',
            'sunset': '18:45',
            'feels_like': '17°C',
            'air_quality': '优',
            'uv_index': '中等'
        }


class RealNewsWeatherService:
    """整合的新闻天气服务"""

    def __init__(self, news_config: NewsConfig = None, weather_config: WeatherConfig = None):
        self.news_service = RealNewsService(news_config)
        self.weather_service = RealWeatherService(weather_config)

    def get_top_news(self, count: int = 10) -> List[str]:
        """获取头条新闻"""
        return self.news_service.fetch_top_headlines(count)

    def get_weather_info(self, city: str = None) -> Dict[str, Any]:
        """获取天气信息"""
        return self.weather_service.fetch_current_weather(city)

    def get_combined_report(self, news_count: int = 10, weather_city: str = None) -> Dict[str, Any]:
        """获取综合报告"""
        news = self.get_top_news(news_count)
        weather = self.get_weather_info(weather_city)

        return {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'news': news,
            'weather': weather,
            'news_count': len(news),
            'weather_city': weather.get('city', '未知')
        }


def load_api_config():
    """从配置文件加载API密钥"""
    config_file = "api_config.json"

    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            logger.error(f"加载API配置失败: {str(e)}")

    # 返回默认空配置
    return {
        'news_api_key': '',
        'weather_api_key': '',
        'default_city': 'Beijing'
    }


def create_news_weather_service() -> RealNewsWeatherService:
    """创建新闻天气服务实例"""
    # 加载API配置
    api_config = load_api_config()

    # 创建配置
    news_config = NewsConfig(
        news_api_key=api_config.get('news_api_key', ''),
        max_articles=10,
        country='cn'
    )

    weather_config = WeatherConfig(
        weather_api_key=api_config.get('weather_api_key', ''),
        city=api_config.get('default_city', 'Beijing'),
        units='metric',
        lang='zh_cn'
    )

    return RealNewsWeatherService(news_config, weather_config)


if __name__ == '__main__':
    # 测试新闻天气服务
    print("🔍 测试真实新闻天气API服务...")
    print("="*50)

    # 创建服务实例
    service = create_news_weather_service()

    # 测试新闻
    print("\\n📰 测试新闻获取...")
    news_list = service.get_top_news(5)
    print(f"获取到 {len(news_list)} 条新闻:")
    for news in news_list:
        print(f"  {news}")

    # 测试天气
    print("\\n🌤️ 测试天气获取...")
    weather_info = service.get_weather_info()
    print(f"天气信息:")
    print(f"  城市: {weather_info.get('city', '未知')}")
    print(f"  温度: {weather_info.get('temperature', '未知')}")
    print(f"  天气: {weather_info.get('condition', '未知')}")
    print(f"  湿度: {weather_info.get('humidity', '未知')}")
    print(f"  风速: {weather_info.get('wind', '未知')}")

    # 测试综合报告
    print("\\n📊 测试综合报告...")
    report = service.get_combined_report()
    print(f"报告生成时间: {report['timestamp']}")
    print(f"新闻数量: {report['news_count']}")
    print(f"天气城市: {report['weather_city']}")

    print("\\n✅ 新闻天气API服务测试完成")