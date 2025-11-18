#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    print("Testing imports...")
    try:
        from standalone_gesture_controller import StandaloneGestureController
        print("[SUCCESS] StandaloneGestureController import successful")

        controller = StandaloneGestureController()
        print("[SUCCESS] StandaloneGestureController initialization successful")

        print("Gesture mappings:")
        for gesture, mapping in controller.gesture_mappings.items():
            print(f"  {gesture}: {mapping}")

        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()