#!/usr/bin/env python3
"""
实时测试手势识别和执行
添加详细日志调试问题
"""

import sys
import time
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    datefmt='%H:%M:%S',
)

from video_processor import VideoProcessor, VideoConfig
from gestures.mediapipe_detector import GestureResult
from actions.executor import execute_action

# 设置所有模块的日志级别
logging.getLogger('video_processor').setLevel(logging.DEBUG)
logging.getLogger('actions.executor').setLevel(logging.DEBUG)

class DebugGestureController:
    def __init__(self):
        # 使用与独立控制器相同的映射
        self.gesture_mappings = {
            'SWIPE_LEFT': {
                'type': 'hotkey',
                'value': 'ctrl+shift+tab',
                'description': '浏览器标签页左切换'
            },
            'SWIPE_RIGHT': {
                'type': 'hotkey',
                'value': 'ctrl+tab',
                'description': '浏览器标签页右切换'
            },
            'THUMBS_UP': {
                'type': 'hotkey',
                'value': 'enter',
                'description': '确认/执行'
            },
            'VICTORY': {
                'type': 'hotkey',
                'value': 'ctrl+t',
                'description': '浏览器新标签页'
            },
        }

        self.last_gesture_time = {}
        self.gesture_cooldown = 2.0  # 增加冷却时间

    def on_gesture_detected(self, gesture_result: GestureResult):
        """处理检测到的手势"""
        gesture_code = gesture_result.gesture_code
        current_time = time.time()

        logging.debug('[CALLBACK] 手势检测回调: %s (置信度: %.2f)',
                    gesture_code, gesture_result.confidence)

        # 检查冷却
        if gesture_code in self.last_gesture_time:
            if current_time - self.last_gesture_time[gesture_code] < self.gesture_cooldown:
                logging.debug('[COOLDOWN] 手势 %s 在冷却期，跳过', gesture_code)
                return

        self.last_gesture_time[gesture_code] = current_time

        # 获取映射
        action_mapping = self.gesture_mappings.get(gesture_code)
        if not action_mapping:
            logging.warning('[MAPPING] 未找到手势映射: %s', gesture_code)
            logging.debug('[MAPPING] 可用映射: %s', list(self.gesture_mappings.keys()))
            return

        logging.info('[GESTURE] 检测到有效手势: %s -> %s (%s)',
                   gesture_code, action_mapping['value'], action_mapping['description'])

        # 执行动作
        try:
            action_type = action_mapping['type']
            action_value = action_mapping['value']
            action_payload = action_mapping.get('payload')

            logging.info('[EXECUTE] 执行动作: %s %s', action_type, action_value)
            success, message = execute_action(action_type, action_value, action_payload)

            if success:
                logging.info('[SUCCESS] 动作执行成功: %s', message)
            else:
                logging.warning('[FAIL] 动作执行失败: %s', message)

        except Exception as exc:
            logging.exception('[ERROR] 动作执行异常: %s', exc)

    def on_action_executed(self, gesture_code: str, success: bool, message: str):
        """动作执行回调"""
        logging.info('[ACTION_CALLBACK] 动作回调: %s -> success=%s, message=%s',
                   gesture_code, success, message)

def main():
    print("实时手势调试测试")
    print("=" * 50)
    print("请确保Chrome浏览器已打开并有多个标签页")
    print("准备测试左右滑动手势切换标签页")
    print()

    controller = DebugGestureController()

    # 配置视频处理
    video_config = VideoConfig(
        camera_id=0,
        width=640,
        height=480,
        fps=30,
        show_preview=True,
        flip_horizontal=True,
        detection_interval=0.2  # 增加检测间隔
    )

    print("初始化VideoProcessor...")
    try:
        processor = VideoProcessor(config=video_config, gesture_mapping=controller.gesture_mappings)

        # 设置回调
        processor.on_gesture_detected = controller.on_gesture_detected
        processor.on_action_executed = controller.on_action_executed

        print("VideoProcessor初始化成功")
        print(f"映射数量: {len(processor.gesture_mapping)}")
        print(f"映射键: {list(processor.gesture_mapping.keys())}")

    except Exception as exc:
        print(f"VideoProcessor初始化失败: {exc}")
        import traceback
        traceback.print_exc()
        return

    print("启动实时手势识别...")
    print("按 Ctrl+C 退出")
    print("-" * 50)

    try:
        processor.start()

        # 等待用户中断
        while processor.running:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("用户中断，正在退出...")
    except Exception as exc:
        print(f"视频处理出错: {exc}")
        import traceback
        traceback.print_exc()
    finally:
        print("停止摄像头...")
        processor.stop()

if __name__ == "__main__":
    main()