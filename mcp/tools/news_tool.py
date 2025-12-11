#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻工具模块
提供新闻获取和处理功能
"""

import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .base_tool import BaseTool, ToolResponse, ToolError

class NewsTool(BaseTool):
    """新闻工具类"""

    def __init__(self):
        super().__init__(
            name="news",
            description="获取最新新闻资讯，支持多种新闻源和语言",
            version="2.0.0"
        )

        # 新闻API配置
        self.news_api_key = os.getenv("NEWS_API_KEY", "")
        self.default_count = 10
        self.default_country = "us"
        self.cache_ttl = 600  # 10分钟缓存

        # 支持的国家和语言
        self.supported_countries = {
            "us": "en", "gb": "en", "ca": "en", "au": "en",
            "cn": "zh", "tw": "zh", "hk": "zh",
            "jp": "ja", "kr": "ko",
            "de": "de", "fr": "fr", "it": "it", "es": "es", "pt": "pt",
            "ru": "ru", "in": "hi"
        }

    async def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """执行新闻工具操作"""
        try:
            if action == "get_news":
                return await self._get_news(parameters)
            elif action == "search_news":
                return await self._search_news(parameters)
            elif action == "get_headlines":
                return await self._get_headlines(parameters)
            elif action == "get_sources":
                return await self._get_news_sources(parameters)
            else:
                raise ToolError(f"不支持的操作: {action}", self.name)

        except Exception as e:
            self.logger.error(f"新闻工具执行失败: {action} - {str(e)}")
            raise ToolError(f"新闻工具执行异常: {str(e)}", self.name)

    async def _get_news(self, params: Dict[str, Any]) -> ToolResponse:
        """获取新闻"""
        count = params.get("count", self.default_count)
        country = params.get("country", self.default_country)
        category = params.get("category", None)
        language = params.get("language", self.supported_countries.get(country, "en"))

        try:
            if self.news_api_key:
                news_data = await self._fetch_real_news(count, country, category, language)
            else:
                news_data = self._get_mock_news(count)

            return ToolResponse(
                success=True,
                data={
                    "articles": news_data,
                    "count": len(news_data),
                    "country": country,
                    "category": category,
                    "language": language,
                    "source": "real_api" if self.news_api_key else "mock",
                    "fetch_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"获取新闻失败: {str(e)}")
            raise ToolError(f"获取新闻失败: {str(e)}", self.name)

    async def _search_news(self, params: Dict[str, Any]) -> ToolResponse:
        """搜索新闻"""
        query = params.get("query", "")
        count = params.get("count", self.default_count)
        language = params.get("language", "en")
        sort_by = params.get("sort_by", "publishedAt")

        if not query:
            raise ToolError("搜索关键词不能为空", self.name)

        try:
            if self.news_api_key:
                news_data = await self._search_real_news(query, count, language, sort_by)
            else:
                news_data = self._search_mock_news(query, count)

            return ToolResponse(
                success=True,
                data={
                    "articles": news_data,
                    "count": len(news_data),
                    "query": query,
                    "language": language,
                    "sort_by": sort_by,
                    "source": "real_api" if self.news_api_key else "mock",
                    "fetch_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"搜索新闻失败: {str(e)}")
            raise ToolError(f"搜索新闻失败: {str(e)}", self.name)

    async def _get_headlines(self, params: Dict[str, Any]) -> ToolResponse:
        """获取头条新闻"""
        country = params.get("country", self.default_country)
        category = params.get("category", None)
        page_size = params.get("page_size", self.default_count)

        try:
            if self.news_api_key:
                headlines_data = await self._fetch_headlines(country, category, page_size)
            else:
                headlines_data = self._get_mock_headlines(page_size)

            return ToolResponse(
                success=True,
                data={
                    "headlines": headlines_data,
                    "count": len(headlines_data),
                    "country": country,
                    "category": category,
                    "source": "real_api" if self.news_api_key else "mock",
                    "fetch_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"获取头条新闻失败: {str(e)}")
            raise ToolError(f"获取头条新闻失败: {str(e)}", self.name)

    async def _get_news_sources(self, params: Dict[str, Any]) -> ToolResponse:
        """获取新闻源列表"""
        country = params.get("country", None)
        category = params.get("category", None)
        language = params.get("language", None)

        try:
            if self.news_api_key:
                sources_data = await self._fetch_sources(country, category, language)
            else:
                sources_data = self._get_mock_sources()

            return ToolResponse(
                success=True,
                data={
                    "sources": sources_data,
                    "count": len(sources_data),
                    "country": country,
                    "category": category,
                    "language": language,
                    "source": "real_api" if self.news_api_key else "mock",
                    "fetch_time": datetime.now().isoformat()
                }
            )

        except Exception as e:
            self.logger.error(f"获取新闻源失败: {str(e)}")
            raise ToolError(f"获取新闻源失败: {str(e)}", self.name)

    async def _fetch_real_news(self, count: int, country: str, category: str, language: str) -> List[Dict[str, Any]]:
        """从真实API获取新闻"""
        try:
            from newsapi import NewsApiClient
            newsapi = NewsApiClient(api_key=self.news_api_key)

            # 构建请求参数
            request_params = {
                "page_size": min(count, 100),  # API限制最多100条
                "language": language
            }

            # 根据请求类型选择API端点
            if category:
                request_params["category"] = category
                if country != "all":
                    request_params["country"] = country
                response = newsapi.get_top_headlines(**request_params)
            else:
                if country == "cn":
                    # 对于中国，使用关键词搜索
                    response = newsapi.get_everything(
                        q='科技 OR 财经 OR 国际',
                        language=language,
                        page_size=request_params["page_size"],
                        sort_by="publishedAt"
                    )
                else:
                    if country != "all":
                        request_params["country"] = country
                    response = newsapi.get_top_headlines(**request_params)

            if response["status"] == "ok":
                articles = []
                for article in response.get("articles", []):
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "content": article.get("content", ""),
                        "author": article.get("author", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "url": article.get("url", ""),
                        "image_url": article.get("urlToImage", ""),
                        "published_at": article.get("publishedAt", ""),
                        "category": category or "general"
                    })
                return articles[:count]
            else:
                raise Exception(f"API返回错误: {response.get('message', '未知错误')}")

        except ImportError:
            self.logger.warning("newsapi库未安装，使用模拟数据")
            return self._get_mock_news(count)
        except Exception as e:
            self.logger.error(f"获取真实新闻失败: {str(e)}")
            raise e

    async def _search_real_news(self, query: str, count: int, language: str, sort_by: str) -> List[Dict[str, Any]]:
        """从真实API搜索新闻"""
        try:
            from newsapi import NewsApiClient
            newsapi = NewsApiClient(api_key=self.news_api_key)

            response = newsapi.get_everything(
                q=query,
                language=language,
                sort_by=sort_by,
                page_size=min(count, 100)
            )

            if response["status"] == "ok":
                articles = []
                for article in response.get("articles", []):
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "content": article.get("content", ""),
                        "author": article.get("author", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "url": article.get("url", ""),
                        "image_url": article.get("urlToImage", ""),
                        "published_at": article.get("publishedAt", ""),
                        "relevance_score": self._calculate_relevance(query, article)
                    })
                return articles[:count]
            else:
                raise Exception(f"API返回错误: {response.get('message', '未知错误')}")

        except Exception as e:
            self.logger.error(f"搜索真实新闻失败: {str(e)}")
            raise e

    async def _fetch_headlines(self, country: str, category: str, page_size: int) -> List[Dict[str, Any]]:
        """获取头条新闻"""
        try:
            from newsapi import NewsApiClient
            newsapi = NewsApiClient(api_key=self.news_api_key)

            params = {"page_size": min(page_size, 100)}
            if country != "all":
                params["country"] = country
            if category:
                params["category"] = category

            response = newsapi.get_top_headlines(**params)

            if response["status"] == "ok":
                headlines = []
                for article in response.get("articles", []):
                    headlines.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "source": article.get("source", {}).get("name", ""),
                        "url": article.get("url", ""),
                        "image_url": article.get("urlToImage", ""),
                        "published_at": article.get("publishedAt", ""),
                        "is_headline": True,
                        "category": category or "general"
                    })
                return headlines
            else:
                raise Exception(f"API返回错误: {response.get('message', '未知错误')}")

        except Exception as e:
            self.logger.error(f"获取头条新闻失败: {str(e)}")
            raise e

    async def _fetch_sources(self, country: str, category: str, language: str) -> List[Dict[str, Any]]:
        """获取新闻源"""
        try:
            from newsapi import NewsApiClient
            newsapi = NewsApiClient(api_key=self.news_api_key)

            params = {}
            if country:
                params["country"] = country
            if category:
                params["category"] = category
            if language:
                params["language"] = language

            response = newsapi.get_sources(**params)

            if response["status"] == "ok":
                sources = []
                for source in response.get("sources", []):
                    sources.append({
                        "id": source.get("id", ""),
                        "name": source.get("name", ""),
                        "description": source.get("description", ""),
                        "url": source.get("url", ""),
                        "category": source.get("category", ""),
                        "language": source.get("language", ""),
                        "country": source.get("country", "")
                    })
                return sources
            else:
                raise Exception(f"API返回错误: {response.get('message', '未知错误')}")

        except Exception as e:
            self.logger.error(f"获取新闻源失败: {str(e)}")
            raise e

    def _get_mock_news(self, count: int) -> List[Dict[str, Any]]:
        """获取模拟新闻"""
        mock_articles = [
            {
                "title": "AI技术在医疗领域取得重大突破",
                "description": "最新研究显示，人工智能在疾病诊断方面准确率超过人类医生",
                "content": "研究人员开发的新型AI系统在多项医疗诊断任务中表现出色...",
                "author": "科技日报",
                "source": "科技新闻",
                "url": "https://example.com/news/1",
                "image_url": "https://example.com/images/news1.jpg",
                "published_at": (datetime.now() - timedelta(hours=2)).isoformat(),
                "category": "technology"
            },
            {
                "title": "全球气候变化会议达成重要协议",
                "description": "195个国家就减排目标达成共识，承诺到2030年减少碳排放",
                "content": "在为期两周的激烈谈判后，与会国家终于就关键议题达成一致...",
                "author": "环保新闻",
                "source": "环球时报",
                "url": "https://example.com/news/2",
                "image_url": "https://example.com/images/news2.jpg",
                "published_at": (datetime.now() - timedelta(hours=4)).isoformat(),
                "category": "environment"
            },
            {
                "title": "新能源汽车销量创历史新高",
                "description": "电动汽车市场份额首次超过传统燃油车",
                "content": "最新数据显示，新能源汽车在全球汽车销量中的占比达到了51%...",
                "author": "汽车周刊",
                "source": "财经新闻",
                "url": "https://example.com/news/3",
                "image_url": "https://example.com/images/news3.jpg",
                "published_at": (datetime.now() - timedelta(hours=6)).isoformat(),
                "category": "business"
            }
        ]
        return mock_articles[:count]

    def _search_mock_news(self, query: str, count: int) -> List[Dict[str, Any]]:
        """模拟搜索新闻"""
        # 简单的关键词匹配
        mock_results = self._get_mock_news(count)
        query_lower = query.lower()

        filtered_results = []
        for article in mock_results:
            if any(word in article["title"].lower() or word in article["description"].lower()
                   for word in query_lower.split()):
                article_copy = article.copy()
                article_copy["relevance_score"] = 0.8  # 模拟相关性得分
                filtered_results.append(article_copy)

        return filtered_results[:count]

    def _get_mock_headlines(self, page_size: int) -> List[Dict[str, Any]]:
        """获取模拟头条"""
        headlines = self._get_mock_news(page_size)
        for headline in headlines:
            headline["is_headline"] = True
        return headlines

    def _get_mock_sources(self) -> List[Dict[str, Any]]:
        """获取模拟新闻源"""
        return [
            {
                "id": "tech-news",
                "name": "科技新闻",
                "description": "最新的科技资讯和创新报道",
                "url": "https://technews.example.com",
                "category": "technology",
                "language": "zh",
                "country": "cn"
            },
            {
                "id": "global-times",
                "name": "环球时报",
                "description": "国际新闻和时事分析",
                "url": "https://global.example.com",
                "category": "general",
                "language": "zh",
                "country": "cn"
            }
        ]

    def _calculate_relevance(self, query: str, article: Dict[str, Any]) -> float:
        """计算新闻与查询的相关性"""
        query_words = query.lower().split()
        title_words = article.get("title", "").lower().split()
        description_words = article.get("description", "").lower().split()

        title_matches = sum(1 for word in query_words if word in title_words)
        description_matches = sum(1 for word in query_words if word in description_words)

        total_words = len(query_words)
        if total_words == 0:
            return 0.0

        # 简单的相关性计算
        relevance = (title_matches * 2 + description_matches) / (total_words * 3)
        return min(relevance, 1.0)

    def get_capabilities(self) -> List[str]:
        """获取工具能力列表"""
        return [
            "get_news",
            "search_news",
            "get_headlines",
            "get_sources"
        ]

    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数模式"""
        return {
            "actions": {
                "get_news": {
                    "description": "获取最新新闻",
                    "parameters": {
                        "count": {"type": "integer", "default": 10, "description": "新闻数量"},
                        "country": {"type": "string", "default": "us", "description": "国家代码"},
                        "category": {"type": "string", "description": "新闻类别"},
                        "language": {"type": "string", "description": "语言代码"}
                    }
                },
                "search_news": {
                    "description": "搜索新闻",
                    "parameters": {
                        "query": {"type": "string", "required": True, "description": "搜索关键词"},
                        "count": {"type": "integer", "default": 10, "description": "结果数量"},
                        "language": {"type": "string", "default": "en", "description": "语言代码"},
                        "sort_by": {"type": "string", "default": "publishedAt", "description": "排序方式"}
                    }
                },
                "get_headlines": {
                    "description": "获取头条新闻",
                    "parameters": {
                        "country": {"type": "string", "default": "us", "description": "国家代码"},
                        "category": {"type": "string", "description": "新闻类别"},
                        "page_size": {"type": "integer", "default": 10, "description": "页面大小"}
                    }
                },
                "get_sources": {
                    "description": "获取新闻源列表",
                    "parameters": {
                        "country": {"type": "string", "description": "国家代码"},
                        "category": {"type": "string", "description": "新闻类别"},
                        "language": {"type": "string", "description": "语言代码"}
                    }
                }
            }
        }

    async def _perform_health_check(self) -> bool:
        """执行健康检查"""
        try:
            # 检查API密钥是否配置
            if not self.news_api_key:
                self.logger.warning("新闻API密钥未配置，将使用模拟数据")

            # 测试基本功能
            test_result = await self._get_news({"count": 1})
            return test_result.success
        except Exception as e:
            self.logger.error(f"新闻工具健康检查失败: {str(e)}")
            return False

# 创建全局新闻工具实例
news_tool = NewsTool()