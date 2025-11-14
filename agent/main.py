import argparse
import json
import logging
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

try:
    import pyautogui  # type: ignore
except Exception:  # pragma: no cover
    pyautogui = None


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
)


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
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        logging.info('Received signal %d, shutting down...', signum)
        self.stop()
    
    def sync_config(self) -> None:
        params = {
            'username': self.config.username,
            'application': self.config.application,
            'os': self.config.os_type,
        }
        logging.info('Fetching config from %s', self.config.base_url)
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
            logging.info('Loaded %d gesture mappings', len(self.mapping))
            
            # Update video processor mapping if it exists
            if self.video_processor:
                self.video_processor.update_mapping(self.mapping)
        except Exception as exc:
            logging.error('Failed to sync config: %s', exc)
            raise
    
    def perform_action(self, gesture_code: str) -> bool:
        logging.info('🎯 检测到手势: %s', gesture_code)  # 显示所有检测到的手势
        action = self.mapping.get(gesture_code)
        if not action:
            logging.warning('No action mapping for gesture: %s', gesture_code)
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
            logging.exception('Failed to perform action for %s', gesture_code)
    
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
            logging.info('Log posted: %s', resp.json())
        except Exception as exc:
            logging.error('Failed to post log: %s', exc)
    
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
            logging.info('Event acknowledged: %s', resp.json())
        except Exception as exc:
            logging.error('Failed to send event: %s', exc)
    
    def start_realtime(self):
        logging.info('Starting real-time gesture detection...')
        self.running = True
        
        try:
            # Initial config sync
            self.sync_config()
            
            # Initialize and start video processor
            self.video_processor = VideoProcessor(self.config.video_config, self.mapping)
            
            # Set callbacks
            self.video_processor.on_gesture_detected = self._on_gesture_detected
            self.video_processor.on_action_executed = self._on_action_executed
            
            # Start video processing
            self.video_processor.start()
            
            logging.info('Real-time gesture detection started')
            logging.info('Press Ctrl+C to stop, or press Space in preview window to pause/resume')
            
            # Keep the main thread alive
            while self.running and not self.should_stop.is_set():
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            logging.info('User interrupted, stopping...')
        except Exception as exc:
            logging.error('Error in realtime mode: %s', exc)
        finally:
            self.stop()
    
    def start_daemon(self):
        logging.info('Starting daemon mode...')
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
                    logging.info('Daemon running, checked config at %s', time.strftime('%H:%M:%S'))
                    self.should_stop.wait(self.config.poll_interval)
                except Exception as exc:
                    logging.error('Error in daemon loop: %s', exc)
                    self.should_stop.wait(5)  # Wait before retry
        except KeyboardInterrupt:
            logging.info('User interrupted, stopping daemon...')
        finally:
            self.stop()
    
    def _on_gesture_detected(self, gesture_result: GestureResult):
        logging.info('Gesture detected: %s (confidence: %.2f)', gesture_result.gesture_code, gesture_result.confidence)
    
    def _on_action_executed(self, gesture_code: str, success: bool, message: str):
        self.post_log(
            gesture_code=gesture_code,
            action_type=self.mapping.get(gesture_code, {}).get('type', 'unknown'),
            action_value=self.mapping.get(gesture_code, {}).get('value', ''),
            status='success' if success else 'failure',
            message=message
        )
    
    def stop(self):
        if not self.running:
            return
        
        logging.info('Stopping gesture agent...')
        self.running = False
        self.should_stop.set()
        
        if self.video_processor:
            self.video_processor.stop()
            self.video_processor = None
        
        logging.info('Gesture agent stopped')
    
    def list_supported_actions(self):
        supported = get_supported_actions()
        logging.info('Supported action types:')
        for action_type, description in supported.items():
            logging.info('  %s: %s', action_type, description)


def load_config(path: Path) -> AgentConfig:
    if not path.exists():
        logging.error('Config file %s not found', path)
        sys.exit(1)
    with path.open('r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f) or {}
    return AgentConfig(cfg)


def interactive_loop(agent: GestureAgent):
    logging.info('Entering interactive mode. Type quit to exit.')
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
    logging.info('Interactive mode exited.')


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
    args = parser.parse_args()
    
    # Default to realtime if no mode specified
    if not any([args.sync, args.watch, args.realtime, args.daemon, args.gesture, args.event, args.actions]):
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
                logging.error('Unable to fetch config: %s', exc)
                sys.exit(1)
        
        if args.sync and not args.watch and not args.gesture and not args.event:
            logging.info('Config sync finished.')
            return
        
        if args.event:
            agent.send_event(args.event)
        
        if args.gesture:
            agent.perform_action(args.gesture)
        
        if args.watch or (not args.sync and not args.gesture and not args.event and not args.realtime and not args.daemon):
            interactive_loop(agent)
        elif args.realtime:
            agent.start_realtime()
        elif args.daemon:
            agent.start_daemon()
            
    except Exception as exc:
        logging.error('Fatal error: %s', exc)
        sys.exit(1)
    finally:
        agent.stop()


if __name__ == '__main__':
    main()
