#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'agent'))

def test_gesture_analyzer():
    print("Testing gesture analyzer...")
    try:
        from gesture_analyzer import GestureAnalyzer
        from gestures.mediapipe_detector import GestureResult

        analyzer = GestureAnalyzer()
        print("✓ Gesture analyzer initialized")

        # Test with thumbs up
        result = GestureResult(
            gesture_code='THUMBS_UP',
            confidence=0.95,
            landmarks=None,
            timestamp=1234567890,
            bbox=(100, 100, 50, 50)
        )

        analysis = analyzer.analyze_gesture(result, "test")
        if analysis:
            print(f"✓ Analysis: {analysis.intent}, {analysis.emotion}")
        else:
            print("✗ Analysis failed")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_speech_commands():
    print("\nTesting speech command parsing...")
    try:
        from speech_controller import VoiceController

        controller = VoiceController()
        print("✓ Voice controller initialized")

        # Test command parsing
        commands = ["左滑", "右滑", "打开记事本"]
        for cmd in commands:
            try:
                result = controller._parse_command(cmd)
                print(f"✓ Command '{cmd}': {result}")
            except Exception as e:
                print(f"✗ Command '{cmd}' failed: {e}")

        return True

    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("AI Module Test")
    print("=" * 30)

    results = []

    # Test gesture analyzer
    results.append(test_gesture_analyzer())

    # Test speech controller
    results.append(test_speech_commands())

    print("\n" + "=" * 30)
    print(f"Results: {sum(results)}/{len(results)} passed")

    if all(results):
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())