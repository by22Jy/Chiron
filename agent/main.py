import argparse
import json
import sys
import signal
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Any, List

import requests
import yaml

from video_processor import VideoProcessor, VideoConfig
from gestures.mediapipe_detector import GestureResult
from actions.executor import get_supported_actions, execute_action
from logger_config import setup_component_logger

# Import new AI features
try:
    from speech_controller import VoiceController, VoiceCommand
    from gesture_analyzer import GestureAnalyzer, GestureAnalysis
    from context_manager import ContextManager
    from visual_status_reporter import VisualStatusReporter
    from gesture_router import GestureRouter, RouteType
    from tts_engine import TTSEngine, TTSConfig, VoiceFeedback
    from visual_feedback import VisualFeedback, VisualFeedbackConfig, AgentState, FeedbackLevel
    from safety_confirmation import SafetyConfirmationManager, request_action_confirmation, handle_confirmation_gesture
    AI_FEATURES_AVAILABLE = True
except ImportError as e:
    print(f'Warning: AI features not available: {e}')
    AI_FEATURES_AVAILABLE = False

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None

# 设置主agent的日志
logger = setup_component_logger("agent")


class AgentConfig:
    def __init__(self, cfg: Dict):
        backend = cfg.get('backend', {})
        agent = cfg.get('agent', {})
        video = cfg.get('video', {})
        self.base_url: str = backend.get('base_url', 'http://127.0.0.1:8080').rstrip('/')
        self.username: Optional[str] = backend.get('username')
        self.application: Optional[str] = backend.get('application')
        self.os_type: str = backend.get('os', 'windows').lower()
        self.source: str = agent.get('source', 'python-agent')
        self.poll_interval: int = int(agent.get('poll_interval', 60))
        # Video configuration
        self.video_config = VideoConfig(
            camera_id=video.get('camera_id', 0),
            width=video.get('width', 640),
            height=video.get('height', 480),
            fps=video.get('fps', 30),
            show_preview=video.get('show_preview', True),
            flip_horizontal=video.get('flip_horizontal', True),
            detection_interval=video.get('detection_interval', 0.1)
        )


