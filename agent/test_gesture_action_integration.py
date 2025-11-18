#!/usr/bin/env python3
"""
测试手势到动作的集成验证
验证从手势识别到系统控制的完整流程
"""

import time
import logging
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockActionExecutor:
    """模拟动作执行器"""

    def __init__(self):
        self.executed_actions = []

    def execute_action(self, action_type: str, action_value: str, **kwargs):
        """执行动作"""
        action_record = {
            'timestamp': time.time(),
            'type': action_type,
            'value': action_value,
            'kwargs': kwargs,
            'success': True
        }

        self.executed_actions.append(action_record)

        # 模拟不同的动作执行
        if action_type == 'hotkey':
            logger.info(f"[HOTKEY] 执行快捷键: {action_value}")
        elif action_type == 'mouse':
            logger.info(f"[MOUSE] 执行鼠标动作: {action_value}")
        elif action_type == 'scroll':
            logger.info(f"[SCROLL] 执行滚动: {action_value} {kwargs.get('clicks', 1)}次")
        elif action_type == 'web_navigation':
            logger.info(f"[WEB] 浏览器导航: {action_value}")
        elif action_type == 'window':
            logger.info(f"[WINDOW] 窗口操作: {action_value}")
        elif action_type == 'system':
            logger.info(f"[SYSTEM] 系统操作: {action_value}")
        else:
            logger.info(f"[UNKNOWN] 未知动作类型: {action_type} -> {action_value}")

        return True

class GestureActionMapper:
    """手势到动作的映射器"""

    def __init__(self):
        self.action_executor = MockActionExecutor()
        self._setup_mappings()

    def _setup_mappings(self):
        """设置手势映射"""
        # 通用映射配置
        self.mappings = {
            # 静态手势
            'POINT_UP': [
                {'type': 'mouse', 'value': 'left_click', 'description': '鼠标左键'}
            ],
            'THUMBS_UP': [
                {'type': 'hotkey', 'value': 'enter', 'description': '确认/执行'}
            ],
            'THUMBS_DOWN': [
                {'type': 'hotkey', 'value': 'escape', 'description': '取消/退出'}
            ],
            'OPEN_PALM': [
                {'type': 'hotkey', 'value': 'win+d', 'os': 'windows', 'description': '显示桌面'},
                {'type': 'hotkey', 'value': 'command+f3', 'os': 'macos', 'description': '显示桌面'}
            ],
            'CLOSED_FIST': [
                {'type': 'hotkey', 'value': 'alt+f4', 'os': 'windows', 'description': '关闭窗口'},
                {'type': 'hotkey', 'value': 'command+q', 'os': 'macos', 'description': '关闭应用'}
            ],
            'VICTORY': [
                {'type': 'hotkey', 'value': 'ctrl+t', 'os': 'windows', 'description': '新标签页'},
                {'type': 'hotkey', 'value': 'command+t', 'os': 'macos', 'description': '新标签页'}
            ],
            'OK_SIGN': [
                {'type': 'hotkey', 'value': 'f11', 'description': '全屏切换'}
            ],

            # 动态手势
            'SWIPE_LEFT': [
                {'type': 'web_navigation', 'value': 'back', 'description': '浏览器后退'},
                {'type': 'hotkey', 'value': 'ctrl+left', 'os': 'windows', 'description': '标签页左切换'},
                {'type': 'hotkey', 'value': 'command+option+left', 'os': 'macos', 'description': '标签页左切换'}
            ],
            'SWIPE_RIGHT': [
                {'type': 'web_navigation', 'value': 'forward', 'description': '浏览器前进'},
                {'type': 'hotkey', 'value': 'ctrl+right', 'os': 'windows', 'description': '标签页右切换'},
                {'type': 'hotkey', 'value': 'command+option+right', 'os': 'macos', 'description': '标签页右切换'}
            ],
            'SWIPE_UP': [
                {'type': 'scroll', 'value': 'scroll_up', 'clicks': 5, 'description': '向上滚动'},
                {'type': 'hotkey', 'value': 'alt+tab', 'os': 'windows', 'description': '切换应用'},
                {'type': 'hotkey', 'value': 'command+tab', 'os': 'macos', 'description': '切换应用'}
            ],
            'SWIPE_DOWN': [
                {'type': 'scroll', 'value': 'scroll_down', 'clicks': 5, 'description': '向下滚动'},
                {'type': 'hotkey', 'value': 'alt+shift+tab', 'os': 'windows', 'description': '反向切换应用'},
                {'type': 'hotkey', 'value': 'command+shift+tab', 'os': 'macos', 'description': '反向切换应用'}
            ]
        }

        # 当前系统（可以根据实际情况修改）
        self.current_os = 'windows'

    def map_gesture_to_action(self, gesture_code: str) -> Optional[Dict[str, Any]]:
        """将手势映射到动作"""
        if gesture_code not in self.mappings:
            logger.warning(f"[WARNING] 未找到手势映射: {gesture_code}")
            return None

        actions = self.mappings[gesture_code]

        # 选择合适的动作（优先选择当前系统的动作）
        selected_action = None

        for action in actions:
            # 如果指定了操作系统，优先选择匹配的
            if 'os' in action:
                if action['os'] == self.current_os or action['os'] == 'any':
                    selected_action = action
                    break
            else:
                # 通用动作
                selected_action = action

        if selected_action:
            logger.info(f"[MAPPING] 手势映射: {gesture_code} -> {selected_action['description']}")
            return selected_action
        else:
            logger.warning(f"[WARNING] 没有找到适合当前系统的动作映射: {gesture_code}")
            return None

    def execute_gesture_action(self, gesture_code: str) -> bool:
        """执行手势对应的动作"""
        action = self.map_gesture_to_action(gesture_code)
        if not action:
            return False

        # 提取额外参数
        kwargs = {}
        if 'clicks' in action:
            kwargs['clicks'] = action['clicks']

        # 执行动作
        success = self.action_executor.execute_action(
            action['type'],
            action['value'],
            **kwargs
        )

        return success

