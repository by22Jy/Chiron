"""
可配置手势识别器
解决硬编码if-else问题，支持配置文件驱动的手势定义
"""

import yaml
import math
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass

@dataclass
class FingerConfig:
    """手指状态配置"""
    thumb: Optional[bool] = None  # None表示不关心
    index: Optional[bool] = None
    middle: Optional[bool] = None
    ring: Optional[bool] = None
    pinky: Optional[bool] = None

@dataclass
class GestureConfig:
    """手势配置"""
    code: str
    name: str
    type: str  # "static" or "dynamic"
    confidence: float

    # 静态手势配置
    fingers: Optional[FingerConfig] = None

    # 动态手势配置
    min_distance: Optional[float] = None
    direction: Optional[str] = None  # "horizontal", "vertical", "diagonal"
    sign: Optional[str] = None  # "positive", "negative"

    # 其他配置
    description: str = ""

class ConfigurableGestureDetector:
    """可配置的手势识别器"""

    def __init__(self, config_file: str = "gesture_definitions.yaml"):
        self.config_file = config_file
        self.static_gestures: Dict[str, GestureConfig] = {}
        self.dynamic_gestures: Dict[str, GestureConfig] = {}

        self.load_config()

    def load_config(self):
        """加载手势配置"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            # 加载静态手势配置
            if 'static_gestures' in config_data:
                for gesture_code, gesture_data in config_data['static_gestures'].items():
                    finger_config = FingerConfig(**gesture_data.get('fingers', {}))

                    self.static_gestures[gesture_code] = GestureConfig(
                        code=gesture_code,
                        name=gesture_data.get('name', ''),
                        type='static',
                        confidence=gesture_data.get('confidence', 0.8),
                        fingers=finger_config,
                        description=gesture_data.get('description', '')
                    )

            # 加载动态手势配置
            if 'dynamic_gestures' in config_data:
                for gesture_code, gesture_data in config_data['dynamic_gestures'].items():

                    self.dynamic_gestures[gesture_code] = GestureConfig(
                        code=gesture_code,
                        name=gesture_data.get('name', ''),
                        type='dynamic',
                        confidence=gesture_data.get('confidence', 0.8),
                        min_distance=gesture_data.get('min_distance', 0.1),
                        direction=gesture_data.get('direction', 'horizontal'),
                        sign=gesture_data.get('sign', 'positive'),
                        description=gesture_data.get('description', '')
                    )

            print(f"✅ 加载了 {len(self.static_gestures)} 个静态手势，{len(self.dynamic_gestures)} 个动态手势")

        except FileNotFoundError:
            print(f" 配置文件 {self.config_file} 不存在，使用默认配置")
            self._create_default_config()
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            self._create_default_config()

    def _create_default_config(self):
        """创建默认配置"""
        default_static_gestures = {
            'POINT_UP': {
                'name': '指向上',
                'confidence': 0.9,
                'fingers': {
                    'thumb': False,
                    'index': True,
                    'middle': False,
                    'ring': False,
                    'pinky': False
                },
                'description': '食指指向上方'
            },
            'THUMBS_UP': {
                'name': '点赞',
                'confidence': 0.9,
                'fingers': {
                    'thumb': True,
                    'index': False,
                    'middle': False,
                    'ring': False,
                    'pinky': False
                },
                'description': '大拇指向上'
            },
            'VICTORY': {
                'name': '胜利手势',
                'confidence': 0.8,
                'fingers': {
                    'thumb': False,
                    'index': True,
                    'middle': True,
                    'ring': False,
                    'pinky': False
                },
                'description': '食指和中指V字形'
            },
            'OK_SIGN': {
                'name': 'OK手势',
                'confidence': 0.8,
                'description': '拇指和食指形成圆圈'
            },
            'OPEN_PALM': {
                'name': '张开手掌',
                'confidence': 0.8,
                'fingers': {
                    'thumb': True,
                    'index': True,
                    'middle': True,
                    'ring': True,
                    'pinky': True
                },
                'description': '五指全部张开'
            },
            'CLOSED_FIST': {
                'name': '握拳',
                'confidence': 0.9,
                'fingers': {
                    'thumb': False,
                    'index': False,
                    'middle': False,
                    'ring': False,
                    'pinky': False
                },
                'description': '五指全部弯曲'
            }
        }

        default_dynamic_gestures = {
            'SWIPE_LEFT': {
                'name': '左滑',
                'confidence': 0.8,
                'min_distance': 0.1,
                'direction': 'horizontal',
                'sign': 'negative',
                'description': '手部向左滑动'
            },
            'SWIPE_RIGHT': {
                'name': '右滑',
                'confidence': 0.8,
                'min_distance': 0.1,
                'direction': 'horizontal',
                'sign': 'positive',
                'description': '手部向右滑动'
            },
            'SWIPE_UP': {
                'name': '上滑',
                'confidence': 0.8,
                'min_distance': 0.1,
                'direction': 'vertical',
                'sign': 'negative',
                'description': '手部向上滑动'
            },
            'SWIPE_DOWN': {
                'name': '下滑',
                'confidence': 0.8,
                'min_distance': 0.1,
                'direction': 'vertical',
                'sign': 'positive',
                'description': '手部向下滑动'
            }
        }

        # 创建内存中的配置
        for code, data in default_static_gestures.items():
            finger_config = FingerConfig(**data.get('fingers', {}))
            self.static_gestures[code] = GestureConfig(
                code=code,
                name=data.get('name', ''),
                type='static',
                confidence=data.get('confidence', 0.8),
                fingers=finger_config,
                description=data.get('description', '')
            )

        for code, data in default_dynamic_gestures.items():
            self.dynamic_gestures[code] = GestureConfig(
                code=code,
                name=data.get('name', ''),
                type='dynamic',
                confidence=data.get('confidence', 0.8),
                min_distance=data.get('min_distance', 0.1),
                direction=data.get('direction', 'horizontal'),
                sign=data.get('sign', 'positive'),
                description=data.get('description', '')
            )

    def recognize_static_gesture(self, finger_states: Dict[str, bool]) -> Optional[Tuple[str, float]]:
        """识别静态手势"""
        best_match = None
        best_confidence = 0.0

        for gesture_code, config in self.static_gestures.items():
            if self._match_finger_states(finger_states, config.fingers):
                if config.confidence > best_confidence:
                    best_match = gesture_code
                    best_confidence = config.confidence

        if best_match:
            return best_match, best_confidence
        return None

    def recognize_dynamic_gesture(self, dx: float, dy: float, distance: float) -> Optional[Tuple[str, float]]:
        """识别动态手势"""
        if distance < 0.05:  # 距离太小，不是手势
            return None

        best_match = None
        best_confidence = 0.0

        for gesture_code, config in self.dynamic_gestures.items():
            if self._match_dynamic_pattern(dx, dy, distance, config):
                if config.confidence > best_confidence:
                    best_match = gesture_code
                    best_confidence = config.confidence

        if best_match:
            return best_match, best_confidence
        return None

    def _match_finger_states(self, current_states: Dict[str, bool], config_states: Optional[FingerConfig]) -> bool:
        """匹配手指状态"""
        if config_states is None:
            return False

        # 检查每个手指的状态
        for finger, state in config_states.__dict__.items():
            if state is not None:  # 只检查配置中指定的手指
                if current_states.get(finger, False) != state:
                    return False

        return True

    def _match_dynamic_pattern(self, dx: float, dy: float, distance: float, config: GestureConfig) -> bool:
        """匹配动态模式"""
        # 检查距离
        if config.min_distance and distance < config.min_distance:
            return False

        # 检查方向
        if config.direction == 'horizontal':
            if abs(dy) > abs(dx) * 0.5:  # 垂直分量太大
                return False
            if config.sign == 'positive' and dx <= 0:
                return False
            if config.sign == 'negative' and dx >= 0:
                return False

        elif config.direction == 'vertical':
            if abs(dx) > abs(dy) * 0.5:  # 水平分量太大
                return False
            if config.sign == 'positive' and dy <= 0:
                return False
            if config.sign == 'negative' and dy >= 0:
                return False

        return True

    def list_gestures(self):
        """列出所有支持的手势"""
        print("🎯 支持的静态手势:")
        for code, config in self.static_gestures.items():
            print(f"  {code}: {config.name} (置信度: {config.confidence}) - {config.description}")

        print("\n🔄 支持的动态手势:")
        for code, config in self.dynamic_gestures.items():
            print(f"  {code}: {config.name} (置信度: {config.confidence}) - {config.description}")

    def save_config_template(self):
        """保存配置模板文件"""
        template = {
            'static_gestures': {
                'CUSTOM_STATIC': {
                    'name': '自定义静态手势',
                    'confidence': 0.8,
                    'fingers': {
                        'thumb': True,
                        'index': False,
                        'middle': True,
                        'ring': False,
                        'pinky': True
                    },
                    'description': '自定义静态手势描述'
                }
            },
            'dynamic_gestures': {
                'CUSTOM_DYNAMIC': {
                    'name': '自定义动态手势',
                    'confidence': 0.8,
                    'min_distance': 0.15,
                    'direction': 'horizontal',
                    'sign': 'negative',
                    'description': '自定义动态手势描述'
                }
            }
        }

        with open('gesture_definitions.yaml', 'w', encoding='utf-8') as f:
            yaml.dump(template, f, default_flow_style=False, allow_unicode=True)

        print("✅ 配置模板已保存到 gesture_definitions.yaml")

# 示例用法
def demo_configurable_detector():
    """演示可配置手势识别器"""
    print("🎯 可配置手势识别器演示")
    print("=" * 40)

    detector = ConfigurableGestureDetector()

    # 显示支持的手势
    detector.list_gestures()

    # 测试静态手势匹配
    print("\n测试静态手势匹配:")

    # 模拟手指状态
    finger_states = {
        'thumb': False,
        'index': True,
        'middle': False,
        'ring': False,
        'pinky': False
    }

    result = detector.recognize_static_gesture(finger_states)
    if result:
        print(f"✅ 识别到静态手势: {result[0]} (置信度: {result[1]})")

    # 测试动态手势匹配
    print("\n测试动态手势匹配:")
    result = detector.recognize_dynamic_gesture(dx=-0.2, dy=0.05, distance=0.15)
    if result:
        print(f"✅ 识别到动态手势: {result[0]} (置信度: {result[1]})")

    # 保存配置模板
    detector.save_config_template()

if __name__ == "__main__":
    demo_configurable_detector()