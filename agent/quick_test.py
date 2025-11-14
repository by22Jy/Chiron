#!/usr/bin/env python3
"""
快速测试改进后的手势识别
"""

import cv2
import time
import logging
import yaml
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
)

def test_gesture_mapping():
    print("🎯 测试手势映射配置")
    print("=" * 40)

    try:
        # 测试本地配置文件
        config_path = Path('local_gestures.yaml')
        if config_path.exists():
            with config_path.open('r', encoding='utf-8') as f:
                local_config = yaml.safe_load(f)

            mappings = local_config.get('local_mappings', {})
            print(f"✅ 找到 {len(mappings)} 个本地手势映射:")

            for i, (gesture_code, action) in enumerate(mappings.items(), 1):
                desc = action.get('description', f"{action.get('type')}:{action.get('value')}")
                print(f"  {i}. {gesture_code} -> {desc}")

            return True
        else:
            print("❌ 本地手势配置文件不存在")
            return False

    except Exception as e:
        print(f"❌ 读取配置文件出错: {e}")
        return False

def test_camera():
    print("\n📹 测试摄像头")
    print("=" * 40)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return False

    ret, frame = cap.read()
    if ret:
        print(f"✅ 摄像头工作正常 - 分辨率: {frame.shape[1]}x{frame.shape[0]}")

        # 显示2秒测试画面
        print("显示测试画面 (3秒)...")
        for i in range(3, 0, -1):
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                cv2.putText(frame, f'Camera Test - {i}s',
                          (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, 'Press Q to quit',
                          (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow('Camera Test', frame)

                key = cv2.waitKey(1000) & 0xFF
                if key == ord('q'):
                    break

        cv2.destroyAllWindows()
        cap.release()
        return True
    else:
        print("❌ 摄像头无法读取画面")
        cap.release()
        return False

def main():
    print("🚀 YOLO-LLM 快速测试工具")
    print("=" * 50)
    print("测试改进后的手势识别系统\n")

    # 测试配置文件
    config_ok = test_gesture_mapping()

    # 测试摄像头
    camera_ok = test_camera()

    print("\n📊 测试结果:")
    print(f"   配置文件: {'✅' if config_ok else '❌'}")
    print(f"   摄像头:   {'✅' if camera_ok else '❌'}")

    if config_ok and camera_ok:
        print("\n🎉 所有测试通过！")
        print("\n现在可以运行:")
        print("  python main.py --realtime")
        print("  python test_gestures.py")
    else:
        print("\n⚠️  请解决上述问题后再运行手势识别")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
    finally:
        cv2.destroyAllWindows()

    input("\n按回车键退出...")