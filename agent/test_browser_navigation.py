#!/usr/bin/env python3
"""
测试浏览器导航手势的快捷键执行
验证Ctrl+PgUp/PgDn是否能正确工作
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from actions.executor import execute_action

def test_browser_shortcuts():
    """测试浏览器导航快捷键"""
    print("测试浏览器导航快捷键...")
    print("=" * 50)
    print("请在打开的Chrome浏览器中进行测试")
    print("准备打开几个标签页以便测试切换功能")
    print()

    print("5秒后开始测试，请准备好...")
    # 等待用户准备
    time.sleep(5)

    test_shortcuts = [
        ('hotkey', 'ctrl+t', '新建标签页'),
        ('hotkey', 'ctrl+t', '再新建一个标签页'),
        ('hotkey', 'ctrl+t', '再新建一个标签页（共3个）'),
        ('hotkey', 'ctrl+pgup', '标签页左切换'),
        ('hotkey', 'ctrl+pgdn', '标签页右切换'),
        ('hotkey', 'ctrl+pgup', '再次左切换'),
        ('hotkey', 'ctrl+w', '关闭当前标签页'),
        ('hotkey', 'ctrl+w', '关闭当前标签页'),
    ]

    print("开始执行快捷键测试...")
    print("请注意浏览器标签页的变化")
    print("-" * 50)

    for i, (action_type, action_value, description) in enumerate(test_shortcuts, 1):
        print(f"{i:2}. {description} ({action_value})")

        try:
            success, message = execute_action(action_type, action_value)
            if success:
                print(f"    [SUCCESS] 成功: {message}")
            else:
                print(f"    [FAIL] 失败: {message}")
        except Exception as e:
            print(f"    [ERROR] 错误: {e}")

        time.sleep(2)  # 给用户时间观察效果

    print("-" * 50)
    print("快捷键测试完成！")
    print("如果标签页切换正常工作，说明手势映射配置正确")

def test_gesture_integration():
    """测试手势集成"""
    print("\n测试手势集成...")
    print("=" * 50)

    try:
        from standalone_gesture_controller import StandaloneGestureController
        controller = StandaloneGestureController()

        print("当前手势映射配置:")
        for gesture, mapping in controller.gesture_mappings.items():
            if 'swipe' in gesture.lower() or gesture in ['VICTORY', 'CLOSED_FIST']:
                print(f"  {gesture:15} -> {mapping['value']:15} : {mapping['description']}")

        print("\n建议测试流程:")
        print("1. 打开Chrome浏览器")
        print("2. 打开多个标签页")
        print("3. 启动手势控制: python standalone_gesture_controller.py")
        print("4. 测试左滑/右滑手势切换标签页")
        print("5. 测试V手势新建标签页")
        print("6. 测试握拳关闭标签页")

    except Exception as e:
        print(f"错误: {e}")

def main():
    print("YOLO-LLM 浏览器导航测试")
    print("=" * 50)

    test_browser_shortcuts()
    test_gesture_integration()

    print(f"\n{'=' * 50}")
    print("测试完成！")
    print("如果快捷键测试成功，现在可以启动手势控制器:")
    print("python standalone_gesture_controller.py")

if __name__ == "__main__":
    main()