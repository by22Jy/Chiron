#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用电脑控制模块
跨平台的电脑自动化和控制功能
不依赖Windows特定的库，确保更好的兼容性
"""

import os
import sys
import time
import subprocess
import platform
import psutil
import pyautogui
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
import logging
from datetime import datetime
import asyncio
import webbrowser
import shutil
import pathlib

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ControlAction(Enum):
    """控制动作枚举"""
    HOTKEY = "hotkey"
    MOUSE = "mouse"
    CLICK = "click"
    SCROLL = "scroll"
    TEXT = "text"
    SYSTEM = "system"
    FILE = "file"
    APP = "app"
    SCREEN = "screen"
    PROCESS = "process"
    INFO = "info"

@dataclass
class ActionResult:
    """动作结果"""
    success: bool
    message: str
    data: Dict[str, Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.data is None:
            self.data = {}

class UniversalComputerControl:
    """通用电脑控制类"""

    def __init__(self):
        self.system_platform = platform.system()
        self.screen_width, self.screen_height = pyautogui.size()
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1

        # 性能监控
        self.performance_stats = {
            "total_actions": 0,
            "successful_actions": 0,
            "failed_actions": 0,
            "action_history": []
        }

        # 应用路径映射
        self.app_commands = self._initialize_app_commands()

        # 安全设置
        self.safe_mode = True
        self.confirm_dangerous_actions = True

        logger.info(f"通用电脑控制系统初始化完成 - 平台: {self.system_platform}")

    def _initialize_app_commands(self) -> Dict[str, str]:
        """初始化常见应用命令"""
        commands = {}

        if self.system_platform == "Windows":
            commands.update({
                "notepad": "notepad.exe",
                "calculator": "calc.exe",
                "paint": "mspaint.exe",
                "taskmgr": "taskmgr.exe",
                "cmd": "cmd.exe",
                "powershell": "powershell.exe",
                "explorer": "explorer.exe",
                "chrome": "chrome",
                "firefox": "firefox",
                "edge": "msedge",
                "steam": "steam",
                "control_panel": "control"
            })
        elif self.system_platform == "Darwin":  # macOS
            commands.update({
                "notepad": "open -a TextEdit",
                "calculator": "open -a Calculator",
                "chrome": "open -a 'Google Chrome'",
                "safari": "open -a Safari",
                "steam": "open -a Steam",
                "finder": "open -a Finder"
            })
        else:  # Linux
            commands.update({
                "notepad": "gedit",
                "calculator": "gnome-calculator",
                "chrome": "google-chrome",
                "firefox": "firefox",
                "file_manager": "nautilus",
                "terminal": "gnome-terminal"
            })

        return commands

    async def execute_action(self, action_type: str, parameters: Dict[str, Any]) -> ActionResult:
        """执行控制动作"""
        try:
            self.performance_stats["total_actions"] += 1

            action_enum = ControlAction(action_type.lower())

            # 记录动作开始
            start_time = time.time()

            if action_enum == ControlAction.HOTKEY:
                result = await self._execute_hotkey(parameters)
            elif action_enum == ControlAction.MOUSE:
                result = await self._execute_mouse_action(parameters)
            elif action_enum == ControlAction.CLICK:
                result = await self._execute_click(parameters)
            elif action_enum == ControlAction.SCROLL:
                result = await self._execute_scroll(parameters)
            elif action_enum == ControlAction.TEXT:
                result = await self._execute_text_input(parameters)
            elif action_enum == ControlAction.SYSTEM:
                result = await self._execute_system_action(parameters)
            elif action_enum == ControlAction.FILE:
                result = await self._execute_file_action(parameters)
            elif action_enum == ControlAction.APP:
                result = await self._execute_app_action(parameters)
            elif action_enum == ControlAction.SCREEN:
                result = await self._execute_screen_action(parameters)
            elif action_enum == ControlAction.PROCESS:
                result = await self._execute_process_action(parameters)
            elif action_enum == ControlAction.INFO:
                result = await self._execute_info_action(parameters)
            else:
                result = ActionResult(False, f"不支持的动作类型: {action_type}")

            # 记录性能统计
            execution_time = time.time() - start_time
            self.performance_stats["action_history"].append({
                "action": action_type,
                "success": result.success,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat()
            })

            if result.success:
                self.performance_stats["successful_actions"] += 1
            else:
                self.performance_stats["failed_actions"] += 1

            return result

        except ValueError as e:
            logger.error(f"无效的动作类型: {action_type} - {str(e)}")
            return ActionResult(False, f"无效的动作类型: {action_type}")
        except Exception as e:
            logger.error(f"执行动作失败: {action_type} - {str(e)}")
            self.performance_stats["failed_actions"] += 1
            return ActionResult(False, f"执行失败: {str(e)}")

    async def _execute_hotkey(self, params: Dict[str, Any]) -> ActionResult:
        """执行热键组合"""
        try:
            hotkey = params.get("hotkey", "")
            if not hotkey:
                return ActionResult(False, "热键参数不能为空")

            # 安全检查
            if self.safe_mode and hotkey.lower() in ['alt+f4', 'ctrl+alt+del']:
                logger.warning(f"危险热键操作被阻止: {hotkey}")
                return ActionResult(False, f"安全模式阻止危险操作: {hotkey}")

            pyautogui.hotkey(*hotkey.split('+'))
            logger.info(f"热键执行成功: {hotkey}")
            return ActionResult(True, f"热键 {hotkey} 执行成功")

        except Exception as e:
            return ActionResult(False, f"热键执行失败: {str(e)}")

    async def _execute_mouse_action(self, params: Dict[str, Any]) -> ActionResult:
        """执行鼠标动作"""
        try:
            action = params.get("action", "move")
            x = params.get("x", 0)
            y = params.get("y", 0)
            duration = params.get("duration", 0.2)

            # 边界检查
            x = max(0, min(x, self.screen_width - 1))
            y = max(0, min(y, self.screen_height - 1))

            if action == "move":
                pyautogui.moveTo(x, y, duration=duration)
            elif action == "drag":
                pyautogui.dragTo(x, y, duration=duration)
            else:
                return ActionResult(False, f"不支持的鼠标动作: {action}")

            logger.info(f"鼠标动作执行成功: {action} to ({x}, {y})")
            return ActionResult(True, f"鼠标 {action} 到 ({x}, {y}) 成功", {"position": [x, y]})

        except Exception as e:
            return ActionResult(False, f"鼠标动作失败: {str(e)}")

    async def _execute_click(self, params: Dict[str, Any]) -> ActionResult:
        """执行点击动作"""
        try:
            button = params.get("button", "left")
            clicks = params.get("clicks", 1)
            interval = params.get("interval", 0.1)
            x = params.get("x")
            y = params.get("y")

            if x is not None and y is not None:
                # 点击指定位置
                pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
                position = [x, y]
            else:
                # 点击当前位置
                pyautogui.click(clicks=clicks, interval=interval, button=button)
                current_pos = pyautogui.position()
                position = [current_pos.x, current_pos.y]

            logger.info(f"点击执行成功: {button} x{clicks} at {position}")
            return ActionResult(True, f"{button} 键点击 {clicks} 次成功", {"position": position})

        except Exception as e:
            return ActionResult(False, f"点击失败: {str(e)}")

    async def _execute_scroll(self, params: Dict[str, Any]) -> ActionResult:
        """执行滚动动作"""
        try:
            direction = params.get("direction", "down")
            amount = params.get("amount", 3)
            x = params.get("x")
            y = params.get("y")

            if x is not None and y is not None:
                pyautogui.moveTo(x, y)

            scroll_value = amount if direction == "down" else -amount
            pyautogui.scroll(scroll_value)

            logger.info(f"滚动执行成功: {direction} {amount}")
            return ActionResult(True, f"滚动 {direction} {amount} 单位成功")

        except Exception as e:
            return ActionResult(False, f"滚动失败: {str(e)}")

    async def _execute_text_input(self, params: Dict[str, Any]) -> ActionResult:
        """执行文本输入"""
        try:
            text = params.get("text", "")
            interval = params.get("interval", 0.01)

            if not text:
                return ActionResult(False, "文本内容不能为空")

            pyautogui.typewrite(text, interval=interval)
            logger.info(f"文本输入成功: {text[:50]}...")
            return ActionResult(True, f"输入文本成功 (长度: {len(text)})")

        except Exception as e:
            return ActionResult(False, f"文本输入失败: {str(e)}")

    async def _execute_system_action(self, params: Dict[str, Any]) -> ActionResult:
        """执行系统动作"""
        try:
            action = params.get("action", "")

            if action == "screenshot":
                screenshot_path = params.get("path", f"screenshot_{int(time.time())}.png")
                screenshot = pyautogui.screenshot()
                screenshot.save(screenshot_path)
                return ActionResult(True, f"截图保存成功: {screenshot_path}", {"path": screenshot_path})

            elif action == "screen_info":
                info = {
                    "resolution": [self.screen_width, self.screen_height],
                    "platform": self.system_platform,
                    "primary_screen": True
                }
                return ActionResult(True, "屏幕信息获取成功", info)

            elif action == "system_info":
                info = {
                    "platform": self.system_platform,
                    "platform_release": platform.release(),
                    "platform_version": platform.version(),
                    "architecture": platform.machine(),
                    "processor": platform.processor(),
                    "cpu_count": psutil.cpu_count(),
                    "memory_total": psutil.virtual_memory().total,
                    "memory_available": psutil.virtual_memory().available,
                    "disk_usage": {
                        "total": psutil.disk_usage('/').total if self.system_platform != "Windows" else psutil.disk_usage('C:').total,
                        "free": psutil.disk_usage('/').free if self.system_platform != "Windows" else psutil.disk_usage('C:').free
                    }
                }
                return ActionResult(True, "系统信息获取成功", info)

            elif action == "open_url":
                url = params.get("url", "")
                if not url:
                    return ActionResult(False, "URL不能为空")

                webbrowser.open(url)
                return ActionResult(True, f"URL打开成功: {url}")

            elif action == "lock":
                if self.system_platform == "Windows":
                    os.system("rundll32.exe user32.dll,LockWorkStation")
                elif self.system_platform == "Darwin":
                    os.system('/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession -suspend')
                else:
                    os.system("xdg-screensaver lock")
                return ActionResult(True, "系统锁屏成功")

            elif action == "shutdown":
                if self.safe_mode:
                    return ActionResult(False, "安全模式禁止关机操作")
                if self.system_platform == "Windows":
                    os.system("shutdown /s /t 1")
                elif self.system_platform == "Darwin":
                    os.system("shutdown -h now")
                else:
                    os.system("shutdown now")
                return ActionResult(True, "系统关机成功")

            elif action == "restart":
                if self.safe_mode:
                    return ActionResult(False, "安全模式禁止重启操作")
                if self.system_platform == "Windows":
                    os.system("shutdown /r /t 1")
                elif self.system_platform == "Darwin":
                    os.system("shutdown -r now")
                else:
                    os.system("reboot")
                return ActionResult(True, "系统重启成功")

            elif action == "sleep":
                if self.system_platform == "Windows":
                    os.system("rundll32.exe powrprof.dll,SetSuspendState Sleep")
                elif self.system_platform == "Darwin":
                    os.system("pmset sleepnow")
                else:
                    os.system("systemctl suspend")
                return ActionResult(True, "系统休眠成功")

            else:
                return ActionResult(False, f"不支持的系统动作: {action}")

        except Exception as e:
            return ActionResult(False, f"系统动作失败: {str(e)}")

    async def _execute_file_action(self, params: Dict[str, Any]) -> ActionResult:
        """执行文件动作"""
        try:
            action = params.get("action", "")
            path = params.get("path", "")

            if not path:
                return ActionResult(False, "文件路径不能为空")

            if action == "open":
                if self.system_platform == "Windows":
                    os.startfile(path)
                else:
                    opener = "open" if self.system_platform == "Darwin" else "xdg-open"
                    subprocess.call([opener, path])
                return ActionResult(True, f"文件打开成功: {path}")

            elif action == "exists":
                exists = os.path.exists(path)
                file_type = "directory" if os.path.isdir(path) else "file" if os.path.isfile(path) else "other"
                return ActionResult(True, f"文件存在性检查完成: {path}", {
                    "exists": exists,
                    "type": file_type
                })

            elif action == "list":
                if os.path.isdir(path):
                    files = os.listdir(path)
                    file_info = []
                    for file in files:
                        file_path = os.path.join(path, file)
                        try:
                            stat = os.stat(file_path)
                            file_info.append({
                                "name": file,
                                "type": "directory" if os.path.isdir(file_path) else "file",
                                "size": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                            })
                        except:
                            file_info.append({
                                "name": file,
                                "type": "unknown",
                                "size": 0,
                                "modified": None
                            })
                    return ActionResult(True, f"文件夹列表获取成功: {path}", {"files": file_info})
                else:
                    return ActionResult(False, f"路径不是文件夹: {path}")

            elif action == "create_folder":
                os.makedirs(path, exist_ok=True)
                return ActionResult(True, f"文件夹创建成功: {path}")

            elif action == "write_text":
                content = params.get("content", "")
                if not content:
                    return ActionResult(False, "文件内容不能为空")

                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return ActionResult(True, f"文件写入成功: {path}")

            elif action == "read_text":
                if not os.path.isfile(path):
                    return ActionResult(False, f"文件不存在: {path}")

                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return ActionResult(True, f"文件读取成功: {path}", {"content": content})

            elif action == "copy":
                destination = params.get("destination", "")
                if not destination:
                    return ActionResult(False, "目标路径不能为空")

                if os.path.isfile(path):
                    shutil.copy2(path, destination)
                elif os.path.isdir(path):
                    shutil.copytree(path, destination)
                return ActionResult(True, f"文件复制成功: {path} -> {destination}")

            elif action == "move":
                destination = params.get("destination", "")
                if not destination:
                    return ActionResult(False, "目标路径不能为空")

                shutil.move(path, destination)
                return ActionResult(True, f"文件移动成功: {path} -> {destination}")

            elif action == "delete":
                if self.safe_mode and not params.get("confirm", False):
                    return ActionResult(False, "安全模式需要确认才能删除文件")

                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                return ActionResult(True, f"文件删除成功: {path}")

            else:
                return ActionResult(False, f"不支持的文件动作: {action}")

        except Exception as e:
            return ActionResult(False, f"文件动作失败: {str(e)}")

    async def _execute_app_action(self, params: Dict[str, Any]) -> ActionResult:
        """执行应用动作"""
        try:
            action = params.get("action", "")
            app_name = params.get("app_name", "")
            app_path = params.get("app_path", "")

            if not action:
                return ActionResult(False, "应用动作不能为空")

            if action == "launch":
                if app_path:
                    # 使用指定路径启动
                    subprocess.Popen(app_path.split())
                    return ActionResult(True, f"应用启动成功: {app_path}")

                elif app_name:
                    # 使用预定义应用名启动
                    if app_name in self.app_commands:
                        app_command = self.app_commands[app_name]
                        subprocess.Popen(app_command.split())
                        return ActionResult(True, f"应用启动成功: {app_name}")
                    else:
                        return ActionResult(False, f"未知应用: {app_name}")

                else:
                    return ActionResult(False, "应用名称或路径不能为空")

            elif action == "launch_with_url":
                url = params.get("url", "")
                if not url:
                    return ActionResult(False, "URL不能为空")

                webbrowser.open(url)
                return ActionResult(True, f"应用通过URL启动成功: {url}")

            elif action == "list":
                running_apps = []
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                    try:
                        running_apps.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cpu": round(proc.info['cpu_percent'], 2),
                            "memory": round(proc.info['memory_percent'], 2)
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                # 按CPU使用率排序
                running_apps.sort(key=lambda x: x['cpu'], reverse=True)

                return ActionResult(True, f"获取到 {len(running_apps)} 个运行中的应用", {"apps": running_apps[:50]})

            elif action == "close":
                if not app_name:
                    return ActionResult(False, "应用名称不能为空")

                # 查找并关闭应用进程
                killed_processes = []
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if (app_name.lower() in proc.info['name'].lower() or
                            any(app_name.lower() in cmd_part.lower() for cmd_part in proc.info['cmdline'] or [])):
                            proc.terminate()
                            killed_processes.append(proc.info['name'])
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                if killed_processes:
                    return ActionResult(True, f"应用关闭成功: {', '.join(killed_processes)}")
                else:
                    return ActionResult(False, f"未找到运行中的应用: {app_name}")

            elif action == "install_steam_game":
                # Steam游戏安装
                game_id = params.get("game_id", "")
                if not game_id:
                    return ActionResult(False, "Steam游戏ID不能为空")

                steam_url = f"steam://install/{game_id}"
                webbrowser.open(steam_url)
                return ActionResult(True, f"Steam游戏安装启动: {game_id}")

            elif action == "purchase_steam_game":
                # Steam游戏购买
                game_id = params.get("game_id", "")
                if not game_id:
                    return ActionResult(False, "Steam游戏ID不能为空")

                steam_url = f"https://store.steampowered.com/app/{game_id}/"
                webbrowser.open(steam_url)
                return ActionResult(True, f"Steam游戏购买页面打开: {game_id}")

            elif action == "open_website":
                website = params.get("website", "")
                if not website:
                    return ActionResult(False, "网站地址不能为空")

                if not website.startswith(('http://', 'https://')):
                    website = 'https://' + website

                webbrowser.open(website)
                return ActionResult(True, f"网站打开成功: {website}")

            else:
                return ActionResult(False, f"不支持的应用动作: {action}")

        except Exception as e:
            return ActionResult(False, f"应用动作失败: {str(e)}")

    async def _execute_screen_action(self, params: Dict[str, Any]) -> ActionResult:
        """执行屏幕动作"""
        try:
            action = params.get("action", "")

            if action == "capture":
                x = params.get("x", 0)
                y = params.get("y", 0)
                width = params.get("width", self.screen_width)
                height = params.get("height", self.screen_height)
                save_path = params.get("save_path", f"screen_capture_{int(time.time())}.png")

                # 截取指定区域
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
                screenshot.save(save_path)

                return ActionResult(True, f"屏幕截图成功: {save_path}", {
                    "path": save_path,
                    "region": [x, y, width, height]
                })

            elif action == "get_mouse_position":
                position = pyautogui.position()
                return ActionResult(True, "鼠标位置获取成功", {
                    "x": position.x,
                    "y": position.y
                })

            elif action == "find_color":
                x = params.get("x", self.screen_width // 2)
                y = params.get("y", self.screen_height // 2)

                color = pyautogui.pixel(x, y)
                hex_color = '#{:02x}{:02x}{:02x}'.format(*color)

                return ActionResult(True, f"像素颜色获取成功: ({x}, {y})", {
                    "rgb": list(color),
                    "hex": hex_color,
                    "position": [x, y]
                })

            else:
                return ActionResult(False, f"不支持的屏幕动作: {action}")

        except Exception as e:
            return ActionResult(False, f"屏幕动作失败: {str(e)}")

    async def _execute_process_action(self, params: Dict[str, Any]) -> ActionResult:
        """执行进程动作"""
        try:
            action = params.get("action", "")
            pid = params.get("pid", "")
            process_name = params.get("process_name", "")

            if not action:
                return ActionResult(False, "进程动作不能为空")

            if action == "list":
                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent', 'memory_percent', 'create_time']):
                    try:
                        processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "status": proc.info['status'],
                            "cpu": round(proc.info['cpu_percent'], 2),
                            "memory": round(proc.info['memory_percent'], 2),
                            "create_time": datetime.fromtimestamp(proc.info['create_time']).isoformat()
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                # 按内存使用率排序
                processes.sort(key=lambda x: x['memory'], reverse=True)

                return ActionResult(True, f"获取到 {len(processes)} 个进程", {"processes": processes[:100]})

            elif action == "info":
                if pid:
                    try:
                        proc = psutil.Process(int(pid))
                        info = {
                            "pid": proc.pid,
                            "name": proc.name(),
                            "status": proc.status(),
                            "cpu": round(proc.cpu_percent(), 2),
                            "memory": round(proc.memory_percent(), 2),
                            "create_time": datetime.fromtimestamp(proc.create_time()).isoformat(),
                            "exe": proc.exe(),
                            "cwd": proc.cwd(),
                            "cmdline": proc.cmdline()
                        }
                        return ActionResult(True, f"进程信息获取成功: PID {pid}", info)
                    except psutil.NoSuchProcess:
                        return ActionResult(False, f"进程不存在: PID {pid}")
                else:
                    return ActionResult(False, "PID不能为空")

            elif action == "kill":
                if self.safe_mode:
                    return ActionResult(False, "安全模式禁止终止进程")

                if pid:
                    try:
                        proc = psutil.Process(int(pid))
                        proc.terminate()
                        return ActionResult(True, f"进程终止成功: PID {pid}")
                    except psutil.NoSuchProcess:
                        return ActionResult(False, f"进程不存在: PID {pid}")

                elif process_name:
                    killed_count = 0
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            if process_name.lower() in proc.info['name'].lower():
                                proc.terminate()
                                killed_count += 1
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            continue

                    if killed_count > 0:
                        return ActionResult(True, f"终止了 {killed_count} 个进程: {process_name}")
                    else:
                        return ActionResult(False, f"未找到匹配的进程: {process_name}")

                else:
                    return ActionResult(False, "PID或进程名不能为空")

            else:
                return ActionResult(False, f"不支持的进程动作: {action}")

        except Exception as e:
            return ActionResult(False, f"进程动作失败: {str(e)}")

    async def _execute_info_action(self, params: Dict[str, Any]) -> ActionResult:
        """执行信息获取动作"""
        try:
            action = params.get("action", "")

            if action == "performance_stats":
                stats = self.get_performance_stats()
                return ActionResult(True, "性能统计获取成功", stats)

            elif action == "available_actions":
                actions = [action.value for action in ControlAction]
                return ActionResult(True, "可用动作列表获取成功", {"actions": actions})

            elif action == "app_commands":
                return ActionResult(True, "应用命令列表获取成功", {"commands": self.app_commands})

            elif action == "system_capabilities":
                capabilities = {
                    "platform": self.system_platform,
                    "screen_resolution": [self.screen_width, self.screen_height],
                    "safe_mode": self.safe_mode,
                    "supports_automation": True,
                    "supports_file_operations": True,
                    "supports_process_management": True,
                    "supports_app_management": True
                }
                return ActionResult(True, "系统能力获取成功", capabilities)

            else:
                return ActionResult(False, f"不支持的信息动作: {action}")

        except Exception as e:
            return ActionResult(False, f"信息动作失败: {str(e)}")

    def get_performance_stats(self) -> Dict[str, Any]:
        """获取性能统计信息"""
        success_rate = 0
        if self.performance_stats["total_actions"] > 0:
            success_rate = (self.performance_stats["successful_actions"] / self.performance_stats["total_actions"]) * 100

        recent_actions = self.performance_stats["action_history"][-10:]
        avg_execution_time = 0
        if recent_actions:
            avg_execution_time = sum(action["execution_time"] for action in recent_actions) / len(recent_actions)

        return {
            "total_actions": self.performance_stats["total_actions"],
            "successful_actions": self.performance_stats["successful_actions"],
            "failed_actions": self.performance_stats["failed_actions"],
            "success_rate": round(success_rate, 2),
            "recent_actions": recent_actions,
            "avg_execution_time": round(avg_execution_time, 3),
            "system_info": {
                "platform": self.system_platform,
                "screen_resolution": [self.screen_width, self.screen_height],
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available
            }
        }

    def export_configuration(self) -> Dict[str, Any]:
        """导出配置信息"""
        return {
            "system_platform": self.system_platform,
            "screen_resolution": [self.screen_width, self.screen_height],
            "app_commands": self.app_commands,
            "safe_mode": self.safe_mode,
            "confirm_dangerous_actions": self.confirm_dangerous_actions,
            "supported_actions": [action.value for action in ControlAction],
            "timestamp": datetime.now().isoformat()
        }

# 全局实例
computer_control = UniversalComputerControl()

# 异步接口函数
async def execute_computer_action(action_type: str, parameters: Dict[str, Any]) -> ActionResult:
    """执行电脑控制动作的异步接口"""
    return await computer_control.execute_action(action_type, parameters)

def get_computer_stats() -> Dict[str, Any]:
    """获取电脑统计信息"""
    return computer_control.get_performance_stats()

# 测试代码
async def test_universal_computer_control():
    """测试通用电脑控制功能"""
    print("=== 通用电脑控制测试 ===")

    # 测试屏幕信息
    result = await execute_computer_action("system", {"action": "screen_info"})
    print(f"屏幕信息测试: {result.success} - {result.message}")
    if result.success:
        print(f"  分辨率: {result.data['resolution']}")

    # 测试系统信息
    result = await execute_computer_action("system", {"action": "system_info"})
    print(f"系统信息测试: {result.success} - {result.message}")
    if result.success:
        info = result.data
        print(f"  平台: {info['platform']}")
        print(f"  CPU核心数: {info['cpu_count']}")
        print(f"  内存总量: {info['memory_total'] / (1024**3):.1f}GB")

    # 测试鼠标位置
    result = await execute_computer_action("screen", {"action": "get_mouse_position"})
    print(f"鼠标位置测试: {result.success} - {result.message}")
    if result.success:
        pos = result.data
        print(f"  当前位置: ({pos['x']}, {pos['y']})")

    # 测试应用列表
    result = await execute_computer_action("app", {"action": "list"})
    print(f"应用列表测试: {result.success} - {result.message}")
    if result.success:
        apps = result.data['apps'][:5]  # 只显示前5个
        for app in apps:
            print(f"  {app['name']} (PID: {app['pid']}, CPU: {app['cpu']}%)")

    # 测试进程列表
    result = await execute_computer_action("process", {"action": "list"})
    print(f"进程列表测试: {result.success} - {result.message}")
    if result.success:
        processes = result.data['processes'][:5]  # 只显示前5个
        for proc in processes:
            print(f"  {proc['name']} (PID: {proc['pid']}, 内存: {proc['memory']}%)")

    # 测试系统能力
    result = await execute_computer_action("info", {"action": "system_capabilities"})
    print(f"系统能力测试: {result.success} - {result.message}")
    if result.success:
        capabilities = result.data
        print(f"  平台: {capabilities['platform']}")
        print(f"  自动化支持: {capabilities['supports_automation']}")

    # 显示性能统计
    stats = get_computer_stats()
    print(f"\n性能统计:")
    print(f"  总动作数: {stats['total_actions']}")
    print(f"  成功率: {stats['success_rate']}%")
    print(f"  平均执行时间: {stats['avg_execution_time']}秒")

if __name__ == "__main__":
    asyncio.run(test_universal_computer_control())