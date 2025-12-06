"""
天气 MCP 工具

通过DeepSeek大模型智能处理天气相关任务
"""

import asyncio
import requests
import json
import time
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from ..config import TOOLS_CONFIG

logger = logging.getLogger(__name__)


class WeatherTool:
    """天气工具"""

    def __init__(self):
        self.config = TOOLS_CONFIG["weather"]
        self.cache = {}
        self.cache_timeout = 1800  # 30分钟缓存

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行天气工具操作"""

        action = parameters.get("action", "")
        logger.info(f"执行天气工具操作: {action}")

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
            elif action == "create_weather_report":
                return await self._create_weather_report(parameters)
            else:
                return {
                    "success": False,
                    "error": f"未知的天气操作: {action}",
                    "available_actions": [
                        "get_current_weather", "get_forecast", "analyze_weather",
                        "weather_recommendation", "compare_weather", "create_weather_report"
                    ]
                }

        except Exception as e:
            logger.error(f"天气工具执行错误: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "action": action
            }

    async def _get_current_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取当前天气"""

        city = params.get("city", "Beijing")
        units = params.get("units", "metric")

        try:
            # 检查缓存
            cache_key = f"current_{city}_{units}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if time.time() - cached_data["timestamp"] < self.cache_timeout:
                    logger.info("使用缓存天气数据")
                    return cached_data["data"]

            # 尝试获取真实天气数据
            weather_data = await self._fetch_real_weather(city, units)

            if weather_data["success"]:
                # 缓存数据
                self.cache[cache_key] = {
                    "timestamp": time.time(),
                    "data": weather_data
                }
                return weather_data
            else:
                # 使用模拟天气数据
                mock_weather = await self._generate_mock_weather(city)
                return mock_weather

        except Exception as e:
            logger.error(f"获取天气失败: {str(e)}")
            return await self._generate_mock_weather(city)

    async def _get_forecast(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取天气预报"""

        city = params.get("city", "Beijing")
        days = params.get("days", 5)
        units = params.get("units", "metric")

        try:
            # 生成天气预报（使用模拟数据，实际可以调用天气API的预报接口）
            forecast_data = await self._generate_forecast_data(city, days, units)

            return {
                "success": True,
                "city": city,
                "forecast": forecast_data,
                "days": days,
                "units": units,
                "generated_time": time.strftime('%Y-%m-%d %H:%M:%S')
            }

        except Exception as e:
            logger.error(f"获取天气预报失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "city": city
            }

    async def _analyze_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """分析天气情况"""

        city = params.get("city", "Beijing")
        weather_data = params.get("weather_data")

        if not weather_data:
            # 先获取天气数据
            current_weather = await self._get_current_weather({"city": city})
            if not current_weather["success"]:
                return current_weather
            weather_data = current_weather["weather"]

        try:
            # 使用DeepSeek进行天气分析
            analysis = await self._perform_weather_analysis(weather_data, city)

            return {
                "success": True,
                "city": city,
                "analysis": analysis,
                "weather_data": weather_data
            }

        except Exception as e:
            logger.error(f"天气分析失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _weather_recommendation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """天气建议"""

        city = params.get("city", "Beijing")
        activity_type = params.get("activity_type", "general")

        try:
            # 获取当前天气
            current_weather = await self._get_current_weather({"city": city})
            if not current_weather["success"]:
                return current_weather

            weather_data = current_weather["weather"]

            # 基于天气和活动类型生成建议
            recommendations = await self._generate_recommendations(weather_data, activity_type)

            return {
                "success": True,
                "city": city,
                "activity_type": activity_type,
                "current_weather": weather_data,
                "recommendations": recommendations
            }

        except Exception as e:
            logger.error(f"生成天气建议失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _compare_weather(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """比较不同城市天气"""

        cities = params.get("cities", ["Beijing", "Shanghai"])
        metrics = params.get("metrics", ["temperature", "humidity", "condition"])

        try:
            comparison_data = []
            for city in cities:
                weather_data = await self._get_current_weather({"city": city})
                if weather_data["success"]:
                    comparison_data.append({
                        "city": city,
                        "weather": weather_data["weather"]
                    })

            # 生成比较分析
            comparison_analysis = await self._perform_weather_comparison(comparison_data, metrics)

            return {
                "success": True,
                "cities": cities,
                "metrics": metrics,
                "comparison_data": comparison_data,
                "analysis": comparison_analysis
            }

        except Exception as e:
            logger.error(f"天气比较失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _create_weather_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """创建天气报告"""

        cities = params.get("cities", ["Beijing"])
        report_type = params.get("report_type", "daily")
        include_forecast = params.get("include_forecast", True)

        try:
            report_data = {
                "title": f"{report_type.title()}天气报告",
                "generated_time": time.strftime('%Y-%m-%d %H:%M:%S'),
                "cities_weather": []
            }

            # 获取各城市天气
            for city in cities:
                current_weather = await self._get_current_weather({"city": city})
                if current_weather["success"]:
                    city_report = {
                        "city": city,
                        "current_weather": current_weather["weather"]
                    }

                    # 添加预报
                    if include_forecast:
                        forecast = await self._get_forecast({"city": city, "days": 3})
                        if forecast["success"]:
                            city_report["forecast"] = forecast["forecast"]

                    report_data["cities_weather"].append(city_report)

            # 生成报告摘要
            summary = await self._generate_weather_summary(report_data["cities_weather"])
            report_data["summary"] = summary

            return {
                "success": True,
                "report": report_data,
                "metadata": {
                    "report_type": report_type,
                    "cities_count": len(cities),
                    "include_forecast": include_forecast
                }
            }

        except Exception as e:
            logger.error(f"创建天气报告失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _fetch_real_weather(self, city: str, units: str) -> Dict[str, Any]:
        """获取真实天气数据"""

        api_key = self.config.get("api_key")
        if not api_key:
            return {"success": False, "error": "天气API密钥未配置"}

        try:
            # 构建请求参数
            params = {
                "q": city,
                "appid": api_key,
                "units": units,
                "lang": self.config.get("lang", "zh_cn")
            }

            # 发送请求
            response = requests.get(
                f"{self.config['base_url']}/weather",
                params=params,
                timeout=10
            )

            response.raise_for_status()
            data = response.json()

            # 解析天气数据
            weather_info = {
                "city": city,
                "date": time.strftime('%Y年%m月%d日'),
                "temperature": f"{round(data['main']['temp'])}°{'C' if units == 'metric' else 'F'}",
                "feels_like": f"{round(data['main']['feels_like'])}°{'C' if units == 'metric' else 'F'}",
                "condition": data['weather'][0]['description'].capitalize(),
                "humidity": f"{data['main']['humidity']}%",
                "pressure": f"{data['main']['pressure']} hPa",
                "wind_speed": f"{data['wind'].get('speed', 0)} m/s",
                "wind_direction": self._get_wind_direction(data['wind'].get('deg', 0)),
                "visibility": f"{data.get('visibility', 0) / 1000:.1f} km",
                "sunrise": time.strftime('%H:%M', time.localtime(data['sys']['sunrise'])),
                "sunset": time.strftime('%H:%M', time.localtime(data['sys']['sunset'])),
                "icon": data['weather'][0]['icon'],
                "coordinates": {
                    "lat": data['coord']['lat'],
                    "lon": data['coord']['lon']
                }
            }

            return {
                "success": True,
                "weather": weather_info,
                "source": "real_api"
            }

        except Exception as e:
            logger.error(f"获取真实天气失败: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _generate_mock_weather(self, city: str) -> Dict[str, Any]:
        """生成模拟天气数据"""

        # 模拟不同城市的天气
        city_weather_map = {
            "Beijing": {
                "temperature": "18°C",
                "condition": "晴朗",
                "humidity": "45%",
                "wind_speed": "3.2 m/s"
            },
            "Shanghai": {
                "temperature": "22°C",
                "condition": "多云",
                "humidity": "65%",
                "wind_speed": "2.8 m/s"
            },
            "Guangzhou": {
                "temperature": "28°C",
                "condition": "小雨",
                "humidity": "78%",
                "wind_speed": "1.5 m/s"
            },
            "Shenzhen": {
                "temperature": "26°C",
                "condition": "阴天",
                "humidity": "70%",
                "wind_speed": "2.1 m/s"
            }
        }

        default_weather = {
            "temperature": "20°C",
            "condition": "晴朗",
            "humidity": "50%",
            "wind_speed": "2.5 m/s"
        }

        weather_data = city_weather_map.get(city, default_weather)

        mock_weather = {
            "city": city,
            "date": time.strftime('%Y年%m月%d日'),
            "temperature": weather_data["temperature"],
            "feels_like": weather_data["temperature"],
            "condition": weather_data["condition"],
            "humidity": weather_data["humidity"],
            "pressure": "1013 hPa",
            "wind_speed": weather_data["wind_speed"],
            "wind_direction": "东南风",
            "visibility": "10 km",
            "sunrise": "06:30",
            "sunset": "18:45",
            "icon": "01d",
            "coordinates": {
                "lat": 39.9042,
                "lon": 116.4074
            }
        }

        return {
            "success": True,
            "weather": mock_weather,
            "source": "mock_data"
        }

    async def _generate_forecast_data(self, city: str, days: int, units: str) -> List[Dict[str, Any]]:
        """生成预报数据"""

        forecast = []
        base_temp = 20 if city == "Beijing" else 25

        conditions = ["晴", "多云", "阴", "小雨", "晴转多云", "多云转晴"]

        for i in range(days):
            forecast_date = datetime.now() + timedelta(days=i+1)
            temp_variation = (i % 3) * 2 - 2  # -2, 0, 2 的变化

            day_forecast = {
                "date": forecast_date.strftime('%Y-%m-%d'),
                "day_of_week": forecast_date.strftime('%A'),
                "temperature_max": f"{base_temp + temp_variation + 5}°{'C' if units == 'metric' else 'F'}",
                "temperature_min": f"{base_temp + temp_variation - 2}°{'C' if units == 'metric' else 'F'}",
                "condition": conditions[i % len(conditions)],
                "humidity": f"{50 + (i % 3) * 10}%",
                "wind_speed": f"{2 + (i % 2) * 1} m/s",
                "precipitation": f"{i % 4 * 10}%",
                "icon": f"{(i % 4) + 1:02d}d"
            }
            forecast.append(day_forecast)

        return forecast

    async def _perform_weather_analysis(self, weather_data: Dict[str, Any], city: str) -> Dict[str, Any]:
        """执行天气分析"""

        temperature = weather_data.get("temperature", "")
        condition = weather_data.get("condition", "")
        humidity = weather_data.get("humidity", "")

        # 智能分析
        analysis = {
            "overall_rating": "舒适",
            "comfort_score": 85,
            "activity_suitability": [],
            "clothing_suggestions": [],
            "health_advice": [],
            "special_notes": []
        }

        # 温度分析
        temp_num = 18  # 默认温度
        try:
            temp_num = int(temperature.replace("°C", "").replace("°F", ""))
        except:
            pass

        if temp_num < 10:
            analysis["overall_rating"] = "寒冷"
            analysis["comfort_score"] = 30
            analysis["clothing_suggestions"] = ["厚外套", "围巾", "手套"]
            analysis["health_advice"] = ["注意保暖", "避免长时间户外活动"]
        elif temp_num < 20:
            analysis["overall_rating"] = "凉爽"
            analysis["comfort_score"] = 70
            analysis["clothing_suggestions"] = ["薄外套", "长袖"]
            analysis["activity_suitability"] = ["适合户外活动", "适合运动"]
        elif temp_num < 30:
            analysis["overall_rating"] = "舒适"
            analysis["comfort_score"] = 90
            analysis["clothing_suggestions"] = ["轻便衣物", "短袖"]
            analysis["activity_suitability"] = ["各种户外活动", "运动健身"]
        else:
            analysis["overall_rating"] = "炎热"
            analysis["comfort_score"] = 60
            analysis["clothing_suggestions"] = ["轻薄衣物", "防晒用品"]
            analysis["health_advice"] = ["注意防晒", "多补充水分"]
            analysis["activity_suitability"] = ["室内活动", "水上活动"]

        # 天气条件分析
        if "雨" in condition:
            analysis["special_notes"].append("有降雨，建议携带雨具")
            analysis["clothing_suggestions"].append("防水外套")

        if "晴" in condition:
            analysis["special_notes"].append("天气晴朗，紫外线较强")
            analysis["clothing_suggestions"].append("太阳镜", "防晒霜")

        return analysis

    async def _generate_recommendations(self, weather_data: Dict[str, Any], activity_type: str) -> List[str]:
        """生成天气建议"""

        recommendations = []
        condition = weather_data.get("condition", "")
        temperature = weather_data.get("temperature", "")

        # 基于活动类型的建议
        if activity_type == "outdoor":
            if "雨" in condition:
                recommendations.append("天气有雨，建议改期或选择室内活动")
                recommendations.append("如需户外活动，请携带雨具")
            else:
                recommendations.append("天气适合户外活动")
                recommendations.append("建议准备防晒用品")

        elif activity_type == "exercise":
            if int(temperature.replace("°C", "")) > 30:
                recommendations.append("温度较高，建议早晨或傍晚运动")
                recommendations.append("运动时注意补充水分")
            elif int(temperature.replace("°C", "")) < 10:
                recommendations.append("温度较低，建议选择室内运动")
                recommendations.append("户外运动需充分热身")
            else:
                recommendations.append("温度适宜，适合各种运动")

        elif activity_type == "travel":
            if "雨" in condition:
                recommendations.append("有降雨，影响出行计划")
                recommendations.append("建议携带雨具和防水装备")
            else:
                recommendations.append("天气良好，适合出行")
                recommendations.append("建议关注目的地天气变化")

        else:
            # 通用建议
            recommendations.append("根据天气情况适当增减衣物")
            if "晴" in condition:
                recommendations.append("注意防晒")

        return recommendations

    async def _perform_weather_comparison(self, comparison_data: List[Dict[str, Any]], metrics: List[str]) -> Dict[str, Any]:
        """执行天气比较"""

        if len(comparison_data) < 2:
            return {"error": "需要至少两个城市的数据进行比较"}

        comparison_results = {
            "cities": [data["city"] for data in comparison_data],
            "metrics_comparison": {},
            "rankings": {},
            "summary": ""
        }

        # 比较各项指标
        for metric in metrics:
            metric_data = []
            for city_data in comparison_data:
                weather = city_data["weather"]
                if metric == "temperature":
                    temp = weather.get("temperature", "0°C").replace("°C", "")
                    metric_data.append((city_data["city"], float(temp)))
                elif metric == "humidity":
                    humidity = weather.get("humidity", "0%").replace("%", "")
                    metric_data.append((city_data["city"], float(humidity)))
                else:
                    metric_data.append((city_data["city"], 0))

            # 排序
            metric_data.sort(key=lambda x: x[1], reverse=(metric in ["temperature", "humidity"]))
            comparison_results["metrics_comparison"][metric] = metric_data

        return comparison_results

    async def _generate_weather_summary(self, cities_weather: List[Dict[str, Any]]) -> Dict[str, Any]:
        """生成天气摘要"""

        total_cities = len(cities_weather)
        conditions_count = {}
        avg_temperature = 0

        for city_data in cities_weather:
            weather = city_data["current_weather"]
            condition = weather.get("condition", "")
            temp_str = weather.get("temperature", "18°C").replace("°C", "")

            # 统计天气条件
            conditions_count[condition] = conditions_count.get(condition, 0) + 1

            # 计算平均温度
            try:
                avg_temperature += float(temp_str)
            except:
                avg_temperature += 18

        avg_temperature /= total_cities

        summary = {
            "total_cities": total_cities,
            "average_temperature": f"{round(avg_temperature)}°C",
            "most_common_condition": max(conditions_count.items(), key=lambda x: x[1])[0] if conditions_count else "未知",
            "conditions_distribution": conditions_count,
            "overall_assessment": "天气状况良好" if avg_temperature >= 15 and avg_temperature <= 25 else "天气需要关注"
        }

        return summary

    def _get_wind_direction(self, degrees: int) -> str:
        """获取风向描述"""
        directions = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
        index = round(degrees / 45) % 8
        return f"{directions[index]}风"