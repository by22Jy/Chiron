#!/usr/bin/env python3
"""
测试独立手势控制器的基本功能
"""

import sys
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))

from standalone_gesture_controller import StandaloneGestureController

def test_controller():
    """测试控制器基本功能"""
    print("TEST: 测试独立手势控制器基本功能")
    print("=" * 50)

    controller = StandaloneGestureController()

    # 测试手势映射
    print("\n[TEST] 测试手势映射...")
    test_gestures = ['POINT_UP', 'THUMBS_UP', 'SWIPE_LEFT', 'SWIPE_RIGHT']

    for gesture in test_gestures:
        mapping = controller.gesture_mappings.get(gesture)
        if mapping:
            print(f"  {gesture}: {mapping['action_type']} -> {mapping['description']}")
        else:
            print(f"  {gesture}: 未找到映射")

    # 显示可用手势
    print("\n[INFO] 显示可用手势列表:")
    controller.list_available_gestures()

    print("\n[SUCCESS] 独立手势控制器测试完成!")
    print("现在可以使用以下命令启动实时控制:")
    print("python standalone_gesture_controller.py")

if __name__ == "__main__":
    test_controller()