#!/usr/bin/env python3
"""
调试手势映射问题
检查映射是否正确设置和匹配
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def debug_mapping():
    """调试映射问题"""
    print("调试手势映射问题...")
    print("=" * 50)

    # 1. 检查独立控制器的映射
    try:
        from standalone_gesture_controller import StandaloneGestureController
        controller = StandaloneGestureController()

        print("1. 独立控制器手势映射:")
        for gesture, mapping in controller.gesture_mappings.items():
            print(f"   {gesture:15} -> {mapping['value']:15} : {mapping['description']}")

        print(f"\n映射总数: {len(controller.gesture_mappings)}")

    except Exception as e:
        print(f"独立控制器错误: {e}")

    # 2. 检查MediaPipe检测器输出
    try:
        from gestures.mediapipe_detector import MediaPipeGestureDetector

        print("\n2. MediaPipe手势检测器测试:")
        detector = MediaPipeGestureDetector()

        # 模拟测试
        test_landmarks = [(0.5, 0.5, 0)] * 21  # 简单的landmarks
        gesture_code, confidence = detector._recognize_gesture(test_landmarks)

        print(f"   测试手势识别: {gesture_code} (置信度: {confidence})")

    except Exception as e:
        print(f"MediaPipe检测器错误: {e}")

    # 3. 检查VideoProcessor的映射接收
    try:
        from video_processor import VideoProcessor, VideoConfig
        from standalone_gesture_controller import StandaloneGestureController

        print("\n3. VideoProcessor映射测试:")
        controller = StandaloneGestureController()
        video_config = VideoConfig()

        processor = VideoProcessor(config=video_config, gesture_mapping=controller.gesture_mappings)

        print(f"   VideoProcessor接收的映射数: {len(processor.gesture_mapping)}")
        print(f"   映射键: {list(processor.gesture_mapping.keys())}")

        # 检查映射格式
        for gesture, mapping in processor.gesture_mapping.items():
            print(f"   {gesture}: type={mapping.get('type')}, value={mapping.get('value')}")

    except Exception as e:
        print(f"VideoProcessor错误: {e}")
        import traceback
        traceback.print_exc()

    # 4. 测试快捷键执行
    try:
        print("\n4. 快捷键执行测试:")
        from actions.executor import execute_action

        test_hotkeys = [
            ('hotkey', 'ctrl+pgup', 'PageUp'),
            ('hotkey', 'ctrl+pgdn', 'PageDown'),
            ('hotkey', 'ctrl+tab', 'Tab切换'),
        ]

        for action_type, action_value, desc in test_hotkeys:
            print(f"   测试 {desc} ({action_value})...")
            success, message = execute_action(action_type, action_value)
            print(f"   结果: {'[SUCCESS]' if success else '[FAIL]'} - {message}")

    except Exception as e:
        print(f"快捷键测试错误: {e}")

def main():
    debug_mapping()

if __name__ == "__main__":
    main()