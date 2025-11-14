#!/usr/bin/env python3
"""
手势测试工具
用于测试和显示所有支持的手势
"""

import cv2
import time
import yaml
import sys
from gestures.mediapipe_detector import MediaPipeGestureDetector

def test_all_gestures():
    print("🖐️  YOLO-LLM 手势识别测试工具")
    print("=" * 50)
    print("显示所有支持的手势和实时识别结果")
    print("按 'q' 键退出")
    print()

    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ 无法打开摄像头")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # 初始化手势检测器
    detector = MediaPipeGestureDetector()

    # 支持的手势列表
    supported_gestures = {
        'POINT_UP': '食指指向上',
        'POINT_INDEX': '食指指向前',
        'THUMBS_UP': '👍 点赞',
        'THUMBS_DOWN': '👎 点踩',
        'OPEN_PALM': '✋ 张开手掌',
        'CLOSED_FIST': '✊ 握拳',
        'VICTORY': '✌️ 胜利手势',
        'OK_SIGN': '👌 OK手势'
    }

    print("支持的手势:")
    for code, name in supported_gestures.items():
        print(f"  {code}: {name}")
    print()

    frame_count = 0
    last_gesture = None
    gesture_count = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            frame = cv2.flip(frame, 1)  # 水平翻转

            # 检测手势
            gesture_results = detector.detect_hands(frame)

            current_gesture = None
            if gesture_results:
                result = gesture_results[0]  # 取第一个检测结果
                current_gesture = result.gesture_code
                confidence = result.confidence

                # 只显示新手势（避免重复显示）
                if current_gesture != last_gesture:
                    gesture_name = supported_gestures.get(current_gesture, current_gesture)
                    print(f"🎯 检测到手势: {current_gesture} ({gesture_name}) - 置信度: {confidence:.2f}")
                    last_gesture = current_gesture
                    gesture_count += 1

                # 在画面上显示手势
                cv2.putText(frame, f'Gesture: {current_gesture}',
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.putText(frame, f'Confidence: {confidence:.2f}',
                          (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, 'No gesture detected',
                          (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # 显示统计信息
            cv2.putText(frame, f'Frame: {frame_count} | Gestures: {gesture_count}',
                      (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # 显示操作提示
            cv2.putText(frame, 'Press SPACE to pause, Q to quit',
                      (10, frame.shape[0] - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

            cv2.imshow('Gesture Recognition Test', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord(' '):
                print("⏸️  暂停 - 按空格继续...")
                cv2.waitKey(0)

    except KeyboardInterrupt:
        print("\n⏹️  用户中断")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        detector.close()

        print(f"\n📊 测试统计:")
        print(f"   总帧数: {frame_count}")
        print(f"   检测到手势: {gesture_count}次")
        print(f"   最后手势: {last_gesture or 'None'}")

if __name__ == "__main__":
    test_all_gestures()