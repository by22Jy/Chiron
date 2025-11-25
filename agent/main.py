import argparse
import json
import sys
import signal
import threading
import time
from pathlib import Path
from typing import Dict, Optional, Any

import requests
import yaml

from video_processor import VideoProcessor, VideoConfig
from gestures.mediapipe_detector import GestureResult
from actions.executor import get_supported_actions
from logger_config import setup_component_logger

# Import new AI features
try:
    from speech_controller import VoiceController, VoiceCommand
    from gesture_analyzer import GestureAnalyzer, GestureAnalysis
    AI_FEATURES_AVAILABLE = True
except ImportError as e:
    logger.warning(f'AI features not available: {e}')
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
        self.voice_controller: Optional[VoiceController] = None
        self.gesture_analyzer: Optional[GestureAnalyzer] = None

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
                logger.info('🤖 AI features initialized successfully')
            except Exception as e:
                logger.warning(f'Failed to initialize AI features: {e}')
                AI_FEATURES_AVAILABLE = False
    
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

            # Start video processing
            logger.info('[AGENT] Starting video processor...')
            self.video_processor.start()

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
                self.video_processor.start()
            
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
        logger.info('[AGENT] Gesture detected: %s (confidence: %.2f)', gesture_result.gesture_code, gesture_result.confidence)
        logger.info('[AGENT] Available mappings in agent: %s', list(self.mapping.keys()))

        # Check if we have a mapping for this gesture
        gesture_code_original = gesture_result.gesture_code
        gesture_code_lower = gesture_code_original.lower()

        has_mapping_original = gesture_code_original in self.mapping
        has_mapping_lower = gesture_code_lower in self.mapping

        logger.info('[AGENT] Mapping check: %s -> %s, %s -> %s',
                    gesture_code_original, has_mapping_original,
                    gesture_code_lower, has_mapping_lower)

        if has_mapping_original:
            action = self.mapping[gesture_code_original]
            logger.info('[AGENT] Found action mapping: %s', action)
        elif has_mapping_lower:
            action = self.mapping[gesture_code_lower]
            logger.info('[AGENT] Found action mapping (lowercase): %s', action)
        else:
            logger.warning('[AGENT] No action mapping found for gesture: %s', gesture_code_original)
    
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
            logger.info('🎤 Voice control started')
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
        logger.info(f'🎤 Voice command: {command.command_type} - {command.parameters}')
        self.send_event('voice_command', {
            'command_type': command.command_type,
            'parameters': command.parameters,
            'confidence': command.confidence,
            'raw_text': command.raw_text
        })

    def _on_speech_text(self, text: str):
        """处理识别到的语音文本"""
        logger.info(f'🎤 Speech recognized: {text}')
        self.send_event('speech_recognized', {'text': text})

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
