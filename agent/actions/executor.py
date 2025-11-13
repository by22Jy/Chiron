import pyautogui
import subprocess
import logging
import platform
import time
from typing import Tuple, Optional, Dict, Any
from abc import ABC, abstractmethod
import json


class ActionExecutor(ABC):
    @abstractmethod
    def execute(self, action_value: str, payload: Optional[str] = None) -> Tuple[bool, str]:
        pass


class HotkeyExecutor(ActionExecutor):
    def execute(self, action_value: str, payload: Optional[str] = None) -> Tuple[bool, str]:
        if not action_value:
            return False, 'Empty hotkey value'
        
        try:
            keys = [k.strip() for k in action_value.replace('+', ' ').split() if k.strip()]
            if not keys:
                return False, 'Invalid hotkey definition'
            
            logging.info('Pressing hotkey: %s', '+'.join(keys))
            pyautogui.hotkey(*keys)
            return True, f'Hotkey {action_value} sent'
        except Exception as exc:
            return False, f'Hotkey execution failed: {exc}'


class MouseExecutor(ActionExecutor):
    def execute(self, action_value: str, payload: Optional[str] = None) -> Tuple[bool, str]:
        try:
            if payload:
                data = json.loads(payload)
                x = data.get('x', 0)
                y = data.get('y', 0)
            else:
                # Parse from action_value (e.g., '100,200')
                coords = action_value.split(',')
                if len(coords) != 2:
                    return False, 'Invalid mouse coordinates format'
                x, y = int(coords[0].strip()), int(coords[1].strip())
            
            logging.info('Moving mouse to: (%d, %d)', x, y)
            pyautogui.moveTo(x, y, duration=0.3)
            return True, f'Mouse moved to ({x}, {y})'
        except Exception as exc:
            return False, f'Mouse move failed: {exc}'


class ClickExecutor(ActionExecutor):
    def execute(self, action_value: str, payload: Optional[str] = None) -> Tuple[bool, str]:
        try:
            button = action_value.lower() if action_value else 'left'
            if button not in ['left', 'right', 'middle']:
                return False, f'Invalid mouse button: {button}'
            
            clicks = 1
            if payload:
                data = json.loads(payload)
                clicks = data.get('clicks', 1)
            
            logging.info('Clicking %s button %d time(s)', button, clicks)
            pyautogui.click(button=button, clicks=clicks)
            return True, f'{button.capitalize()} click executed {clicks} time(s)'
        except Exception as exc:
            return False, f'Click execution failed: {exc}'


class ScrollExecutor(ActionExecutor):
    def execute(self, action_value: str, payload: Optional[str] = None) -> Tuple[bool, str]:
        try:
            clicks = int(action_value) if action_value.isdigit() else 1
            direction = 'down' if clicks > 0 else 'up'
            
            logging.info('Scrolling %s %d clicks', direction, abs(clicks))
            pyautogui.scroll(clicks)
            return True, f'Scrolled {direction} {abs(clicks)} clicks'
        except Exception as exc:
            return False, f'Scroll execution failed: {exc}'


class TextExecutor(ActionExecutor):
    def execute(self, action_value: str, payload: Optional[str] = None) -> Tuple[bool, str]:
        try:
            text = payload if payload else action_value
            if not text:
                return False, 'No text provided'
            
            logging.info('Typing text: %s', text[:50] + '...' if len(text) > 50 else text)
            pyautogui.typewrite(text, interval=0.05)
            return True, f'Text typed: {len(text)} characters'
        except Exception as exc:
            return False, f'Text typing failed: {exc}'


class WindowExecutor(ActionExecutor):
    def execute(self, action_value: str, payload: Optional[str] = None) -> Tuple[bool, str]:
        try:
            action = action_value.lower()
            if action == 'maximize':
                pyautogui.hotkey('alt', 'space')
                time.sleep(0.1)
                pyautogui.press('x')
            elif action == 'minimize':
                pyautogui.hotkey('alt', 'space')
                time.sleep(0.1)
                pyautogui.press('n')
            elif action == 'close':
                pyautogui.hotkey('alt', 'f4')
            elif action == 'switch':
                pyautogui.hotkey('alt', 'tab')
            else:
                return False, f'Unsupported window action: {action}'
            
            return True, f'Window action {action} executed'
        except Exception as exc:
            return False, f'Window action failed: {exc}'


class SystemExecutor(ActionExecutor):
    def execute(self, action_value: str, payload: Optional[str] = None) -> Tuple[bool, str]:
        try:
            if action_value == 'volume_up':
                if platform.system() == 'Windows':
                    subprocess.run(['powershell', '-Command', '(New-Object -comObject WScript.Shell).SendKeys([char]175)'], capture_output=True)
                else:
                    pyautogui.press('volumeup')
            elif action_value == 'volume_down':
                if platform.system() == 'Windows':
                    subprocess.run(['powershell', '-Command', '(New-Object -comObject WScript.Shell).SendKeys([char]174)'], capture_output=True)
                else:
                    pyautogui.press('volumedown')
            elif action_value == 'mute':
                if platform.system() == 'Windows':
                    subprocess.run(['powershell', '-Command', '(New-Object -comObject WScript.Shell).SendKeys([char]173)'], capture_output=True)
                else:
                    pyautogui.press('volumemute')
            elif action_value == 'screenshot':
                screenshot = pyautogui.screenshot()
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f'screenshot_{timestamp}.png'
                screenshot.save(filename)
                return True, f'Screenshot saved as {filename}'
            else:
                return False, f'Unsupported system action: {action_value}'
            
            return True, f'System action {action_value} executed'
        except Exception as exc:
            return False, f'System action failed: {exc}'


class ActionManager:
    def __init__(self):
        self.executors = {
            'hotkey': HotkeyExecutor(),
            'mouse': MouseExecutor(),
            'click': ClickExecutor(),
            'scroll': ScrollExecutor(),
            'text': TextExecutor(),
            'window': WindowExecutor(),
            'system': SystemExecutor(),
        }
        logging.info('Action manager initialized with %d executor types', len(self.executors))
    
    def execute_action(self, action_type: str, action_value: str, payload: Optional[str] = None) -> Tuple[bool, str]:
        executor = self.executors.get(action_type.lower())
        if not executor:
            return False, f'Action type {action_type} not supported'
        
        try:
            success, message = executor.execute(action_value, payload)
            return success, message
        except Exception as exc:
            return False, f'Action execution error: {exc}'
    
    def get_supported_actions(self) -> Dict[str, str]:
        return {
            'hotkey': 'Keyboard hotkey combinations (e.g., ctrl+c, alt+tab)',
            'mouse': 'Move mouse to coordinates (x,y or JSON payload)',
            'click': 'Mouse click actions (left/right/middle)',
            'scroll': 'Mouse scroll (positive/negative integer)',
            'text': 'Type text content',
            'window': 'Window operations (maximize/minimize/close/switch)',
            'system': 'System actions (volume_up/down/mute/screenshot)',
        }


# Global action manager instance
action_manager = ActionManager()


def execute_action(action_type: str, action_value: str, payload: Optional[str] = None) -> Tuple[bool, str]:
    return action_manager.execute_action(action_type, action_value, payload)


def get_supported_actions() -> Dict[str, str]:
    return action_manager.get_supported_actions()

