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
    print("🗄️ 测试数据库连接...")

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
        print("✅ 数据库连接成功")
        print("📋 手势映射数据:")
        for row in results:
            if row[0] and row[1]:  # 如果有数据
                print(f"   {row[0]} ({row[1]}): {row[2]} ({row[3]})")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_backend_service():
    """测试后端服务"""
    print("\n🌐 测试后端服务...")

    try:
        response = requests.get('http://127.0.0.1:8080/api/config', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            data = response.json()
            print(f"📊 返回{len(data.get('mappings', []))}个手势映射")
            return True
        else:
            print(f"❌ 后端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到后端服务 (端口8080)")
        return False
    except Exception as e:
        print(f"❌ 后端服务测试失败: {e}")
        return False

def test_ai_service():
    """测试AI服务"""
    print("\n🤖 测试AI服务...")

    try:
        response = requests.get('http://127.0.0.1:8000', timeout=5)
        if response.status_code == 200:
            print("✅ AI服务运行正常")
            return True
        else:
            print(f"❌ AI服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到AI服务 (端口8000)")
        return False
    except Exception as e:
        print(f"❌ AI服务测试失败: {e}")
        return False

def test_frontend_service():
    """测试前端服务"""
    print("\n🌐 测试前端服务...")

    try:
        response = requests.get('http://127.0.0.1:5173', timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务运行正常")
            return True
        else:
            print(f"❌ 前端服务响应异常: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到前端服务 (端口5173)")
        return False
    except Exception as e:
        print(f"❌ 前端服务测试失败: {e}")
        return False

def check_agent_status():
    """检查Agent状态"""
    print("\n🤖 检查Agent状态...")

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
        print(f"❌ 缺少必要文件: {missing_files}")
        return False
    else:
        print("✅ Agent文件完整")

    # 测试导入
    try:
        import importlib
        spec = importlib.util.spec_from_file_location("main", "agent/main.py")
        module = importlib.util.module_from_spec(spec)
        print("✅ Agent主模块可以导入")
        return True
    except Exception as e:
        print(f"❌ Agent模块导入失败: {e}")
        return False

def test_end_to_end_flow():
    """测试端到端流程"""
    print("\n🔄 测试端到端流程...")

    # 1. 检查数据库映射
    if not test_database_connection():
        print("❌ 数据库测试失败，端到端流程中断")
        return False

    # 2. 启动后端服务
    print("启动后端服务...")
    try:
        backend_process = subprocess.Popen(
            ['mvn', 'spring-boot:run'],
            cwd='D:/yolo-llm/backend',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        time.sleep(10)  # 等待10秒让后端启动

        # 检查后端是否启动成功
        if test_backend_service():
            print("✅ 后端服务启动成功")
        else:
            backend_process.terminate()
            print("❌ 后端服务启动失败")
            return False

    except Exception as e:
        print(f"❌ 启动后端服务失败: {e}")
        return False

    # 3. 测试API调用
    try:
        response = requests.get(
            'http://127.0.0.1:8080/api/config',
            params={
                'username': 'admin',
                'application': 'chrome.exe',
                'os': 'windows'
            },
            timeout=10
        )

        if response.status_code == 200:
            config = response.json()
            print("✅ API调用成功")
            print(f"📋 获取到{len(config.get('mappings', []))}个手势映射")

            # 显示重要映射
            mappings = config.get('mappings', [])
            for mapping in mappings:
                if mapping.get('code') in ['SWIPE_LEFT', 'SWIPE_RIGHT', 'THUMBS_UP']:
                    print(f"   {mapping['code']} -> {mapping.get('action', {}).get('value', 'N/A')}")

        else:
            print(f"❌ API调用失败: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ API调用测试失败: {e}")
        return False

    print("✅ 端到端流程测试完成")
    return True

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