class GestureAgent:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.mapping: Dict[str, Dict] = {}
        self.video_processor: Optional[VideoProcessor] = None
        self.running = False
        self.should_stop = threading.Event()

        # AI Features
        self.ai_features_available = AI_FEATURES_AVAILABLE
        self.voice_controller: Optional[VoiceController] = None
        self.gesture_analyzer: Optional[GestureAnalyzer] = None
        self.context_manager: Optional[ContextManager] = None
        self.visual_status_reporter: Optional[VisualStatusReporter] = None
        self.gesture_router: Optional[GestureRouter] = None

        # Phase 4 Features: TTS, Visual Feedback, and Safety Confirmation
        self.tts_engine: Optional[TTSEngine] = None
        self.visual_feedback: Optional[VisualFeedback] = None
        self.safety_confirmation: Optional[SafetyConfirmationManager] = None

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, self._signal_handler)

        # Initialize AI features if available
        if AI_FEATURES_AVAILABLE:
            try:
                self.voice_controller = VoiceController(config.base_url)
                self.gesture_analyzer = GestureAnalyzer(config.base_url)

                # Initialize ContextManager with visual context configuration
                context_config = {
                    "max_history_size": 50,
                    "object_timeout": 5.0
                }
                self.context_manager = ContextManager(context_config)

                # Initialize GestureRouter with context manager
                self.gesture_router = GestureRouter(self.context_manager)

                # Initialize VisualStatusReporter
                reporter_config = {
                    "report_interval": 30.0,  # 30秒上报一次
                    "api_timeout": 10.0,
                    "enable_change_detection": True
                }
                self.visual_status_reporter = VisualStatusReporter(
                    base_url=config.base_url,
                    context_manager=self.context_manager,
                    config=reporter_config
                )

                # Initialize TTS Engine
                tts_config = TTSConfig(
                    enabled=True,
                    engine_type="offline",  # 默认使用离线模式
                    voice="zh-CN-XiaoxiaoNeural",
                    rate=200,
                    volume=0.8
                )
                self.tts_engine = TTSEngine(tts_config)

                # Initialize Visual Feedback
                visual_config = VisualFeedbackConfig(
                    enable_status_display=True,
                    enable_message_overlay=True,
                    enable_progress_bar=True,
                    enable_gesture_indicators=True
                )
                self.visual_feedback = VisualFeedback(visual_config)

                # Initialize Safety Confirmation Manager
                safety_config = {
                    "default_timeout": 30.0,
                    "max_pending_requests": 3,
                    "auto_approve_safe_actions": True
                }
                self.safety_confirmation = SafetyConfirmationManager(safety_config)

                logger.info('[AI] AI features initialized successfully')
                logger.info('[AI] ContextManager initialized for visual context')
                logger.info('[AI] GestureRouter initialized for fast/slow path routing')
                logger.info('[AI] VisualStatusReporter initialized for status reporting')
                logger.info('[AI] TTS Engine initialized for voice feedback')
                logger.info('[AI] Visual Feedback initialized for UI feedback')
                logger.info('[AI] Safety Confirmation Manager initialized for operation security')
            except Exception as e:
                logger.warning(f'Failed to initialize AI features: {e}')
                self.ai_features_available = False
    
    def _signal_handler(self, signum, frame):
        logger.info('Received signal %d, shutting down...', signum)
        self.stop()
    
    def sync_config(self) -> None:
        params = {
            'username': self.config.username,
            'application': self.config.application,
            'os': self.config.os_type,
        }
        logger.info('Fetching config from %s', self.config.base_url)
        try:
            resp = requests.get(f'{self.config.base_url}/api/config', params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            mappings = data.get('mappings', [])
            self.mapping = {}
            for item in mappings:
                action = item.get('action') or {}
                self.mapping[item.get('code')] = {
                    'type': action.get('type'),
                    'value': action.get('value'),
                    'os': action.get('osType'),
                    'description': action.get('description'),
                    'payload': action.get('payloadJson'),
                }
            logger.info('Loaded %d gesture mappings', len(self.mapping))
            
            # Update video processor mapping if it exists
            if self.video_processor:
                self.video_processor.update_mapping(self.mapping)
        except Exception as exc:
            logger.error('Failed to sync config: %s', exc)
            raise
    
    def perform_action(self, gesture_code: str) -> bool:
        logger.info('🎯 检测到手势: %s', gesture_code)  # 显示所有检测到的手势
        action = self.mapping.get(gesture_code)
        if not action:
            logger.warning('No action mapping for gesture: %s', gesture_code)
            return False

        action_type = (action.get('type') or '').lower()
        action_value = action.get('value') or ''
        action_payload = action.get('payload')

        # 安全确认机制 - 检查是否需要用户确认
        if self.safety_confirmation:
            def execute_with_confirmation():
                """执行动作的内部函数"""
                nonlocal success, message
                try:
                    from actions.executor import execute_action
                    success, message = execute_action(action_type, action_value, action_payload)
                except Exception as exc:
                    message = f'Execution failed: {exc}'
                    logger.exception('Failed to perform action for %s', gesture_code)

            # 请求安全确认
            confirmation_id = self.safety_confirmation.request_confirmation(
                action_type=action_type,
                action_value=action_value,
                action_payload=action_payload,
                confirmation_callback=lambda response: self._handle_confirmation_response(
                    response, execute_with_confirmation, gesture_code
                )
            )

            if confirmation_id is None:
                # 不需要确认，直接执行
                execute_with_confirmation()
            else:
                # 需要确认，等待用户手势确认
                logger.info(f' 等待用户确认操作: {action_type} - {action_value}')
                if self.tts_engine:
                    self.tts_engine.speak_async(f"请确认{action_type}操作")
                if self.visual_feedback:
                    self.visual_feedback.set_state(
                        AgentState.PROCESSING,
                        f"等待确认: {action_type}"
                    )
                return True  # 等待确认中
        else:
            # 没有安全确认机制，直接执行
            success = False
            message = ''
            try:
                from actions.executor import execute_action
                success, message = execute_action(action_type, action_value, action_payload)
            except Exception as exc:
                message = f'Execution failed: {exc}'
                logger.exception('Failed to perform action for %s', gesture_code)
    
        self.post_log(
            gesture_code=gesture_code,
            action_type=action_type,
            action_value=action_value,
            status='success' if success else 'failure',
            message=message or ('Executed' if success else 'No action executed'),
        )
        return success

    def _handle_confirmation_response(self, response, execute_action_func, gesture_code: str):
        """处理安全确认响应"""
        if response.status.value == "approved":
            logger.info(f"✅ 用户确认操作: {gesture_code}")
            if self.tts_engine:
                self.tts_engine.speak_async("操作已确认")
            if self.visual_feedback:
                self.visual_feedback.set_state(AgentState.EXECUTING, "执行已确认的操作")

            # 执行动作
            execute_action_func()

            # 记录执行结果
            self.post_log(
                gesture_code=gesture_code,
                action_type=execute_action_func.__closure__[0].cell_contents if hasattr(execute_action_func, '__closure__') else 'unknown',
                action_value='',
                status='success' if True else 'failure',  # 这里需要在execute_action_func中设置状态
                message='Operation confirmed and executed'
            )

            if self.visual_feedback:
                self.visual_feedback.set_state(AgentState.SUCCESS, "操作完成")

        else:
            logger.info(f"❌ 用户拒绝操作: {gesture_code}")
            if self.tts_engine:
                self.tts_engine.speak_async("操作已取消")
            if self.visual_feedback:
                self.visual_feedback.set_state(AgentState.IDLE, "操作已取消")

    def handle_gesture_confirmation(self, gesture_result: GestureResult) -> bool:
        """处理手势确认"""
        if self.safety_confirmation:
            return self.safety_confirmation.handle_gesture_confirmation(gesture_result)
        return False

    def post_log(
        self,
        gesture_code: str,
        action_type: str,
        action_value: str,
        status: str,
        message: str,
    ) -> None:
        payload = {
            'username': self.config.username,
            'application': self.config.application,
            'gestureCode': gesture_code,
            'actionType': action_type,
            'actionValue': action_value,
            'status': status,
            'message': message,
            'sourceAgent': self.config.source,
        }
        try:
            resp = requests.post(
                f'{self.config.base_url}/api/audit/log',
                json=payload,
                timeout=10,
            )
            resp.raise_for_status()
            logger.info('Log posted: %s', resp.json())
        except Exception as exc:
            logger.error('Failed to post log: %s', exc)
    
    def send_event(self, event_type: str, payload: Optional[dict] = None) -> None:
        body = {
            'eventType': event_type,
            'username': self.config.username,
            'application': self.config.application,
            'payload': json.dumps(payload or {}),
        }
        try:
            resp = requests.post(f'{self.config.base_url}/api/event', json=body, timeout=10)
            resp.raise_for_status()
            logger.info('Event acknowledged: %s', resp.json())
        except Exception as exc:
            logger.error('Failed to send event: %s', exc)
    
    def start_realtime(self):
        logger.info('[AGENT] Starting real-time gesture detection...')
        self.running = True

        try:
            logger.info('[AGENT] Syncing configuration from backend...')
            # Initial config sync
            self.sync_config()
            logger.info('[AGENT] Configuration synced. Loaded %d gesture mappings', len(self.mapping))
            logger.info('[AGENT] Available mappings: %s', list(self.mapping.keys()))

            # Initialize and start video processor
            logger.info('[AGENT] Initializing video processor...')
            self.video_processor = VideoProcessor(self.config.video_config, self.mapping)

            # Set callbacks
            logger.info('[AGENT] Setting up callbacks...')
            self.video_processor.on_gesture_detected = self._on_gesture_detected
            self.video_processor.on_action_executed = self._on_action_executed

            # Set YOLO detection callback if ContextManager is available
            if self.context_manager:
                self.video_processor.on_yolo_objects_detected = self._on_yolo_objects_detected
                logger.info('[AGENT] YOLO detection callback connected to ContextManager')

            # Phase 4: 设置视觉反馈回调
            if self.visual_feedback:
                self.video_processor.on_frame_display = self._on_frame_display
                logger.info('[AGENT] Visual feedback callback connected')

            # Start video processing
            logger.info('[AGENT] Starting video processor...')
            self.video_processor.start()

            # Start visual status reporter if available
            if self.visual_status_reporter:
                self.visual_status_reporter.start()
                logger.info('[AGENT] Visual status reporter started')

            logger.info('[AGENT] Real-time gesture detection started successfully')
            logger.info('[AGENT] Press Ctrl+C to stop, or press Space in preview window to pause/resume')
            
            # Keep the main thread alive
            while self.running and not self.should_stop.is_set():
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            logger.info('User interrupted, stopping...')
        except Exception as exc:
            logger.error('Error in realtime mode: %s', exc)
        finally:
            self.stop()
    
    def start_daemon(self):
        logger.info('Starting daemon mode...')
        self.running = True
        
        try:
            self.sync_config()
            
            # Start video processor if gestures are mapped
            if self.mapping:
                self.video_processor = VideoProcessor(self.config.video_config, self.mapping)
                self.video_processor.on_gesture_detected = self._on_gesture_detected
                self.video_processor.on_action_executed = self._on_action_executed

                # Set YOLO detection callback if ContextManager is available
                if self.context_manager:
                    self.video_processor.on_yolo_objects_detected = self._on_yolo_objects_detected
                    logger.info('[AGENT] YOLO detection callback connected to ContextManager')

                # Phase 4: 设置视觉反馈回调
                if self.visual_feedback:
                    self.video_processor.on_frame_display = self._on_frame_display
                    logger.info('[AGENT] Visual feedback callback connected')

                self.video_processor.start()

                # Start visual status reporter if available
                if self.visual_status_reporter:
                    self.visual_status_reporter.start()
                    logger.info('[AGENT] Visual status reporter started (daemon mode)')

            # Config polling loop
            while self.running and not self.should_stop.is_set():
                try:
                    self.sync_config()
                    logger.info('Daemon running, checked config at %s', time.strftime('%H:%M:%S'))
                    self.should_stop.wait(self.config.poll_interval)
                except Exception as exc:
                    logger.error('Error in daemon loop: %s', exc)
                    self.should_stop.wait(5)  # Wait before retry
        except KeyboardInterrupt:
            logger.info('User interrupted, stopping daemon...')
        finally:
            self.stop()
    
    def _on_gesture_detected(self, gesture_result: GestureResult):
        """处理检测到的手势，使用快慢通道路由策略"""
        try:
            gesture_code = gesture_result.gesture_code
            confidence = gesture_result.confidence
            logger.info(f'[GESTURE] Detected: {gesture_code} (confidence: {confidence:.2f})')

            # Phase 4.2: 首先检查是否为确认手势
            if self.handle_gesture_confirmation(gesture_result):
                logger.info(f'[SAFETY] 处理确认手势: {gesture_code}')
                if self.visual_feedback:
                    self.visual_feedback.add_message(
                        f"确认手势: {gesture_code}",
                        FeedbackLevel.SUCCESS,
                        duration=1.5
                    )
                return  # 确认手势已处理，不再进行常规路由

            # Phase 4: 提供视觉和语音反馈
            if self.visual_feedback:
                self.visual_feedback.add_message(
                    f"检测到手势: {gesture_code}",
                    FeedbackLevel.INFO,
                    duration=2.0
                )
                self.visual_feedback.set_state(AgentState.PROCESSING)

            # 使用手势路由器进行路由决策
            if self.gesture_router:
                visual_context = self.context_manager.get_current_context() if self.context_manager else None
                route_decision = self.gesture_router.route_gesture(gesture_result, visual_context)

                logger.info(f'[ROUTING] {gesture_code} -> {route_decision.route_type.value} ({route_decision.reasoning})')

                # 根据路由决策处理手势
                if route_decision.route_type == RouteType.IGNORE:
                    logger.debug(f'[ROUTING] Ignoring gesture: {gesture_code}')
                    return

                elif route_decision.route_type == RouteType.FAST_PATH:
                    # 快通道：直接执行预定义动作（带安全确认）
                    if route_decision.expected_action:
                        action_type = route_decision.expected_action.get('type')
                        action_value = route_decision.expected_action.get('value')
                        action_payload = route_decision.expected_action.get('payload')

                        logger.info(f'[FAST_PATH] Executing: {action_type} - {action_value}')

                        # Phase 4.2: 安全确认机制
                        def execute_fast_action():
                            # Phase 4: 执行前反馈
                            if self.visual_feedback:
                                self.visual_feedback.set_state(AgentState.EXECUTING, f"执行{action_type}")
                                self.visual_feedback.set_progress(0.5, "执行动作")

                            if self.tts_engine:
                                self.tts_engine.speak_async("正在执行操作")

                            success, message = execute_action(action_type, action_value, action_payload)

                            # Phase 4: 执行后反馈
                            if self.visual_feedback:
                                if success:
                                    self.visual_feedback.set_state(AgentState.SUCCESS, "操作完成")
                                    self.visual_feedback.add_message("执行成功", FeedbackLevel.SUCCESS)
                                else:
                                    self.visual_feedback.set_state(AgentState.ERROR, "操作失败")
                                    self.visual_feedback.add_message(f"执行失败: {message}", FeedbackLevel.ERROR)
                                self.visual_feedback.set_progress(1.0)

                            if self.tts_engine:
                                if success:
                                    VoiceFeedback.speak_feedback(VoiceFeedback.SUCCESS)
                                else:
                                    VoiceFeedback.speak_feedback(VoiceFeedback.FAILED)

                        # 请求安全确认
                        if self.safety_confirmation:
                            confirmation_id = self.safety_confirmation.request_confirmation(
                                action_type=action_type,
                                action_value=action_value,
                                action_payload=action_payload,
                                confirmation_callback=lambda response: self._handle_confirmation_response(
                                    response, execute_fast_action, gesture_code
                                )
                            )

                            if confirmation_id is None:
                                # 不需要确认，直接执行
                                execute_fast_action()
                            else:
                                # 需要确认，等待用户手势确认
                                logger.info(f'[SAFETY] 快通道操作需要确认: {action_type}')
                                if self.tts_engine:
                                    self.tts_engine.speak_async(f"请确认{action_type}操作")
                                if self.visual_feedback:
                                    self.visual_feedback.set_state(
                                        AgentState.PROCESSING,
                                        f"等待确认: {action_type}"
                                    )
                        else:
                            # 没有安全确认机制，直接执行
                            execute_fast_action()
                        return

                elif route_decision.route_type == RouteType.SLOW_PATH:
                    # 慢通道：发送到后端进行LLM意图分析
                    # Phase 4: 思考状态反馈
                    if self.visual_feedback:
                        self.visual_feedback.set_state(AgentState.THINKING, "分析意图中...")
                        self.visual_feedback.set_progress(0.3, "LLM分析")

                    if self.tts_engine:
                        self.tts_engine.speak_async("正在分析指令意图")

                    self._send_slow_path_gesture(gesture_result, route_decision)
                    return

            # 回退到传统的映射处理（如果没有路由器或路由失败）
            gesture_code_original = gesture_result.gesture_code
            gesture_code_lower = gesture_code_original.lower()

            has_mapping_original = gesture_code_original in self.mapping
            has_mapping_lower = gesture_code_lower in self.mapping

            if has_mapping_original:
                action = self.mapping[gesture_code_original]
                self._execute_gesture_action(gesture_code_original, action)
            elif has_mapping_lower:
                action = self.mapping[gesture_code_lower]
                self._execute_gesture_action(gesture_code_lower, action)
            else:
                logger.warning(f'[FALLBACK] No action mapping found for gesture: {gesture_code_original}')

        except Exception as exc:
            logger.exception(f'[GESTURE] Error processing gesture: {exc}')
            self.post_log(
                gesture_code=gesture_result.gesture_code,
                action_type='error',
                action_value='',
                status='failure',
                message=str(exc)
            )

    def _execute_gesture_action(self, gesture_code: str, action: Dict[str, Any]):
        """执行手势动作"""
        action_type = action.get('type')
        action_value = action.get('value')
        action_payload = action.get('payload')

        if action_type:
            logger.info(f'[FALLBACK] Executing: {action_type} - {action_value}')
            success, message = execute_action(action_type, action_value, action_payload)

            if self.on_action_executed:
                self.on_action_executed(gesture_code, success, message)

            self.post_log(
                gesture_code=gesture_code,
                action_type=action_type,
                action_value=action_value,
                status='success' if success else 'failure',
                message=message
            )
        else:
            logger.warning(f'[FALLBACK] No action type for: {gesture_code}')

    def _send_slow_path_gesture(self, gesture_result: GestureResult, route_decision):
        """发送慢通道手势到后端进行LLM意图分析"""
        try:
            # 获取视觉上下文
            visual_context = self.get_visual_context_for_llm()

            # 构建慢通道手势事件
            event_data = {
                'gesture_code': gesture_result.gesture_code,
                'gesture_confidence': gesture_result.confidence,
                'gesture_bbox': gesture_result.bbox,
                'handedness': getattr(gesture_result, 'handedness', 'unknown'),
                'route_reasoning': route_decision.reasoning,
                'visual_context': visual_context,
                'available_objects': visual_context.get('available_objects', []),
                'scene_description': visual_context.get('visual_context', {}).get('scene_description', ''),
                'intent_analysis_required': True
            }

            # 发送到后端进行LLM分析
            self.send_event('slow_path_gesture', event_data)
            logger.info(f'[SLOW_PATH] Sent gesture for LLM analysis: {gesture_result.gesture_code}')

        except Exception as e:
            logger.error(f'[SLOW_PATH] Failed to send gesture for analysis: {e}')
    
    def _on_action_executed(self, gesture_code: str, success: bool, message: str):
        logger.info('[AGENT] Action executed: gesture=%s, success=%s, message=%s',
                    gesture_code, success, message)

        # Get action details for logging
        action = self.mapping.get(gesture_code, {})
        action_type = action.get('type', 'unknown')
        action_value = action.get('value', '')

        logger.info('[AGENT] Action details: type=%s, value=%s', action_type, action_value)

        self.post_log(
            gesture_code=gesture_code,
            action_type=action_type,
            action_value=action_value,
            status='success' if success else 'failure',
            message=message
        )

    def _on_yolo_objects_detected(self, detected_objects: List[Dict]):
        """处理YOLO物体检测结果"""
        if not self.context_manager:
            return

        try:
            # 更新ContextManager中的视觉上下文
            self.context_manager.update_context(
                detected_objects=detected_objects,
                frame_id=0  # Will be updated by video processor
            )

            # 记录检测到的物体
            object_names = [obj['name'] for obj in detected_objects if obj.get('confidence', 0) > 0.5]
            if object_names:
                logger.debug(f'[CONTEXT] YOLO检测到物体: {", ".join(object_names)}')

        except Exception as e:
            logger.error(f'[CONTEXT] 更新视觉上下文失败: {e}')

    def get_visual_context_for_llm(self) -> Dict[str, Any]:
        """获取用于LLM的视觉上下文"""
        if not self.context_manager:
            return {"visual_context": None, "available_objects": []}

        return self.context_manager.get_context_for_llm()
    
    def start_voice_control(self):
        """启动语音控制"""
        if not AI_FEATURES_AVAILABLE or not self.voice_controller:
            logger.warning('Voice control not available')
            return False

        try:
            # 设置语音命令回调
            self.voice_controller.on_command_detected = self._on_voice_command
            self.voice_controller.on_speech_text = self._on_speech_text

            # 启动语音监听
            self.voice_controller.start_listening()
            logger.info('[语音] Voice control started')
            return True
        except Exception as e:
            logger.error(f'Failed to start voice control: {e}')
            return False

    def stop_voice_control(self):
        """停止语音控制"""
        if self.voice_controller:
            self.voice_controller.stop_listening()
            logger.info('🔇 Voice control stopped')

    def analyze_gesture_intent(self, gesture_result: GestureResult, context: str = "") -> Optional[GestureAnalysis]:
        """分析手势意图"""
        if not AI_FEATURES_AVAILABLE or not self.gesture_analyzer:
            logger.warning('Gesture analysis not available')
            return None

        try:
            analysis = self.gesture_analyzer.analyze_gesture(gesture_result, context)
            if analysis:
                logger.info(f'✨ Gesture analysis: {analysis.intent}')
            return analysis
        except Exception as e:
            logger.error(f'Failed to analyze gesture: {e}')
            return None

    def _on_voice_command(self, command: VoiceCommand):
        """处理语音命令"""
        logger.info(f'[语音] Voice command: {command.command_type} - {command.parameters}')
        self.send_event('voice_command', {
            'command_type': command.command_type,
            'parameters': command.parameters,
            'confidence': command.confidence,
            'raw_text': command.raw_text
        })

    def _on_speech_text(self, text: str):
        """处理识别到的语音文本"""
        logger.info(f'[语音] Speech recognized: {text}')

        # 获取视觉上下文并发送给后端
        visual_context = self.get_visual_context_for_llm()

        # 发送包含视觉上下文的语音识别事件
        self.send_event('speech_recognized', {
            'text': text,
            'visual_context': visual_context,
            'available_objects': visual_context.get('available_objects', []),
            'scene_description': visual_context.get('visual_context', {}).get('scene_description', '')
        })

    def _on_frame_display(self, frame, gestures=None):
        """视觉反馈回调：在帧上绘制Agent状态和反馈"""
        if self.visual_feedback:
            try:
                return self.visual_feedback.draw_feedback(frame, gestures)
            except Exception as e:
                logger.error(f"Visual feedback error: {e}")
        return frame

    def stop(self):
        if not self.running:
            return

        logger.info('Stopping gesture agent...')
        self.running = False
        self.should_stop.set()

        # Stop video processor
        if self.video_processor:
            self.video_processor.stop()
            self.video_processor = None

        # Stop voice control
        self.stop_voice_control()

        # Stop visual status reporter
        if self.visual_status_reporter:
            self.visual_status_reporter.stop()
            logger.info('Visual status reporter stopped')

        # Phase 4: 清理TTS和视觉反馈
        if self.tts_engine:
            self.tts_engine.cleanup()
            logger.info('TTS engine cleaned up')

        if self.visual_feedback:
            self.visual_feedback.reset()
            logger.info('Visual feedback reset')

        logger.info('Gesture agent stopped')
    
    def list_supported_actions(self):
        supported = get_supported_actions()
        logger.info('Supported action types:')
        for action_type, description in supported.items():
            logger.info('  %s: %s', action_type, description)


def load_config(path: Path) -> AgentConfig:
    if not path.exists():
        logger.error('Config file %s not found', path)
        sys.exit(1)
    with path.open('r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f) or {}
    return AgentConfig(cfg)


def interactive_loop(agent: GestureAgent):
    logger.info('Entering interactive mode. Type quit to exit.')
    while True:
        try:
            raw = input('Gesture code> ').strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not raw:
            continue
        if raw.lower() in {'quit', 'exit'}:
            break
        if raw.startswith('event:'):
            _, evt = raw.split(':', 1)
            agent.send_event(evt.strip() or 'custom_event')
            continue
        if raw.lower() == 'actions':
            agent.list_supported_actions()
            continue
        agent.perform_action(raw)
    logger.info('Interactive mode exited.')


def main():
    parser = argparse.ArgumentParser(description='YOLO-LLM Gesture Control Agent')
    parser.add_argument('--config', default='config.yaml', help='Path to config.yaml')
    parser.add_argument('--sync', action='store_true', help='Only sync config and exit')
    parser.add_argument('--watch', action='store_true', help='Sync config then enter interactive loop')
    parser.add_argument('--realtime', action='store_true', help='Start real-time gesture detection (default)')
    parser.add_argument('--daemon', action='store_true', help='Start daemon mode with config polling')
    parser.add_argument('--gesture', help='Single gesture code to execute once')
    parser.add_argument('--event', help='Send an eventType to /api/event')
    parser.add_argument('--actions', action='store_true', help='List supported action types')
    parser.add_argument('--voice', action='store_true', help='Enable voice control')
    parser.add_argument('--analyze-gesture', help='Analyze gesture intent (gesture_code)')
    parser.add_argument('--chat', help='Chat with AI assistant')
    args = parser.parse_args()
    
    # Default to realtime if no mode specified
    if not any([args.sync, args.watch, args.realtime, args.daemon, args.gesture, args.event, args.actions, args.voice, args.analyze_gesture, args.chat]):
        args.realtime = True
    
    cfg = load_config(Path(args.config))
    agent = GestureAgent(cfg)
    
    try:
        if args.actions:
            agent.list_supported_actions()
            return

        # Sync config for all modes except pure actions list
            try:
                agent.sync_config()
            except Exception as exc:
                logger.error('Unable to fetch config: %s', exc)
                sys.exit(1)
        
        if args.sync and not args.watch and not args.gesture and not args.event:
            logger.info('Config sync finished.')
            return
        
        if args.event:
            agent.send_event(args.event)
        
        if args.gesture:
            agent.perform_action(args.gesture)

        if args.voice:
            if not agent.start_voice_control():
                logger.error('Failed to start voice control')
                sys.exit(1)
            logger.info('Voice control enabled. Press Ctrl+C to stop.')
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info('Stopping voice control...')

        if args.analyze_gesture:
            if not AI_FEATURES_AVAILABLE:
                logger.error('AI features not available')
                sys.exit(1)

            from gestures.mediapipe_detector import GestureResult
            # Create a dummy gesture result for analysis
            gesture_result = GestureResult(
                gesture_code=args.analyze_gesture,
                confidence=0.9,
                bbox=(100, 100, 100, 100)
            )

            analysis = agent.analyze_gesture_intent(gesture_result)
            if analysis:
                print(f"\n🎭 手势分析结果:")
                print(f"手势: {analysis.gesture_code.upper()}")
                print(f"意图: {analysis.intent}")
                print(f"情感: {analysis.emotion}")
                print(f"上下文: {analysis.context}")
                print(f"建议: {', '.join(analysis.suggestions)}")
                print(f"\n🤖 AI回应: {analysis.response_text}")
            else:
                logger.error('Failed to analyze gesture')

        if args.chat:
            if not AI_FEATURES_AVAILABLE:
                logger.error('AI features not available')
                sys.exit(1)

            print(f"\n💬 AI助手 - 您可以说 '退出' 或 'exit' 来结束对话")
            print(f"您: {args.chat}")

            try:
                response = requests.post(
                    f"{agent.config.base_url}/api/llm/chat",
                    json={
                        "message": args.chat,
                        "context": "用户通过命令行启动对话"
                    },
                    timeout=15
                )

                if response.status_code == 200:
                    result = response.json()
                    print(f"AI: {result.get('response', '无法回应')}")
                else:
                    print(f"AI: 对话服务暂时不可用")

            except Exception as e:
                logger.error(f"Chat failed: {e}")
                print(f"AI: 对话服务出现错误")

        if args.watch or (not args.sync and not args.gesture and not args.event and not args.realtime and not args.daemon and not args.voice and not args.analyze_gesture and not args.chat):
            interactive_loop(agent)
        elif args.realtime:
            # Start with both gesture detection and voice control
            agent.start_realtime()
            if AI_FEATURES_AVAILABLE and args.voice:
                agent.start_voice_control()
        elif args.daemon:
            agent.start_daemon()
            
    except Exception as exc:
        logger.error('Fatal error: %s', exc)
        sys.exit(1)
    finally:
        agent.stop()


if __name__ == '__main__':
    main()
