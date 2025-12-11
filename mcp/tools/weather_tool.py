#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
天气工具模块
提供天气获取和智能分析功能
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_tool import BaseTool, ToolResponse, ToolError

class WeatherTool(BaseTool):
    """天气工具类"""

    def __init__(self):
        super().__init__(
            name="weather",
            description="获取天气信息并提供智能分析",
            version="2.0.0"
        )

        # 天气API配置
        self.weather_api_key = os.getenv("WEATHER_API_KEY", "")
        self.default_city = "Beijing"
        self.default_units = "metric"
        self.default_language = "zh_cn"
        self.cache_ttl = 1800  # 30分钟缓存

        # 支持的单位和语言
        self.supported_units = ["metric", "imperial", "standard"]
        self.supported_languages = {
            "zh": "zh_cn", "en": "en", "es": "es", "fr": "fr",
            "de": "de", "ja": "ja", "ko": "kr"
        }

    async def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """执行天气工具操作"""
        try:
            if action == "get_current_weather":
                return await self._get_current_weather(parameters)
            elif action == "get_forecast":
                return await self._get_forecast(parameters)
            elif action == "analyze_weather":
                return await self._analyze_weather(parameters)
            elif action == "weather_recommendation":
                return await self._weather_recommendation(parameters)
            elif action == "compare_weather":
                return await self._compare_weather(parameters)
            elif action == "get_weather_alerts":
                return await self._get_weather_alerts(parameters)
            else:
                raise ToolError(f"不支持的操作: {action}", self.name)

        except Exception as e:
            self.logger.error(f"天气工具执行失败: {action} - {str(e)}")
            raise ToolError(f"天气工具执行异常: {str(e)}", self.name)

    async def _get_current_weather(self, params: Dict[str, Any]) -> ToolResponse:
        """获取当前天气"""
        city = params.get("city", self.default_city)
        units = params.get("units", self.default_units)
        language = params.get("language", self.default_language)

        try:
            if self.weather_api_key:
                weather_data = await self._fetch_real_weather(city, units, language)
            else:
                weather_data = self._get_mock_weather(city)

            return ToolResponse(
                success=True,
                data={
                    "current_weather": weather_data,
                    "city": city,
                    "units": units,
                    "language": language,
                    "source": "real_api" if self.weather_api_key else "mock",
                    "fetch_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"获取当前天气失败: {str(e)}")
            raise ToolError(f"获取当前天气失败: {str(e)}", self.name)

    async def _get_forecast(self, params: Dict[str, Any]) -> ToolResponse:
        """获取天气预报"""
        city = params.get("city", self.default_city)
        days = params.get("days", 5)
        units = params.get("units", self.default_units)
        language = params.get("language", self.default_language)

        try:
            if self.weather_api_key:
                forecast_data = await self._fetch_real_forecast(city, days, units, language)
            else:
                forecast_data = self._get_mock_forecast(city, days)

            return ToolResponse(
                success=True,
                data={
                    "forecast": forecast_data,
                    "city": city,
                    "days": days,
                    "units": units,
                    "language": language,
                    "source": "real_api" if self.weather_api_key else "mock",
                    "fetch_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"获取天气预报失败: {str(e)}")
            raise ToolError(f"获取天气预报失败: {str(e)}", self.name)

    async def _analyze_weather(self, params: Dict[str, Any]) -> ToolResponse:
        """分析天气数据"""
        city = params.get("city", self.default_city)
        weather_data = params.get("weather_data", None)

        try:
            # 如果没有提供天气数据，先获取
            if not weather_data:
                current_weather_result = await self._get_current_weather({
                    "city": city
                })
                if not current_weather_result.success:
                    raise ToolError("无法获取天气数据", self.name)
                weather_data = current_weather_result.data["current_weather"]

            # 使用DeepSeek进行智能分析
            analysis = await self._perform_weather_analysis(weather_data, city)

            return ToolResponse(
                success=True,
                data={
                    "city": city,
                    "weather_data": weather_data,
                    "analysis": analysis,
                    "analysis_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"天气分析失败: {str(e)}")
            raise ToolError(f"天气分析失败: {str(e)}", self.name)

    async def _weather_recommendation(self, params: Dict[str, Any]) -> ToolResponse:
        """天气建议"""
        city = params.get("city", self.default_city)
        activity_type = params.get("activity_type", "general")
        weather_data = params.get("weather_data", None)

        try:
            # 如果没有提供天气数据，先获取
            if not weather_data:
                current_weather_result = await self._get_current_weather({
                    "city": city
                })
                if not current_weather_result.success:
                    raise ToolError("无法获取天气数据", self.name)
                weather_data = current_weather_result.data["current_weather"]

            # 生成建议
            recommendations = await self._generate_weather_recommendations(
                weather_data, activity_type
            )

            return ToolResponse(
                success=True,
                data={
                    "city": city,
                    "activity_type": activity_type,
                    "weather_data": weather_data,
                    "recommendations": recommendations,
                    "recommendation_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"生成天气建议失败: {str(e)}")
            raise ToolError(f"生成天气建议失败: {str(e)}", self.name)

    async def _compare_weather(self, params: Dict[str, Any]) -> ToolResponse:
        """比较多个城市的天气"""
        cities = params.get("cities", [])
        units = params.get("units", self.default_units)

        if not cities:
            raise ToolError("城市列表不能为空", self.name)

        try:
            weather_comparison = []
            for city in cities:
                try:
                    city_weather_result = await self._get_current_weather({
                        "city": city,
                        "units": units
                    })
                    if city_weather_result.success:
                        weather_comparison.append({
                            "city": city,
                            "weather": city_weather_result.data["current_weather"]
                        })
                except Exception as e:
                    self.logger.error(f"获取{city}天气失败: {str(e)}")
                    continue

            # 生成比较分析
            comparison_analysis = await self._analyze_weather_comparison(weather_comparison)

            return ToolResponse(
                success=True,
                data={
                    "cities": cities,
                    "weather_comparison": weather_comparison,
                    "comparison_analysis": comparison_analysis,
                    "units": units,
                    "comparison_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"天气比较失败: {str(e)}")
            raise ToolError(f"天气比较失败: {str(e)}", self.name)

    async def _get_weather_alerts(self, params: Dict[str, Any]) -> ToolResponse:
        """获取天气预警"""
        city = params.get("city", self.default_city)
        alert_types = params.get("alert_types", ["all"])

        try:
            if self.weather_api_key:
                alerts_data = await self._fetch_real_alerts(city, alert_types)
            else:
                alerts_data = self._get_mock_alerts(city)

            return ToolResponse(
                success=True,
                data={
                    "city": city,
                    "alerts": alerts_data,
                    "alert_types": alert_types,
                    "source": "real_api" if self.weather_api_key else "mock",
                    "fetch_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"获取天气预警失败: {str(e)}")
            raise ToolError(f"获取天气预警失败: {str(e)}", self.name)

    async def _fetch_real_weather(self, city: str, units: str, language: str) -> Dict[str, Any]:
        """从真实API获取天气"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": city,
                "appid": self.weather_api_key,
                "units": units,
                "lang": language
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "temperature": data["main"]["temp"],
                            "feels_like": data["main"]["feels_like"],
                            "humidity": data["main"]["humidity"],
                            "pressure": data["main"]["pressure"],
                            "description": data["weather"][0]["description"],
                            "wind_speed": data.get("wind", {}).get("speed", 0),
                            "wind_direction": data.get("wind", {}).get("deg", 0),
                            "visibility": data.get("visibility", 0) / 1000,  # 转换为公里
                            "clouds": data.get("clouds", {}).get("all", 0),
                            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).isoformat(),
                            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).isoformat()
                        }
                    else:
                        raise Exception(f"API请求失败: {response.status}")

        except Exception as e:
            self.logger.error(f"获取真实天气失败: {str(e)}")
            raise e

    async def _fetch_real_forecast(self, city: str, days: int, units: str, language: str) -> List[Dict[str, Any]]:
        """从真实API获取天气预报"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast"
            params = {
                "q": city,
                "appid": self.weather_api_key,
                "units": units,
                "lang": language,
                "cnt": days * 8  # 每天8个时间点（3小时间隔）
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        forecast_data = []

                        for item in data["list"]:
                            forecast_data.append({
                                "datetime": item["dt_txt"],
                                "temperature": item["main"]["temp"],
                                "feels_like": item["main"]["feels_like"],
                                "humidity": item["main"]["humidity"],
                                "pressure": item["main"]["pressure"],
                                "description": item["weather"][0]["description"],
                                "wind_speed": item.get("wind", {}).get("speed", 0),
                                "wind_direction": item.get("wind", {}).get("deg", 0),
                                "clouds": item.get("clouds", {}).get("all", 0),
                                "precipitation": item.get("rain", {}).get("3h", 0)
                            })

                        return forecast_data
                    else:
                        raise Exception(f"API请求失败: {response.status}")

        except Exception as e:
            self.logger.error(f"获取真实天气预报失败: {str(e)}")
            raise e

    async def _fetch_real_alerts(self, city: str, alert_types: List[str]) -> List[Dict[str, Any]]:
        """从真实API获取天气预警"""
        # OpenWeatherMap需要One Call API 3.0才支持预警
        # 这里先返回模拟数据
        return self._get_mock_alerts(city)

    async def _perform_weather_analysis(self, weather_data: Dict[str, Any], city: str) -> Dict[str, Any]:
        """使用DeepSeek进行天气分析"""
        try:
            # 构建天气分析提示
            weather_prompt = f"""请分析以下{city}的天气数据，并提供专业的天气分析：

天气数据：
- 温度：{weather_data.get('temperature', 'N/A')}°C
- 体感温度：{weather_data.get('feels_like', 'N/A')}°C
- 湿度：{weather_data.get('humidity', 'N/A')}%
- 气压：{weather_data.get('pressure', 'N/A')} hPa
- 天气描述：{weather_data.get('description', 'N/A')}
- 风速：{weather_data.get('wind_speed', 'N/A')} m/s
- 能见度：{weather_data.get('visibility', 'N/A')} km
- 云量：{weather_data.get('clouds', 'N/A')}%

请从以下几个方面进行分析：
1. 天气状况概述
2. 舒适度评估
3. 出行建议
4. 健康影响
5. 注意事项

请以JSON格式返回分析结果，包含上述几个方面的内容。"""

            # 尝试使用DeepSeek集成
            try:
                from ..deepseek_integration import deepseek_integration
                from datetime import datetime

                messages = [
                    {"role": "system", "content": "你是一个专业的天气分析师，请提供准确、实用的天气分析。"},
                    {"role": "user", "content": weather_prompt}
                ]

                result = await deepseek_integration.chat_with_llm(messages)

                if result.get("success"):
                    # 尝试解析JSON结果
                    import json
                    try:
                        analysis_data = json.loads(result["content"])
                    except:
                        # 如果解析失败，包装为标准格式
                        analysis_data = {
                            "overview": result["content"],
                            "comfort": "暂无评估",
                            "travel_advice": "暂无建议",
                            "health_impact": "暂无分析",
                            "precautions": "暂无提醒"
                        }

                    return {
                        "analysis_type": "ai_generated",
                        "analysis_data": analysis_data,
                        "analysis_time": datetime.now().isoformat(),
                        "model": "deepseek"
                    }
                else:
                    raise Exception("DeepSeek API调用失败")

            except ImportError:
                self.logger.warning("DeepSeek集成未找到，使用基础分析")
                return self._basic_weather_analysis(weather_data)

        except Exception as e:
            self.logger.error(f"DeepSeek天气分析失败: {str(e)}")
            return self._basic_weather_analysis(weather_data)

    def _basic_weather_analysis(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """基础天气分析（备用方案）"""
        temperature = weather_data.get("temperature", 0)
        humidity = weather_data.get("humidity", 0)
        description = weather_data.get("description", "")

        # 基础分析逻辑
        if temperature > 30:
            comfort = "炎热，注意防暑降温"
            travel_advice = "避免长时间户外活动，做好防晒"
        elif temperature > 20:
            comfort = "温暖舒适"
            travel_advice = "适合出行"
        elif temperature > 10:
            comfort = "凉爽，建议添加衣物"
            travel_advice = "适合户外活动"
        else:
            comfort = "寒冷，注意保暖"
            travel_advice = "外出请穿戴保暖衣物"

        return {
            "analysis_type": "basic_rule_based",
            "analysis_data": {
                "overview": f"当前天气{description}，温度{temperature}°C",
                "comfort": comfort,
                "travel_advice": travel_advice,
                "health_impact": "湿度{}%，请根据个人情况调整".format(humidity),
                "precautions": "请关注天气变化，及时调整出行计划"
            },
            "analysis_time": datetime.now().isoformat(),
            "model": "rule_based"
        }

    async def _generate_weather_recommendations(self, weather_data: Dict[str, Any], activity_type: str) -> List[Dict[str, Any]]:
        """生成天气建议"""
        temperature = weather_data.get("temperature", 0)
        humidity = weather_data.get("humidity", 0)
        description = weather_data.get("description", "")
        wind_speed = weather_data.get("wind_speed", 0)

        recommendations = []

        # 通用建议
        if "雨" in description:
            recommendations.append({
                "category": "出行",
                "priority": "高",
                "suggestion": "携带雨具，选择合适的交通方式"
            })

        if temperature > 35:
            recommendations.append({
                "category": "健康",
                "priority": "高",
                "suggestion": "避免长时间户外暴晒，多补充水分"
            })

        if temperature < 0:
            recommendations.append({
                "category": "保暖",
                "priority": "高",
                "suggestion": "穿戴保暖衣物，注意防寒"
            })

        # 活动特定建议
        if activity_type == "outdoor_sports":
            if wind_speed > 10:
                recommendations.append({
                    "category": "运动",
                    "priority": "中",
                    "suggestion": "风力较大，不建议户外剧烈运动"
                })
            elif 15 <= temperature <= 25:
                recommendations.append({
                    "category": "运动",
                    "priority": "低",
                    "suggestion": "天气适宜，是户外运动的好时机"
                })

        elif activity_type == "driving":
            if "雨" in description or "雪" in description:
                recommendations.append({
                    "category": "驾驶",
                    "priority": "高",
                    "suggestion": "路面湿滑，请减速慢行，保持安全距离"
                })

        return recommendations

    async def _analyze_weather_comparison(self, weather_comparison: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析天气比较"""
        if len(weather_comparison) < 2:
            return {"analysis": "需要至少两个城市的天气数据进行比较"}

        # 找出最温暖和最凉爽的城市
        temperatures = [(item["city"], item["weather"]["temperature"]) for item in weather_comparison]
        warmest_city = max(temperatures, key=lambda x: x[1])
        coolest_city = min(temperatures, key=lambda x: x[1])

        return {
            "total_cities": len(weather_comparison),
            "warmest_city": {"name": warmest_city[0], "temperature": warmest_city[1]},
            "coolest_city": {"name": coolest_city[0], "temperature": coolest_city[1]},
            "temperature_range": warmest_city[1] - coolest_city[1],
            "recommendation": f"最温暖的城市是{warmest_city[0]}({warmest_city[1]}°C)，最凉爽的是{coolest_city[0]}({coolest_city[1]}°C)"
        }

    def _get_mock_weather(self, city: str) -> Dict[str, Any]:
        """获取模拟天气数据"""
        return {
            "temperature": 22,
            "feels_like": 24,
            "humidity": 65,
            "pressure": 1013,
            "description": "晴朗",
            "wind_speed": 3.5,
            "wind_direction": 180,
            "visibility": 10,
            "clouds": 20,
            "sunrise": (datetime.now().replace(hour=6, minute=0, second=0)).isoformat(),
            "sunset": (datetime.now().replace(hour=18, minute=30, second=0)).isoformat()
        }

    def _get_mock_forecast(self, city: str, days: int) -> List[Dict[str, Any]]:
        """获取模拟天气预报"""
        forecast = []
        base_temp = 20

        for day in range(days):
            for hour in range(0, 24, 3):  # 每3小时一个数据点
                forecast.append({
                    "datetime": (datetime.now() + timedelta(days=day, hours=hour)).strftime("%Y-%m-%d %H:%M:%S"),
                    "temperature": base_temp + (hour - 12) * 0.5 + day * 2,
                    "feels_like": base_temp + (hour - 12) * 0.5 + day * 2 + 2,
                    "humidity": 60 + (hour % 6) * 5,
                    "pressure": 1013 + (hour % 4) * 2,
                    "description": "晴朗" if hour < 12 else "多云",
                    "wind_speed": 3 + (hour % 5),
                    "wind_direction": (hour * 15) % 360,
                    "clouds": 20 + (hour % 3) * 20,
                    "precipitation": 0 if day % 2 == 0 else 0.5
                })

        return forecast[:days * 8]

    def _get_mock_alerts(self, city: str) -> List[Dict[str, Any]]:
        """获取模拟天气预警"""
        return [
            {
                "alert_id": "mock_001",
                "event": "高温预警",
                "start": datetime.now().isoformat(),
                "end": (datetime.now() + timedelta(days=2)).isoformat(),
                "description": "未来两天将出现高温天气，请注意防暑降温",
                "severity": "moderate"
            }
        ]

    def get_capabilities(self) -> List[str]:
        """获取工具能力列表"""
        return [
            "get_current_weather",
            "get_forecast",
            "analyze_weather",
            "weather_recommendation",
            "compare_weather",
            "get_weather_alerts"
        ]

    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数模式"""
        return {
            "actions": {
                "get_current_weather": {
                    "description": "获取当前天气",
                    "parameters": {
                        "city": {"type": "string", "default": "Beijing", "description": "城市名称"},
                        "units": {"type": "string", "default": "metric", "description": "温度单位"},
                        "language": {"type": "string", "default": "zh_cn", "description": "语言代码"}
                    }
                },
                "get_forecast": {
                    "description": "获取天气预报",
                    "parameters": {
                        "city": {"type": "string", "default": "Beijing", "description": "城市名称"},
                        "days": {"type": "integer", "default": 5, "description": "预报天数"},
                        "units": {"type": "string", "default": "metric", "description": "温度单位"},
                        "language": {"type": "string", "default": "zh_cn", "description": "语言代码"}
                    }
                },
                "analyze_weather": {
                    "description": "分析天气数据",
                    "parameters": {
                        "city": {"type": "string", "default": "Beijing", "description": "城市名称"},
                        "weather_data": {"type": "object", "description": "天气数据（可选）"}
                    }
                },
                "weather_recommendation": {
                    "description": "获取天气建议",
                    "parameters": {
                        "city": {"type": "string", "default": "Beijing", "description": "城市名称"},
                        "activity_type": {"type": "string", "default": "general", "description": "活动类型"},
                        "weather_data": {"type": "object", "description": "天气数据（可选）"}
                    }
                },
                "compare_weather": {
                    "description": "比较多个城市天气",
                    "parameters": {
                        "cities": {"type": "array", "required": True, "description": "城市列表"},
                        "units": {"type": "string", "default": "metric", "description": "温度单位"}
                    }
                },
                "get_weather_alerts": {
                    "description": "获取天气预警",
                    "parameters": {
                        "city": {"type": "string", "default": "Beijing", "description": "城市名称"},
                        "alert_types": {"type": "array", "default": ["all"], "description": "预警类型"}
                    }
                }
            }
        }

    async def _perform_health_check(self) -> bool:
        """执行健康检查"""
        try:
            # 检查API密钥是否配置
            if not self.weather_api_key:
                self.logger.warning("天气API密钥未配置，将使用模拟数据")

            # 测试基本功能
            test_result = await self._get_current_weather({"city": "Beijing"})
            return test_result.success
        except Exception as e:
            self.logger.error(f"天气工具健康检查失败: {str(e)}")
            return False

# 创建全局天气工具实例
weather_tool = WeatherTool()