#!/usr/bin/env python3
"""
摄像头测试和诊断工具
用于诊断和解决摄像头黑屏问题
"""

import cv2
import time
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
)

def test_camera_ids(max_id=5):
    """测试多个摄像头设备ID"""
    print("🔍 正在扫描可用摄像头设备...")

    available_cameras = []

    for camera_id in range(max_id + 1):
        print(f"测试摄像头 ID: {camera_id}")

        cap = cv2.VideoCapture(camera_id)

        # 检查摄像头是否成功打开
        if cap.isOpened():
            # 尝试读取一帧
            ret, frame = cap.read()

            if ret:
                height, width = frame.shape[:2]
                print(f"✅ 摄像头 {camera_id}: {width}x{height}")
                available_cameras.append({
                    'id': camera_id,
                    'width': width,
                    'height': height,
                    'backend': cap.getBackendName()
                })

                # 显示测试画面
                print(f"   显示摄像头 {camera_id} 的测试画面 (3秒)...")
                for i in range(3, 0, -1):
                    ret, frame = cap.read()
                    if ret:
                        cv2.putText(frame, f'Camera {camera_id} - {i}s',
                                  (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        cv2.imshow(f'Camera {camera_id} Test', frame)
                        if cv2.waitKey(1000) & 0xFF == ord('q'):
                            break
                    print(f"   倒计时: {i}")

                cv2.destroyWindow(f'Camera {camera_id} Test')
            else:
                print(f"❌ 摄像头 {camera_id}: 能打开但无法读取画面")

            cap.release()
        else:
            print(f"❌ 摄像头 {camera_id}: 无法打开")

    cv2.destroyAllWindows()
    return available_cameras

def test_camera_properties(camera_id):
    """测试摄像头属性和设置"""
    print(f"\n🔧 详细测试摄像头 {camera_id} 的属性...")

    cap = cv2.VideoCapture(camera_id)

    if not cap.isOpened():
        print(f"❌ 无法打开摄像头 {camera_id}")
        return False

    # 获取支持的分辨率
    resolutions = [
        (320, 240), (640, 480), (800, 600), (1024, 768),
        (1280, 720), (1920, 1080)
    ]

    print("支持的分辨率测试:")
    for width, height in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        ret, frame = cap.read()
        if ret and actual_width == width and actual_height == height:
            print(f"✅ {width}x{height}")
        else:
            print(f"❌ {width}x{height} (实际: {actual_width}x{actual_height})")

    # 测试不同的API后端
    backends = {
        cv2.CAP_DSHOW: "DirectShow",
        cv2.CAP_MSMF: "Media Foundation",
        cv2.CAP_FFMPEG: "FFmpeg"
    }

    print("\n可用的API后端:")
    for backend_id, backend_name in backends.items():
        try:
            cap.release()
            cap = cv2.VideoCapture(camera_id + backend_id)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print(f"✅ {backend_name}")
                else:
                    print(f"❌ {backend_name} - 无法读取")
            else:
                print(f"❌ {backend_name} - 无法打开")
        except Exception as e:
            print(f"❌ {backend_name} - 错误: {e}")

    cap.release()
    return True

def create_optimized_config(available_cameras):
    """创建优化的配置文件"""
    if not available_cameras:
        print("\n❌ 没有找到可用的摄像头")
        return False

    # 选择最佳摄像头（通常是ID最小的）
    best_camera = available_cameras[0]

    print(f"\n✅ 选择摄像头 {best_camera['id']} 作为默认摄像头")
    print(f"   分辨率: {best_camera['width']}x{best_camera['height']}")
    print(f"   后端: {best_camera['backend']}")

    # 创建优化的配置
    optimized_config = f"""backend:
  base_url: 'http://127.0.0.1:8080'
  username: 'admin'
  application: 'chrome.exe'
  os: 'windows'

agent:
  source: 'python-agent@dev'
  poll_interval: 60

video:
  camera_id: {best_camera['id']}         # 摄像头设备ID (自动检测)
  width: {min(best_camera['width'], 640)}  # 视频宽度 (优化性能)
  height: {min(best_camera['height'], 480)} # 视频高度 (优化性能)
  fps: 30             # 帧率
  show_preview: true  # 是否显示预览窗口
  flip_horizontal: true  # 水平翻转摄像头图像
  detection_interval: 0.1  # 手势检测间隔(秒)
"""

    # 备份原配置
    try:
        import shutil
        shutil.copy('config.yaml', 'config.yaml.backup')
        print("✅ 原配置已备份为 config.yaml.backup")
    except:
        pass

    # 写入新配置
    with open('config.yaml', 'w', encoding='utf-8') as f:
        f.write(optimized_config)

    print("✅ 已创建优化的配置文件 config.yaml")
    return True

def main():
    print("🎥 YOLO-LLM 摄像头诊断工具")
    print("=" * 50)

    try:
        # 1. 扫描可用摄像头
        available_cameras = test_camera_ids(5)

        if not available_cameras:
            print("\n❌ 未找到任何可用的摄像头设备！")
            print("\n可能的解决方案:")
            print("1. 检查摄像头是否已连接")
            print("2. 检查摄像头权限设置")
            print("3. 重新插拔USB摄像头")
            print("4. 检查其他应用是否占用摄像头")
            return False

        # 2. 详细测试最佳摄像头
        best_camera_id = available_cameras[0]['id']
        test_camera_properties(best_camera_id)

        # 3. 创建优化配置
        create_optimized_config(available_cameras)

        print(f"\n🎉 摄像头诊断完成！")
        print(f"建议使用摄像头 ID: {available_cameras[0]['id']}")
        print(f"现在可以运行: python main.py --realtime")

        return True

    except Exception as e:
        print(f"\n❌ 诊断过程中发生错误: {e}")
        return False

    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

    print("\n按任意键退出...")
    input()