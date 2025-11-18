#!/usr/bin/env python3
"""
测试Windows浏览器快捷键是否有效
尝试不同的快捷键组合
"""

import sys
import time
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from actions.executor import execute_action

def test_browser_hotkeys():
    """测试不同的浏览器快捷键"""
    print("测试Windows浏览器快捷键...")
    print("=" * 50)
    print("请在Chrome浏览器中打开多个标签页")
    print("我们将测试不同的快捷键组合")
    print()

    test_hotkeys = [
        # 常见的标签页切换快捷键
        ('hotkey', 'ctrl+pgup', 'PageUp方式标签页左切换'),
        ('hotkey', 'ctrl+pgdn', 'PageDown方式标签页右切换'),
        ('hotkey', 'ctrl+tab', 'Tab方式标签页切换'),
        ('hotkey', 'ctrl+1', '数字键切换到第1个标签页'),
        ('hotkey', 'ctrl+9', '数字键切换到最后一个标签页'),
        ('hotkey', 'ctrl+shift+tab', '反向Tab切换'),
        ('hotkey', 'ctrl+w', '关闭标签页'),
        ('hotkey', 'ctrl+t', '新建标签页'),
    ]

    print("开始测试快捷键...")
    print("-" * 50)

    for i, (action_type, action_value, description) in enumerate(test_hotkeys, 1):
        print(f"{i:2}. 测试: {description}")
        print(f"    快捷键: {action_value}")

        print("    3秒后执行，请观察浏览器...")
        time.sleep(3)

        try:
            success, message = execute_action(action_type, action_value)
            print(f"    结果: {'✓ 成功' if success else '✗ 失败'} - {message}")
        except Exception as e:
            print(f"    错误: {e}")

        print("    等待2秒...")
        time.sleep(2)
        print()

    print("-" * 50)
    print("快捷键测试完成！")

def test_alternative_hotkeys():
    """测试替代快捷键"""
    print("测试替代快捷键组合...")
    print("=" * 50)

    alternative_hotkeys = [
        # 一些可能有效的替代方案
        ('hotkey', 'ctrl+pagedown', 'PageDown全小写'),
        ('hotkey', 'ctrl+pageup', 'PageUp全小写'),
        ('hotkey', 'ctrl+pagedown', 'PageDown全小写'),
        ('hotkey', 'ctrl+home', 'Home键'),
        ('hotkey', 'ctrl+end', 'End键'),
    ]

    for i, (action_type, action_value, description) in enumerate(alternative_hotkeys, 1):
        print(f"{i}. {description}: {action_value}")

        print("   3秒后执行...")
        time.sleep(3)

        try:
            success, message = execute_action(action_type, action_value)
            print(f"   结果: {'✓ 成功' if success else '✗ 失败'} - {message}")
        except Exception as e:
            print(f"   错误: {e}")

        time.sleep(2)

if __name__ == "__main__":
    print("Windows浏览器快捷键测试工具")
    print("=" * 50)
    print("确保Chrome浏览器已打开并有多个标签页")
    print()

    test_browser_hotkeys()
    test_alternative_hotkeys()

    print("\n" + "=" * 50)
    print("测试完成！")
    print("请观察哪些快捷键能正常工作")
    print("然后将有效的快捷键更新到手势映射中")