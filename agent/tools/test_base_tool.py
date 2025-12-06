"""
BaseTool单元测试

测试BaseTool抽象基类的核心功能
"""

import unittest
import logging
from unittest.mock import Mock, patch
from typing import Dict, Any

from base_tool import BaseTool, ToolResult, ToolStatus


class MockTool(BaseTool):
    """用于测试的Mock工具类"""

    def __init__(self, should_fail=False, validation_fail=False):
        super().__init__()
        self.should_fail = should_fail
        self.validation_fail = validation_fail

    @property
    def name(self) -> str:
        return "mock_tool"

    @property
    def description(self) -> str:
        return "Mock tool for testing"

    @property
    def supported_actions(self) -> list:
        return ["test_action", "failing_action"]

    @property
    def required_permissions(self) -> list:
        return ["test_permission"]

    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        if self.validation_fail:
            return False
        return action in self.supported_actions and isinstance(parameters, dict)

    def execute_action(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        if self.should_fail:
            return ToolResult(
                success=False,
                message="Mock execution failed"
            )

        return ToolResult(
            success=True,
            message=f"Mock {action} executed successfully",
            data={"action": action, "parameters": parameters}
        )


class TestBaseTool(unittest.TestCase):
    """BaseTool测试类"""

    def setUp(self):
        """测试前准备"""
        self.success_tool = MockTool(should_fail=False)
        self.failing_tool = MockTool(should_fail=True)
        self.validation_tool = MockTool(validation_fail=True)

    def test_tool_properties(self):
        """测试工具属性"""
        self.assertEqual(self.success_tool.name, "mock_tool")
        self.assertEqual(self.success_tool.description, "Mock tool for testing")
        self.assertEqual(self.success_tool.supported_actions, ["test_action", "failing_action"])
        self.assertEqual(self.success_tool.required_permissions, ["test_permission"])

    def test_initial_status(self):
        """测试初始状态"""
        self.assertEqual(self.success_tool.get_status(), ToolStatus.IDLE)
        self.assertIsNone(self.success_tool.get_last_result())

    def test_successful_execution(self):
        """测试成功执行"""
        result = self.success_tool.execute("test_action", {"param1": "value1"})

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Mock test_action executed successfully")
        self.assertEqual(result.data["action"], "test_action")
        self.assertEqual(result.data["parameters"]["param1"], "value1")
        self.assertIsNotNone(result.execution_time)
        self.assertEqual(self.success_tool.get_status(), ToolStatus.COMPLETED)

    def test_failing_execution(self):
        """测试执行失败"""
        result = self.failing_tool.execute("test_action", {})

        self.assertFalse(result.success)
        self.assertEqual(result.message, "Mock execution failed")
        self.assertEqual(self.failing_tool.get_status(), ToolStatus.FAILED)

    def test_unsupported_action(self):
        """测试不支持的动作"""
        result = self.success_tool.execute("unsupported_action", {})

        self.assertFalse(result.success)
        self.assertIn("不支持动作", result.message)
        self.assertEqual(self.success_tool.get_status(), ToolStatus.FAILED)

    def test_validation_failure(self):
        """测试参数验证失败"""
        result = self.validation_tool.execute("test_action", {})

        self.assertFalse(result.success)
        self.assertIn("参数验证失败", result.message)
        self.assertEqual(self.validation_tool.get_status(), ToolStatus.FAILED)

    def test_parameter_defaults(self):
        """测试参数默认值"""
        result = self.success_tool.execute("test_action")

        self.assertTrue(result.success)
        self.assertEqual(result.data["parameters"], {})

    def test_context_defaults(self):
        """测试上下文默认值"""
        result = self.success_tool.execute("test_action", {})

        self.assertTrue(result.success)
        # 工具应该能够处理空的上下文

    def test_execution_exception(self):
        """测试执行异常"""
        class ExceptionTool(BaseTool):
            @property
            def name(self) -> str:
                return "exception_tool"

            @property
            def description(self) -> str:
                return "Tool that throws exceptions"

            @property
            def supported_actions(self) -> list:
                return ["exception_action"]

            @property
            def required_permissions(self) -> list:
                return []

            def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
                return True

            def execute_action(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
                raise ValueError("Test exception")

        exception_tool = ExceptionTool()
        result = exception_tool.execute("exception_action", {})

        self.assertFalse(result.success)
        self.assertIn("发生异常", result.message)
        self.assertIn("Test exception", result.error_details)
        self.assertEqual(exception_tool.get_status(), ToolStatus.FAILED)

    def test_reset_status(self):
        """测试重置状态"""
        # 执行一个操作
        self.success_tool.execute("test_action", {})
        self.assertEqual(self.success_tool.get_status(), ToolStatus.COMPLETED)

        # 重置状态
        self.success_tool.reset_status()
        self.assertEqual(self.success_tool.get_status(), ToolStatus.IDLE)
        self.assertIsNone(self.success_tool.get_last_result())

    def test_get_capabilities(self):
        """测试获取工具能力"""
        capabilities = self.success_tool.get_capabilities()

        self.assertEqual(capabilities["name"], "mock_tool")
        self.assertEqual(capabilities["description"], "Mock tool for testing")
        self.assertEqual(capabilities["supported_actions"], ["test_action", "failing_action"])
        self.assertEqual(capabilities["required_permissions"], ["test_permission"])
        self.assertEqual(capabilities["status"], ToolStatus.IDLE.value)

    def test_validate_parameters_base(self):
        """测试基础参数验证"""
        # 测试必需参数
        result = self.success_tool.validate_parameters_base(
            "test_action", {"required": "value"},
            required_params=["required"], optional_params=["optional"]
        )
        self.assertTrue(result)

        # 测试缺少必需参数
        result = self.success_tool.validate_parameters_base(
            "test_action", {"optional": "value"},
            required_params=["required"], optional_params=["optional"]
        )
        self.assertFalse(result)

        # 测试非字典参数
        result = self.success_tool.validate_parameters_base(
            "test_action", "not_a_dict",
            required_params=[], optional_params=[]
        )
        self.assertFalse(result)

    def test_tool_str_representation(self):
        """测试工具字符串表示"""
        str_repr = str(self.success_tool)
        self.assertIn("MockTool", str_repr)
        self.assertIn("mock_tool", str_repr)
        self.assertIn("idle", str_repr)

    def test_tool_result_to_dict(self):
        """测试ToolResult转换为字典"""
        result = ToolResult(
            success=True,
            message="Test message",
            data={"key": "value"},
            context_update={"ctx": "update"},
            execution_time=1.5
        )

        result_dict = result.to_dict()

        self.assertTrue(result_dict["success"])
        self.assertEqual(result_dict["message"], "Test message")
        self.assertEqual(result_dict["data"], {"key": "value"})
        self.assertEqual(result_dict["context_update"], {"ctx": "update"})
        self.assertEqual(result_dict["execution_time"], 1.5)


if __name__ == '__main__':
    # 配置日志以避免测试输出混乱
    logging.basicConfig(level=logging.CRITICAL)

    unittest.main(verbosity=2)