import cv2
import threading
import time
import logging
from typing import Optional, Callable, Dict, Any
from queue import Queue, Empty
import numpy as np
from dataclasses import dataclass

from gestures.mediapipe_detector import MediaPipeGestureDetector, GestureResult
from actions.executor import execute_action


@dataclass
class VideoConfig:
    camera_id: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    show_preview: bool = True
    flip_horizontal: bool = True
    detection_interval: float = 0.1  # seconds between gesture detections


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
        
        # Callbacks
        self.on_gesture_detected: Optional[Callable[[GestureResult], None]] = None
        self.on_action_executed: Optional[Callable[[str, bool, str], None]] = None
        
    def initialize(self) -> bool:
        try:
            # Initialize camera
            self.cap = cv2.VideoCapture(self.config.camera_id)
            if not self.cap.isOpened():
                logging.error('Failed to open camera %d', self.config.camera_id)
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.height)
            self.cap.set(cv2.CAP_PROP_FPS, self.config.fps)
            
            # Initialize gesture detector
            self.detector = MediaPipeGestureDetector()
            
            logging.info('Video processor initialized: %dx%d @ %dfps', self.config.width, self.config.height, self.config.fps)
            return True
        except Exception as exc:
            logging.error('Failed to initialize video processor: %s', exc)
            return False
    
    def start(self):
        if self.running:
            logging.warning('Video processor already running')
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
        
        logging.info('Video processor started')
    
    def stop(self):
        logging.info('Stopping video processor...')
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
        
        logging.info('Video processor stopped')
    
    def pause(self):
        self.paused = True
        logging.info('Video processor paused')
    
    def resume(self):
        self.paused = False
        logging.info('Video processor resumed')
    
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
                    logging.error('Failed to capture frame')
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
                        
                        if gesture_results:
                            for gesture_result in gesture_results:
                                self._handle_gesture(gesture_result)
                                self.gesture_count += 1
                                
                                if self.on_gesture_detected:
                                    self.on_gesture_detected(gesture_result)
                        
                        # Put frame with results for display
                        display_data = {
                            'frame': frame,
                            'gestures': gesture_results or []
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
                            'gestures': []
                        }
                        try:
                            self.result_queue.put(display_data, timeout=0.1)
                        except:
                            pass
                            
                except Empty:
                    continue
                except Exception as exc:
                    logging.error('Error processing frame: %s', exc)
            else:
                time.sleep(0.1)
        
    def _display_results(self):
        while self.running:
            if not self.paused:
                try:
                    display_data = self.result_queue.get(timeout=0.1)
                    frame = display_data['frame']
                    gestures = display_data['gestures']
                    
                    # Draw gesture information
                    for i, gesture in enumerate(gestures):
                        if gesture.bbox:
                            x, y, w, h = gesture.bbox
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                            
                            # Draw gesture label
                            label = f'{gesture.gesture_code}: {gesture.confidence:.2f}'
                            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
                    # Draw statistics
                    stats_text = f'Frames: {self.frame_count} | Gestures: {self.gesture_count}'
                    cv2.putText(frame, stats_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                    
                    # Show preview window
                    cv2.imshow('YOLO-LLM Agent - Gesture Detection', frame)
                    
                    # Handle key presses
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q') or key == 27:  # 'q' or ESC
                        logging.info('User requested stop')
                        self.running = False
                    elif key == ord(' '):  # Space to pause/resume
                        if self.paused:
                            self.resume()
                        else:
                            self.pause()
                            
                except Empty:
                    continue
                except Exception as exc:
                    logging.error('Error displaying results: %s', exc)
            else:
                time.sleep(0.1)
        
    def _handle_gesture(self, gesture_result: GestureResult):
        action_config = self.gesture_mapping.get(gesture_result.gesture_code)
        if not action_config:
            logging.warning('No action mapping for gesture: %s', gesture_result.gesture_code)
            return
            
        action_type = action_config.get('type')
        action_value = action_config.get('value')
        action_payload = action_config.get('payload')
        
        if not action_type:
            logging.warning('No action type for gesture: %s', gesture_result.gesture_code)
            return
            
        logging.info('Executing action for gesture %s: %s - %s', gesture_result.gesture_code, action_type, action_value)
        
        success, message = execute_action(action_type, action_value, action_payload)
        
        if self.on_action_executed:
            self.on_action_executed(gesture_result.gesture_code, success, message)
        
        if success:
            logging.info('Action executed successfully: %s', message)
        else:
            logging.warning('Action execution failed: %s', message)
    
    def update_mapping(self, new_mapping: Dict[str, Dict]):
        self.gesture_mapping = new_mapping
        logging.info('Updated gesture mapping with %d entries', len(new_mapping))
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            'frame_count': self.frame_count,
            'gesture_count': self.gesture_count,
            'running': self.running,
            'paused': self.paused,
            'mapping_count': len(self.gesture_mapping)
        }

