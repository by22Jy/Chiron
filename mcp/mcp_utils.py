#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP服务器工具模块
包含重试机制、错误处理、缓存等功能
"""

import time
import asyncio
import hashlib
from typing import Dict, Any, Optional, List
from functools import wraps
from datetime import datetime, timedelta
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MCPRetryException(Exception):
    """MCP重试异常"""
    pass

class MCPTimeoutException(Exception):
    """MCP超时异常"""
    pass

def retry_with_backoff(max_retries: int = 3, backoff_factor: float = 1.0, exceptions: tuple = (Exception,)):
    """
    带指数退避的重试装饰器

    Args:
        max_retries: 最大重试次数
        backoff_factor: 退避因子
        exceptions: 需要重试的异常类型
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        wait_time = backoff_factor * (2 ** (attempt - 1))
                        logger.info(f"第 {attempt} 次重试 {func.__name__}，等待 {wait_time:.1f} 秒...")
                        await asyncio.sleep(wait_time)

                    result = await func(*args, **kwargs)
                    if attempt > 0:
                        logger.info(f"{func.__name__} 在第 {attempt} 次重试后成功")
                    return result

                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"{func.__name__} 失败 (尝试 {attempt + 1}/{max_retries + 1}): {str(e)}")
                    else:
                        logger.error(f"{func.__name__} 在 {max_retries + 1} 次尝试后仍然失败: {str(e)}")

            # 所有重试都失败了
            raise MCPRetryException(f"函数 {func.__name__} 在 {max_retries + 1} 次尝试后失败: {str(last_exception)}")

        return wrapper
    return decorator

