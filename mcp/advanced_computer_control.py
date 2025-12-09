#!/usr/bin/env python3
"""
高级电脑控制工具集
支持更灵活的智能操控，类似OpenAI Computer Use
"""

import os
import time
import subprocess
import psutil
import pyautogui
import win32gui
import win32con
import win32api
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json
from datetime import datetime

# 设置pyautogui安全措施
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

@dataclass
class WindowInfo:
    """窗口信息"""
    title: str
    handle: int
    rect: Tuple[int, int, int, int]  # left, top, right, bottom
    visible: bool
    process_name: str

@dataclass
class ScreenElement:
    """屏幕元素信息"""
    element_type: str  # "button", "text", "input", "image", "icon"
    text: Optional[str]
    position: Tuple[int, int]
    size: Tuple[int, int]
    confidence: float
    screenshot_path: Optional[str]

class AdvancedComputerController:
    """高级电脑控制器 - 支持复杂应用操作"""

    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.current_window = None

    def get_all_windows(self) -> List[WindowInfo]:
        """获取所有窗口信息"""
        windows = []

        def enum_window_callback(hwnd, windows_list):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                if window_title.strip():
                    rect = win32gui.GetWindowRect(hwnd)
                    left, top, right, bottom = rect

                    # 获取进程信息
                    _, pid = win32gui.GetWindowThreadProcessId(hwnd)
                    try:
                        process = psutil.Process(pid)
                        process_name = process.name()
                    except:
                        process_name = "unknown"

                    window_info = WindowInfo(
                        title=window_title,
                        handle=hwnd,
                        rect=rect,
                        visible=True,
                        process_name=process_name
                    )
                    windows_list.append(window_info)

        win32gui.EnumWindows(enum_window_callback, windows)
        return windows

    def find_window_by_title(self, title_keywords: List[str]) -> Optional[WindowInfo]:
        """根据关键词查找窗口"""
        windows = self.get_all_windows()

        for window in windows:
            title_lower = window.title.lower()
            if any(keyword.lower() in title_lower for keyword in title_keywords):
                return window

        return None

    def activate_window(self, window: WindowInfo) -> bool:
        """激活指定窗口"""
        try:
            # 恢复窗口
            if win32gui.IsIconic(window.handle):
                win32gui.ShowWindow(window.handle, win32con.SW_RESTORE)
            else:
                win32gui.ShowWindow(window.handle, win32con.SW_SHOW)

            # 置顶
            win32gui.SetForegroundWindow(window.handle)
            time.sleep(0.5)

            return True
        except Exception as e:
            print(f"激活窗口失败: {e}")
            return False

    def launch_application(self, app_name: str) -> bool:
        """启动应用程序"""
        try:
            # 常见应用程序映射
            app_commands = {
                "steam": "steam://",
                "notepad": "notepad",
                "calculator": "calc",
                "browser": "chrome",
                "chrome": "chrome",
                "firefox": "firefox",
                "word": "winword",
                "excel": "excel",
                "powerpoint": "powerpnt",
                "explorer": "explorer",
                "taskmgr": "taskmgr",
                "cmd": "cmd",
                "powershell": "powershell",
                "vscode": "code",
                "wechat": "weixin",
                "qq": "qq"
            }

            command = app_commands.get(app_name.lower(), app_name)
            subprocess.Popen(command, shell=True)
            time.sleep(2)
            return True

        except Exception as e:
            print(f"启动应用失败: {e}")
            return False

    def find_screen_elements(self, element_type: str = None, text_contains: str = None) -> List[ScreenElement]:
        """查找屏幕元素 (使用OCR或图像识别)"""
        elements = []

        # 截图
        screenshot = pyautogui.screenshot()
        screenshot_path = f"temp_screenshot_{int(time.time())}.png"
        screenshot.save(screenshot_path)

        # 这里可以集成OCR库(如pytesseract)或图像识别库
        # 简化实现，返回一些模拟的屏幕元素
        try:
            # 实际项目中这里应该使用：
            # 1. OCR识别文本元素
            # 2. 图像匹配找到按钮和图标
            # 3. 计算机视觉识别UI元素

            if element_type == "button":
                # 模拟找到按钮
                elements.append(ScreenElement(
                    element_type="button",
                    text="确认",
                    position=(100, 200),
                    size=(80, 30),
                    confidence=0.9,
                    screenshot_path=screenshot_path
                ))
            elif element_type == "input" and text_contains:
                # 模拟找到输入框
                elements.append(ScreenElement(
                    element_type="input",
                    text=f"包含'{text_contains}'的输入框",
                    position=(150, 300),
                    size=(200, 25),
                    confidence=0.85,
                    screenshot_path=screenshot_path
                ))
        except Exception as e:
            print(f"查找屏幕元素失败: {e}")

        return elements

    def click_element(self, element: ScreenElement) -> bool:
        """点击屏幕元素"""
        try:
            x, y = element.position
            pyautogui.click(x, y)
            return True
        except Exception as e:
            print(f"点击元素失败: {e}")
            return False

    def type_text(self, text: str, position: Optional[Tuple[int, int]] = None) -> bool:
        """输入文本"""
        try:
            if position:
                x, y = position
                pyautogui.click(x, y)
                time.sleep(0.2)

            pyautogui.typewrite(text, interval=0.1)
            return True
        except Exception as e:
            print(f"输入文本失败: {e}")
            return False

    def execute_steam_workflow(self, action: str, game_name: str = None) -> Dict[str, Any]:
        """执行Steam相关操作"""
        result = {"success": False, "message": "", "steps": []}

        try:
            # 1. 启动Steam
            if not self.launch_application("steam"):
                result["message"] = "启动Steam失败"
                return result

            result["steps"].append("Steam启动成功")
            time.sleep(5)  # 等待Steam完全启动

            # 2. 查找Steam窗口
            steam_window = self.find_window_by_title(["steam"])
            if not steam_window:
                result["message"] = "未找到Steam窗口"
                return result

            result["steps"].append("找到Steam窗口")

            # 3. 激活Steam窗口
            if not self.activate_window(steam_window):
                result["message"] = "激活Steam窗口失败"
                return result

            result["steps"].append("Steam窗口激活成功")

            # 4. 根据不同操作执行相应动作
            if action == "buy_game" and game_name:
                result["steps"].append(f"准备购买游戏: {game_name}")
                # 这里需要实现具体的购买流程
                # 搜索游戏 -> 进入商店页面 -> 点击购买 -> 确认支付

            elif action == "library":
                result["steps"].append("打开游戏库")
                # 按快捷键打开游戏库
                pyautogui.hotkey('tab')  # 切换到库标签

            elif action == "store":
                result["steps"].append("打开商店")
                # 按快捷键打开商店
                pyautogui.hotkey('tab', 'shift')  # 切换到商店标签

            result["success"] = True
            result["message"] = f"Steam操作 '{action}' 执行成功"

        except Exception as e:
            result["message"] = f"Steam操作失败: {str(e)}"

        return result

    def execute_application_workflow(self, app_name: str, action: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """执行应用程序工作流"""
        parameters = parameters or {}
        result = {"success": False, "message": "", "steps": []}

        try:
            # 1. 启动应用
            if not self.launch_application(app_name):
                result["message"] = f"启动{app_name}失败"
                return result

            result["steps"].append(f"{app_name}启动成功")
            time.sleep(3)

            # 2. 查找并激活应用窗口
            app_window = self.find_window_by_title([app_name])
            if app_window:
                self.activate_window(app_window)
                result["steps"].append(f"{app_name}窗口激活成功")

            # 3. 根据应用类型执行具体操作
            if app_name.lower() == "steam":
                return self.execute_steam_workflow(action, parameters.get("game_name"))

            elif app_name.lower() in ["chrome", "firefox", "browser"]:
                result["steps"].append(f"浏览器操作: {action}")
                # 实现浏览器相关操作

            elif app_name.lower() == "notepad":
                result["steps"].append(f"记事本操作: {action}")
                if action == "type":
                    text = parameters.get("text", "")
                    self.type_text(text)
                    result["steps"].append(f"输入文本: {text[:50]}...")

            result["success"] = True
            result["message"] = f"{app_name}操作 '{action}' 执行成功"

        except Exception as e:
            result["message"] = f"应用操作失败: {str(e)}"

        return result

    def get_screen_info(self) -> Dict[str, Any]:
        """获取屏幕信息"""
        windows = self.get_all_windows()
        active_window = win32gui.GetForegroundWindow()
        active_title = win32gui.GetWindowText(active_window)

        return {
            "screen_resolution": (self.screen_width, self.screen_height),
            "active_window": active_title,
            "all_windows": [
                {
                    "title": w.title,
                    "process": w.process_name,
                    "visible": w.visible,
                    "rect": w.rect
                } for w in windows[:20]  # 返回前20个窗口
            ],
            "timestamp": datetime.now().isoformat()
        }

# 全局控制器实例
computer_controller = AdvancedComputerController()