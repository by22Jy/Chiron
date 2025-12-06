"""
Context Manager集成测试

测试ContextManager的核心功能和集成
"""

import unittest
import sys
import os
import time

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(__file__))

from context_manager import ContextManager

class TestContextIntegration(unittest.TestCase):
    """Context Manager集成测试类"""

    def setUp(self):
        """测试前准备"""
        self.config = {
            "max_history_size": 10,
            "object_timeout": 2.0
        }
        self.context_manager = ContextManager(self.config)

    def test_context_manager_initialization(self):
        """测试ContextManager初始化"""
        self.assertIsNotNone(self.context_manager)
        self.assertIsNone(self.context_manager.get_current_context())
        self.assertEqual(len(self.context_manager.get_detected_objects()), 0)

    def test_yolo_objects_integration(self):
        """测试YOLO物体检测集成"""
        # 模拟YOLO检测结果
        detected_objects = [
            {"name": "cup", "confidence": 0.85, "bbox": [100, 100, 200, 200]},
            {"name": "laptop", "confidence": 0.92, "bbox": [300, 300, 500, 400]}
        ]

        # 更新ContextManager
        context = self.context_manager.update_context(
            detected_objects=detected_objects,
            frame_id=1
        )

        # 验证上下文更新
        self.assertEqual(len(context.detected_objects), 2)
        self.assertEqual(context.detected_objects[0].name, "cup")
        self.assertEqual(context.detected_objects[1].name, "laptop")

        # 验证获取物体列表
        object_names = self.context_manager.get_detected_objects()
        self.assertIn("cup", object_names)
        self.assertIn("laptop", object_names)

    def test_scene_summary_generation(self):
        """测试场景摘要生成"""
        # 添加物体到上下文
        detected_objects = [
            {"name": "keyboard", "confidence": 0.93, "bbox": [100, 300, 400, 350]},
            {"name": "mouse", "confidence": 0.81, "bbox": [450, 320, 500, 370]}
        ]

        self.context_manager.update_context(detected_objects=detected_objects, frame_id=1)

        # 获取场景摘要
        summary = self.context_manager.get_scene_summary()

        # 验证摘要内容
        self.assertIn("scene_description", summary)
        self.assertIn("detected_objects", summary)
        self.assertIn("timestamp", summary)
        self.assertEqual(len(summary["detected_objects"]), 2)

    def test_llm_context_format(self):
        """测试LLM格式上下文输出"""
        # 添加物体和手势到上下文
        detected_objects = [
            {"name": "phone", "confidence": 0.88, "bbox": [50, 50, 150, 150]},
            {"name": "book", "confidence": 0.76, "bbox": [200, 100, 300, 200]}
        ]

        gesture_data = {
            "gesture_type": "POINT_UP",
            "confidence": 0.78,
            "action": "select"
        }

        self.context_manager.update_context(
            detected_objects=detected_objects,
            gesture_info=gesture_data,
            frame_id=1
        )

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
        self.assertEqual(visual_context["detected_objects"][0]["name"], "phone")
        self.assertEqual(visual_context["detected_objects"][1]["name"], "book")

        # 验证手势信息
        self.assertIsNotNone(visual_context["current_gesture"])
        self.assertEqual(visual_context["current_gesture"]["gesture_type"], "POINT_UP")

        # 验证交互提示
        hints = llm_context["interaction_hints"]
        self.assertTrue(len(hints) > 0)
        self.assertTrue(any("phone" in hint or "book" in hint for hint in hints))
        self.assertTrue(any("指向" in hint for hint in hints))

    def test_interaction_hints_generation(self):
        """测试交互提示生成"""
        # 测试指向手势的提示
        gesture_data = {
            "gesture_type": "POINT_UP",
            "confidence": 0.9,
            "action": "select"
        }

        detected_objects = [
            {"name": "monitor", "confidence": 0.95, "bbox": [0, 0, 800, 600]}
        ]

        llm_context = self.context_manager.get_context_for_llm()
        # 手动调用内部方法来测试提示生成
        hints = self.context_manager._generate_interaction_hints({
            "detected_objects": detected_objects,
            "current_gesture": gesture_data
        })

        self.assertTrue(len(hints) > 0)
        self.assertTrue(any("monitor" in hint for hint in hints))
        self.assertTrue(any("指向" in hint for hint in hints))

        # 测试确认手势的提示
        gesture_data["gesture_type"] = "THUMBS_UP"
        hints = self.context_manager._generate_interaction_hints({
            "detected_objects": detected_objects,
            "current_gesture": gesture_data
        })

        # THUMBS_UP手势应该有肯定的提示
        self.assertTrue(len(hints) > 0)

    def test_object_persistence(self):
        """测试物体持久化功能"""
        # 第一次检测
        detected_objects_1 = [
            {"name": "book", "confidence": 0.9, "bbox": [200, 200, 300, 300]}
        ]
        self.context_manager.update_context(detected_objects=detected_objects_1, frame_id=1)

        # 验证物体被检测到
        objects_after_first = self.context_manager.get_detected_objects()
        self.assertIn("book", objects_after_first)

        # 短时间内第二次检测（没有新物体）
        time.sleep(0.1)  # 等待一小段时间
        context_2 = self.context_manager.update_context(detected_objects=[], frame_id=2)

        # 验证物体仍然存在（持久化）
        book_objects = [obj for obj in context_2.detected_objects if obj.name == "book"]
        self.assertEqual(len(book_objects), 1)
        # 持久化的物体置信度应该降低
        self.assertLess(book_objects[0].confidence, 0.9)

    def test_gesture_integration(self):
        """测试手势信息集成"""
        # 测试不同手势类型
        gestures = [
            {"gesture_type": "VICTORY", "confidence": 0.85, "action": "toggle"},
            {"gesture_type": "OK_SIGN", "confidence": 0.78, "action": "confirm"},
            {"gesture_type": "THUMBS_UP", "confidence": 0.92, "action": "approve"}
        ]

        for gesture_data in gestures:
            context = self.context_manager.update_context(
                gesture_info=gesture_data,
                frame_id=len(self.context_manager._context_history) + 1
            )

            self.assertIsNotNone(context.current_gesture)
            self.assertEqual(context.current_gesture.gesture_type, gesture_data["gesture_type"])
            self.assertEqual(context.current_gesture.confidence, gesture_data["confidence"])
            self.assertEqual(context.current_gesture.action, gesture_data["action"])

    def test_emotion_integration(self):
        """测试情绪信息集成"""
        emotion_data = {
            "emotion": "happy",
            "confidence": 0.87,
            "face_bbox": [150, 100, 250, 200]
        }

        context = self.context_manager.update_context(
            emotion_info=emotion_data,
            frame_id=1
        )

        self.assertIsNotNone(context.current_emotion)
        self.assertEqual(context.current_emotion.emotion, "happy")
        self.assertEqual(context.current_emotion.confidence, 0.87)

        # 获取LLM上下文并验证情绪信息
        llm_context = self.context_manager.get_context_for_llm()
        visual_context = llm_context["visual_context"]
        self.assertEqual(visual_context["emotion"], "happy")

    def test_history_management(self):
        """测试历史记录管理"""
        # 创建多个上下文更新
        for i in range(15):  # 超过配置的最大历史记录大小(10)
            detected_objects = [
                {"name": f"object_{i}", "confidence": 0.8, "bbox": [0, 0, 10, 10]}
            ]
            self.context_manager.update_context(detected_objects=detected_objects, frame_id=i)

        # 验证历史记录大小限制
        stats = self.context_manager.get_statistics()
        self.assertEqual(stats["history_size"], 10)  # 应该限制为配置的最大值
        self.assertEqual(stats["total_updates"], 15)  # 但总更新次数应该正确

    def test_statistics_tracking(self):
        """测试统计信息跟踪"""
        # 初始统计信息
        stats = self.context_manager.get_statistics()
        self.assertEqual(stats["total_updates"], 0)
        self.assertEqual(stats["object_detections"], 0)
        self.assertEqual(stats["gesture_detections"], 0)

        # 添加一些上下文
        self.context_manager.update_context(
            detected_objects=[{"name": "test", "confidence": 0.9, "bbox": [0, 0, 10, 10]}],
            gesture_info={"gesture_type": "POINT_UP", "confidence": 0.8},
            frame_id=1
        )

        # 验证统计信息更新
        stats = self.context_manager.get_statistics()
        self.assertEqual(stats["total_updates"], 1)
        self.assertEqual(stats["object_detections"], 1)
        self.assertEqual(stats["gesture_detections"], 1)

    def test_error_handling(self):
        """测试错误处理"""
        # 测试无效的物体数据
        invalid_objects = [
            {"name": "invalid", "confidence": "invalid_confidence"},  # 无效的置信度
            {"confidence": 0.5},  # 缺少名称
        ]

        # 应该不会抛出异常，而是跳过无效数据
        context = self.context_manager.update_context(detected_objects=invalid_objects, frame_id=1)
        self.assertEqual(len(context.detected_objects), 0)

        # 测试无效的手势数据
        invalid_gesture = {
            "gesture_type": "INVALID",
            "confidence": "invalid_confidence"
        }

        context = self.context_manager.update_context(gesture_info=invalid_gesture, frame_id=2)
        self.assertIsNone(context.current_gesture)

    def test_callback_system(self):
        """测试回调系统"""
        callback_called = []
        callback_contexts = []

        def test_callback(context):
            callback_called.append(True)
            callback_contexts.append(context)

        # 注册回调
        self.context_manager.add_update_callback(test_callback)

        # 更新上下文
        test_objects = [{"name": "callback_test", "confidence": 0.9, "bbox": [0, 0, 10, 10]}]
        context = self.context_manager.update_context(detected_objects=test_objects, frame_id=1)

        # 验证回调被调用
        self.assertEqual(len(callback_called), 1)
        self.assertEqual(callback_contexts[0], context)

        # 移除回调
        self.context_manager.remove_update_callback(test_callback)
        self.context_manager.update_context(detected_objects=test_objects, frame_id=2)

        # 验证回调不再被调用
        self.assertEqual(len(callback_called), 1)

if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)