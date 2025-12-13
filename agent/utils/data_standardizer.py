#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent端数据格式标准化工具
负责处理与Backend通信的数据格式标准化
"""

import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class DataStandardizer:
    """数据标准化工具类"""

    def __init__(self):
        self.backend_url = "http://127.0.0.1:8080"

    def create_standard_request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建标准格式的请求数据

        Args:
            endpoint: API端点名称
            data: 原始数据

        Returns:
            标准化的请求数据
        """
        standard_request = {
            "timestamp": self.get_current_iso_timestamp(),
            "request_id": self.generate_request_id(),
            "endpoint": endpoint
        }

        # 根据端点类型添加特定字段
        if endpoint == "gesture-analysis":
            standard_request.update({
                "prompt": data.get("prompt", ""),
                "gesture_code": self.standardize_gesture_name(data.get("gesture_code", "")),
                "confidence": data.get("confidence", 0.0),
                "context": data.get("context", "")
            })
        elif endpoint == "voice-command":
            standard_request.update({
                "command": data.get("command", ""),
                "context": data.get("context", "")
            })
        elif endpoint == "intelligent":
            # 处理智能编排请求
            if "user_intent" in data:
                standard_request["user_intent"] = self._standardize_user_intent(data["user_intent"])
            else:
                # 兼容旧格式
                standard_request["message"] = data.get("message", "")
                standard_request["context"] = data.get("context", "")
        else:
            # 通用处理
            standard_request.update(data)

        return standard_request

    def parse_standard_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析Backend返回的标准响应格式

        Args:
            response: Backend响应数据

        Returns:
            标准化后的响应数据
        """
        # 检查是否为新的标准格式
        if "status" in response and "data" in response:
            return self._parse_new_format(response)
        else:
            # 兼容旧格式
            return self._parse_legacy_format(response)

    def _parse_new_format(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析新的标准格式响应"""
        result = {
            "success": response.get("status") == "success",
            "status": response.get("status", "unknown"),
            "message": response.get("message", ""),
            "timestamp": response.get("timestamp", ""),
            "data": response.get("data", {})
        }

        # 从data中提取原始响应
        data = response.get("data", {})
        if "original_response" in data:
            result["response"] = data["original_response"]

        return result

    def _parse_legacy_format(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """解析旧格式响应并转换为标准格式"""
        return {
            "success": response.get("success", False),
            "status": "success" if response.get("success", False) else "error",
            "message": response.get("response", ""),
            "timestamp": self.convert_timestamp_to_iso(response.get("timestamp")),
            "data": {
                "original_response": response.get("response", ""),
                "original_success": response.get("success", False)
            }
        }

    def standardize_gesture_name(self, gesture_name: str) -> str:
        """
        标准化手势名称为大写下划线格式

        Args:
            gesture_name: 原始手势名称

        Returns:
            标准化的手势名称，如果输入为None或空字符串则返回None
        """
        if gesture_name is None or gesture_name == "":
            return None

        # 转换为大写并用下划线替换空格
        standardized = gesture_name.upper().replace(" ", "_")

        # 常见手势名称映射
        gesture_mapping = {
            "V": "VICTORY",
            "OK": "OK_SIGN",
            "THUMBSUP": "THUMBS_UP",
            "POINTUP": "POINT_UP",
            "FIST": "CLOSED_FIST"
        }

        return gesture_mapping.get(standardized, standardized)

    def _standardize_user_intent(self, user_intent: Dict[str, Any]) -> Dict[str, Any]:
        """标准化用户意图数据"""
        if not isinstance(user_intent, dict):
            return user_intent

        standardized = user_intent.copy()

        # 确保时间戳是ISO格式
        if "timestamp" in standardized:
            standardized["timestamp"] = self.convert_timestamp_to_iso(standardized["timestamp"])
        else:
            standardized["timestamp"] = self.get_current_iso_timestamp()

        return standardized

    def get_current_iso_timestamp(self) -> str:
        """获取当前ISO格式时间戳"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def convert_timestamp_to_iso(self, timestamp: Union[str, int, float, None]) -> str:
        """
        将各种格式的时间戳转换为ISO格式

        Args:
            timestamp: 时间戳（字符串、整数、浮点数或None）

        Returns:
            ISO格式的时间戳字符串
        """
        if timestamp is None:
            return self.get_current_iso_timestamp()

        if isinstance(timestamp, str):
            # 如果已经是ISO格式，直接返回
            if "T" in timestamp and ("Z" in timestamp or "+" in timestamp):
                return timestamp
            # 尝试解析为数字
            try:
                numeric_timestamp = float(timestamp)
                return self._convert_numeric_to_iso(numeric_timestamp)
            except ValueError:
                return self.get_current_iso_timestamp()
        elif isinstance(timestamp, (int, float)):
            return self._convert_numeric_to_iso(timestamp)

        return self.get_current_iso_timestamp()

    def _convert_numeric_to_iso(self, timestamp: Union[int, float]) -> str:
        """将数字时间戳转换为ISO格式"""
        try:
            # 判断是秒还是毫秒
            if timestamp > 1e10:  # 毫秒
                dt = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
            else:  # 秒
                dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except (ValueError, OSError):
            return self.get_current_iso_timestamp()

    def generate_request_id(self) -> str:
        """生成唯一的请求ID"""
        return f"req_{int(time.time() * 1000)}_{id(self)}"

    def validate_response_format(self, response: Dict[str, Any]) -> bool:
        """
        验证响应格式是否符合标准

        Args:
            response: 响应数据

        Returns:
            是否符合标准格式
        """
        required_fields = ["status", "data", "message", "timestamp"]

        # 检查新格式
        if all(field in response for field in required_fields):
            return True

        # 检查旧格式兼容性
        if "success" in response and "response" in response:
            return True

        return False

    def create_audit_log_payload(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建审计日志的标准化载荷

        Args:
            event_data: 事件数据

        Returns:
            标准化的审计日志载荷
        """
        return {
            "eventType": event_data.get("event_type", "unknown"),
            "username": event_data.get("username", "agent"),
            "application": event_data.get("application", "yolo-llm-agent"),
            "payload": json.dumps(event_data.get("payload", {}), ensure_ascii=False),
            "timestamp": self.get_current_iso_timestamp()
        }