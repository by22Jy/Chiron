"""
VisualStatusReporter - 视觉状态上报器

负责定期向后端上报视觉状态信息，包括：
- 检测到的物体列表
- 手势识别状态
- 场景变化分析
- 上下文摘要
"""

import time
import threading
import json
import logging
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from context_manager import ContextManager, VisualContext

@dataclass
class VisualStatusReport:
    """视觉状态报告"""
    timestamp: float
    detected_objects: List[Dict[str, Any]]
    current_gesture: Optional[Dict[str, Any]]
    scene_description: str
    object_count: int
    gesture_count: int
    scene_changes: List[str]
    context_summary: str
    frame_id: int

@dataclass
class SceneChange:
    """场景变化记录"""
    change_type: str  # 'object_added', 'object_removed', 'gesture_detected'
    description: str
    confidence: float
    timestamp: float

class VisualStatusReporter:
    """视觉状态上报器

    定期收集视觉上下文信息并上报给后端系统
    支持场景变化检测和智能摘要生成
    """

    def __init__(self, base_url: str, context_manager: ContextManager, config: Dict[str, Any] = None):
        self.base_url = base_url.rstrip('/')
        self.context_manager = context_manager
        self.config = config or {}

        # 配置参数
        self.report_interval = self.config.get("report_interval", 30.0)  # 30秒上报一次
        self.api_timeout = self.config.get("api_timeout", 10.0)
        self.enable_change_detection = self.config.get("enable_change_detection", True)
        self.max_scene_changes = self.config.get("max_scene_changes", 10)

        # 状态管理
        self.last_report: Optional[VisualStatusReport] = None
        self.last_objects: List[str] = []
        self.last_gesture: Optional[str] = None
        self.scene_changes: List[SceneChange] = []

        # 线程控制
        self.running = False
        self.report_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

        # 统计信息
        self.stats = {
            "total_reports": 0,
            "successful_reports": 0,
            "failed_reports": 0,
            "scene_changes_detected": 0,
            "last_report_time": None,
            "start_time": time.time()
        }

        self.logger = logging.getLogger(__name__)
        self.logger.info("VisualStatusReporter initialized")

    def start(self):
        """启动定期上报"""
        if self.running:
            self.logger.warning("VisualStatusReporter is already running")
            return

        self.running = True
        self.stop_event.clear()

        self.report_thread = threading.Thread(
            target=self._report_loop,
            name="VisualStatusReporter",
            daemon=True
        )
        self.report_thread.start()

        self.logger.info(f"VisualStatusReporter started (interval: {self.report_interval}s)")

    def stop(self):
        """停止定期上报"""
        if not self.running:
            return

        self.logger.info("Stopping VisualStatusReporter...")
        self.running = False
        self.stop_event.set()

        if self.report_thread and self.report_thread.is_alive():
            self.report_thread.join(timeout=5.0)

        self.logger.info("VisualStatusReporter stopped")

    def _report_loop(self):
        """上报循环"""
        while self.running and not self.stop_event.is_set():
            try:
                self._generate_and_send_report()

                # 等待下次上报
                self.stop_event.wait(self.report_interval)

            except Exception as e:
                self.logger.error(f"Error in report loop: {e}")
                # 出错时等待较短时间后重试
                self.stop_event.wait(5.0)

    def _generate_and_send_report(self):
        """生成并发送报告"""
        try:
            # 生成当前报告
            current_report = self._generate_current_report()

            if current_report:
                # 发送到后端
                success = self._send_report_to_backend(current_report)

                # 更新统计信息
                self._update_stats(success)

                # 更新上次报告状态
                if success:
                    self.last_report = current_report
                    self._update_last_state(current_report)
                    return True  # Return True on successful send

        except Exception as e:
            self.logger.error(f"Error generating/sending report: {e}")
            self.stats["failed_reports"] += 1

        return False  # Return False on failure

    def _generate_current_report(self) -> Optional[VisualStatusReport]:
        """生成当前视觉状态报告"""
        try:
            # 获取当前上下文
            context = self.context_manager.get_current_context()
            if not context:
                return None

            # 获取场景摘要
            scene_summary = self.context_manager.get_scene_summary()

            # 检测场景变化
            if self.enable_change_detection:
                self._detect_scene_changes(context)

            # 转换物体信息
            detected_objects = []
            for obj in context.detected_objects:
                detected_objects.append({
                    "name": obj.name,
                    "confidence": obj.confidence,
                    "bbox": obj.bbox
                })

            # 转换手势信息
            current_gesture = None
            if context.current_gesture:
                current_gesture = {
                    "gesture_type": context.current_gesture.gesture_type,
                    "confidence": context.current_gesture.confidence,
                    "action": context.current_gesture.action
                }

            # 生成上下文摘要
            context_summary = self._generate_context_summary(context)

            # 创建报告
            report = VisualStatusReport(
                timestamp=context.timestamp,
                detected_objects=detected_objects,
                current_gesture=current_gesture,
                scene_description=context.scene_description,
                object_count=len(detected_objects),
                gesture_count=1 if current_gesture else 0,
                scene_changes=[asdict(change) for change in self.scene_changes[-self.max_scene_changes:]],
                context_summary=context_summary,
                frame_id=context.frame_id
            )

            return report

        except Exception as e:
            self.logger.error(f"Error generating current report: {e}")
            return None

    def _detect_scene_changes(self, context: VisualContext):
        """检测场景变化"""
        current_objects = [obj.name for obj in context.detected_objects]
        current_gesture = context.current_gesture.gesture_type if context.current_gesture else None

        # 检测物体变化
        if set(current_objects) != set(self.last_objects):
            # 新增的物体
            added_objects = set(current_objects) - set(self.last_objects)
            for obj_name in added_objects:
                obj = next((o for o in context.detected_objects if o.name == obj_name), None)
                if obj:
                    change = SceneChange(
                        change_type="object_added",
                        description=f"检测到新物体: {obj_name}",
                        confidence=obj.confidence,
                        timestamp=context.timestamp
                    )
                    self.scene_changes.append(change)
                    self.stats["scene_changes_detected"] += 1

            # 移除的物体
            removed_objects = set(self.last_objects) - set(current_objects)
            for obj_name in removed_objects:
                change = SceneChange(
                    change_type="object_removed",
                    description=f"物体消失: {obj_name}",
                    confidence=1.0,
                    timestamp=context.timestamp
                )
                self.scene_changes.append(change)
                self.stats["scene_changes_detected"] += 1

        # 检测手势变化
        if current_gesture != self.last_gesture and current_gesture:
            if context.current_gesture:
                change = SceneChange(
                    change_type="gesture_detected",
                    description=f"检测到手势: {current_gesture}",
                    confidence=context.current_gesture.confidence,
                    timestamp=context.timestamp
                )
                self.scene_changes.append(change)
                self.stats["scene_changes_detected"] += 1

        # 限制变化记录数量
        if len(self.scene_changes) > self.max_scene_changes * 2:
            self.scene_changes = self.scene_changes[-self.max_scene_changes:]

    def _generate_context_summary(self, context: VisualContext) -> str:
        """生成上下文摘要"""
        summary_parts = []

        # 物体摘要
        if context.detected_objects:
            high_confidence_objects = [obj for obj in context.detected_objects if obj.confidence > 0.7]
            if high_confidence_objects:
                object_names = [obj.name for obj in high_confidence_objects[:3]]  # 只取前3个
                summary_parts.append(f"主要物体: {', '.join(object_names)}")

        # 手势摘要
        if context.current_gesture:
            summary_parts.append(f"当前手势: {context.current_gesture.gesture_type}")

        # 情绪摘要
        if context.current_emotion:
            summary_parts.append(f"情绪状态: {context.current_emotion.emotion}")

        return "; ".join(summary_parts) if summary_parts else "场景状态稳定"

    def _send_report_to_backend(self, report: VisualStatusReport) -> bool:
        """发送报告到后端"""
        try:
            # 准备请求数据
            payload = {
                "eventType": "visual_status_report",
                "payload": json.dumps(asdict(report), ensure_ascii=False),
                "timestamp": datetime.now().isoformat()
            }

            # 发送请求
            response = requests.post(
                f"{self.base_url}/api/event",
                json=payload,
                timeout=self.api_timeout
            )

            if response.status_code == 200:
                self.logger.debug(f"Visual status report sent successfully")
                return True
            else:
                self.logger.warning(f"Failed to send visual status report: HTTP {response.status_code}")
                return False

        except requests.exceptions.Timeout:
            self.logger.warning("Visual status report request timeout")
            return False
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Visual status report request failed: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending visual status report: {e}")
            return False

    def _update_stats(self, success: bool):
        """更新统计信息"""
        self.stats["total_reports"] += 1
        if success:
            self.stats["successful_reports"] += 1
        else:
            self.stats["failed_reports"] += 1
        self.stats["last_report_time"] = datetime.now().isoformat()

    def _update_last_state(self, report: VisualStatusReport):
        """更新上次状态记录"""
        self.last_objects = [obj["name"] for obj in report.detected_objects]
        self.last_gesture = report.current_gesture["gesture_type"] if report.current_gesture else None

    def send_immediate_report(self) -> bool:
        """立即发送一次报告"""
        self.logger.info("Sending immediate visual status report")
        return self._generate_and_send_report() is not None

    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = self.stats.copy()
        stats["running"] = self.running
        stats["report_interval"] = self.report_interval
        stats["success_rate"] = (
            stats["successful_reports"] / stats["total_reports"] * 100
            if stats["total_reports"] > 0 else 0
        )
        stats["uptime_seconds"] = time.time() - stats["start_time"]
        stats["pending_scene_changes"] = len(self.scene_changes)
        return stats

    def get_recent_scene_changes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """获取最近的场景变化"""
        return [asdict(change) for change in self.scene_changes[-limit:]]

    def clear_scene_changes(self):
        """清空场景变化记录"""
        self.scene_changes.clear()
        self.logger.info("Scene changes cleared")

    def set_report_interval(self, interval: float):
        """设置上报间隔"""
        if interval > 0:
            self.report_interval = interval
            self.logger.info(f"Report interval updated to {interval}s")

    def __str__(self) -> str:
        """字符串表示"""
        stats = self.get_statistics()
        return (f"VisualStatusReporter(running={self.running}, "
                f"reports={stats['total_reports']}, "
                f"success_rate={stats['success_rate']:.1f}%)")