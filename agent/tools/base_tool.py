"""
BaseTool - 工具系统抽象基类

定义了所有工具的统一接口和通用行为
提供工具注册、执行和错误处理的标准化机制
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging
import json
import traceback


class ToolStatus(Enum):
    """工具状态枚举"""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ToolResult:
    """工具执行结果"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    context_update: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None
    execution_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'success': self.success,
            'message': self.message,
            'data': self.data,
            'context_update': self.context_update,
            'error_details': self.error_details,
            'execution_time': self.execution_time
        }


class BaseTool(ABC):
    """
    工具系统抽象基类

    所有具体工具都必须继承此类并实现相应方法
    提供统一的工具接口和标准化的执行流程
    """

    def __init__(self):
        self.status = ToolStatus.IDLE
        self.logger = logging.getLogger(self.__class__.__name__)
        self._last_result: Optional[ToolResult] = None

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称 - 必须唯一"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    @abstractmethod
    def supported_actions(self) -> List[str]:
        """支持的动作列表"""
        pass

    @property
    @abstractmethod
    def required_permissions(self) -> List[str]:
        """所需权限列表"""
        pass

    @abstractmethod
    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """
        验证参数有效性

        Args:
            action: 动作名称
            parameters: 参数字典

        Returns:
            bool: 参数是否有效
        """
        pass

    @abstractmethod
    def execute_action(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """
        执行具体动作

        Args:
            action: 动作名称
            parameters: 动作参数
            context: 执行上下文

        Returns:
            ToolResult: 执行结果
        """
        pass

    def execute(self, action: str, parameters: Optional[Dict[str, Any]] = None,
                context: Optional[Dict[str, Any]] = None) -> ToolResult:
        """
        执行动作的统一入口方法

        Args:
            action: 动作名称
            parameters: 动作参数 (可选)
            context: 执行上下文 (可选)

        Returns:
            ToolResult: 执行结果
        """
        import time
        start_time = time.time()

        # 默认值处理
        if parameters is None:
            parameters = {}
        if context is None:
            context = {}

        self.logger.info(f"开始执行工具: {self.name}, 动作: {action}")
        self.logger.debug(f"参数: {parameters}, 上下文: {context}")

        # 更新状态
        self.status = ToolStatus.RUNNING

        try:
            # 验证动作是否支持
            if action not in self.supported_actions:
                error_msg = f"工具 {self.name} 不支持动作: {action}"
                self.logger.error(error_msg)
                result = ToolResult(
                    success=False,
                    message=error_msg,
                    error_details=f"支持的动作: {self.supported_actions}"
                )
                self.status = ToolStatus.FAILED
                return result

            # 验证参数
            if not self.validate_parameters(action, parameters):
                error_msg = f"工具 {self.name} 动作 {action} 的参数验证失败"
                self.logger.error(error_msg)
                result = ToolResult(
                    success=False,
                    message=error_msg,
                    error_details=f"无效的参数: {parameters}"
                )
                self.status = ToolStatus.FAILED
                return result

            # 执行具体动作
            result = self.execute_action(action, parameters, context)

            # 计算执行时间
            execution_time = time.time() - start_time
            result.execution_time = execution_time

            # 更新状态
            if result.success:
                self.status = ToolStatus.COMPLETED
                self.logger.info(f"工具执行成功: {self.name}.{action}, 耗时: {execution_time:.2f}秒")
            else:
                self.status = ToolStatus.FAILED
                self.logger.error(f"工具执行失败: {self.name}.{action}, 错误: {result.message}")

            self._last_result = result
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"工具 {self.name} 执行动作 {action} 时发生异常: {str(e)}"
            self.logger.error(error_msg)
            self.logger.debug(f"异常堆栈: {traceback.format_exc()}")

            result = ToolResult(
                success=False,
                message=error_msg,
                error_details=traceback.format_exc(),
                execution_time=execution_time
            )

            self.status = ToolStatus.FAILED
            self._last_result = result
            return result

    def get_status(self) -> ToolStatus:
        """获取当前状态"""
        return self.status

    def get_last_result(self) -> Optional[ToolResult]:
        """获取最后一次执行结果"""
        return self._last_result

    def reset_status(self) -> None:
        """重置工具状态"""
        self.status = ToolStatus.IDLE
        self._last_result = None

    def get_capabilities(self) -> Dict[str, Any]:
        """
        获取工具能力描述

        Returns:
            Dict[str, Any]: 工具能力信息
        """
        return {
            'name': self.name,
            'description': self.description,
            'supported_actions': self.supported_actions,
            'required_permissions': self.required_permissions,
            'status': self.status.value,
            'last_result': self._last_result.to_dict() if self._last_result else None
        }

    def validate_parameters_base(self, action: str, parameters: Dict[str, Any],
                                required_params: List[str], optional_params: List[str] = None) -> bool:
        """
        基础参数验证方法

        Args:
            action: 动作名称
            parameters: 参数字典
            required_params: 必需参数列表
            optional_params: 可选参数列表

        Returns:
            bool: 参数是否有效
        """
        if not isinstance(parameters, dict):
            self.logger.error(f"参数必须是字典类型，得到: {type(parameters)}")
            return False

        # 检查必需参数
        for param in required_params:
            if param not in parameters or parameters[param] is None:
                self.logger.error(f"缺少必需参数: {param}")
                return False

        # 检查是否有多余的参数
        allowed_params = set(required_params + (optional_params or []))
        for param in parameters:
            if param not in allowed_params:
                self.logger.warning(f"未知参数: {param}")

        return True

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', status='{self.status.value}')"

    def __repr__(self) -> str:
        return self.__str__()