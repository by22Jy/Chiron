"""
ToolRegistry单元测试

测试ToolRegistry工具注册表的功能
"""

import unittest
import threading
import time
from unittest.mock import Mock

from base_tool import BaseTool, ToolResult, ToolStatus
from tool_registry import ToolRegistry, ToolRegistration
from test_base_tool import MockTool


class TestToolRegistration(unittest.TestCase):
    """ToolRegistration测试类"""

    def test_tool_registration_creation(self):
        """测试ToolRegistration创建"""
        tool = MockTool()
        registration = ToolRegistration(
            tool=tool,
            registered_at=time.time(),
            enabled=True,
            metadata={"version": "1.0"}
        )

        self.assertEqual(registration.tool, tool)
        self.assertTrue(registration.enabled)
        self.assertEqual(registration.metadata["version"], "1.0")


class TestToolRegistry(unittest.TestCase):
    """ToolRegistry测试类"""

    def setUp(self):
        """测试前准备"""
        # 清空单例实例
        if hasattr(ToolRegistry, '_instance'):
            ToolRegistry._instance = None
        if hasattr(ToolRegistry, '_lock'):
            ToolRegistry._lock = threading.Lock()

        self.registry = ToolRegistry()
        self.tool1 = MockTool()
        self.tool2 = MockTool(should_fail=True)

    def tearDown(self):
        """测试后清理"""
        self.registry.clear_registry()

    def test_singleton_pattern(self):
        """测试单例模式"""
        registry1 = ToolRegistry()
        registry2 = ToolRegistry()
        self.assertIs(registry1, registry2)

    def test_register_tool(self):
        """测试工具注册"""
        result = self.registry.register_tool(self.tool1)

        self.assertTrue(result)
        self.assertIn(self.tool1.name, self.registry._tools)
        self.assertEqual(self.registry._tools[self.tool1.name].tool, self.tool1)

    def test_register_tool_validation(self):
        """测试工具注册验证"""
        # 测试非BaseTool类型
        result = self.registry.register_tool("not_a_tool")
        self.assertFalse(result)

        # 测试空名称工具
        class EmptyNameTool(BaseTool):
            @property
            def name(self) -> str:
                return ""

            @property
            def description(self) -> str:
                return "Empty name tool"

            @property
            def supported_actions(self) -> list:
                return []

            @property
            def required_permissions(self) -> list:
                return []

            def validate_parameters(self, action: str, parameters) -> bool:
                return True

            def execute_action(self, action: str, parameters, context) -> ToolResult:
                return ToolResult(success=True, message="OK")

        empty_tool = EmptyNameTool()
        result = self.registry.register_tool(empty_tool)
        self.assertFalse(result)

    def test_register_duplicate_tool(self):
        """测试重复注册工具"""
        # 注册第一个工具
        result1 = self.registry.register_tool(self.tool1)
        self.assertTrue(result1)

        # 注册同名工具（应该覆盖）
        result2 = self.registry.register_tool(self.tool2)
        self.assertTrue(result2)

        # 验证被覆盖
        self.assertEqual(self.registry._tools[self.tool1.name].tool, self.tool2)

    def test_unregister_tool(self):
        """测试工具注销"""
        # 先注册
        self.registry.register_tool(self.tool1)
        self.assertIn(self.tool1.name, self.registry._tools)

        # 注销
        result = self.registry.unregister_tool(self.tool1.name)
        self.assertTrue(result)
        self.assertNotIn(self.tool1.name, self.registry._tools)

    def test_unregister_nonexistent_tool(self):
        """测试注销不存在的工具"""
        result = self.registry.unregister_tool("nonexistent_tool")
        self.assertFalse(result)

    def test_get_tool(self):
        """测试获取工具"""
        # 注册工具
        self.registry.register_tool(self.tool1)

        # 获取工具
        tool = self.registry.get_tool(self.tool1.name)
        self.assertEqual(tool, self.tool1)

        # 获取不存在的工具
        tool = self.registry.get_tool("nonexistent_tool")
        self.assertIsNone(tool)

    def test_get_disabled_tool(self):
        """测试获取已禁用的工具"""
        self.registry.register_tool(self.tool1, enabled=False)
        tool = self.registry.get_tool(self.tool1.name)
        self.assertIsNone(tool)

    def test_list_tools(self):
        """测试列出工具"""
        # 注册工具
        self.registry.register_tool(self.tool1, enabled=True)
        self.registry.register_tool(self.tool2, enabled=False)

        # 只列出启用的工具
        enabled_tools = self.registry.list_tools()
        self.assertIn(self.tool1.name, enabled_tools)
        self.assertNotIn(self.tool2.name, enabled_tools)

        # 列出所有工具
        all_tools = self.registry.list_tools(include_disabled=True)
        self.assertIn(self.tool1.name, all_tools)
        self.assertIn(self.tool2.name, all_tools)

    def test_execute_tool(self):
        """测试执行工具"""
        self.registry.register_tool(self.tool1)

        result = self.registry.execute_tool(
            self.tool1.name,
            "test_action",
            {"param": "value"}
        )

        self.assertTrue(result.success)
        self.assertEqual(result.message, "Mock test_action executed successfully")

    def test_execute_nonexistent_tool(self):
        """测试执行不存在的工具"""
        result = self.registry.execute_tool("nonexistent_tool", "action", {})
        self.assertFalse(result.success)
        self.assertIn("不存在或已禁用", result.message)

    def test_execute_disabled_tool(self):
        """测试执行已禁用的工具"""
        self.registry.register_tool(self.tool1, enabled=False)

        result = self.registry.execute_tool(self.tool1.name, "test_action", {})
        self.assertFalse(result.success)
        self.assertIn("不存在或已禁用", result.message)

    def test_enable_disable_tool(self):
        """测试启用/禁用工具"""
        # 注册工具
        self.registry.register_tool(self.tool1)

        # 禁用工具
        result = self.registry.disable_tool(self.tool1.name)
        self.assertTrue(result)
        self.assertFalse(self.registry._tools[self.tool1.name].enabled)

        # 获取已禁用的工具
        tool = self.registry.get_tool(self.tool1.name)
        self.assertIsNone(tool)

        # 重新启用工具
        result = self.registry.enable_tool(self.tool1.name)
        self.assertTrue(result)
        self.assertTrue(self.registry._tools[self.tool1.name].enabled)

        # 获取已启用的工具
        tool = self.registry.get_tool(self.tool1.name)
        self.assertEqual(tool, self.tool1)

    def test_get_tool_capabilities(self):
        """测试获取工具能力"""
        self.registry.register_tool(self.tool1)

        capabilities = self.registry.get_tool_capabilities(self.tool1.name)

        self.assertIsNotNone(capabilities)
        self.assertEqual(capabilities["name"], "mock_tool")
        self.assertEqual(capabilities["supported_actions"], ["test_action", "failing_action"])

    def test_get_all_capabilities(self):
        """测试获取所有工具能力"""
        self.registry.register_tool(self.tool1)
        self.registry.register_tool(self.tool2)

        all_capabilities = self.registry.get_all_capabilities()

        self.assertIn(self.tool1.name, all_capabilities)
        self.assertIn(self.tool2.name, all_capabilities)

    def test_get_tool_status(self):
        """测试获取工具状态"""
        self.registry.register_tool(self.tool1)

        # 测试启用状态
        status = self.registry.get_tool_status(self.tool1.name)
        self.assertEqual(status, "idle")

        # 禁用工具
        self.registry.disable_tool(self.tool1.name)
        status = self.registry.get_tool_status(self.tool1.name)
        self.assertEqual(status, "disabled")

    def test_get_registry_info(self):
        """测试获取注册表信息"""
        # 注册工具
        self.registry.register_tool(self.tool1, enabled=True)
        self.registry.register_tool(self.tool2, enabled=False)

        info = self.registry.get_registry_info()

        self.assertEqual(info["total_tools"], 2)
        self.assertEqual(info["enabled_tools"], 1)
        self.assertEqual(info["disabled_tools"], 1)
        self.assertIn(self.tool1.name, info["tool_names"])
        self.assertIn(self.tool2.name, info["disabled_tool_names"])

    def test_clear_registry(self):
        """测试清空注册表"""
        # 注册工具
        self.registry.register_tool(self.tool1)
        self.registry.register_tool(self.tool2)

        # 清空注册表
        self.registry.clear_registry()

        self.assertEqual(len(self.registry._tools), 0)
        self.assertEqual(self.registry.get_registry_info()["total_tools"], 0)

    def test_reset_all_tools(self):
        """测试重置所有工具状态"""
        # 注册工具
        self.registry.register_tool(self.tool1)

        # 执行工具以改变状态
        self.registry.execute_tool(self.tool1.name, "test_action", {})

        # 验证状态改变
        self.assertEqual(self.tool1.get_status(), ToolStatus.COMPLETED)

        # 重置所有工具
        self.registry.reset_all_tools()

        # 验证状态重置
        self.assertEqual(self.tool1.get_status(), ToolStatus.IDLE)

    def test_thread_safety(self):
        """测试线程安全性"""
        results = []
        errors = []

        def register_tool(tool_id):
            try:
                tool = MockTool()
                # 修改工具名称使其唯一
                tool._name = f"tool_{tool_id}"
                result = self.registry.register_tool(tool)
                results.append(result)
            except Exception as e:
                errors.append(e)

        # 创建多个线程同时注册工具
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_tool, args=(i,))
            threads.append(thread)

        # 启动所有线程
        for thread in threads:
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证没有错误
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results))

    def test_magic_methods(self):
        """测试魔法方法"""
        self.registry.register_tool(self.tool1)

        # 测试__len__
        self.assertEqual(len(self.registry), 1)

        # 测试__contains__
        self.assertIn(self.tool1.name, self.registry)
        self.assertNotIn("nonexistent_tool", self.registry)

        # 测试__str__
        str_repr = str(self.registry)
        self.assertIn("ToolRegistry", str_repr)
        self.assertIn("total=1", str_repr)
        self.assertIn("enabled=1", str_repr)

    def test_execute_tool_exception_handling(self):
        """测试执行工具时的异常处理"""
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

            def validate_parameters(self, action: str, parameters) -> bool:
                return True

            def execute_action(self, action: str, parameters, context) -> ToolResult:
                raise ValueError("Test exception in tool execution")

        exception_tool = ExceptionTool()
        self.registry.register_tool(exception_tool)

        result = self.registry.execute_tool(exception_tool.name, "exception_action", {})

        self.assertFalse(result.success)
        self.assertIn("发生异常", result.message)


if __name__ == '__main__':
    # 配置日志以避免测试输出混乱
    import logging
    logging.basicConfig(level=logging.CRITICAL)

    unittest.main(verbosity=2)