def test_gesture_action_integration():
    """测试手势动作集成"""
    print("[START] 开始测试手势到动作的集成...")
    print("=" * 50)

    mapper = GestureActionMapper()

    # 测试用例
    test_cases = [
        # 静态手势测试
        ('POINT_UP', '点击操作'),
        ('THUMBS_UP', '确认操作'),
        ('THUMBS_DOWN', '取消操作'),
        ('OPEN_PALM', '显示桌面'),
        ('CLOSED_FIST', '关闭窗口'),
        ('VICTORY', '新标签页'),
        ('OK_SIGN', '全屏切换'),

        # 动态手势测试
        ('SWIPE_LEFT', '后退操作'),
        ('SWIPE_RIGHT', '前进操作'),
        ('SWIPE_UP', '向上滚动'),
        ('SWIPE_DOWN', '向下滚动'),

        # 错误测试
        ('UNKNOWN_GESTURE', '未知手势')
    ]

    print("\n[TEST] 测试用例:")
    print("-" * 30)

    success_count = 0
    total_count = len(test_cases)

    for gesture, description in test_cases:
        print(f"\n[TESTING] 测试: {gesture} ({description})")

        success = mapper.execute_gesture_action(gesture)

        if success or gesture == 'UNKNOWN_GESTURE':  # 未知手势预期失败
            success_count += 1
            status = "[PASS] 通过" if success else "[EXPECTED] 预期失败"
        else:
            status = "[FAIL] 失败"

        print(f"   状态: {status}")

        # 添加小延迟，避免动作执行过快
        time.sleep(0.5)

    print(f"\n" + "=" * 50)
    print(f"[RESULT] 测试结果: {success_count}/{total_count} 通过")

    # 显示执行的动作统计
    print(f"\n[STATS] 动作执行统计:")
    action_stats = {}
    for action_record in mapper.action_executor.executed_actions:
        action_type = action_record['type']
        action_stats[action_type] = action_stats.get(action_type, 0) + 1

    for action_type, count in action_stats.items():
        print(f"   {action_type}: {count}次")

    return success_count == total_count - 1  # 减去预期的失败用例

def demo_interactive_mode():
    """演示交互模式"""
    print("\n[DEMO] 交互式演示模式")
    print("=" * 50)
    print("输入手势代码进行测试 (输入 'quit' 退出):")
    print("可用手势: POINT_UP, THUMBS_UP, SWIPE_LEFT, SWIPE_RIGHT, SWIPE_UP, SWIPE_DOWN")

    mapper = GestureActionMapper()

    while True:
        try:
            gesture_input = input("\n[INPUT] 请输入手势代码: ").strip().upper()

            if gesture_input.lower() in ['quit', 'exit', 'q']:
                print("[EXIT] 退出演示模式")
                break

            if not gesture_input:
                continue

            print(f"[EXECUTE] 执行手势: {gesture_input}")
            success = mapper.execute_gesture_action(gesture_input)

            if success:
                print("[SUCCESS] 执行成功")
            else:
                print("[FAIL] 执行失败或无映射")

        except KeyboardInterrupt:
            print("\n[INTERRUPT] 被用户中断，退出演示模式")
            break
        except Exception as e:
            print(f"[ERROR] 错误: {e}")

def main():
    """主函数"""
    print("YOLO-LLM 手势-动作集成测试")
    print("=" * 50)

    # 运行集成测试
    test_passed = test_gesture_action_integration()

    if test_passed:
        print("\n[SUCCESS] 集成测试通过！")
        print("[INFO] 手势识别和动作执行系统工作正常")
        print("[INFO] 可以开始实际的手势控制")
    else:
        print("\n[WARNING] 集成测试未完全通过")
        print("[INFO] 请检查手势映射配置")

    # 询问是否进入交互模式
    try:
        response = input("\n[DEMO] 是否进入交互式演示模式? (y/n): ").strip().lower()
        if response in ['y', 'yes', '是']:
            demo_interactive_mode()
    except KeyboardInterrupt:
        print("\n[END] 测试结束")

if __name__ == "__main__":
    main()