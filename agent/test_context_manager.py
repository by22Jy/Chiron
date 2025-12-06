"""
ContextManager单元测试

测试视觉上下文管理器的各项功能
"""

import unittest
import time
import json
import tempfile
import os
from context_manager import ContextManager, VisualContext, DetectedObject, GestureInfo, EmotionInfo

class TestContextManager(unittest.TestCase):
    """ContextManager测试类"""

    def setUp(self):
        """测试前准备"""
        self.config = {
            "max_history_size": 10,
            "object_timeout": 2.0
        }
        self.context_manager = ContextManager(self.config)

    def test_context_creation(self):
        """测试上下文管理器创建"""
        self.assertIsNotNone(self.context_manager)
        self.assertIsNone(self.context_manager.get_current_context())
        self.assertEqual(len(self.context_manager.get_detected_objects()), 0)

    def test_update_context_with_objects(self):
        """测试更新物体检测上下文"""
        # 模拟YOLO检测结果
        detected_objects = [
            {
                "name": "cup",
                "confidence": 0.85,
                "bbox": [100, 100, 200, 200],
                "frame_id": 1
            },
            {
                "name": "laptop",
                "confidence": 0.92,
                "bbox": [300, 200, 600, 400],
                "frame_id": 1
            }
        ]

        context = self.context_manager.update_context(
            detected_objects=detected_objects,
            frame_id=1
        )

        # 验证上下文
        self.assertIsInstance(context, VisualContext)
        self.assertEqual(len(context.detected_objects), 2)
        self.assertEqual(context.detected_objects[0].name, "cup")
        self.assertEqual(context.detected_objects[1].name, "laptop")
        self.assertIsNone(context.current_gesture)

        # 验证获取方法
        object_names = self.context_manager.get_detected_objects()
        self.assertIn("cup", object_names)
        self.assertIn("laptop", object_names)

    def test_update_context_with_gesture(self):
        """测试更新手势信息"""
        gesture_data = {
            "gesture_type": "POINT_UP",
            "confidence": 0.78,
            "action": "select",
            "hand_landmarks": [[0.1, 0.2], [0.3, 0.4]]
        }

        context = self.context_manager.update_context(
            gesture_info=gesture_data,
            frame_id=2
        )

        # 验证手势信息
        self.assertIsNotNone(context.current_gesture)
        self.assertEqual(context.current_gesture.gesture_type, "POINT_UP")
        self.assertEqual(context.current_gesture.confidence, 0.78)
        self.assertEqual(context.current_gesture.action, "select")

    def test_update_context_with_emotion(self):
        """测试更新情绪信息"""
        emotion_data = {
            "emotion": "happy",
            "confidence": 0.65,
            "face_bbox": [150, 100, 250, 200]
        }

        context = self.context_manager.update_context(
            emotion_info=emotion_data,
            frame_id=3
        )

        # 验证情绪信息
        self.assertIsNotNone(context.current_emotion)
        self.assertEqual(context.current_emotion.emotion, "happy")
        self.assertEqual(context.current_emotion.confidence, 0.65)

    def test_full_context_update(self):
        """测试完整上下文更新"""
        detected_objects = [
            {"name": "phone", "confidence": 0.88, "bbox": [50, 50, 150, 150]}
        ]
        gesture_data = {
            "gesture_type": "THUMBS_UP",
            "confidence": 0.91,
            "action": "confirm"
        }
        emotion_data = {
            "emotion": "neutral",
            "confidence": 0.72
        }

        context = self.context_manager.update_context(
            detected_objects=detected_objects,
            gesture_info=gesture_data,
            emotion_info=emotion_data,
            frame_id=4
        )

        # 验证完整上下文
        self.assertEqual(len(context.detected_objects), 1)
        self.assertEqual(context.detected_objects[0].name, "phone")
        self.assertEqual(context.current_gesture.gesture_type, "THUMBS_UP")
        self.assertEqual(context.current_emotion.emotion, "neutral")
        self.assertIn("phone", context.scene_description)
        self.assertIn("THUMBS_UP", context.scene_description)

    def test_object_persistence(self):
        """测试物体持久化功能"""
        # 第一次更新 - 检测到杯子
        detected_objects = [
            {"name": "cup", "confidence": 0.9, "bbox": [100, 100, 200, 200]}
        ]
        self.context_manager.update_context(detected_objects=detected_objects, frame_id=1)

        # 第二次更新 - 没有检测到杯子（但在超时时间内）
        time.sleep(0.5)  # 等待0.5秒
        context = self.context_manager.update_context(detected_objects=[], frame_id=2)

        # 验证杯子仍然存在（持久化）
        cup_objects = [obj for obj in context.detected_objects if obj.name == "cup"]
        self.assertEqual(len(cup_objects), 1)
        # 持久化的物体置信度应该降低
        self.assertLess(cup_objects[0].confidence, 0.9)

    def test_object_timeout(self):
        """测试物体超时清理"""
        # 检测到物体
        detected_objects = [
            {"name": "book", "confidence": 0.85, "bbox": [200, 200, 300, 300]}
        ]
        self.context_manager.update_context(detected_objects=detected_objects, frame_id=1)

        # 等待超过超时时间
        time.sleep(2.5)  # 超过2秒的超时时间
        context = self.context_manager.update_context(detected_objects=[], frame_id=2)

        # 验证物体已被清理
        book_objects = [obj for obj in context.detected_objects if obj.name == "book"]
        self.assertEqual(len(book_objects), 0)

    def test_scene_summary(self):
        """测试场景摘要生成"""
        detected_objects = [
            {"name": "keyboard", "confidence": 0.93, "bbox": [100, 300, 400, 350]},
            {"name": "mouse", "confidence": 0.76, "bbox": [450, 320, 500, 370]}
        ]
        gesture_data = {
            "gesture_type": "OK_SIGN",
            "confidence": 0.84
        }

        self.context_manager.update_context(
            detected_objects=detected_objects,
            gesture_info=gesture_data,
            frame_id=5
        )

        summary = self.context_manager.get_scene_summary()

        # 验证摘要内容
        self.assertIn("keyboard", summary["scene_description"])
        self.assertIn("mouse", summary["scene_description"])
        self.assertIn("OK_SIGN", summary["scene_description"])
        self.assertEqual(len(summary["detected_objects"]), 2)
        self.assertEqual(summary["current_gesture"]["gesture_type"], "OK_SIGN")

    def test_context_for_llm(self):
        """测试LLM上下文格式"""
        detected_objects = [
            {"name": "monitor", "confidence": 0.95, "bbox": [0, 0, 800, 600]}
        ]
        gesture_data = {
            "gesture_type": "POINT_UP",
            "confidence": 0.87,
            "action": "select"
        }

        self.context_manager.update_context(
            detected_objects=detected_objects,
            gesture_info=gesture_data,
            frame_id=6
        )

        llm_context = self.context_manager.get_context_for_llm()

        # 验证LLM上下文结构
        self.assertIn("visual_context", llm_context)
        self.assertIn("available_objects", llm_context)
        self.assertIn("interaction_hints", llm_context)
        self.assertIn("timestamp", llm_context)

        # 验证交互提示
        hints = llm_context["interaction_hints"]
        self.assertTrue(any("monitor" in hint for hint in hints))
        self.assertTrue(any("指向" in hint for hint in hints))

    def test_history_management(self):
        """测试历史记录管理"""
        # 创建多个上下文更新
        for i in range(15):  # 超过配置的最大历史记录大小(10)
            self.context_manager.update_context(
                detected_objects=[{"name": f"object_{i}", "confidence": 0.8, "bbox": [0, 0, 10, 10]}],
                frame_id=i
            )

        # 验证历史记录大小限制
        stats = self.context_manager.get_statistics()
        self.assertEqual(stats["history_size"], 10)  # 应该限制为配置的最大值
        self.assertEqual(stats["total_updates"], 15)  # 但总更新次数应该正确

    def test_update_callbacks(self):
        """测试更新回调机制"""
        callback_called = []
        callback_context = None

        def test_callback(context):
            callback_called.append(True)
            nonlocal callback_context
            callback_context = context

        # 注册回调
        self.context_manager.add_update_callback(test_callback)

        # 更新上下文
        test_objects = [{"name": "test_item", "confidence": 0.9, "bbox": [0, 0, 10, 10]}]
        context = self.context_manager.update_context(detected_objects=test_objects, frame_id=7)

        # 验证回调被调用
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_context, context)

        # 移除回调
        self.context_manager.remove_update_callback(test_callback)
        self.context_manager.update_context(detected_objects=test_objects, frame_id=8)

        # 验证回调不再被调用
        self.assertEqual(len(callback_called), 1)

    def test_context_export(self):
        """测试上下文导出"""
        # 创建一些上下文数据
        detected_objects = [
            {"name": "export_test", "confidence": 0.88, "bbox": [10, 10, 20, 20]}
        ]
        self.context_manager.update_context(detected_objects=detected_objects, frame_id=9)

        # 导出到临时文件
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name

        try:
            self.context_manager.export_context(temp_file)

            # 验证导出文件
            with open(temp_file, 'r', encoding='utf-8') as f:
                exported_data = json.load(f)

            self.assertIn("current_context", exported_data)
            self.assertIn("statistics", exported_data)
            self.assertIn("export_timestamp", exported_data)

            # 验证导出的上下文数据
            current_context = exported_data["current_context"]
            self.assertEqual(len(current_context["detected_objects"]), 1)
            self.assertEqual(current_context["detected_objects"][0]["name"], "export_test")

        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.unlink(temp_file)

    def test_context_clear(self):
        """测试上下文清空"""
        # 创建一些上下文
        self.context_manager.update_context(
            detected_objects=[{"name": "clear_test", "confidence": 0.9, "bbox": [0, 0, 10, 10]}],
            frame_id=10
        )

        # 验证上下文存在
        self.assertIsNotNone(self.context_manager.get_current_context())

        # 清空上下文
        self.context_manager.clear_context()

        # 验证上下文已清空
        self.assertIsNone(self.context_manager.get_current_context())
        self.assertEqual(len(self.context_manager.get_detected_objects()), 0)

    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效的物体数据
        invalid_objects = [
            {"name": "invalid", "confidence": "invalid_confidence"},  # 无效的置信度
            {"confidence": 0.5},  # 缺少名称
        ]

        # 应该不会抛出异常，而是跳过无效数据
        context = self.context_manager.update_context(detected_objects=invalid_objects, frame_id=11)
        self.assertEqual(len(context.detected_objects), 0)

        # 测试无效的手势数据
        invalid_gesture = {
            "gesture_type": "INVALID",
            "confidence": "invalid_confidence"
        }

        context = self.context_manager.update_context(gesture_info=invalid_gesture, frame_id=12)
        self.assertIsNone(context.current_gesture)

    def test_string_representation(self):
        """测试字符串表示"""
        # 空上下文
        str_empty = str(self.context_manager)
        self.assertIn("No current context", str_empty)

        # 有上下文
        self.context_manager.update_context(
            detected_objects=[{"name": "string_test", "confidence": 0.9, "bbox": [0, 0, 10, 10]}],
            frame_id=13
        )

        str_with_context = str(self.context_manager)
        self.assertIn("1 objects", str_with_context)
        self.assertIn("no_gesture", str_with_context)

if __name__ == '__main__':
    unittest.main()