def timeout_handler(seconds: int):
    """
    超时处理装饰器

    Args:
        seconds: 超时时间（秒）
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(func(*args, **kwargs), timeout=seconds)
            except asyncio.TimeoutError:
                raise MCPTimeoutException(f"函数 {func.__name__} 执行超时 ({seconds} 秒)")

        return wrapper
    return decorator

class MCPCache:
    """MCP响应缓存"""

    def __init__(self, default_ttl: int = 300):  # 默认5分钟TTL
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl

    def _generate_cache_key(self, tool_name: str, params: Dict[str, Any]) -> str:
        """生成缓存键"""
        # 创建稳定的参数字符串
        sorted_params = sorted(params.items())
        param_str = str(sorted_params)
        cache_key = f"{tool_name}:{hashlib.md5(param_str.encode()).hexdigest()}"
        return cache_key

    def get(self, tool_name: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """获取缓存数据"""
        cache_key = self._generate_cache_key(tool_name, params)

        if cache_key in self.cache:
            cache_data = self.cache[cache_key]
            if time.time() - cache_data['timestamp'] < cache_data['ttl']:
                logger.debug(f"缓存命中: {tool_name}")
                return cache_data['data']
            else:
                # 缓存过期，删除
                del self.cache[cache_key]
                logger.debug(f"缓存过期: {tool_name}")

        return None

    def set(self, tool_name: str, params: Dict[str, Any], data: Dict[str, Any], ttl: Optional[int] = None):
        """设置缓存数据"""
        cache_key = self._generate_cache_key(tool_name, params)
        cache_ttl = ttl if ttl is not None else self.default_ttl

        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time(),
            'ttl': cache_ttl
        }
        logger.debug(f"缓存设置: {tool_name} (TTL: {cache_ttl}s)")

    def clear(self, tool_name: Optional[str] = None):
        """清除缓存"""
        if tool_name:
            # 清除特定工具的缓存
            keys_to_remove = [k for k in self.cache.keys() if k.startswith(f"{tool_name}:")]
            for key in keys_to_remove:
                del self.cache[key]
            logger.info(f"已清除 {tool_name} 的缓存")
        else:
            # 清除所有缓存
            self.cache.clear()
            logger.info("已清除所有缓存")

    def get_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        total_entries = len(self.cache)
        expired_entries = sum(
            1 for entry in self.cache.values()
            if time.time() - entry['timestamp'] >= entry['ttl']
        )

        return {
            'total_entries': total_entries,
            'active_entries': total_entries - expired_entries,
            'expired_entries': expired_entries
        }

class MCPPerformanceMonitor:
    """MCP性能监控"""

    def __init__(self):
        self.metrics: Dict[str, List[Dict[str, Any]]] = {}

    def record_request(self, tool_name: str, duration: float, success: bool, error: Optional[str] = None):
        """记录请求性能数据"""
        if tool_name not in self.metrics:
            self.metrics[tool_name] = []

        metric = {
            'timestamp': time.time(),
            'duration': duration,
            'success': success,
            'error': error
        }

        self.metrics[tool_name].append(metric)

        # 只保留最近1000条记录
        if len(self.metrics[tool_name]) > 1000:
            self.metrics[tool_name] = self.metrics[tool_name][-1000:]

    def get_performance_report(self, tool_name: Optional[str] = None) -> Dict[str, Any]:
        """获取性能报告"""
        if tool_name:
            if tool_name not in self.metrics:
                return {}
            metrics_data = {tool_name: self.metrics[tool_name]}
        else:
            metrics_data = self.metrics

        report = {}

        for name, records in metrics_data.items():
            if not records:
                continue

            durations = [r['duration'] for r in records]
            successes = [r for r in records if r['success']]

            report[name] = {
                'total_requests': len(records),
                'successful_requests': len(successes),
                'success_rate': len(successes) / len(records) * 100,
                'avg_duration': sum(durations) / len(durations),
                'min_duration': min(durations),
                'max_duration': max(durations),
                'last_request_time': records[-1]['timestamp']
            }

            # 添加错误统计
            errors = [r['error'] for r in records if not r['success'] and r['error']]
            if errors:
                error_counts = {}
                for error in errors:
                    error_counts[error] = error_counts.get(error, 0) + 1
                report[name]['common_errors'] = sorted(error_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return report

class MCPErrorHandler:
    """MCP错误处理器"""

    def __init__(self):
        self.error_counts: Dict[str, int] = {}
        self.last_errors: List[Dict[str, Any]] = []

    def handle_error(self, error: Exception, tool_name: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """处理错误并返回标准化错误响应"""
        error_type = type(error).__name__
        error_message = str(error)

        # 记录错误统计
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1

        # 记录最近错误
        error_record = {
            'timestamp': time.time(),
            'tool_name': tool_name,
            'error_type': error_type,
            'error_message': error_message,
            'context': context or {}
        }

        self.last_errors.append(error_record)

        # 只保留最近100条错误
        if len(self.last_errors) > 100:
            self.last_errors = self.last_errors[-100:]

        # 根据错误类型返回不同的响应
        if isinstance(error, MCPTimeoutException):
            return {
                'success': False,
                'error': 'TIMEOUT',
                'message': f'请求超时: {error_message}',
                'retry_after': 5  # 建议5秒后重试
            }
        elif isinstance(error, MCPRetryException):
            return {
                'success': False,
                'error': 'RETRY_EXHAUSTED',
                'message': f'重试次数已用完: {error_message}',
                'retry_after': 30  # 建议30秒后重试
            }
        elif isinstance(error, ConnectionError):
            return {
                'success': False,
                'error': 'CONNECTION_ERROR',
                'message': f'网络连接错误: {error_message}',
                'retry_after': 10  # 建议10秒后重试
            }
        elif isinstance(error, ValueError):
            return {
                'success': False,
                'error': 'INVALID_PARAMETER',
                'message': f'参数错误: {error_message}',
                'retry_after': None  # 参数错误不需要重试
            }
        else:
            return {
                'success': False,
                'error': 'UNKNOWN_ERROR',
                'message': f'未知错误: {error_message}',
                'retry_after': 15  # 默认建议15秒后重试
            }

    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        return {
            'total_errors': sum(self.error_counts.values()),
            'error_types': dict(self.error_counts),
            'recent_errors': self.last_errors[-10:],  # 最近10个错误
            'error_rate': len(self.last_errors) / max(len(self.last_errors), 1) * 100
        }

# 全局实例
mcp_cache = MCPCache()
mcp_monitor = MCPPerformanceMonitor()
mcp_error_handler = MCPErrorHandler()