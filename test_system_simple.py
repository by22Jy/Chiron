#!/usr/bin/env python3
"""
测试完整的YOLO-LLM系统状态
包括后端、数据库、AI服务、前端和agent
"""

import sys
import time
import requests
import subprocess
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

def test_database_connection():
    """测试数据库连接"""
    print("测试数据库连接...")

    try:
        import mysql.connector

        conn = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='Wangjiayi1',
            database='yolo_platform'
        )

        cursor = conn.cursor()

        # 检查手势映射数据
        cursor.execute("""
            SELECT g.code as gesture, g.name, a.action_value, a.action_type
            FROM gestures g
            LEFT JOIN mappings m ON g.id = m.gesture_id
            LEFT JOIN actions a ON m.action_id = a.id
            WHERE g.code IN ('SWIPE_LEFT', 'SWIPE_RIGHT', 'THUMBS_UP', 'VICTORY')
            ORDER BY g.code, m.priority DESC
        """)

        results = cursor.fetchall()
        print("[OK] 数据库连接成功")
        print("手势映射数据:")
        for row in results:
            if row[0] and row[1]:  # 如果有数据
                print(f"   {row[0]} ({row[1]}): {row[2]} ({row[3]})")

        conn.close()
        return True

    except Exception as e:
        print(f"[FAIL] 数据库连接失败: {e}")
        return False

def test_backend_service():
    """测试后端服务"""
    print("\n测试后端服务...")

    try:
        response = requests.get('http://127.0.0.1:8081/api/config', timeout=5)
        if response.status_code == 200:
            print("[OK] 后端服务运行正常")
            data = response.json()
            print(f"返回{len(data.get('mappings', []))}个手势映射")
            return True
        else:
            print(f"[FAIL] 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] 无法连接到后端服务 (端口8081)")
        return False
    except Exception as e:
        print(f"[FAIL] 后端服务测试失败: {e}")
        return False

def test_ai_service():
    """测试AI服务"""
    print("\n测试AI服务...")

    try:
        response = requests.get('http://127.0.0.1:8000', timeout=5)
        if response.status_code == 200:
            print("[OK] AI服务运行正常")
            return True
        else:
            print(f"[FAIL] AI服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] 无法连接到AI服务 (端口8000)")
        return False
    except Exception as e:
        print(f"[FAIL] AI服务测试失败: {e}")
        return False

def test_frontend_service():
    """测试前端服务"""
    print("\n测试前端服务...")

    try:
        response = requests.get('http://127.0.0.1:5173', timeout=5)
        if response.status_code == 200:
            print("[OK] 前端服务运行正常")
            return True
        else:
            print(f"[FAIL] 前端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[FAIL] 无法连接到前端服务 (端口5173)")
        return False
    except Exception as e:
        print(f"[FAIL] 前端服务测试失败: {e}")
        return False

def check_agent_status():
    """检查Agent状态"""
    print("\n检查Agent状态...")

    # 检查必要文件
    required_files = [
        'agent/main.py',
        'agent/config.yaml',
        'agent/video_processor.py',
        'agent/gestures/mediapipe_detector.py',
        'agent/actions/executor.py',
        'agent/standalone_gesture_controller.py'
    ]

    missing_files = []
    for file_path in required_files:
        full_path = Path(file_path)
        if not full_path.exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"[FAIL] 缺少必要文件: {missing_files}")
        return False
    else:
        print("[OK] Agent文件完整")

    # 测试导入
    try:
        import importlib
        spec = importlib.util.spec_from_file_location("main", "agent/main.py")
        module = importlib.util.module_from_spec(spec)
        print("[OK] Agent主模块可以导入")
        return True
    except Exception as e:
        print(f"[FAIL] Agent模块导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("YOLO-LLM 系统状态检查")
    print("=" * 50)

    # 检查各个组件
    results = {}

    print("1. 检查Agent状态")
    results['agent'] = check_agent_status()

    print("\n2. 检查数据库连接")
    results['database'] = test_database_connection()

    print("\n3. 检查各服务状态")
    results['backend'] = test_backend_service()
    results['ai'] = test_ai_service()
    results['frontend'] = test_frontend_service()

    # 汇总结果
    print(f"\n{'='*50}")
    print("系统状态汇总:")

    all_success = True
    for component, status in results.items():
        status_text = "[OK] 正常" if status else "[FAIL] 异常"
        print(f"   {component:15} : {status_text}")
        if not status:
            all_success = False

    print(f"\n总体状态: {'[OK] 所有组件正常' if all_success else '[FAIL] 存在问题'}")

    if all_success:
        print("\n[SUCCESS] 系统准备就绪！")
        print("可以执行以下测试:")
        print("   1. python agent/test_browser_navigation.py (浏览器快捷键测试)")
        print("   2. python agent/standalone_gesture_controller.py (独立手势控制)")
        print("   3. python agent/main.py --realtime (原始agent控制)")
    else:
        print("\n[WARNING] 需要修复失败的组件")

    return all_success

if __name__ == "__main__":
    main()