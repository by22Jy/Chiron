"""
Agent工具系统自测脚本

测试整个工具系统的集成功能，包括：
- 工具注册和发现
- 工具执行
- 错误处理
- 并发安全
"""

import sys
import time
import threading
import logging
from typing import Dict, Any

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 导入工具系统
try:
    from tools import BaseTool, ToolResult, ToolRegistry, register_core_tools
    from tools.system_tool import SystemTool
    from tools.file_tool import FileTool
    from tools.input_tool import InputTool
except ImportError as e:
    logger.error(f"导入工具系统失败: {e}")
    sys.exit(1)


class TestSuite:
    """测试套件"""

    def __init__(self):
        self.registry = ToolRegistry()
        self.test_results = []

    def run_test(self, test_name: str, test_func):
        """运行单个测试"""
        logger.info(f"运行测试: {test_name}")
        try:
            result = test_func()
            if result:
                logger.info(f"✅ {test_name} - 通过")
                self.test_results.append((test_name, "PASS", ""))
            else:
                logger.error(f"❌ {test_name} - 失败")
                self.test_results.append((test_name, "FAIL", "测试返回False"))
        except Exception as e:
            logger.error(f"❌ {test_name} - 异常: {e}")
            self.test_results.append((test_name, "ERROR", str(e)))

    def test_core_tools_registration(self):
        """测试核心工具注册"""
        # 注册核心工具
        registry = register_core_tools()

        # 检查工具是否注册成功
        tools = registry.list_tools()
        expected_tools = ["system", "file", "input"]

        for tool_name in expected_tools:
            if tool_name not in tools:
                logger.error(f"核心工具 {tool_name} 未注册")
                return False

        logger.info(f"已注册工具: {tools}")
        return True

    def test_system_tool_functionality(self):
        """测试系统工具功能"""
        system_tool = SystemTool()
        self.registry.register_tool(system_tool)

        # 测试获取屏幕尺寸（安全的操作）
        result = self.registry.execute_tool("system", "get_screen_size", {})

        if not result.success:
            logger.error(f"获取屏幕尺寸失败: {result.message}")
            return False

        logger.info(f"屏幕尺寸: {result.data}")

        # 测试截图功能
        result = self.registry.execute_tool(
            "system", "screenshot",
            {"filename": "test_screenshot.png"}
        )

        if not result.success:
            logger.error(f"截图失败: {result.message}")
            return False

        logger.info(f"截图成功: {result.data['filepath']}")
        return True

    def test_file_tool_functionality(self):
        """测试文件工具功能"""
        file_tool = FileTool()
        self.registry.register_tool(file_tool)

        # 测试创建文件
        test_content = "这是测试文件内容\n测试Agent工具系统"
        result = self.registry.execute_tool(
            "file", "write_file",
            {
                "filepath": "test_output.txt",
                "content": test_content
            }
        )

        if not result.success:
            logger.error(f"创建文件失败: {result.message}")
            return False

        # 测试读取文件
        result = self.registry.execute_tool(
            "file", "read_file",
            {"filepath": "test_output.txt"}
        )

        if not result.success:
            logger.error(f"读取文件失败: {result.message}")
            return False

        if result.data["content"] != test_content:
            logger.error("文件内容不匹配")
            return False

        # 测试文件信息
        result = self.registry.execute_tool(
            "file", "get_file_info",
            {"filepath": "test_output.txt"}
        )

        if not result.success:
            logger.error(f"获取文件信息失败: {result.message}")
            return False

        logger.info(f"文件信息: 大小={result.data['size']} bytes")
        return True

    def test_input_tool_functionality(self):
        """测试输入工具功能"""
        input_tool = InputTool()
        self.registry.register_tool(input_tool)

        # 测试获取鼠标位置（安全操作）
        result = self.registry.execute_tool("input", "get_mouse_position", {})

        if not result.success:
            logger.error(f"获取鼠标位置失败: {result.message}")
            return False

        logger.info(f"鼠标位置: {result.data}")

        # 测试获取屏幕尺寸
        result = self.registry.execute_tool("input", "get_screen_size", {})

        if not result.success:
            logger.error(f"获取屏幕尺寸失败: {result.message}")
            return False

        logger.info(f"屏幕尺寸: {result.data}")
        return True

    def test_error_handling(self):
        """测试错误处理"""
        file_tool = FileTool()
        self.registry.register_tool(file_tool)

        # 测试执行不存在的动作
        result = self.registry.execute_tool("file", "nonexistent_action", {})

        if result.success:
            logger.error("不存在的动作不应该成功")
            return False

        # 测试执行不存在的工具
        result = self.registry.execute_tool("nonexistent_tool", "action", {})

        if result.success:
            logger.error("不存在的工具不应该成功")
            return False

        # 测试参数验证失败
        result = self.registry.execute_tool("file", "read_file", {})

        if result.success:
            logger.error("缺少必需参数不应该成功")
            return False

        logger.info("错误处理测试通过")
        return True

    def test_tool_capabilities(self):
        """测试工具能力获取"""
        # 注册所有核心工具
        register_core_tools()

        # 获取所有工具能力
        capabilities = self.registry.get_all_capabilities()

        if not capabilities:
            logger.error("未获取到工具能力")
            return False

        logger.info("工具能力:")
        for tool_name, caps in capabilities.items():
            logger.info(f"  {tool_name}: {caps['description']}")
            logger.info(f"    支持动作: {caps['supported_actions']}")
            logger.info(f"    需要权限: {caps['required_permissions']}")

        return True

    def test_concurrent_execution(self):
        """测试并发执行"""
        input_tool = InputTool()
        self.registry.register_tool(input_tool)

        results = []
        errors = []

        def execute_get_position(thread_id):
            try:
                result = self.registry.execute_tool("input", "get_mouse_position", {})
                results.append((thread_id, result.success))
            except Exception as e:
                errors.append((thread_id, str(e)))

        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=execute_get_position, args=(i,))
            threads.append(thread)

        # 启动所有线程
        start_time = time.time()
        for thread in threads:
            thread.start()

        # 等待完成
        for thread in threads:
            thread.join()

        execution_time = time.time() - start_time

        # 检查结果
        if errors:
            logger.error(f"并发执行中出现错误: {errors}")
            return False

        if len(results) != 5:
            logger.error(f"期望5个结果，实际得到{len(results)}个")
            return False

        if not all(success for _, success in results):
            logger.error("部分并发执行失败")
            return False

        logger.info(f"并发执行测试通过，耗时: {execution_time:.2f}秒")
        return True

    def test_registry_info(self):
        """测试注册表信息"""
        # 注册一些工具
        register_core_tools()

        # 获取注册表信息
        info = self.registry.get_registry_info()

        logger.info("注册表信息:")
        logger.info(f"  总工具数: {info['total_tools']}")
        logger.info(f"  启用工具: {info['enabled_tools']}")
        logger.info(f"  禁用工具: {info['disabled_tools']}")
        logger.info(f"  工具列表: {info['tool_names']}")

        return info["total_tools"] > 0

    def run_all_tests(self):
        """运行所有测试"""
        logger.info("开始Agent工具系统自测")
        logger.info("=" * 50)

        # 定义测试用例
        test_cases = [
            ("核心工具注册", self.test_core_tools_registration),
            ("系统工具功能", self.test_system_tool_functionality),
            ("文件工具功能", self.test_file_tool_functionality),
            ("输入工具功能", self.test_input_tool_functionality),
            ("错误处理", self.test_error_handling),
            ("工具能力获取", self.test_tool_capabilities),
            ("并发执行", self.test_concurrent_execution),
            ("注册表信息", self.test_registry_info),
        ]

        # 运行所有测试
        for test_name, test_func in test_cases:
            self.run_test(test_name, test_func)

        # 输出测试结果汇总
        logger.info("=" * 50)
        logger.info("测试结果汇总:")

        passed = 0
        failed = 0
        errors = 0

        for test_name, status, error in self.test_results:
            status_icon = "✅" if status == "PASS" else "❌"
            logger.info(f"{status_icon} {test_name}: {status}")
            if status != "PASS":
                logger.info(f"   错误: {error}")

            if status == "PASS":
                passed += 1
            elif status == "FAIL":
                failed += 1
            else:
                errors += 1

        logger.info("=" * 50)
        logger.info(f"总计: {len(self.test_results)} 个测试")
        logger.info(f"通过: {passed}")
        logger.info(f"失败: {failed}")
        logger.info(f"错误: {errors}")

        success_rate = (passed / len(self.test_results)) * 100
        logger.info(f"成功率: {success_rate:.1f}%")

        return success_rate >= 80  # 80%以上成功率视为测试通过


def cleanup_test_files():
    """清理测试文件"""
    import os

    test_files = ["test_output.txt", "test_screenshot.png"]
    for file in test_files:
        try:
            if os.path.exists(file):
                os.remove(file)
                logger.info(f"已清理测试文件: {file}")
        except Exception as e:
            logger.warning(f"清理文件 {file} 失败: {e}")


def main():
    """主函数"""
    try:
        # 运行测试套件
        test_suite = TestSuite()
        success = test_suite.run_all_tests()

        # 清理测试文件
        cleanup_test_files()

        # 根据测试结果设置退出码
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试执行异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()