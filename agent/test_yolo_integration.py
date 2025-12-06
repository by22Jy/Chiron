"""
YOLO集成测试

测试YOLO物体检测与ContextManager的集成
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from context_manager import ContextManager
from video_processor import VideoProcessor, VideoConfig

class TestYOLOIntegration(unittest.TestCase):
    """YOLO集成测试类"""

    def setUp(self):
        """测试前准备"""
        self.config = VideoConfig(
            yolo_detection_interval=0.5,  # 0.5秒检测间隔用于测试
            ai_service_url="http://127.0.0.1:8000"
        )
        self.gesture_mapping = {}
        self.context_manager = ContextManager({
            "max_history_size": 10,
            "object_timeout": 2.0
        })

    def test_video_processor_yolo_initialization(self):
        """测试VideoProcessor的YOLO功能初始化"""
        processor = VideoProcessor(self.config, self.gesture_mapping)

        # 验证YOLO相关属性
        self.assertTrue(hasattr(processor, 'yolo_detection_enabled'))
        self.assertTrue(hasattr(processor, 'yolo_objects'))
        self.assertTrue(hasattr(processor, 'on_yolo_objects_detected'))

    def test_context_manager_initialization(self):
        """测试ContextManager初始化"""
        self.assertIsNotNone(self.context_manager)
        self.assertIsNone(self.context_manager.get_current_context())

    def test_yolo_objects_callback_integration(self):
        """测试YOLO物体检测回调集成"""
        processor = VideoProcessor(self.config, self.gesture_mapping)

        # 设置回调
        callback_called = False
        detected_objects = []

        def test_callback(objects):
            nonlocal callback_called
            callback_called = True
            detected_objects.extend(objects)

        processor.on_yolo_objects_detected = test_callback

        # 模拟YOLO检测结果
        test_objects = [
            {"name": "cup", "confidence": 0.85, "bbox": [100, 100, 200, 200]},
            {"name": "laptop", "confidence": 0.92, "bbox": [300, 300, 500, 400]}
        ]

        # 调用回调（模拟检测到物体）
        if processor.on_yolo_objects_detected:
            processor.on_yolo_objects_detected(test_objects)

        # 验证回调被调用
        self.assertTrue(callback_called)
        self.assertEqual(len(detected_objects), 2)
        self.assertEqual(detected_objects[0]["name"], "cup")
        self.assertEqual(detected_objects[1]["name"], "laptop")

    def test_context_manager_yolo_integration(self):
        """测试ContextManager与YOLO检测的集成"""
        # 模拟YOLO检测结果
        detected_objects = [
            {"name": "phone", "confidence": 0.88, "bbox": [50, 50, 150, 150]},
            {"name": "book", "confidence": 0.76, "bbox": [200, 100, 300, 200]}
        ]

        # 更新ContextManager
        context = self.context_manager.update_context(
            detected_objects=detected_objects,
            frame_id=1
        )

        # 验证上下文更新
        self.assertEqual(len(context.detected_objects), 2)
        self.assertEqual(context.detected_objects[0].name, "phone")
        self.assertEqual(context.detected_objects[1].name, "book")

        # 验证获取物体列表
        object_names = self.context_manager.get_detected_objects()
        self.assertIn("phone", object_names)
        self.assertIn("book", object_names)

    def test_context_manager_llm_format(self):
        """测试ContextManager的LLM格式输出"""
        # 添加一些物体到上下文
        detected_objects = [
            {"name": "keyboard", "confidence": 0.93, "bbox": [100, 300, 400, 350]},
            {"name": "mouse", "confidence": 0.81, "bbox": [450, 320, 500, 370]}
        ]

        self.context_manager.update_context(detected_objects=detected_objects, frame_id=1)

        # 获取LLM格式上下文
        llm_context = self.context_manager.get_context_for_llm()

        # 验证LLM上下文结构
        self.assertIn("visual_context", llm_context)
        self.assertIn("available_objects", llm_context)
        self.assertIn("interaction_hints", llm_context)
        self.assertIn("timestamp", llm_context)

        # 验证物体信息
        visual_context = llm_context["visual_context"]
        self.assertEqual(len(visual_context["detected_objects"]), 2)
        self.assertEqual(visual_context["detected_objects"][0]["name"], "keyboard")
        self.assertEqual(visual_context["detected_objects"][1]["name"], "mouse")

        # 验证交互提示
        hints = llm_context["interaction_hints"]
        self.assertTrue(len(hints) > 0)
        self.assertTrue(any("keyboard" in hint for hint in hints))

    @patch('requests.post')
    def test_yolo_detection_api_call(self, mock_post):
        """测试YOLO检测API调用"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "objects": [
                {"name": "monitor", "confidence": 0.95, "bbox": [0, 0, 800, 600]}
            ]
        }
        mock_post.return_value = mock_response

        processor = VideoProcessor(self.config, self.gesture_mapping)

        # 模拟帧数据
        import numpy as np
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # 调用YOLO检测
        detected_objects = processor.detect_yolo_objects(frame)

        # 验证API调用
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        self.assertEqual(call_args[0][0], "http://127.0.0.1:8000/detect/file")
        self.assertIn("image", call_args[1]["json"])

        # 验证返回结果
        self.assertEqual(len(detected_objects), 1)
        self.assertEqual(detected_objects[0]["name"], "monitor")
        self.assertEqual(detected_objects[0]["confidence"], 0.95)

    def test_yolo_detection_disabled(self):
        """测试YOLO检测禁用时的行为"""
        processor = VideoProcessor(self.config, self.gesture_mapping)
        processor.set_yolo_detection_enabled(False)

        # 模拟帧数据
        import numpy as np
        frame = np.zeros((480, 640, 3), dtype=np.uint8)

        # 调用YOLO检测
        detected_objects = processor.detect_yolo_objects(frame)

        # 验证返回空列表
        self.assertEqual(len(detected_objects), 0)

    def test_scene_description_generation(self):
        """测试场景描述生成"""
        # 添加物体和手势到上下文
        detected_objects = [
            {"name": "cup", "confidence": 0.85, "bbox": [100, 100, 200, 200]},
            {"name": "laptop", "confidence": 0.92, "bbox": [300, 200, 600, 400]}
        ]

        gesture_data = {
            "gesture_type": "POINT_UP",
            "confidence": 0.78,
            "action": "select"
        }

        context = self.context_manager.update_context(
            detected_objects=detected_objects,
            gesture_info=gesture_data,
            frame_id=1
        )

        # 验证场景描述
        self.assertIn("cup", context.scene_description)
        self.assertIn("laptop", context.scene_description)
        self.assertIn("POINT_UP", context.scene_description)

    def test_object_persistence(self):
        """测试物体持久化功能"""
        # 第一次检测
        detected_objects_1 = [
            {"name": "book", "confidence": 0.9, "bbox": [200, 200, 300, 300]}
        ]
        self.context_manager.update_context(detected_objects=detected_objects_1, frame_id=1)

        # 短时间内第二次检测（没有新物体）
        context_2 = self.context_manager.update_context(detected_objects=[], frame_id=2)

        # 验证物体仍然存在（持久化）
        book_objects = [obj for obj in context_2.detected_objects if obj.name == "book"]
        self.assertEqual(len(book_objects), 1)
        # 持久化的物体置信度应该降低
        self.assertLess(book_objects[0].confidence, 0.9)

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)