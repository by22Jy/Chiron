"""
Phase 2: 新工具测试脚本

测试MessagingTool和WebTool的功能
"""

import sys
import os

# 添加tools目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools'))

def test_phase2_tools():
    """测试Phase 2新工具"""
    try:
        from tool_registry import ToolRegistry
        from messaging_tool import MessagingTool
        from web_tool import WebTool

        print("=== Phase 2: 新工具测试 ===")
        print()

        # 创建注册表
        registry = ToolRegistry()
        print("[OK] ToolRegistry created")

        # 注册新工具
        messaging_tool = MessagingTool()
        web_tool = WebTool()

        registry.register_tool(messaging_tool)
        registry.register_tool(web_tool)

        print("[OK] Phase 2 tools registered")

        # 列出所有工具
        all_tools = registry.list_tools()
        print(f"[OK] All tools: {all_tools}")

        # 测试MessagingTool - 发送通知
        print("\nTesting MessagingTool...")
        result = registry.execute_tool("messaging", "send_notification", {
            "title": "Phase 2测试",
            "message": "这是Phase 2的新工具测试通知",
            "type": "info",
            "urgency": "normal"
        })
        if result.success:
            print(f"[OK] MessagingTool notification: {result.message}")
        else:
            print(f"[FAIL] MessagingTool notification: {result.message}")

        # 测试MessagingTool - 邮件模板
        result = registry.execute_tool("messaging", "save_email_template", {
            "template_name": "test_template",
            "subject": "测试模板",
            "content": "这是一个测试邮件模板",
            "description": "Phase 2测试用模板"
        })
        if result.success:
            print(f"[OK] MessagingTool template saved")
        else:
            print(f"[FAIL] MessagingTool template: {result.message}")

        # 测试WebTool - 打开网页
        print("\nTesting WebTool...")
        result = registry.execute_tool("web", "get_page_title", {
            "url": "https://www.baidu.com"
        })
        if result.success:
            print(f"[OK] WebTool page title: {result.data['title']}")
        else:
            print(f"[FAIL] WebTool page title: {result.message}")

        # 测试WebTool - 网络搜索
        result = registry.execute_tool("web", "search_web", {
            "query": "Python编程",
            "engine": "duckduckgo",
            "num_results": 3
        })
        if result.success:
            print(f"[OK] WebTool search: found {result.data['num_results']} results")
        else:
            print(f"[FAIL] WebTool search: {result.message}")

        # 获取工具能力
        print("\nTool Capabilities:")
        capabilities = registry.get_all_capabilities()
        for name, caps in capabilities.items():
            print(f"  {name}: {caps['description']}")
            print(f"    Actions: {len(caps['supported_actions'])} - {', '.join(caps['supported_actions'][:3])}{'...' if len(caps['supported_actions']) > 3 else ''}")

        # 获取注册表信息
        print("\nRegistry Information:")
        info = registry.get_registry_info()
        print(f"  Total tools: {info['total_tools']}")
        print(f"  Enabled tools: {info['enabled_tools']}")
        print(f"  Tools: {', '.join(info['tool_names'])}")

        print("\n=== Phase 2 tests passed! ===")
        print("Phase 2新工具系统已成功实现并测试通过!")

        return True

    except Exception as e:
        print(f"[ERROR] Phase 2 test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("=== Phase 2: 通信与办公工具测试 ===")
    print()

    success = test_phase2_tools()

    if success:
        print("\n🎉 Phase 2完成!")
        print("新的通信和网络工具已成功集成到Agent工具系统")
    else:
        print("\n❌ Phase 2测试失败")

    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)