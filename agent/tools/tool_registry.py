"""
ToolRegistry - 工具注册表

提供动态工具注册、查找和管理功能
实现单例模式确保全局唯一的工具注册表实例
"""

from typing import Dict, List, Optional, Type, Any
import logging
import threading
from dataclasses import dataclass

try:
    from .base_tool import BaseTool, ToolResult
except ImportError:
    from base_tool import BaseTool, ToolResult


@dataclass
class ToolRegistration:
    """工具注册信息"""
    tool: BaseTool
    registered_at: float
    enabled: bool = True
    metadata: Optional[Dict[str, Any]] = None


class ToolRegistry:
    """
    工具注册表 - 单例模式

    管理所有已注册的工具，提供动态注册、查找和执行功能
    线程安全，支持并发操作
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ToolRegistry, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._tools: Dict[str, ToolRegistration] = {}
                    self._logger = logging.getLogger(self.__class__.__name__)
                    self._initialized = True
                    self._logger.info("工具注册表初始化完成")

    def register_tool(self, tool: BaseTool, enabled: bool = True,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        注册工具

        Args:
            tool: 工具实例
            enabled: 是否启用 (默认True)
            metadata: 元数据 (可选)

        Returns:
            bool: 注册是否成功
        """
        if not isinstance(tool, BaseTool):
            self._logger.error(f"工具必须继承自BaseTool，得到: {type(tool)}")
            return False

        tool_name = tool.name
        if not tool_name:
            self._logger.error("工具名称不能为空")
            return False

        import time

        with self._lock:
            # 检查是否已存在同名工具
            if tool_name in self._tools:
                existing_tool = self._tools[tool_name].tool
                self._logger.warning(f"工具 '{tool_name}' 已存在，将被替换")
                self._logger.info(f"原有工具: {existing_tool}, 新工具: {tool}")

            # 注册工具
            registration = ToolRegistration(
                tool=tool,
                registered_at=time.time(),
                enabled=enabled,
                metadata=metadata
            )

            self._tools[tool_name] = registration
            self._logger.info(f"成功注册工具: {tool_name}, 启用状态: {enabled}")
            return True

    def unregister_tool(self, tool_name: str) -> bool:
        """
        注销工具

        Args:
            tool_name: 工具名称

        Returns:
            bool: 注销是否成功
        """
        with self._lock:
            if tool_name not in self._tools:
                self._logger.error(f"工具 '{tool_name}' 不存在")
                return False

            del self._tools[tool_name]
            self._logger.info(f"成功注销工具: {tool_name}")
            return True

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取工具实例

        Args:
            tool_name: 工具名称

        Returns:
            Optional[BaseTool]: 工具实例，如果不存在则返回None
        """
        with self._lock:
            registration = self._tools.get(tool_name)
            if not registration:
                return None

            if not registration.enabled:
                self._logger.warning(f"工具 '{tool_name}' 已禁用")
                return None

            return registration.tool

    def list_tools(self, include_disabled: bool = False) -> List[str]:
        """
        列出所有已注册的工具名称

        Args:
            include_disabled: 是否包含已禁用的工具

        Returns:
            List[str]: 工具名称列表
        """
        with self._lock:
            if include_disabled:
                return list(self._tools.keys())
            else:
                return [name for name, reg in self._tools.items() if reg.enabled]

    def get_tool_capabilities(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """
        获取工具能力描述

        Args:
            tool_name: 工具名称

        Returns:
            Optional[Dict[str, Any]]: 工具能力信息
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return None
        return tool.get_capabilities()

    def get_all_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有已启用工具的能力描述

        Returns:
            Dict[str, Dict[str, Any]]: 所有工具的能力信息
        """
        capabilities = {}
        enabled_tools = self.list_tools()

        for tool_name in enabled_tools:
            tool = self.get_tool(tool_name)
            if tool:
                capabilities[tool_name] = tool.get_capabilities()

        return capabilities

    def execute_tool(self, tool_name: str, action: str,
                    parameters: Optional[Dict[str, Any]] = None,
                    context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        执行工具动作

        Args:
            tool_name: 工具名称
            action: 动作名称
            parameters: 动作参数 (可选)
            context: 执行上下文 (可选)

        Returns:
            ToolResult: 执行结果
        """
        self._logger.info(f"准备执行工具: {tool_name}.{action}")

        tool = self.get_tool(tool_name)
        if not tool:
            error_msg = f"工具 '{tool_name}' 不存在或已禁用"
            self._logger.error(error_msg)
            return ToolResult(
                success=False,
                message=error_msg,
                error_details=f"可用工具: {self.list_tools()}"
            )

        try:
            result = tool.execute(action, parameters, context)
            self._logger.info(f"工具执行完成: {tool_name}.{action}, 成功: {result.success}")
            return result

        except Exception as e:
            error_msg = f"执行工具 '{tool_name}' 时发生异常: {str(e)}"
            self._logger.error(error_msg)
            return ToolResult(
                success=False,
                message=error_msg
            )

    def enable_tool(self, tool_name: str) -> bool:
        """
        启用工具

        Args:
            tool_name: 工具名称

        Returns:
            bool: 操作是否成功
        """
        with self._lock:
            if tool_name not in self._tools:
                self._logger.error(f"工具 '{tool_name}' 不存在")
                return False

            self._tools[tool_name].enabled = True
            self._logger.info(f"已启用工具: {tool_name}")
            return True

    def disable_tool(self, tool_name: str) -> bool:
        """
        禁用工具

        Args:
            tool_name: 工具名称

        Returns:
            bool: 操作是否成功
        """
        with self._lock:
            if tool_name not in self._tools:
                self._logger.error(f"工具 '{tool_name}' 不存在")
                return False

            self._tools[tool_name].enabled = False
            self._logger.info(f"已禁用工具: {tool_name}")
            return True

    def get_tool_status(self, tool_name: str) -> Optional[str]:
        """
        获取工具状态

        Args:
            tool_name: 工具名称

        Returns:
            Optional[str]: 工具状态，如果不存在则返回None
        """
        with self._lock:
            registration = self._tools.get(tool_name)
            if not registration:
                return None

            if not registration.enabled:
                return "disabled"

            return registration.tool.get_status().value

    def get_registry_info(self) -> Dict[str, Any]:
        """
        获取注册表信息

        Returns:
            Dict[str, Any]: 注册表统计信息
        """
        with self._lock:
            total_tools = len(self._tools)
            enabled_tools = len([reg for reg in self._tools.values() if reg.enabled])
            disabled_tools = total_tools - enabled_tools

            return {
                'total_tools': total_tools,
                'enabled_tools': enabled_tools,
                'disabled_tools': disabled_tools,
                'tool_names': self.list_tools(),
                'disabled_tool_names': [name for name in self.list_tools(include_disabled=True)
                                       if name not in self.list_tools()]
            }

    def clear_registry(self) -> None:
        """清空注册表"""
        with self._lock:
            self._tools.clear()
            self._logger.info("工具注册表已清空")

    def reset_all_tools(self) -> None:
        """重置所有工具状态"""
        with self._lock:
            for registration in self._tools.values():
                if registration.enabled:
                    registration.tool.reset_status()

            self._logger.info("所有工具状态已重置")

    def __len__(self) -> int:
        """返回已注册工具数量"""
        return len(self._tools)

    def __contains__(self, tool_name: str) -> bool:
        """检查工具是否已注册"""
        return tool_name in self._tools

    def __str__(self) -> str:
        info = self.get_registry_info()
        return (f"ToolRegistry(total={info['total_tools']}, "
                f"enabled={info['enabled_tools']}, "
                f"disabled={info['disabled_tools']})")

    def __repr__(self) -> str:
        return self.__str__()