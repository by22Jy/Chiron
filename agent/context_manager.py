"""
ContextManager - 视觉上下文管理器

管理Agent的视觉上下文信息，包括YOLO检测结果、手势识别、状态信息等
为后端LLM提供丰富的环境上下文，提高命令理解准确性
"""

import json
import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging

@dataclass
class DetectedObject:
    """检测到的物体信息"""
    name: str
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]
    timestamp: float
    frame_id: int = 0

@dataclass
class GestureInfo:
    """手势信息"""
    gesture_type: str
    confidence: float
    hand_landmarks: Optional[List[List[float]]] = None
    timestamp: float = 0.0
    action: Optional[str] = None

@dataclass
class PoseInfo:
    """姿态信息"""
    pose_keypoints: Optional[List[List[float]]] = None
    bounding_box: Optional[List[int]] = None
    timestamp: float = 0.0
    person_detected: bool = False

@dataclass
class EmotionInfo:
    """情绪信息"""
    emotion: str
    confidence: float
    face_bbox: Optional[List[int]] = None
    timestamp: float = 0.0

@dataclass
class VisualContext:
    """完整的视觉上下文"""
    detected_objects: List[DetectedObject]
    current_gesture: Optional[GestureInfo]
    current_pose: Optional[PoseInfo]
    current_emotion: Optional[EmotionInfo]
    scene_description: str
    timestamp: float
    frame_id: int

