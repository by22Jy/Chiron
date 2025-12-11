#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP基础工具类
提供所有工具的通用接口和功能
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel
import asyncio
import logging

logger = logging.getLogger(__name__)

class ToolResponse(BaseModel):
    """工具响应基类"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    error: Optional[str] = None
    tool_name: Optional[str] = None
    execution_time: Optional[float] = None
    timestamp: datetime = None

    def __init__(self, **data):
        if 'timestamp' not in data:
            data['timestamp'] = datetime.now()
        super().__init__(**data)

class ToolError(Exception):
    """工具异常基类"""
    def __init__(self, message: str, tool_name: str = None, error_code: str = None):
        self.message = message
        self.tool_name = tool_name
        self.error_code = error_code
        super().__init__(message)

class BaseTool(ABC):
    """MCP工具基类"""

    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        self.name = name
        self.description = description
        self.version = version
        self.logger = logging.getLogger(f"mcp.tools.{name}")

        # 工具元数据
        self.metadata = {
            "name": name,
            "description": description,
            "version": version,
            "created_at": datetime.now(),
            "last_used": None,
            "usage_count": 0,
            "error_count": 0
        }

        # 性能统计
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0
        }

    @abstractmethod
    async def execute(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """
        执行工具操作

        Args:
            action: 要执行的操作名称
            parameters: 操作参数

        Returns:
            ToolResponse: 执行结果
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        获取工具能力列表

        Returns:
            List[str]: 支持的操作列表
        """
        pass

    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        获取工具参数模式

        Returns:
            Dict[str, Any]: JSON Schema格式的参数定义
        """
        pass

    async def safe_execute(self, action: str, parameters: Dict[str, Any]) -> ToolResponse:
        """
        安全执行工具操作（带异常处理和统计）

        Args:
            action: 要执行的操作名称
            parameters: 操作参数

        Returns:
            ToolResponse: 执行结果
        """
        start_time = asyncio.get_event_loop().time()

        try:
            # 验证参数
            validation_result = self.validate_parameters(action, parameters)
            if not validation_result.valid:
                return ToolResponse(
                    success=False,
                    error=f"参数验证失败: {validation_result.error}",
                    tool_name=self.name
                )

            # 执行操作
            self.logger.info(f"执行工具操作: {self.name}.{action}")
            result = await self.execute(action, parameters)

            # 更新统计
            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(execution_time, True)

            # 设置响应信息
            result.tool_name = self.name
            result.execution_time = execution_time

            return result

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            self._update_stats(execution_time, False)

            self.logger.error(f"工具执行失败: {self.name}.{action} - {str(e)}")
            return ToolResponse(
                success=False,
                error=f"工具执行异常: {str(e)}",
                tool_name=self.name,
                execution_time=execution_time
            )

    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> 'ValidationResult':
        """
        验证参数（子类可重写）

        Args:
            action: 操作名称
            parameters: 参数字典

        Returns:
            ValidationResult: 验证结果
        """
        schema = self.get_schema()
        if action not in schema.get("actions", {}):
            return ValidationResult(False, f"不支持的操作: {action}")

        # 基本验证 - 子类可以重写以实现更复杂的验证
        return ValidationResult(True)

    def _update_stats(self, execution_time: float, success: bool):
        """更新性能统计"""
        self.stats["total_calls"] += 1
        self.stats["total_execution_time"] += execution_time
        self.stats["average_execution_time"] = (
            self.stats["total_execution_time"] / self.stats["total_calls"]
        )

        if success:
            self.stats["successful_calls"] += 1
        else:
            self.stats["failed_calls"] += 1

        # 更新元数据
        self.metadata["last_used"] = datetime.now()
        self.metadata["usage_count"] += 1
        if not success:
            self.metadata["error_count"] += 1

    def get_stats(self) -> Dict[str, Any]:
        """获取工具统计信息"""
        return {
            "metadata": {
                **self.metadata,
                "created_at": self.metadata["created_at"].isoformat(),
                "last_used": self.metadata["last_used"].isoformat() if self.metadata["last_used"] else None
            },
            "stats": self.stats,
            "success_rate": (
                self.stats["successful_calls"] / max(self.stats["total_calls"], 1) * 100
            )
        }

    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0
        }
        self.metadata["usage_count"] = 0
        self.metadata["error_count"] = 0
        self.metadata["last_used"] = None

    async def health_check(self) -> Dict[str, Any]:
        """
        工具健康检查

        Returns:
            Dict[str, Any]: 健康状态信息
        """
        try:
            # 执行基本操作检查工具是否正常
            test_result = await self._perform_health_check()

            return {
                "tool_name": self.name,
                "status": "healthy" if test_result else "unhealthy",
                "version": self.version,
                "last_check": datetime.now().isoformat(),
                "stats": self.get_stats()
            }
        except Exception as e:
            return {
                "tool_name": self.name,
                "status": "error",
                "error": str(e),
                "version": self.version,
                "last_check": datetime.now().isoformat()
            }

    async def _perform_health_check(self) -> bool:
        """
        执行健康检查（子类可重写）

        Returns:
            bool: 工具是否健康
        """
        # 默认健康检查：工具可以正常获取能力列表
        try:
            capabilities = self.get_capabilities()
            return len(capabilities) > 0
        except:
            return False

class ValidationResult:
    """参数验证结果"""
    def __init__(self, valid: bool, error: str = None):
        self.valid = valid
        self.error = error

class ToolCapability:
    """工具能力描述"""
    def __init__(self, name: str, description: str, parameters: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}