"""
WebTool - 网络工具

提供网页操作、网络请求、内容获取等功能
支持浏览器控制和网络数据交互
"""

import requests
import webbrowser
import logging
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import json
import os
from bs4 import BeautifulSoup

try:
    from .base_tool import BaseTool, ToolResult
except ImportError:
    from base_tool import BaseTool, ToolResult


class WebTool(BaseTool):
    """网络工具"""

    def __init__(self):
        super().__init__()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    @property
    def name(self) -> str:
        return "web"

    @property
    def description(self) -> str:
        return "网络工具：网页操作、网络请求、内容获取、搜索引擎等"

    @property
    def supported_actions(self) -> List[str]:
        return [
            "open_url",
            "fetch_content",
            "search_web",
            "download_file",
            "get_page_title",
            "extract_links",
            "extract_images",
            "submit_form",
            "api_request",
            "check_url_status"
        ]

    @property
    def required_permissions(self) -> List[str]:
        return ["network_access", "browser_control"]

    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """验证参数有效性"""
        if action in ["open_url", "fetch_content", "get_page_title", "extract_links", "extract_images", "check_url_status"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["url"],
                optional_params=["timeout", "headers", "cookies"]
            )

        elif action in ["search_web"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["query"],
                optional_params=["engine", "num_results", "language"]
            )

        elif action in ["download_file"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["url", "save_path"],
                optional_params=["timeout", "chunk_size"]
            )

        elif action in ["submit_form"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["url", "form_data"],
                optional_params=["method", "headers"]
            )

        elif action in ["api_request"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["url"],
                optional_params=["method", "headers", "data", "params"]
            )

        else:
            self.logger.error(f"不支持的动作: {action}")
            return False

    def execute_action(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """执行具体动作"""
        try:
            if action == "open_url":
                return self._open_url(parameters, context)
            elif action == "fetch_content":
                return self._fetch_content(parameters, context)
            elif action == "search_web":
                return self._search_web(parameters, context)
            elif action == "download_file":
                return self._download_file(parameters, context)
            elif action == "get_page_title":
                return self._get_page_title(parameters, context)
            elif action == "extract_links":
                return self._extract_links(parameters, context)
            elif action == "extract_images":
                return self._extract_images(parameters, context)
            elif action == "submit_form":
                return self._submit_form(parameters, context)
            elif action == "api_request":
                return self._api_request(parameters, context)
            elif action == "check_url_status":
                return self._check_url_status(parameters, context)
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的网络动作: {action}"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"执行网络动作 {action} 失败: {str(e)}"
            )

    def _open_url(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """打开网页URL"""
        url = parameters["url"]
        timeout = parameters.get("timeout", 10)

        try:
            # 验证URL格式
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "https://" + url

            # 使用系统默认浏览器打开
            webbrowser.open(url)

            return ToolResult(
                success=True,
                message=f"网页已在浏览器中打开: {url}",
                data={
                    "url": url,
                    "browser_opened": True
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"打开网页失败: {str(e)}"
            )

    def _fetch_content(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """获取网页内容"""
        url = parameters["url"]
        timeout = parameters.get("timeout", 30)
        headers = parameters.get("headers", {})
        cookies = parameters.get("cookies", {})
        clean_html = parameters.get("clean_html", True)

        try:
            # 验证URL格式
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "https://" + url

            # 发送请求
            response = self.session.get(
                url,
                timeout=timeout,
                headers=headers,
                cookies=cookies
            )
            response.raise_for_status()

            # 获取内容
            content_type = response.headers.get('content-type', '').lower()

            if 'text/html' in content_type:
                if clean_html:
                    # 清理HTML，提取文本内容
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # 移除脚本和样式
                    for script in soup(["script", "style"]):
                        script.decompose()

                    content = soup.get_text()
                    content = '\n'.join(line.strip() for line in content.splitlines() if line.strip())
                else:
                    content = response.text

                # 提取基本信息
                soup = BeautifulSoup(response.content, 'html.parser')
                title = soup.title.string if soup.title else "无标题"

                return ToolResult(
                    success=True,
                    message=f"成功获取网页内容: {url}",
                    data={
                        "url": url,
                        "title": title,
                        "content_type": content_type,
                        "content_length": len(content),
                        "content": content[:5000] + "..." if len(content) > 5000 else content,
                        "full_content": content
                    }
                )
            else:
                # 非HTML内容
                return ToolResult(
                    success=True,
                    message=f"成功获取内容: {url}",
                    data={
                        "url": url,
                        "content_type": content_type,
                        "content_length": len(response.content),
                        "content": response.content[:1000] if len(response.content) < 1000 else response.content[:1000]
                    }
                )

        except requests.exceptions.RequestException as e:
            return ToolResult(
                success=False,
                message=f"获取网页内容失败: {str(e)}"
            )

    def _search_web(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """网络搜索"""
        query = parameters["query"]
        engine = parameters.get("engine", "duckduckgo")
        num_results = parameters.get("num_results", 10)
        language = parameters.get("language", "zh-cn")

        try:
            results = []

            if engine == "duckduckgo":
                results = self._search_duckduckgo(query, num_results)
            elif engine == "bing":
                results = self._search_bing(query, num_results, language)
            elif engine == "google":
                results = self._search_google(query, num_results, language)
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的搜索引擎: {engine}"
                )

            return ToolResult(
                success=True,
                message=f"使用 {engine} 搜索 '{query}' 找到 {len(results)} 个结果",
                data={
                    "query": query,
                    "engine": engine,
                    "num_results": len(results),
                    "results": results
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"网络搜索失败: {str(e)}"
            )

    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict[str, Any]]:
        """使用DuckDuckGo搜索"""
        try:
            # DuckDuckGo即时答案API
            url = "https://duckduckgo.com/html/"
            params = {
                "q": query,
                "kl": "cn-zh"
            }

            response = self.session.post(url, data=params, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            results = []

            # 解析搜索结果
            for result in soup.find_all('div', class_='result')[:num_results]:
                title_tag = result.find('a', class_='result__a')
                snippet_tag = result.find('a', class_='result__snippet')

                if title_tag and snippet_tag:
                    results.append({
                        "title": title_tag.get_text().strip(),
                        "url": title_tag.get('href', ''),
                        "snippet": snippet_tag.get_text().strip()
                    })

            return results

        except Exception as e:
            self.logger.error(f"DuckDuckGo搜索失败: {e}")
            return []

    def _search_bing(self, query: str, num_results: int, language: str) -> List[Dict[str, Any]]:
        """使用Bing搜索"""
        try:
            url = "https://www.bing.com/search"
            params = {
                "q": query,
                "setlang": language,
                "count": num_results
            }

            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            results = []

            # 解析搜索结果
            for result in soup.find_all('li', class_='b_algo')[:num_results]:
                title_tag = result.find('h2')
                link_tag = result.find('a')
                snippet_tag = result.find('div', class_='b_caption')

                if title_tag and link_tag:
                    results.append({
                        "title": title_tag.get_text().strip(),
                        "url": link_tag.get('href', ''),
                        "snippet": snippet_tag.get_text().strip() if snippet_tag else ""
                    })

            return results

        except Exception as e:
            self.logger.error(f"Bing搜索失败: {e}")
            return []

    def _search_google(self, query: str, num_results: int, language: str) -> List[Dict[str, Any]]:
        """使用Google搜索（注意：可能需要处理反爬虫）"""
        # 由于Google的反爬虫措施，这里提供一个基础的实现
        # 在实际使用中可能需要使用其他API或服务
        self.logger.warning("Google搜索可能受到反爬虫限制")
        return []

    def _download_file(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """下载文件"""
        url = parameters["url"]
        save_path = parameters["save_path"]
        timeout = parameters.get("timeout", 300)
        chunk_size = parameters.get("chunk_size", 8192)

        try:
            # 发送请求
            response = self.session.get(url, stream=True, timeout=timeout)
            response.raise_for_status()

            # 确保保存目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 下载文件
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

            return ToolResult(
                success=True,
                message=f"文件下载成功: {save_path}",
                data={
                    "url": url,
                    "save_path": save_path,
                    "total_size": total_size,
                    "downloaded_size": downloaded_size,
                    "content_type": response.headers.get('content-type', '')
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"文件下载失败: {str(e)}"
            )

    def _get_page_title(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """获取网页标题"""
        url = parameters["url"]
        timeout = parameters.get("timeout", 10)

        try:
            # 验证URL格式
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "https://" + url

            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.title.string if soup.title else "无标题"

            return ToolResult(
                success=True,
                message=f"获取页面标题成功",
                data={
                    "url": url,
                    "title": title.strip(),
                    "status_code": response.status_code
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"获取页面标题失败: {str(e)}"
            )

    def _extract_links(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """提取网页链接"""
        url = parameters["url"]
        timeout = parameters.get("timeout", 10)

        try:
            # 验证URL格式
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "https://" + url

            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            links = []

            # 提取所有链接
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text().strip()

                # 处理相对链接
                if href.startswith('/'):
                    href = urljoin(url, href)
                elif not href.startswith(('http://', 'https://')):
                    continue

                links.append({
                    "url": href,
                    "text": text,
                    "title": link.get('title', '')
                })

            return ToolResult(
                success=True,
                message=f"提取到 {len(links)} 个链接",
                data={
                    "url": url,
                    "links": links,
                    "count": len(links)
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"提取链接失败: {str(e)}"
            )

    def _extract_images(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """提取网页图片"""
        url = parameters["url"]
        timeout = parameters.get("timeout", 10)

        try:
            # 验证URL格式
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "https://" + url

            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            images = []

            # 提取所有图片
            for img in soup.find_all('img'):
                src = img.get('src', '')
                alt = img.get('alt', '')
                title = img.get('title', '')

                if not src:
                    continue

                # 处理相对链接
                if src.startswith('/'):
                    src = urljoin(url, src)
                elif not src.startswith(('http://', 'https://')):
                    # 可能是相对路径
                    src = urljoin(url, src)

                images.append({
                    "src": src,
                    "alt": alt,
                    "title": title,
                    "width": img.get('width', ''),
                    "height": img.get('height', '')
                })

            return ToolResult(
                success=True,
                message=f"提取到 {len(images)} 个图片",
                data={
                    "url": url,
                    "images": images,
                    "count": len(images)
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"提取图片失败: {str(e)}"
            )

    def _submit_form(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """提交表单"""
        url = parameters["url"]
        form_data = parameters["form_data"]
        method = parameters.get("method", "POST")
        headers = parameters.get("headers", {})
        timeout = parameters.get("timeout", 30)

        try:
            if method.upper() == "POST":
                response = self.session.post(
                    url,
                    data=form_data,
                    headers=headers,
                    timeout=timeout
                )
            else:
                response = self.session.get(
                    url,
                    params=form_data,
                    headers=headers,
                    timeout=timeout
                )

            response.raise_for_status()

            return ToolResult(
                success=True,
                message=f"表单提交成功: {method} {url}",
                data={
                    "url": url,
                    "method": method,
                    "status_code": response.status_code,
                    "response_headers": dict(response.headers),
                    "response_content": response.text[:1000] if len(response.text) > 1000 else response.text
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"表单提交失败: {str(e)}"
            )

    def _api_request(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """发送API请求"""
        url = parameters["url"]
        method = parameters.get("method", "GET")
        headers = parameters.get("headers", {})
        data = parameters.get("data", {})
        params = parameters.get("params", {})
        timeout = parameters.get("timeout", 30)

        try:
            # 准备请求参数
            request_kwargs = {
                "url": url,
                "timeout": timeout,
                "headers": headers
            }

            if method.upper() in ["POST", "PUT", "PATCH"]:
                if headers.get("content-type", "").startswith("application/json"):
                    request_kwargs["json"] = data
                else:
                    request_kwargs["data"] = data
            else:
                request_kwargs["params"] = params

            # 发送请求
            response = self.session.request(method, **request_kwargs)

            # 尝试解析JSON响应
            try:
                response_data = response.json()
            except:
                response_data = response.text

            return ToolResult(
                success=True,
                message=f"API请求成功: {method} {url}",
                data={
                    "url": url,
                    "method": method,
                    "status_code": response.status_code,
                    "response_headers": dict(response.headers),
                    "response_data": response_data
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"API请求失败: {str(e)}"
            )

    def _check_url_status(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """检查URL状态"""
        url = parameters["url"]
        timeout = parameters.get("timeout", 10)

        try:
            # 验证URL格式
            parsed_url = urlparse(url)
            if not parsed_url.scheme:
                url = "https://" + url

            # 发送HEAD请求
            response = self.session.head(url, timeout=timeout, allow_redirects=True)

            return ToolResult(
                success=True,
                message=f"URL状态检查完成: {url}",
                data={
                    "url": url,
                    "status_code": response.status_code,
                    "status_text": response.reason,
                    "headers": dict(response.headers),
                    "final_url": response.url,
                    "is_accessible": 200 <= response.status_code < 400
                }
            )

        except requests.exceptions.RequestException as e:
            return ToolResult(
                success=False,
                message=f"URL不可访问: {str(e)}",
                data={
                    "url": url,
                    "error": str(e),
                    "is_accessible": False
                }
            )