class ContextManager:
    """视觉上下文管理器

    负责收集、管理和提供视觉上下文信息
    支持多线程安全的上下文更新和查询
    """

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)

        # 当前上下文
        self._current_context: Optional[VisualContext] = None
        self._context_lock = threading.RLock()

        # 历史记录（用于趋势分析）
        self._context_history: List[VisualContext] = []
        self._max_history_size = self.config.get("max_history_size", 100)

        # 物体追踪（用于物体持久化）
        self._object_tracker: Dict[str, DetectedObject] = {}
        self._object_timeout = self.config.get("object_timeout", 10.0)  # 物体保持时间（秒）

        # 上下文更新回调
        self._update_callbacks: List[callable] = []

        # 统计信息
        self._stats = {
            "total_updates": 0,
            "object_detections": 0,
            "gesture_detections": 0,
            "last_update": None
        }

        self.logger.info("ContextManager initialized")

    def update_context(self,
                      detected_objects: List[Dict[str, Any]] = None,
                      gesture_info: Dict[str, Any] = None,
                      pose_info: Dict[str, Any] = None,
                      emotion_info: Dict[str, Any] = None,
                      frame_id: int = 0) -> VisualContext:
        """更新视觉上下文

        Args:
            detected_objects: YOLO检测到的物体列表
            gesture_info: 手势识别信息
            pose_info: 姿态识别信息
            emotion_info: 情绪识别信息
            frame_id: 帧ID

        Returns:
            更新后的VisualContext对象
        """
        with self._context_lock:
            timestamp = time.time()

            # 处理检测到的物体
            processed_objects = self._process_detected_objects(detected_objects or [], timestamp)

            # 处理手势信息
            current_gesture = self._process_gesture_info(gesture_info, timestamp)

            # 处理姿态信息
            current_pose = self._process_pose_info(pose_info, timestamp)

            # 处理情绪信息
            current_emotion = self._process_emotion_info(emotion_info, timestamp)

            # 生成场景描述
            scene_description = self._generate_scene_description(processed_objects, current_gesture)

            # 创建新的上下文
            new_context = VisualContext(
                detected_objects=processed_objects,
                current_gesture=current_gesture,
                current_pose=current_pose,
                current_emotion=current_emotion,
                scene_description=scene_description,
                timestamp=timestamp,
                frame_id=frame_id
            )

            # 更新当前上下文
            self._current_context = new_context

            # 添加到历史记录
            self._add_to_history(new_context)

            # 更新统计信息
            self._update_stats(new_context)

            # 触发更新回调
            self._trigger_update_callbacks(new_context)

            self.logger.debug(f"Context updated: {len(processed_objects)} objects, "
                            f"gesture: {current_gesture.gesture_type if current_gesture else None}")

            return new_context

    def _process_detected_objects(self, objects_data: List[Dict[str, Any]], timestamp: float) -> List[DetectedObject]:
        """处理检测到的物体"""
        processed_objects = []
        current_time = time.time()

        for obj_data in objects_data:
            try:
                # 验证必要字段
                if not obj_data.get("name"):
                    self.logger.warning(f"Missing object name: {obj_data}")
                    continue

                obj = DetectedObject(
                    name=obj_data.get("name", "unknown"),
                    confidence=float(obj_data.get("confidence", 0.0)),
                    bbox=obj_data.get("bbox", []),
                    timestamp=timestamp,
                    frame_id=obj_data.get("frame_id", 0)
                )
                processed_objects.append(obj)

                # 更新物体追踪器
                self._object_tracker[obj.name] = obj

            except (ValueError, TypeError) as e:
                self.logger.warning(f"Invalid object data: {obj_data}, error: {e}")
                continue

        # 清理过期的物体追踪记录
        self._cleanup_expired_objects(current_time)

        # 添加持久化的物体（如果它们在当前帧中没有检测到）
        persistent_objects = self._get_persistent_objects(timestamp)
        for persistent_obj in persistent_objects:
            if persistent_obj.name not in [obj.name for obj in processed_objects]:
                processed_objects.append(persistent_obj)

        return processed_objects

    def _process_gesture_info(self, gesture_data: Dict[str, Any], timestamp: float) -> Optional[GestureInfo]:
        """处理手势信息"""
        if not gesture_data:
            return None

        try:
            return GestureInfo(
                gesture_type=gesture_data.get("gesture_type", ""),
                confidence=float(gesture_data.get("confidence", 0.0)),
                hand_landmarks=gesture_data.get("hand_landmarks"),
                timestamp=timestamp,
                action=gesture_data.get("action")
            )
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Invalid gesture data: {gesture_data}, error: {e}")
            return None

    def _process_pose_info(self, pose_data: Dict[str, Any], timestamp: float) -> Optional[PoseInfo]:
        """处理姿态信息"""
        if not pose_data:
            return None

        try:
            return PoseInfo(
                pose_keypoints=pose_data.get("pose_keypoints"),
                bounding_box=pose_data.get("bounding_box"),
                timestamp=timestamp,
                person_detected=pose_data.get("person_detected", False)
            )
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Invalid pose data: {pose_data}, error: {e}")
            return None

    def _process_emotion_info(self, emotion_data: Dict[str, Any], timestamp: float) -> Optional[EmotionInfo]:
        """处理情绪信息"""
        if not emotion_data:
            return None

        try:
            return EmotionInfo(
                emotion=emotion_data.get("emotion", ""),
                confidence=float(emotion_data.get("confidence", 0.0)),
                face_bbox=emotion_data.get("face_bbox"),
                timestamp=timestamp
            )
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Invalid emotion data: {emotion_data}, error: {e}")
            return None

    def _generate_scene_description(self, objects: List[DetectedObject], gesture: Optional[GestureInfo]) -> str:
        """生成场景描述"""
        if not objects and not gesture:
            return "场景中未检测到明显的物体或手势"

        description_parts = []

        if objects:
            # 按置信度排序物体
            sorted_objects = sorted(objects, key=lambda x: x.confidence, reverse=True)
            top_objects = sorted_objects[:5]  # 只取前5个最自信的物体

            object_names = [obj.name for obj in top_objects]
            if len(object_names) == 1:
                description_parts.append(f"检测到物体: {object_names[0]}")
            else:
                description_parts.append(f"检测到物体: {', '.join(object_names[:-1])} 和 {object_names[-1]}")

        if gesture:
            description_parts.append(f"当前手势: {gesture.gesture_type}")

        return "; ".join(description_parts)

    def _cleanup_expired_objects(self, current_time: float):
        """清理过期的物体追踪记录"""
        expired_keys = []
        for key, obj in self._object_tracker.items():
            if current_time - obj.timestamp > self._object_timeout:
                expired_keys.append(key)

        for key in expired_keys:
            del self._object_tracker[key]

    def _get_persistent_objects(self, current_timestamp: float) -> List[DetectedObject]:
        """获取持久化的物体（仍然有效的物体）"""
        persistent_objects = []
        for obj in self._object_tracker.values():
            if current_timestamp - obj.timestamp <= self._object_timeout:
                # 创建一个持久化的物体对象（置信度稍微降低）
                persistent_obj = DetectedObject(
                    name=obj.name,
                    confidence=obj.confidence * 0.8,  # 降低置信度
                    bbox=obj.bbox,
                    timestamp=obj.timestamp,
                    frame_id=obj.frame_id
                )
                persistent_objects.append(persistent_obj)

        return persistent_objects

    def _add_to_history(self, context: VisualContext):
        """添加到历史记录"""
        self._context_history.append(context)

        # 保持历史记录大小限制
        if len(self._context_history) > self._max_history_size:
            self._context_history = self._context_history[-self._max_history_size:]

    def _update_stats(self, context: VisualContext):
        """更新统计信息"""
        self._stats["total_updates"] += 1
        self._stats["object_detections"] += len(context.detected_objects)
        if context.current_gesture:
            self._stats["gesture_detections"] += 1
        self._stats["last_update"] = datetime.now().isoformat()

    def _trigger_update_callbacks(self, context: VisualContext):
        """触发更新回调"""
        for callback in self._update_callbacks:
            try:
                callback(context)
            except Exception as e:
                self.logger.error(f"Error in context update callback: {e}")

    def get_current_context(self) -> Optional[VisualContext]:
        """获取当前上下文"""
        with self._context_lock:
            return self._current_context

    def get_detected_objects(self) -> List[str]:
        """获取当前检测到的物体名称列表"""
        with self._context_lock:
            if not self._current_context:
                return []
            return [obj.name for obj in self._current_context.detected_objects]

    def get_scene_summary(self) -> Dict[str, Any]:
        """获取场景摘要（用于发送给后端LLM）"""
        with self._context_lock:
            if not self._current_context:
                return {
                    "scene_description": "无视觉上下文",
                    "detected_objects": [],
                    "current_gesture": None,
                    "timestamp": time.time()
                }

            context = self._current_context

            # 构建物体列表（只包含名称和置信度）
            objects_info = [
                {"name": obj.name, "confidence": obj.confidence}
                for obj in context.detected_objects
            ]

            # 构建手势信息
            gesture_info = None
            if context.current_gesture:
                gesture_info = {
                    "gesture_type": context.current_gesture.gesture_type,
                    "confidence": context.current_gesture.confidence,
                    "action": context.current_gesture.action
                }

            return {
                "scene_description": context.scene_description,
                "detected_objects": objects_info,
                "current_gesture": gesture_info,
                "pose_detected": context.current_pose.person_detected if context.current_pose else False,
                "emotion": context.current_emotion.emotion if context.current_emotion else None,
                "timestamp": context.timestamp,
                "frame_id": context.frame_id
            }

    def get_context_for_llm(self) -> Dict[str, Any]:
        """获取用于LLM的上下文信息

        Returns:
            格式化的上下文字典，包含LLM需要的关键信息
        """
        summary = self.get_scene_summary()

        # 添加额外的上下文信息用于LLM理解
        llm_context = {
            "visual_context": summary,
            "available_objects": summary["detected_objects"],
            "recent_gestures": [],  # 可以添加最近的手势历史
            "interaction_hints": self._generate_interaction_hints(summary),
            "timestamp": summary["timestamp"]
        }

        return llm_context

    def _generate_interaction_hints(self, scene_summary: Dict[str, Any]) -> List[str]:
        """生成交互提示（帮助LLM理解可能的用户意图）"""
        hints = []

        objects = scene_summary.get("detected_objects", [])
        if objects:
            object_names = [obj["name"] for obj in objects if obj["confidence"] > 0.5]
            if object_names:
                hints.append(f"用户可能想要与 {', '.join(object_names)} 进行交互")

        gesture = scene_summary.get("current_gesture")
        if gesture and gesture.get("gesture_type"):
            gesture_type = gesture["gesture_type"]
            if gesture_type == "POINT_UP":
                hints.append("用户正在指向某个物体，可能想要选择或打开它")
            elif gesture_type == "THUMBS_UP":
                hints.append("用户表示肯定或确认")
            elif gesture_type == "VICTORY":
                hints.append("用户做出胜利手势，可能表示成功或完成")
            elif gesture_type == "OK_SIGN":
                hints.append("用户表示OK或确认")

        return hints

    def add_update_callback(self, callback: callable):
        """添加上下文更新回调函数"""
        self._update_callbacks.append(callback)

    def remove_update_callback(self, callback: callable):
        """移除上下文更新回调函数"""
        if callback in self._update_callbacks:
            self._update_callbacks.remove(callback)

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self._context_lock:
            stats = self._stats.copy()
            stats["history_size"] = len(self._context_history)
            stats["tracked_objects"] = len(self._object_tracker)
            return stats

    def clear_context(self):
        """清空上下文"""
        with self._context_lock:
            self._current_context = None
            self._context_history.clear()
            self._object_tracker.clear()
            self.logger.info("Context cleared")

    def export_context(self, filepath: str):
        """导出当前上下文到文件"""
        with self._context_lock:
            if not self._current_context:
                raise ValueError("No context to export")

            context_data = {
                "current_context": asdict(self._current_context),
                "statistics": self.get_statistics(),
                "export_timestamp": datetime.now().isoformat()
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"Context exported to {filepath}")

    def __str__(self) -> str:
        """字符串表示"""
        with self._context_lock:
            if not self._current_context:
                return "ContextManager: No current context"

            obj_count = len(self._current_context.detected_objects)
            gesture = self._current_context.current_gesture
            gesture_str = f"gesture={gesture.gesture_type}" if gesture else "no_gesture"

            return f"ContextManager: {obj_count} objects, {gesture_str}, age={time.time() - self._current_context.timestamp:.1f}s"