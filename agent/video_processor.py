import cv2
import threading
import time
from typing import Optional, Callable, Dict, Any, List
from queue import Queue, Empty
import numpy as np
from dataclasses import dataclass

from gestures.mediapipe_detector import MediaPipeGestureDetector, GestureResult
from actions.executor import execute_action
from logger_config import setup_component_logger

# Import AI service for YOLO detection
try:
    import requests
    import base64
    import json
    YOLO_DETECTION_AVAILABLE = True
except ImportError:
    YOLO_DETECTION_AVAILABLE = False

# 设置VideoProcessor的日志
logger = setup_component_logger("video")


@dataclass
class VideoConfig:
    camera_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    show_preview: bool = True
    flip_horizontal: bool = True
    detection_interval: float = 0.1  # seconds between gesture detections
    yolo_detection_interval: float = 1.0  # seconds between YOLO detections
    ai_service_url: str = "http://127.0.0.1:8000"  # AI service URL for YOLO detection


class VideoProcessor:
    def __init__(self, config: VideoConfig, gesture_mapping: Dict[str, Dict]):
        self.config = config
        self.gesture_mapping = gesture_mapping
        self.running = False
        self.paused = False
        
        # Initialize components
        self.detector = None
        self.cap = None
        
        # Threading
        self.capture_thread = None
        self.processing_thread = None
        self.display_thread = None
        
        # Queues for thread communication
        self.frame_queue = Queue(maxsize=2)
        self.result_queue = Queue(maxsize=10)
        
        # Statistics
        self.frame_count = 0
        self.gesture_count = 0
        self.last_detection_time = 0
        self.yolo_detection_count = 0
        self.last_yolo_detection_time = 0

        # Gesture Control State
        self.gesture_control_enabled = True  # Default: enabled
        self.control_toggle_gesture = "victory"  # VICTORY gesture toggles control
        self.last_toggle_time = 0
        self.toggle_cooldown = 2.0  # seconds between toggles to prevent rapid switching

        # YOLO Detection
        self.yolo_objects = []  # Current YOLO detected objects
        self.yolo_detection_enabled = YOLO_DETECTION_AVAILABLE

        # Callbacks
        self.on_gesture_detected: Optional[Callable[[GestureResult], None]] = None
        self.on_action_executed: Optional[Callable[[str, bool, str], None]] = None
        self.on_control_toggled: Optional[Callable[[bool], None]] = None
        self.on_yolo_objects_detected: Optional[Callable[[List[Dict]], None]] = None
        
    def initialize(self) -> bool:
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(self.config.camera_id)
            if not self.cap.isOpened():
                logger.error('Failed to open camera %d', self.config.camera_id)
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            # Initialize gesture detector (现在支持动态手势)
            self.detector = MediaPipeGestureDetector()
            
            logger.info('Video processor initialized: %dx%d @ %dfps', self.config.width, self.config.height, self.config.fps)
            return True
        except Exception as exc:
            logger.error('Failed to initialize video processor: %s', exc)
            return False
    
    def start(self):
        if self.running:
            logger.warning('Video processor already running')
            return
        
        if not self.initialize():
            return
        
        self.running = True
        self.paused = False
        
        # Start threads
        self.capture_thread = threading.Thread(target=self._capture_frames, name='CaptureThread')
        self.processing_thread = threading.Thread(target=self._process_frames, name='ProcessingThread')
        if self.config.show_preview:
            self.display_thread = threading.Thread(target=self._display_results, name='DisplayThread')
        
        self.capture_thread.start()
        self.processing_thread.start()
        if self.display_thread:
            self.display_thread.start()
        
        logger.info('Video processor started')
    
    def stop(self):
        logger.info('Stopping video processor...')
        self.running = False
        
        # Wait for threads to finish
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2)
        if self.display_thread and self.display_thread.is_alive():
            self.display_thread.join(timeout=2)
        
        # Cleanup
        if self.cap:
            self.cap.release()
        if self.detector:
            self.detector.close()
        cv2.destroyAllWindows()
        
        logger.info('Video processor stopped')
    
    def pause(self):
        self.paused = True
        logger.info('Video processor paused')

    def resume(self):
        self.paused = False
        logger.info('Video processor resumed')

    def toggle_gesture_control(self) -> bool:
        """Toggle gesture control on/off and return new state"""
        current_time = time.time()

        # Check cooldown to prevent rapid toggling
        if current_time - self.last_toggle_time < self.toggle_cooldown:
            logger.debug('Toggle on cooldown, skipping')
            return self.gesture_control_enabled

        self.gesture_control_enabled = not self.gesture_control_enabled
        self.last_toggle_time = current_time

        status = "启用" if self.gesture_control_enabled else "禁用"
        logger.info('🎛️ 手势控制已%s (VICTORY手势切换)', status)

        # Trigger callback if set
        if self.on_control_toggled:
            self.on_control_toggled(self.gesture_control_enabled)

        return self.gesture_control_enabled

    def set_gesture_control_enabled(self, enabled: bool):
        """Manually set gesture control state"""
        if self.gesture_control_enabled != enabled:
            self.gesture_control_enabled = enabled
            status = "启用" if enabled else "禁用"
            logger.info('🎛️ 手势控制已手动%s', status)

            # Trigger callback if set
            if self.on_control_toggled:
                self.on_control_toggled(enabled)

    def is_gesture_control_enabled(self) -> bool:
        """Check if gesture control is currently enabled"""
        return self.gesture_control_enabled

    def detect_yolo_objects(self, frame: np.ndarray) -> List[Dict]:
        """使用AI服务进行YOLO物体检测"""
        if not self.yolo_detection_enabled:
            return []

        try:
            # 编码图片为base64
            _, buffer = cv2.imencode('.jpg', frame)
            img_base64 = base64.b64encode(buffer).decode('utf-8')

            # 发送到AI服务进行检测
            response = requests.post(
                f"{self.config.ai_service_url}/detect/file",
                json={"image": img_base64},
                timeout=3.0
            )

            if response.status_code == 200:
                result = response.json()
                objects = result.get('objects', [])

                # 转换为标准格式
                detected_objects = []
                for obj in objects:
                    detected_objects.append({
                        "name": obj.get("name", "unknown"),
                        "confidence": obj.get("confidence", 0.0),
                        "bbox": obj.get("bbox", []),
                        "frame_id": self.frame_count
                    })

                logger.debug(f"YOLO检测到 {len(detected_objects)} 个物体")
                return detected_objects
            else:
                logger.warning(f"YOLO检测失败: HTTP {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"YOLO检测错误: {e}")
            return []

    def set_yolo_detection_enabled(self, enabled: bool):
        """启用或禁用YOLO检测"""
        self.yolo_detection_enabled = enabled and YOLO_DETECTION_AVAILABLE
        status = "启用" if self.yolo_detection_enabled else "禁用"
        logger.info(f'🔍 YOLO检测已{status}')

    def _capture_frames(self):
        while self.running:
            if not self.paused:
                ret, frame = self.cap.read()
                if ret:
                    if self.config.flip_horizontal:
                        frame = cv2.flip(frame, 1)
                    
                    try:
                        self.frame_queue.put(frame, timeout=0.1)
                        self.frame_count += 1
                    except:
                        # Queue full, skip frame
                        pass
                else:
                    logger.error('Failed to capture frame')
                    break
            else:
                time.sleep(0.1)
        
    def _process_frames(self):
        while self.running:
            if not self.paused:
                try:
                    frame = self.frame_queue.get(timeout=0.1)
                    current_time = time.time()
                    
                    # Detect gestures at specified intervals
                    if current_time - self.last_detection_time >= self.config.detection_interval:
                        gesture_results = self.detector.detect_hands(frame)
                        self.last_detection_time = current_time

                        # Perform YOLO detection at specified intervals
                        yolo_objects = []
                        if current_time - self.last_yolo_detection_time >= self.config.yolo_detection_interval:
                            yolo_objects = self.detect_yolo_objects(frame)
                            self.last_yolo_detection_time = current_time
                            self.yolo_objects = yolo_objects
                            self.yolo_detection_count += 1

                            # Trigger YOLO detection callback
                            if self.on_yolo_objects_detected and yolo_objects:
                                self.on_yolo_objects_detected(yolo_objects)

                        if gesture_results:
                            for gesture_result in gesture_results:
                                self._handle_gesture(gesture_result)
                                self.gesture_count += 1

                                if self.on_gesture_detected:
                                    self.on_gesture_detected(gesture_result)

                        # Put frame with results for display
                        display_data = {
                            'frame': frame,
                            'gestures': gesture_results or [],
                            'yolo_objects': yolo_objects
                        }
                        
                        try:
                            self.result_queue.put(display_data, timeout=0.1)
                        except:
                            # Result queue full, skip
                            pass
                    else:
                        # Still put frame for display without detection
                        display_data = {
                            'frame': frame,
                            'gestures': [],
                            'yolo_objects': self.yolo_objects  # Use current YOLO objects
                        }
                        try:
                            self.result_queue.put(display_data, timeout=0.1)
                        except:
                            pass
                            
                except Empty:
                    continue
                except Exception as exc:
                    logger.error('Error processing frame: %s', exc)
            else:
                time.sleep(0.1)
        
    def _display_results(self):
        while self.running:
            if not self.paused:
                try:
                    display_data = self.result_queue.get(timeout=0.1)
                    frame = display_data['frame']
                    gestures = display_data['gestures']
                    yolo_objects = display_data.get('yolo_objects', [])

                    # Draw YOLO object information
                    for obj in yolo_objects:
                        if obj.get('bbox'):
                            x, y, x2, y2 = obj['bbox']  # YOLO format: [x1, y1, x2, y2]
                            cv2.rectangle(frame, (x, y), (x2, y2), (255, 0, 255), 2)  # Purple color for YOLO objects

                            # Draw object label
                            name = obj.get('name', 'unknown')
                            confidence = obj.get('confidence', 0.0)
                            label = f'{name}: {confidence:.2f}'
                            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

                    # Draw gesture information
                    for i, gesture in enumerate(gestures):
                        if gesture.bbox:
                            x, y, w, h = gesture.bbox
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                            # Draw gesture label
                            label = f'{gesture.gesture_code}: {gesture.confidence:.2f}'
                            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Draw statistics
                    stats_text = f'Frames: {self.frame_count} | Gestures: {self.gesture_count} | Objects: {len(yolo_objects)}'
                    cv2.putText(frame, stats_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

                    # Draw gesture control status
                    status_color = (0, 255, 0) if self.gesture_control_enabled else (0, 0, 255)  # Green for enabled, Red for disabled
                    status_text = f'Gesture Control: {"ON" if self.gesture_control_enabled else "OFF"}'
                    cv2.putText(frame, status_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)

                    # Draw control hint
                    hint_text = 'Make VICTORY sign (✌️) to toggle control'
                    cv2.putText(frame, hint_text, (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                    
                    # Show preview window
                    cv2.imshow('YOLO-LLM Agent - Gesture Detection', frame)
                    
                    # Handle key presses
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # 'q' or ESC
                        logger.info('User requested stop')
                        self.running = False
                    elif key == ord(' '):  # Space to pause/resume
                        if self.paused:
                            self.resume()
                        else:
                            self.pause()
                            
                except Empty:
                    continue
                except Exception as exc:
                    logger.error('Error displaying results: %s', exc)
            else:
                time.sleep(0.1)
        
    def _handle_gesture(self, gesture_result: GestureResult):
        # 详细日志记录
        logger.info('[DEBUG] Detected gesture: %s', gesture_result.gesture_code)
        logger.info('[DEBUG] Available mappings: %s', list(self.gesture_mapping.keys()))

        # 检查是否为控制开关手势
        gesture_code_lower = gesture_result.gesture_code.lower()
        if gesture_code_lower == self.control_toggle_gesture:
            new_state = self.toggle_gesture_control()
            logger.info('[TOGGLE] Gesture control toggled to: %s', 'enabled' if new_state else 'disabled')

            # 仍然通知检测到开关手势
            if self.on_gesture_detected:
                self.on_gesture_detected(gesture_result)
            return

        # 检查手势控制是否启用
        if not self.gesture_control_enabled:
            logger.info('[DISABLED] Gesture control is disabled, ignoring gesture: %s', gesture_result.gesture_code)

            # 仍然通知检测到手势，但不执行动作
            if self.on_gesture_detected:
                self.on_gesture_detected(gesture_result)
            return

        # 尝试匹配原始手势码和转换为小写的手势码
        gesture_code_original = gesture_result.gesture_code
        gesture_code_lower = gesture_code_original.lower()

        action_config = self.gesture_mapping.get(gesture_code_original)
        matched_code = gesture_code_original
        if not action_config:
            action_config = self.gesture_mapping.get(gesture_code_lower)
            matched_code = gesture_code_lower

        if action_config:
            logger.info('[MATCH] Found mapping for %s -> %s', gesture_result.gesture_code, matched_code)
        if not action_config:
            logger.warning('[ERROR] No action mapping for gesture: %s', gesture_result.gesture_code)
            logger.warning('[DEBUG] Available mapping keys: %s', self.gesture_mapping.keys())
            return

        action_type = action_config.get('type')
        action_value = action_config.get('value')
        action_payload = action_config.get('payload')

        logger.info('[DEBUG] Action config found for %s: type=%s, value=%s',
                     gesture_result.gesture_code, action_type, action_value)

        if not action_type:
            logger.warning('[ERROR] No action type for gesture: %s', gesture_result.gesture_code)
            return

        logger.info('[ACTION] Executing action for gesture %s: %s - %s',
                     gesture_result.gesture_code, action_type, action_value)

        # 确保浏览器获得焦点并添加延迟
        import pyautogui
        time.sleep(0.1)
        try:
            # 点击屏幕中央获得焦点
            pyautogui.click(pyautogui.size().width // 2, pyautogui.size().height // 2)
            time.sleep(0.2)
        except:
            pass  # 如果点击失败，继续执行

        try:
            success, message = execute_action(action_type, action_value, action_payload)
            logger.info('[ACTION_RESULT] Execute result for %s: success=%s, message=%s',
                         gesture_result.gesture_code, success, message)

            # 为浏览器操作添加响应延迟
            if success and action_type == 'hotkey':
                time.sleep(0.3)

        except Exception as exc:
            logger.exception('[ACTION_ERROR] Exception executing action for %s: %s',
                              gesture_result.gesture_code, exc)
            success, message = False, f'Exception: {exc}'

        if self.on_action_executed:
            self.on_action_executed(gesture_result.gesture_code, success, message)

        if success:
            logger.info('[SUCCESS] Action executed successfully: %s', message)
        else:
            logger.warning('[FAIL] Action execution failed: %s', message)
    
    def update_mapping(self, new_mapping: Dict[str, Dict]):
        self.gesture_mapping = new_mapping
        logger.info('Updated gesture mapping with %d entries', len(new_mapping))
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'frame_count': self.frame_count,
            'gesture_count': self.gesture_count,
            'yolo_detection_count': self.yolo_detection_count,
            'running': self.running,
            'paused': self.paused,
            'mapping_count': len(self.gesture_mapping),
            'gesture_control_enabled': self.gesture_control_enabled,
            'control_toggle_gesture': self.control_toggle_gesture,
            'yolo_detection_enabled': self.yolo_detection_enabled,
            'current_yolo_objects': len(self.yolo_objects)
        }

