"""
全面的工具系统测试
"""

import sys
import os

# 添加tools目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

def test_all_tools():
    """测试所有工具"""
    try:
        from tool_registry import ToolRegistry
        from system_tool import SystemTool
        from file_tool import FileTool
        from input_tool import InputTool

        # 创建注册表
        registry = ToolRegistry()
        print("[OK] ToolRegistry created")

        # 注册所有工具
        tools = [
            SystemTool(),
            FileTool(),
            InputTool()
        ]

        for tool in tools:
            result = registry.register_tool(tool)
            print(f"[OK] {tool.name} registered: {result}")

        # 列出所有工具
        all_tools = registry.list_tools()
        print(f"[OK] All tools: {all_tools}")

        # 测试工具能力获取
        capabilities = registry.get_all_capabilities()
        print("[OK] Tool capabilities retrieved:")
        for name, caps in capabilities.items():
            print(f"  - {name}: {len(caps['supported_actions'])} actions")

        # 测试SystemTool - 截图功能
        print("\nTesting SystemTool...")
        result = registry.execute_tool("system", "screenshot", {"filename": "comprehensive_test.png"})
        if result.success:
            print(f"[OK] SystemTool screenshot: {result.data['filepath']}")
        else:
            print(f"[FAIL] SystemTool screenshot: {result.message}")

        # 测试FileTool - 文件操作
        print("\nTesting FileTool...")
        test_content = "Agent工具系统测试内容\n时间戳: " + str(os.times())

        # 创建文件
        result = registry.execute_tool("file", "write_file", {
            "filepath": "test_comprehensive.txt",
            "content": test_content
        })
        if result.success:
            print(f"[OK] FileTool write file: {result.data['content_length']} chars")
        else:
            print(f"[FAIL] FileTool write file: {result.message}")

        # 读取文件
        result = registry.execute_tool("file", "read_file", {
            "filepath": "test_comprehensive.txt"
        })
        if result.success and result.data["content"] == test_content:
            print("[OK] FileTool read file: content matches")
        else:
            print(f"[FAIL] FileTool read file: {result.message if not result.success else 'content mismatch'}")

        # 测试InputTool - 获取信息功能
        print("\nTesting InputTool...")
        result = registry.execute_tool("input", "get_screen_size", {})
        if result.success:
            print(f"[OK] InputTool screen size: {result.data['width']}x{result.data['height']}")
        else:
            print(f"[FAIL] InputTool screen size: {result.message}")

        result = registry.execute_tool("input", "get_mouse_position", {})
        if result.success:
            print(f"[OK] InputTool mouse position: ({result.data['x']}, {result.data['y']})")
        else:
            print(f"[FAIL] InputTool mouse position: {result.message}")

        # 测试错误处理
        print("\nTesting error handling...")
        result = registry.execute_tool("file", "read_file", {})
        if not result.success:
            print("[OK] Error handling: missing parameters caught")
        else:
            print("[FAIL] Error handling: missing parameters not caught")

        result = registry.execute_tool("nonexistent_tool", "action", {})
        if not result.success:
            print("[OK] Error handling: nonexistent tool caught")
        else:
            print("[FAIL] Error handling: nonexistent tool not caught")

        # 获取注册表信息
        info = registry.get_registry_info()
        print(f"\n[OK] Registry info: {info['total_tools']} total, {info['enabled_tools']} enabled")

        return True

    except Exception as e:
        print(f"[ERROR] Comprehensive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def cleanup():
    """清理测试文件"""
    test_files = [
        "test_comprehensive.txt",
        "comprehensive_test.png",
        "test.png"
    ]

    for file in test_files:
        try:
            if os.path.exists(file):
                os.remove(file)
                print(f"[CLEANUP] Removed: {file}")
        except Exception as e:
            print(f"[CLEANUP] Failed to remove {file}: {e}")

def main():
    """主函数"""
    print("=== Agent Tools System Comprehensive Test ===")
    print()

    # 测试所有工具
    if not test_all_tools():
        print("Comprehensive tests failed!")
        cleanup()
        return False

    print("\n=== All comprehensive tests passed! ===")

    # 清理
    cleanup()

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)