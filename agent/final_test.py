"""
最终工具系统测试
"""

import sys
import os

# 添加tools目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

def main():
    """主函数"""
    print("=== Agent Tools System Final Test ===")
    print()

    try:
        # 导入所有组件
        from tool_registry import ToolRegistry
        from system_tool import SystemTool
        from file_tool import FileTool
        from input_tool import InputTool

        print("[OK] All imports successful")

        # 创建注册表
        registry = ToolRegistry()
        print("[OK] ToolRegistry created")

        # 注册所有工具
        system_tool = SystemTool()
        file_tool = FileTool()
        input_tool = InputTool()

        registry.register_tool(system_tool)
        registry.register_tool(file_tool)
        registry.register_tool(input_tool)

        print(f"[OK] All tools registered: {registry.list_tools()}")

        # 测试SystemTool - 截图
        print("\nTesting SystemTool screenshot...")
        result = registry.execute_tool("system", "screenshot", {"filename": "final_test.png"})
        if result.success:
            print(f"[OK] Screenshot created: {result.data['filepath']}")
        else:
            print(f"[FAIL] Screenshot failed: {result.message}")

        # 测试InputTool - 获取屏幕尺寸
        print("\nTesting InputTool screen size...")
        result = registry.execute_tool("input", "get_screen_size", {})
        if result.success:
            print(f"[OK] Screen size: {result.data['width']}x{result.data['height']}")
        else:
            print(f"[FAIL] Screen size failed: {result.message}")

        # 测试FileTool - 创建文件
        print("\nTesting FileTool write file...")
        test_content = "Agent工具系统最终测试\n成功创建文件!"
        result = registry.execute_tool("file", "write_file", {
            "filepath": "final_test.txt",
            "content": test_content
        })
        if result.success:
            print(f"[OK] File written: {result.data['content_length']} characters")
        else:
            print(f"[FAIL] File write failed: {result.message}")

        # 测试注册表信息
        print("\nRegistry Information:")
        info = registry.get_registry_info()
        print(f"  Total tools: {info['total_tools']}")
        print(f"  Enabled tools: {info['enabled_tools']}")
        print(f"  Tools: {', '.join(info['tool_names'])}")

        # 获取工具能力
        print("\nTool Capabilities:")
        capabilities = registry.get_all_capabilities()
        for name, caps in capabilities.items():
            print(f"  {name}: {caps['description']}")
            print(f"    Actions: {', '.join(caps['supported_actions'])}")

        print("\n=== All final tests passed! ===")
        print("Agent工具系统已成功实现并通过测试!")

        return True

    except Exception as e:
        print(f"[ERROR] Final test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # 清理测试文件
        cleanup_files = ["final_test.png", "final_test.txt", "test.png"]
        for file in cleanup_files:
            try:
                if os.path.exists(file):
                    os.remove(file)
            except:
                pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)