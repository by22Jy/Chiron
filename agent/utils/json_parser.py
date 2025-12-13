#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON响应解析器 - Task 3.1
提供健壮的多层JSON解析策略，处理各种格式错误的LLM响应
"""

import json
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)


class JSONResponseParser:
    """
    健壮的JSON响应解析器

    实现多层解析策略：
    1. 标准JSON解析
    2. 宽松模式解析
    3. 部分解析
    4. 手动重构响应结构
    """

    def __init__(self):
        self.error_stats = {
            "total_attempts": 0,
            "standard_success": 0,
            "lenient_success": 0,
            "partial_success": 0,
            "manual_success": 0,
            "total_failures": 0
        }

        # 默认响应结构
        self.default_response = {
            "action": "unknown",
            "command": "",
            "confidence": 0.0,
            "description": "解析失败，使用默认响应",
            "parsing_strategy": "manual_reconstruction"
        }

    def parse_response(self, response: str) -> Dict[str, Any]:
        """
        多层JSON解析主入口

        Args:
            response: 原始响应字符串

        Returns:
            解析后的字典，包含原始数据和解析策略信息
        """
        self.error_stats["total_attempts"] += 1

        if not response or not isinstance(response, str):
            logger.warning(f"Empty or invalid response type: {type(response)}")
            return self._manual_reconstruction(response)

        # 策略1: 标准JSON解析
        result = self._standard_parse(response)
        if result is not None:
            self.error_stats["standard_success"] += 1
            result["parsing_strategy"] = "standard"
            return result

        # 策略2: 宽松模式解析
        result = self._lenient_parse(response)
        if result is not None:
            self.error_stats["lenient_success"] += 1
            result["parsing_strategy"] = "lenient"
            return result

        # 策略3: 部分解析
        result = self._partial_parse(response)
        if result is not None:
            self.error_stats["partial_success"] += 1
            result["parsing_strategy"] = "partial"
            return result

        # 策略4: 手动重构
        result = self._manual_reconstruction(response)
        self.error_stats["manual_success"] += 1
        result["parsing_strategy"] = "manual_reconstruction"
        return result

    def _standard_parse(self, response: str) -> Optional[Dict[str, Any]]:
        """
        策略1: 标准JSON解析
        """
        try:
            # 清理常见的格式问题
            cleaned_response = self._clean_response_format(response)

            # 标准JSON解析
            result = json.loads(cleaned_response)

            # 验证必需字段
            if self._validate_response_structure(result):
                return result
            else:
                logger.warning("Response validation failed in standard parse")
                return None

        except json.JSONDecodeError as e:
            logger.debug(f"Standard JSON parse failed: {e}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error in standard parse: {e}")
            return None

    def _lenient_parse(self, response: str) -> Optional[Dict[str, Any]]:
        """
        策略2: 宽松模式解析
        处理常见的JSON格式错误
        """
        try:
            # 更激进的清理
            cleaned = self._aggressive_clean(response)

            # 尝试多种JSON模式匹配
            json_matches = self._extract_json_patterns(cleaned)

            for match in json_matches:
                try:
                    result = json.loads(match)
                    if self._validate_response_structure(result):
                        logger.info(f"Lenient parse succeeded with pattern: {match[:50]}...")
                        return result
                except json.JSONDecodeError:
                    continue

            return None

        except Exception as e:
            logger.debug(f"Lenient parse failed: {e}")
            return None

    def _partial_parse(self, response: str) -> Optional[Dict[str, Any]]:
        """
        策略3: 部分解析
        尝试提取可用的键值对
        """
        try:
            # 查找引号包围的键值对
            key_value_pairs = self._extract_key_value_pairs(response)

            if not key_value_pairs:
                return None

            # 构建部分结果
            result = {}
            for key, value in key_value_pairs:
                try:
                    # 尝试解析值
                    if value.startswith('"') and value.endswith('"'):
                        result[key] = value[1:-1]  # 去除引号
                    elif value.lower() in ('true', 'false'):
                        result[key] = value.lower() == 'true'
                    elif value.replace('.', '').isdigit():
                        result[key] = float(value) if '.' in value else int(value)
                    else:
                        result[key] = value
                except Exception:
                    result[key] = value

            # 添加默认必需字段
            self._ensure_required_fields(result)

            logger.info(f"Partial parse extracted {len(key_value_pairs)} key-value pairs")
            return result

        except Exception as e:
            logger.debug(f"Partial parse failed: {e}")
            return None

    def _manual_reconstruction(self, response: str) -> Dict[str, Any]:
        """
        策略4: 手动重构响应结构
        基于关键词分析和模式识别
        """
        try:
            logger.warning(f"Manual reconstruction triggered for response: {response[:100]}...")

            # 分析响应内容
            analysis = self._analyze_response_content(response)

            # 重构响应
            result = {
                "action": analysis.get("action", "unknown"),
                "command": analysis.get("command", ""),
                "confidence": analysis.get("confidence", 0.0),
                "description": analysis.get("description", "解析失败的响应"),
                "parsing_strategy": "manual_reconstruction",
                "original_response_length": len(response),
                "reconstruction_confidence": analysis.get("confidence", 0.0),
                "timestamp": datetime.now().isoformat()
            }

            self.error_stats["manual_success"] += 1
            return result

        except Exception as e:
            logger.error(f"Manual reconstruction failed: {e}")
            return self.default_response.copy()

    def _clean_response_format(self, response: str) -> str:
        """清理响应格式"""
        # 移除前后空白
        response = response.strip()

        # 移除常见的非JSON前缀/后缀
        prefixes_to_remove = ["Here's my response:", "My response:", "Response:", "Result:"]
        suffixes_to_remove = ["End of response.", "End of response", "That's all."]

        for prefix in prefixes_to_remove:
            if response.startswith(prefix):
                response = response[len(prefix):].strip()

        for suffix in suffixes_to_remove:
            if response.endswith(suffix):
                response = response[:-len(suffix)].strip()

        return response

    def _aggressive_clean(self, response: str) -> str:
        """激进的响应清理"""
        # 移除所有非JSON内容
        response = self._clean_response_format(response)

        # 查找第一个 { 和最后一个 }
        start = response.find('{')
        end = response.rfind('}')

        if start != -1 and end != -1 and end > start:
            return response[start:end + 1]

        return response

    def _extract_json_patterns(self, response: str) -> List[str]:
        """从响应中提取JSON模式"""
        patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # 基本JSON模式
            r'\{.*?\}',  # 非贪婪JSON模式
        ]

        matches = []
        for pattern in patterns:
            try:
                found = re.findall(pattern, response, re.DOTALL)
                matches.extend(found)
            except Exception:
                continue

        return matches

    def _extract_key_value_pairs(self, response: str) -> List[Tuple[str, str]]:
        """提取键值对"""
        # 查找 "key": "value" 模式
        pattern = r'"([^"]+)"\s*:\s*"([^"]*)"'
        matches = re.findall(pattern, response)

        return matches

    def _analyze_response_content(self, response: str) -> Dict[str, Any]:
        """分析响应内容并重构结构"""
        analysis = {
            "action": "unknown",
            "command": "",
            "confidence": 0.0,
            "description": "无法解析的响应"
        }

        response_lower = response.lower()

        # 动作类型识别
        action_keywords = {
            "open_app": ["打开", "启动", "运行", "open", "start", "launch", "execute"],
            "system_control": ["音量", "亮度", "关闭", "重启", "volume", "brightness", "shutdown", "restart"],
            "file_operation": ["文件", "保存", "删除", "复制", "file", "save", "delete", "copy"],
            "web_search": ["搜索", "查询", "search", "find", "lookup"],
        }

        max_confidence = 0.0
        for action, keywords in action_keywords.items():
            confidence = sum(1 for keyword in keywords if keyword in response_lower)
            if confidence > max_confidence:
                max_confidence = confidence
                analysis["action"] = action
                analysis["confidence"] = min(confidence / 3.0, 1.0)  # 标准化置信度

        # 命令提取（简单的应用程序名称提取）
        common_apps = ["notepad", "calculator", "chrome", "firefox", "excel", "word", "powerpoint"]
        for app in common_apps:
            if app in response_lower:
                analysis["command"] = f"{app}.exe"
                analysis["confidence"] = max(analysis["confidence"], 0.7)
                break

        # 描述生成
        if len(response) > 10:
            analysis["description"] = response[:100] + "..." if len(response) > 100 else response

        return analysis

    def _validate_response_structure(self, response: Dict[str, Any]) -> bool:
        """验证响应结构"""
        if not isinstance(response, dict):
            return False

        # 检查必需字段
        required_fields = ["action"]
        return all(field in response for field in required_fields)

    def _ensure_required_fields(self, response: Dict[str, Any]) -> None:
        """确保必需字段存在"""
        if "action" not in response:
            response["action"] = "unknown"
        if "confidence" not in response:
            response["confidence"] = 0.0
        if "description" not in response:
            response["description"] = "部分解析的结果"

    def get_error_statistics(self) -> Dict[str, Any]:
        """获取解析错误统计"""
        total = self.error_stats["total_attempts"]
        if total == 0:
            return self.error_stats

        stats = self.error_stats.copy()
        stats["success_rate"] = (stats["standard_success"] + stats["lenient_success"] +
                                stats["partial_success"] + stats["manual_success"]) / total
        return stats

    def reset_statistics(self) -> None:
        """重置统计信息"""
        self.error_stats = {
            "total_attempts": 0,
            "standard_success": 0,
            "lenient_success": 0,
            "partial_success": 0,
            "manual_success": 0,
            "total_failures": 0
        }