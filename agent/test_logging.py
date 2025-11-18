#!/usr/bin/env python3
"""
测试日志输出的简单脚本
"""

import sys
import logging
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

# 配置详细的日志
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
)

def test_logging():
    print("Testing detailed logging...")

    # 测试后端连接和映射
    try:
        print("\n=== 测试后端API连接 ===")
        import requests
        response = requests.get('http://127.0.0.1:8081/api/config?username=admin&application=chrome.exe&os=windows', timeout=10)
        if response.status_code == 200:
            data = response.json()
            mappings = data.get('mappings', [])
            print(f"[SUCCESS] Got {len(mappings)} mappings")

            print("\n=== Gesture Mapping Details ===")
            for mapping in mappings:
                code = mapping.get('code')
                action = mapping.get('action', {})
                action_type = action.get('type')
                action_value = action.get('value')
                description = action.get('description')

                print(f"Gesture: {code:15} -> {action_type:8} ({action_value:15}) : {description}")

        else:
            print(f"[FAIL] Backend API error: {response.status_code}")

    except Exception as e:
        print(f"[FAIL] Backend connection failed: {e}")

    # 测试导入
    try:
        print("\n=== 测试模块导入 ===")
        from gestures.mediapipe_detector import MediaPipeGestureDetector
        print("[SUCCESS] MediaPipeGestureDetector import successful")

        from video_processor import VideoProcessor, VideoConfig
        print("[SUCCESS] VideoProcessor import successful")

        from main import GestureAgent, load_config
        print("[SUCCESS] GestureAgent import successful")

        # 测试配置加载
        config = load_config(Path('config.yaml'))
        print(f"[SUCCESS] Config loaded: backend_url={config.base_url}")

        # 测试agent初始化
        agent = GestureAgent(config)
        print("[SUCCESS] Agent initialized successfully")

        # 测试配置同步
        agent.sync_config()
        print(f"[SUCCESS] Config synced, got {len(agent.mapping)} mappings")
        print(f"Mappable gestures: {list(agent.mapping.keys())}")

    except Exception as e:
        print(f"[FAIL] Module import failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_logging()