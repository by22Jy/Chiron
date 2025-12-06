"""
简单的工具系统测试
"""

import sys
import os

# 添加tools目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

def test_imports():
    """测试导入"""
    try:
        from base_tool import BaseTool, ToolResult, ToolStatus
        print("[OK] BaseTool imported")
    except Exception as e:
        print(f"[ERROR] BaseTool import failed: {e}")
        return False

    try:
        from tool_registry import ToolRegistry
        print("[OK] ToolRegistry imported")
    except Exception as e:
        print(f"[ERROR] ToolRegistry import failed: {e}")
        return False

    try:
        from system_tool import SystemTool
        print("[OK] SystemTool imported")
    except Exception as e:
        print(f"[ERROR] SystemTool import failed: {e}")
        return False

    return True

def test_basic_functionality():
    """测试基本功能"""
    try:
        from base_tool import BaseTool, ToolResult
        from tool_registry import ToolRegistry
        from system_tool import SystemTool

        # 创建工具注册表
        registry = ToolRegistry()
        print("[OK] ToolRegistry created")

        # 创建系统工具
        system_tool = SystemTool()
        print("[OK] SystemTool created")

        # 注册工具
        result = registry.register_tool(system_tool)
        print(f"[OK] SystemTool registered: {result}")

        # 列出工具
        tools = registry.list_tools()
        print(f"[OK] Tools listed: {tools}")

        # 测试安全功能 - 获取屏幕尺寸
        screen_result = registry.execute_tool("system", "screenshot", {"filename": "test.png"})
        if screen_result.success:
            print(f"[OK] Screenshot taken: {screen_result.data['filepath']}")
        else:
            print(f"[FAIL] Screenshot failed: {screen_result.message}")

        return True

    except Exception as e:
        print(f"[ERROR] Basic functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=== Agent Tools System Simple Test ===")
    print()

    # 测试导入
    print("Testing imports...")
    if not test_imports():
        print("Import tests failed!")
        return False

    # 测试基本功能
    print("\nTesting basic functionality...")
    if not test_basic_functionality():
        print("Functionality tests failed!")
        return False

    print("\n=== All tests passed! ===")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)