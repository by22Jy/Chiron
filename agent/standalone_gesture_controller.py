#!/usr/bin/env python3
"""
独立手势控制器
不依赖后端数据库，直接在本地进行手势识别和动作执行
"""

import time
import logging
import sys
from pathlib import Path
from typing import Dict, Optional, Any

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))

from video_processor import VideoProcessor, VideoConfig
from gestures.mediapipe_detector import GestureResult
from actions.executor import execute_action

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 改为DEBUG级别以显示更多日志
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)

class StandaloneGestureController:
    """独立手势控制器"""

    def __init__(self):
        # 本地手势映射配置 (格式要匹配VideoProcessor期望的格式)
        self.gesture_mappings = {
            # 静态手势映射
            'POINT_UP': {
                'type': 'click',
                'value': 'left',
                'description': '鼠标左键点击'
            },
            'THUMBS_UP': {
                'type': 'hotkey',
                'value': 'enter',
                'description': '确认/执行'
            },
            'THUMBS_DOWN': {
                'type': 'hotkey',
                'value': 'escape',
                'description': '取消/退出'
            },
            'OPEN_PALM': {
                'type': 'hotkey',
                'value': 'win+d',
                'description': '显示桌面'
            },
            'CLOSED_FIST': {
                'type': 'hotkey',
                'value': 'alt+f4',
                'description': '关闭窗口'
            },
            'VICTORY': {
                'type': 'hotkey',
                'value': 'ctrl+t',
                'description': '浏览器新标签页'
            },
            'OK_SIGN': {
                'type': 'hotkey',
                'value': 'f11',
                'description': '全屏切换'
            },
            'POINT_INDEX': {
                'type': 'click',
                'value': 'right',
                'description': '鼠标右键点击'
            },

            # 动态手势映射
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
            'SWIPE_UP': {
                'type': 'scroll',
                'value': '5',
                'description': '向上滚动'
            },
            'SWIPE_DOWN': {
                'type': 'scroll',
                'value': '-5',
                'description': '向下滚动'
            }
        }

        # 动作执行统计
        self.action_stats = {}
        self.last_gesture_time = {}
        self.gesture_cooldown = 1.0  # 手势冷却时间（秒）

    def on_gesture_detected(self, gesture_result: GestureResult):
        """处理检测到的手势"""
        gesture_code = gesture_result.gesture_code
        current_time = time.time()

        # 检查手势冷却
        if gesture_code in self.last_gesture_time:
            if current_time - self.last_gesture_time[gesture_code] < self.gesture_cooldown:
                return  # 跳过冷却期的手势

        # 更新手势时间戳
        self.last_gesture_time[gesture_code] = current_time

        # 获取动作映射
        action_mapping = self.gesture_mappings.get(gesture_code)
        if not action_mapping:
            logger.warning(f'未找到手势映射: {gesture_code}')
            return

        logger.info(f'[GESTURE] 检测到手势: {gesture_code} ({action_mapping["description"]})')

        # 更新统计 (VideoProcessor会执行动作)
        self.update_action_stats(gesture_code, True)

    def on_action_executed(self, gesture_code: str, success: bool, message: str):
        """动作执行回调"""
        # 更新统计
        self.update_action_stats(gesture_code, success)

        # 显示结果
        status = "[SUCCESS] 成功" if success else "[FAIL] 失败"
        logger.info(f'   动作执行: {status} - {message}')

    def update_action_stats(self, gesture_code: str, success: bool):
        """更新动作执行统计"""
        if gesture_code not in self.action_stats:
            self.action_stats[gesture_code] = {'success': 0, 'total': 0}

        self.action_stats[gesture_code]['total'] += 1
        if success:
            self.action_stats[gesture_code]['success'] += 1

    def show_statistics(self):
        """显示统计信息"""
        logger.info('\n[STATS] 手势控制统计:')
        logger.info('=' * 40)

        if not self.action_stats:
            logger.info('暂无执行记录')
            return

        for gesture_code, stats in self.action_stats.items():
            total = stats['total']
            success = stats['success']
            success_rate = (success / total * 100) if total > 0 else 0
            mapping = self.gesture_mappings.get(gesture_code, {})
            description = mapping.get('description', '未知')

            logger.info(f'{gesture_code:15} | {description:20} | {success:2}/{total:2} ({success_rate:5.1f}%)')

        logger.info('=' * 40)

    def list_available_gestures(self):
        """列出可用的手势"""
        logger.info('\n[LIST] 可用手势列表:')
        logger.info('=' * 50)

        for gesture_code, mapping in self.gesture_mappings.items():
            logger.info(f'{gesture_code:15} -> {mapping["type"]:8} : {mapping["description"]}')

        logger.info('=' * 50)

    def run_realtime_control(self):
        """运行实时手势控制"""
        logger.info('[START] 启动独立手势控制系统...')
        logger.info('[CAMERA] 摄像头将开启，准备进行手势识别')
        logger.info('[INFO] 提示: 按 Ctrl+C 退出程序')

        # 配置视频处理
        video_config = VideoConfig(
            camera_id=0,
            width=640,
            height=480,
            fps=30,
            show_preview=True,
            flip_horizontal=True,
            detection_interval=0.1
        )

        # 创建视频处理器
        try:
            logger.info('[INIT] 初始化VideoProcessor，映射数量: %d', len(self.gesture_mappings))
            logger.info('[INIT] 手势映射键: %s', list(self.gesture_mappings.keys()))

            processor = VideoProcessor(config=video_config, gesture_mapping=self.gesture_mappings)

            # 设置回调函数
            processor.on_gesture_detected = self.on_gesture_detected
            processor.on_action_executed = self.on_action_executed

            logger.info('[INIT] VideoProcessor初始化成功')
            logger.info('[INIT] 手势映射已设置，总映射数: %d', len(self.gesture_mappings))

        except Exception as exc:
            logger.error(f'[ERROR] 无法初始化摄像头: {exc}')
            logger.exception('[ERROR] 初始化异常详情:')
            return

        logger.info('[SUCCESS] 摄像头初始化成功')
        logger.info('[GESTURE] 开始手势识别...')

        try:
            # 启动视频处理器
            processor.start()

            # 等待直到用户中断
            while processor.running:
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info('\n[INTERRUPT] 用户中断，正在退出...')
        except Exception as exc:
            logger.exception(f'[ERROR] 视频处理出错: {exc}')
        finally:
            logger.info('[STOP] 停止摄像头...')
            processor.stop()

        # 显示统计信息
        self.show_statistics()

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='独立手势控制器')
    parser.add_argument('--list', action='store_true', help='列出可用手势')
    parser.add_argument('--demo', action='store_true', help='演示模式')
    args = parser.parse_args()

    controller = StandaloneGestureController()

    if args.list:
        controller.list_available_gestures()
        return

    if args.demo:
        logger.info('[DEMO] 演示模式: 手势控制功能预览')
        logger.info('[INFO] 以下是可以执行的手势动作:')
        controller.list_available_gestures()
        logger.info('\n[INFO] 要启动实时控制，请运行: python standalone_gesture_controller.py')
        return

    # 运行实时手势控制
    controller.run_realtime_control()

if __name__ == '__main__':
    main()