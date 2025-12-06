"""
SystemTool - 系统操作工具

提供系统级别的操作功能，包括：
- 应用启动和管理
- 窗口操作
- 系统控制
- 截图功能
"""

import pyautogui
import subprocess
import platform
import time
import os
import logging
from typing import Dict, Any, List, Optional

try:
    from .base_tool import BaseTool, ToolResult
except ImportError:
    from base_tool import BaseTool, ToolResult


class SystemTool(BaseTool):
    """系统操作工具"""

    def __init__(self):
        super().__init__()
        pyautogui.FAILSAFE = False  # 禁用安全模式以避免边界问题

    @property
    def name(self) -> str:
        return "system"

    @property
    def description(self) -> str:
        return "系统操作工具：应用启动、窗口管理、系统控制、截图等"

    @property
    def supported_actions(self) -> List[str]:
        return [
            "open_app",
            "close_app",
            "window_maximize",
            "window_minimize",
            "window_close",
            "window_switch",
            "volume_up",
            "volume_down",
            "volume_mute",
            "screenshot",
            "shutdown",
            "restart",
            "sleep"
        ]

    @property
    def required_permissions(self) -> List[str]:
        return ["system_control", "app_management"]

    def validate_parameters(self, action: str, parameters: Dict[str, Any]) -> bool:
        """验证参数有效性"""
        if action in ["open_app", "close_app"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=["app_name"],
                optional_params=["path", "args"]
            )

        elif action in ["screenshot"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=[],
                optional_params=["filename", "save_path"]
            )

        elif action in ["shutdown", "restart", "sleep"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=[],
                optional_params=["delay_seconds", "force"]
            )

        elif action in ["volume_up", "volume_down"]:
            return self.validate_parameters_base(
                action, parameters,
                required_params=[],
                optional_params=["steps"]
            )

        elif action in ["window_maximize", "window_minimize", "window_close", "window_switch"]:
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
            if action == "open_app":
                return self._open_app(parameters, context)
            elif action == "close_app":
                return self._close_app(parameters, context)
            elif action == "window_maximize":
                return self._window_maximize(parameters, context)
            elif action == "window_minimize":
                return self._window_minimize(parameters, context)
            elif action == "window_close":
                return self._window_close(parameters, context)
            elif action == "window_switch":
                return self._window_switch(parameters, context)
            elif action == "volume_up":
                return self._volume_up(parameters, context)
            elif action == "volume_down":
                return self._volume_down(parameters, context)
            elif action == "volume_mute":
                return self._volume_mute(parameters, context)
            elif action == "screenshot":
                return self._screenshot(parameters, context)
            elif action == "shutdown":
                return self._shutdown(parameters, context)
            elif action == "restart":
                return self._restart(parameters, context)
            elif action == "sleep":
                return self._sleep(parameters, context)
            else:
                return ToolResult(
                    success=False,
                    message=f"不支持的系统动作: {action}"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"执行系统动作 {action} 失败: {str(e)}"
            )

    def _open_app(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """打开应用程序"""
        app_name = parameters["app_name"]
        app_path = parameters.get("path")
        app_args = parameters.get("args", [])

        try:
            if app_path:
                # 使用完整路径
                if platform.system() == "Windows":
                    cmd = [app_path] + app_args
                else:
                    cmd = [app_path] + app_args
                subprocess.Popen(cmd)
            else:
                # 使用应用名称
                if platform.system() == "Windows":
                    subprocess.Popen(["start", app_name], shell=True)
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(["open", "-a", app_name] + app_args)
                else:  # Linux
                    subprocess.Popen([app_name] + app_args)

            return ToolResult(
                success=True,
                message=f"成功启动应用: {app_name}",
                data={"app_name": app_name, "app_path": app_path}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"启动应用 {app_name} 失败: {str(e)}"
            )

    def _close_app(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """关闭应用程序"""
        app_name = parameters["app_name"]

        try:
            if platform.system() == "Windows":
                # Windows下使用taskkill
                subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"],
                             capture_output=True)
            elif platform.system() == "Darwin":
                # macOS下使用pkill
                subprocess.run(["pkill", "-f", app_name], capture_output=True)
            else:
                # Linux下使用pkill
                subprocess.run(["pkill", app_name], capture_output=True)

            return ToolResult(
                success=True,
                message=f"成功关闭应用: {app_name}",
                data={"app_name": app_name}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"关闭应用 {app_name} 失败: {str(e)}"
            )

    def _window_maximize(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """最大化当前窗口"""
        try:
            if platform.system() == "Windows":
                pyautogui.hotkey('alt', 'space')
                time.sleep(0.1)
                pyautogui.press('x')
            else:
                # Unix-like系统
                pyautogui.hotkey('alt', 'space')
                time.sleep(0.1)
                pyautogui.press('x')

            return ToolResult(
                success=True,
                message="窗口已最大化"
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"窗口最大化失败: {str(e)}"
            )

    def _window_minimize(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """最小化当前窗口"""
        try:
            if platform.system() == "Windows":
                pyautogui.hotkey('alt', 'space')
                time.sleep(0.1)
                pyautogui.press('n')
            else:
                # Unix-like系统
                pyautogui.hotkey('alt', 'space')
                time.sleep(0.1)
                pyautogui.press('n')

            return ToolResult(
                success=True,
                message="窗口已最小化"
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"窗口最小化失败: {str(e)}"
            )

    def _window_close(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """关闭当前窗口"""
        try:
            pyautogui.hotkey('alt', 'f4')
            return ToolResult(
                success=True,
                message="窗口已关闭"
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"窗口关闭失败: {str(e)}"
            )

    def _window_switch(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """切换窗口"""
        try:
            pyautogui.hotkey('alt', 'tab')
            return ToolResult(
                success=True,
                message="已切换窗口"
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"窗口切换失败: {str(e)}"
            )

    def _volume_up(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """增加音量"""
        steps = parameters.get("steps", 1)

        try:
            if platform.system() == "Windows":
                for _ in range(steps):
                    subprocess.run(['powershell', '-Command',
                                  '(New-Object -comObject WScript.Shell).SendKeys([char]175)'],
                                 capture_output=True)
                    time.sleep(0.1)
            else:
                for _ in range(steps):
                    pyautogui.press('volumeup')
                    time.sleep(0.1)

            return ToolResult(
                success=True,
                message=f"音量增加 {steps} 级",
                data={"steps": steps}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"音量增加失败: {str(e)}"
            )

    def _volume_down(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """降低音量"""
        steps = parameters.get("steps", 1)

        try:
            if platform.system() == "Windows":
                for _ in range(steps):
                    subprocess.run(['powershell', '-Command',
                                  '(New-Object -comObject WScript.Shell).SendKeys([char]174)'],
                                 capture_output=True)
                    time.sleep(0.1)
            else:
                for _ in range(steps):
                    pyautogui.press('volumedown')
                    time.sleep(0.1)

            return ToolResult(
                success=True,
                message=f"音量降低 {steps} 级",
                data={"steps": steps}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"音量降低失败: {str(e)}"
            )

    def _volume_mute(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """静音/取消静音"""
        try:
            if platform.system() == "Windows":
                subprocess.run(['powershell', '-Command',
                              '(New-Object -comObject WScript.Shell).SendKeys([char]173)'],
                             capture_output=True)
            else:
                pyautogui.press('volumemute')

            return ToolResult(
                success=True,
                message="已切换静音状态"
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"静音切换失败: {str(e)}"
            )

    def _screenshot(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """截图"""
        filename = parameters.get("filename")
        save_path = parameters.get("save_path")

        try:
            screenshot = pyautogui.screenshot()

            # 生成文件名
            if not filename:
                timestamp = time.strftime('%Y%m%d_%H%M%S')
                filename = f'screenshot_{timestamp}.png'

            # 确定保存路径
            if save_path:
                if not os.path.exists(save_path):
                    os.makedirs(save_path, exist_ok=True)
                filepath = os.path.join(save_path, filename)
            else:
                filepath = filename

            screenshot.save(filepath)

            return ToolResult(
                success=True,
                message=f"截图已保存: {filepath}",
                data={"filepath": filepath, "filename": filename},
                context_update={"last_screenshot": filepath}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"截图失败: {str(e)}"
            )

    def _shutdown(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """关机"""
        delay_seconds = parameters.get("delay_seconds", 0)
        force = parameters.get("force", False)

        try:
            if platform.system() == "Windows":
                cmd = ["shutdown", "/s"]
                if delay_seconds > 0:
                    cmd.extend(["/t", str(delay_seconds)])
                if force:
                    cmd.append("/f")
            elif platform.system() == "Darwin":
                cmd = ["sudo", "shutdown", "-h", f"+{delay_seconds // 60}"]
            else:  # Linux
                cmd = ["shutdown", "-h", f"+{delay_seconds // 60}"]

            subprocess.run(cmd, capture_output=True)

            return ToolResult(
                success=True,
                message=f"系统将在 {delay_seconds} 秒后关机",
                data={"delay_seconds": delay_seconds, "force": force}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"关机操作失败: {str(e)}"
            )

    def _restart(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """重启"""
        delay_seconds = parameters.get("delay_seconds", 0)
        force = parameters.get("force", False)

        try:
            if platform.system() == "Windows":
                cmd = ["shutdown", "/r"]
                if delay_seconds > 0:
                    cmd.extend(["/t", str(delay_seconds)])
                if force:
                    cmd.append("/f")
            elif platform.system() == "Darwin":
                cmd = ["sudo", "shutdown", "-r", f"+{delay_seconds // 60}"]
            else:  # Linux
                cmd = ["shutdown", "-r", f"+{delay_seconds // 60}"]

            subprocess.run(cmd, capture_output=True)

            return ToolResult(
                success=True,
                message=f"系统将在 {delay_seconds} 秒后重启",
                data={"delay_seconds": delay_seconds, "force": force}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"重启操作失败: {str(e)}"
            )

    def _sleep(self, parameters: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """休眠"""
        delay_seconds = parameters.get("delay_seconds", 0)

        try:
            if platform.system() == "Windows":
                time.sleep(delay_seconds)
                subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "Sleep"],
                             capture_output=True)
            elif platform.system() == "Darwin":
                time.sleep(delay_seconds)
                subprocess.run(["pmset", "sleepnow"], capture_output=True)
            else:  # Linux
                time.sleep(delay_seconds)
                subprocess.run(["systemctl", "suspend"], capture_output=True)

            return ToolResult(
                success=True,
                message=f"系统将在 {delay_seconds} 秒后休眠",
                data={"delay_seconds": delay_seconds}
            )

        except Exception as e:
            return ToolResult(
                success=False,
                message=f"休眠操作失败: {str(e)}"
            )