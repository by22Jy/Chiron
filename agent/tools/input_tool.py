"""
InputTool - 输入工具

提供鼠标和键盘的输入控制功能
"""

import pyautogui
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
import json

try:
    from .base_tool import BaseTool, ToolResult
except ImportError:
    from base_tool import BaseTool, ToolResult


class InputTool(BaseTool):
    """输入工具"""

    def __init__(self):
        super().__init__()
        pyautogui.FAILSAFE = False  # 禁用安全模式以避免边界问题

    @property
    def name(self) -> str:
        return "input"

    @property
    def description(self) -> str:
        return "输入工具：键盘输入、鼠标点击、滚动等"

    @property
    def supported_actions(self) -> List[str]:
        return [
            "mouse_move",
            "mouse_click",
            "mouse_drag",
            "mouse_scroll",
            "type_text",
            "hotkey",
            "key_press",
            "get_mouse_position",
            "get_screen_size"
        ]

    @property
    def required_permissions(self) -> List[str]:
        return ["input_control"]

    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """验证参数有效性"""
        if action in ["mouse_move", "mouse_click", "mouse_drag"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["x", "y"],
                optional_params=["duration", "button", "pause"]
            )

        elif action in ["mouse_scroll"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["clicks"],
                optional_params=["x", "y", "direction"]
            )

        elif action in ["type_text"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["text"],
                optional_params=["interval", "delay"]
            )

        elif action in ["hotkey"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["keys"],
                optional_params=["pause"]
            )

        elif action in ["key_press"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["key"],
                optional_params=["presses", "pause"]
            )

        elif action in ["get_mouse_position", "get_screen_size"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=[],
                optional_params=[]
            )

        else:
            self.logger.error(f"不支持的动作: {action}")
            return False

    def execute_action(self, action: str, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """执行具体动作"""
        try:
            if action == "mouse_move":
                return self._mouse_move(parameters, context)
            elif action == "mouse_click":
                return self._mouse_click(parameters, context)
            elif action == "mouse_drag":
                return self._mouse_drag(parameters, context)
            elif action == "mouse_scroll":
                return self._mouse_scroll(parameters, context)
            elif action == "type_text":
                return self._type_text(parameters, context)
            elif action == "hotkey":
                return self._hotkey(parameters, context)
            elif action == "key_press":
                return self._key_press(parameters, context)
            elif action == "get_mouse_position":
                return self._get_mouse_position(parameters, context)
            elif action == "get_screen_size":
                return self._get_screen_size(parameters, context)
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的输入动作: {action}"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"执行输入动作 {action} 失败: {str(e)}"
            )

    def _mouse_move(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """移动鼠标"""
        x = parameters["x"]
        y = parameters["y"]
        duration = parameters.get("duration", 0.3)

        try:
            # 验证坐标范围
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return ToolResult(
                    success=False,
                    message=f"坐标超出屏幕范围: ({x}, {y}), 屏幕尺寸: {screen_width}x{screen_height}"
                )

            pyautogui.moveTo(x, y, duration=duration)

            return ToolResult(
                success=True,
                message=f"鼠标移动到: ({x}, {y})",
                data={"x": x, "y": y, "duration": duration}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"鼠标移动失败: {str(e)}"
            )

    def _mouse_click(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """鼠标点击"""
        x = parameters["x"]
        y = parameters["y"]
        button = parameters.get("button", "left")
        clicks = parameters.get("clicks", 1)
        pause = parameters.get("pause", 0.1)

        try:
            # 验证按钮
            if button not in ["left", "right", "middle"]:
                return ToolResult(
                    success=False,
                    message=f"不支持的鼠标按钮: {button}"
                )

            # 验证坐标范围
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return ToolResult(
                    success=False,
                    message=f"坐标超出屏幕范围: ({x}, {y}), 屏幕尺寸: {screen_width}x{screen_height}"
                )

            # 移动到目标位置
            pyautogui.moveTo(x, y, duration=0.2)

            # 执行点击
            pyautogui.click(button=button, clicks=clicks, interval=pause)

            return ToolResult(
                success=True,
                message=f"鼠标点击: ({x}, {y}) {button} 按钮 {clicks} 次",
                data={"x": x, "y": y, "button": button, "clicks": clicks}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"鼠标点击失败: {str(e)}"
            )

    def _mouse_drag(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """鼠标拖拽"""
        x = parameters["x"]
        y = parameters["y"]
        button = parameters.get("button", "left")
        duration = parameters.get("duration", 0.5)

        try:
            # 验证按钮
            if button not in ["left", "right", "middle"]:
                return ToolResult(
                    success=False,
                    message=f"不支持的鼠标按钮: {button}"
                )

            # 验证坐标范围
            screen_width, screen_height = pyautogui.size()
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                return ToolResult(
                    success=False,
                    message=f"坐标超出屏幕范围: ({x}, {y}), 屏幕尺寸: {screen_width}x{screen_height}"
                )

            # 获取当前位置
            current_x, current_y = pyautogui.position()

            # 执行拖拽
            pyautogui.dragTo(x, y, duration=duration, button=button)

            return ToolResult(
                success=True,
                message=f"鼠标拖拽: ({current_x}, {current_y}) -> ({x}, {y})",
                data={
                    "start_x": current_x,
                    "start_y": current_y,
                    "end_x": x,
                    "end_y": y,
                    "button": button,
                    "duration": duration
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"鼠标拖拽失败: {str(e)}"
            )

    def _mouse_scroll(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """鼠标滚动"""
        clicks = parameters["clicks"]
        x = parameters.get("x")
        y = parameters.get("y")
        direction = parameters.get("direction", "down")

        try:
            # 处理方向
            if direction == "up":
                clicks = -abs(clicks)
            elif direction == "down":
                clicks = abs(clicks)
            elif clicks > 0:
                direction = "down"
            elif clicks < 0:
                direction = "up"

            # 如果指定了位置，先移动到该位置
            if x is not None and y is not None:
                pyautogui.moveTo(x, y, duration=0.2)
                position_info = f"在位置 ({x}, {y}) "
            else:
                position_info = "在当前位置 "

            # 执行滚动
            pyautogui.scroll(clicks)

            return ToolResult(
                success=True,
                message=f"{position_info}向上滚动 {abs(clicks)} 次" if clicks < 0 else f"{position_info}向下滚动 {abs(clicks)} 次",
                data={
                    "clicks": clicks,
                    "direction": direction,
                    "x": x,
                    "y": y
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"鼠标滚动失败: {str(e)}"
            )

    def _type_text(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """输入文本"""
        text = parameters["text"]
        interval = parameters.get("interval", 0.05)
        delay = parameters.get("delay", 0)

        try:
            # 添加延迟
            if delay > 0:
                time.sleep(delay)

            # 输入文本
            pyautogui.typewrite(text, interval=interval)

            return ToolResult(
                success=True,
                message=f"文本输入完成: {len(text)} 个字符",
                data={
                    "text": text[:100] + "..." if len(text) > 100 else text,
                    "length": len(text),
                    "interval": interval,
                    "delay": delay
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"文本输入失败: {str(e)}"
            )

    def _hotkey(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """组合键"""
        keys = parameters["keys"]
        pause = parameters.get("pause", 0.1)

        try:
            # 处理不同格式的keys参数
            if isinstance(keys, str):
                # 字符串格式，如 "ctrl+c" 或 "ctrl+shift+t"
                if '+' in keys:
                    keys_list = [k.strip() for k in keys.split('+')]
                else:
                    keys_list = [keys]
            elif isinstance(keys, list):
                keys_list = keys
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的keys参数类型: {type(keys)}"
                )

            # 添加暂停
            if pause > 0:
                time.sleep(pause)

            # 执行组合键
            pyautogui.hotkey(*keys_list)

            return ToolResult(
                success=True,
                message=f"组合键执行: {'+'.join(keys_list)}",
                data={
                    "keys": keys_list,
                    "hotkey": '+'.join(keys_list),
                    "pause": pause
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"组合键执行失败: {str(e)}"
            )

    def _key_press(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """按键"""
        key = parameters["key"]
        presses = parameters.get("presses", 1)
        pause = parameters.get("pause", 0.1)

        try:
            # 添加暂停
            if pause > 0:
                time.sleep(pause)

            # 执行按键
            pyautogui.press(key, presses=presses)

            return ToolResult(
                success=True,
                message=f"按键执行: {key} x {presses}",
                data={
                    "key": key,
                    "presses": presses,
                    "pause": pause
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"按键执行失败: {str(e)}"
            )

    def _get_mouse_position(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """获取鼠标位置"""
        try:
            x, y = pyautogui.position()

            return ToolResult(
                success=True,
                message=f"当前鼠标位置: ({x}, {y})",
                data={
                    "x": x,
                    "y": y,
                    "position": {"x": x, "y": y}
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"获取鼠标位置失败: {str(e)}"
            )

    def _get_screen_size(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """获取屏幕尺寸"""
        try:
            width, height = pyautogui.size()

            return ToolResult(
                success=True,
                message=f"屏幕尺寸: {width}x{height}",
                data={
                    "width": width,
                    "height": height,
                    "size": {"width": width, "height": height}
                }
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"获取屏幕尺寸失败: {str(e)}"
            )