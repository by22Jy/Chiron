#!/usr/bin/env python3
"""
快速摄像头修复脚本
解决摄像头黑屏的常见问题
"""

import cv2
import time
import yaml

def quick_fix():
    print("🔧 YOLO-LLM 快速摄像头修复")
    print("=" * 40)

    # 尝试不同的摄像头ID
    working_cameras = []

    for camera_id in range(3):  # 测试 0, 1, 2
        print(f"\n测试摄像头 {camera_id}...")
        cap = cv2.VideoCapture(camera_id)

        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ 摄像头 {camera_id} 工作正常")
                working_cameras.append(camera_id)

                # 显示2秒测试画面
                for i in range(2, 0, -1):
                    ret, frame = cap.read()
                    if ret:
                        cv2.putText(frame, f'Camera {camera_id} - Working!',
                                  (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.imshow(f'Camera {camera_id} Test', frame)
                        cv2.waitKey(1000)
                    print(f"   {i}...")

                cv2.destroyWindow(f'Camera {camera_id} Test')
            else:
                print(f"❌ 摄像头 {camera_id} 无法读取画面")
            cap.release()
        else:
            print(f"❌ 摄像头 {camera_id} 无法打开")

    cv2.destroyAllWindows()

    if not working_cameras:
        print("\n❌ 没有找到工作的摄像头！")
        print("\n请检查:")
        print("1. 摄像头是否正确连接")
        print("2. 摄像头权限是否允许")
        print("3. 其他应用是否占用了摄像头")
        return False

    # 更新配置文件
    best_camera_id = working_cameras[0]
    print(f"\n✅ 使用摄像头 {best_camera_id}")

    try:
        # 读取现有配置
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        # 更新摄像头ID
        config['video']['camera_id'] = best_camera_id
        # 优化分辨率
        config['video']['width'] = 640
        config['video']['height'] = 480

        # 写回配置
        with open('config.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        print(f"✅ 已更新 config.yaml 中的摄像头ID为 {best_camera_id}")

    except Exception as e:
        print(f"⚠️  无法更新配置文件: {e}")
        print("请手动修改 config.yaml 中的 camera_id 为", best_camera_id)

    print(f"\n🎉 修复完成！现在可以运行:")
    print(f"   python main.py --realtime")

    return True

if __name__ == "__main__":
    try:
        quick_fix()
    except Exception as e:
        print(f"❌ 修复过程中出错: {e}")
    finally:
        cv2.destroyAllWindows()

    input("\n按回车键退出...")