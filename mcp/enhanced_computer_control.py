#!/usr/bin/env python3
"""
增强版高级电脑控制工具集
新增智能自动化、OCR识别、语音控制等功能
"""

import os
import time
import subprocess
import psutil
import pyautogui
import win32gui
import win32con
import win32api
import win32clipboard
import win32process
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass
import json
from datetime import datetime, timedelta
import threading
import queue
import speech_recognition as sr
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import cv2
import numpy as np
from pathlib import Path

# 导入基础控制器
from mcp.advanced_computer_control import (
    AdvancedComputerController,
    WindowInfo,
    ScreenElement,
    computer_controller as base_controller
)

# 设置pyautogui安全措施
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3

@dataclass
class AutomationStep:
    """自动化步骤"""
    action: str
    parameters: Dict[str, Any]
    description: str
    wait_before: float = 0.0
    wait_after: float = 0.0
    condition: Optional[str] = None

@dataclass
class VoiceCommand:
    """语音命令"""
    keyword: str
    action: Callable
    description: str
    confidence_threshold: float = 0.7

class EnhancedComputerController(AdvancedComputerController):
    """增强版电脑控制器 - 支持智能自动化和语音控制"""

    def __init__(self):
        super().__init__()
        self.automation_queue = queue.Queue()
        self.is_running = False
        self.voice_enabled = False
        self.voice_recognizer = sr.Recognizer()
        self.microphone = None
        self.ocr_enabled = True
        self.screenshot_history = []
        self.max_screenshots = 50

        # 初始化语音识别
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.voice_recognizer.adjust_for_ambient_noise(source)
            self.voice_enabled = True
            print("语音识别初始化成功")
        except Exception as e:
            print(f"语音识别初始化失败: {e}")
            self.voice_enabled = False

    def smart_find_element(self, element_type: str, search_params: Dict[str, Any] = None) -> Optional[ScreenElement]:
        """智能查找屏幕元素，结合OCR和图像识别"""
        search_params = search_params or {}

        try:
            # 截取屏幕
            screenshot = pyautogui.screenshot()
            screenshot_path = f"temp_search_{int(time.time())}.png"
            screenshot.save(screenshot_path)

            # 转换为OpenCV格式
            cv_image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

            # 使用OCR查找文本元素
            if element_type in ["text", "input", "button", "link"]:
                elements = self._find_text_elements(cv_image, screenshot_path, search_params)
                if elements:
                    return elements[0]  # 返回置信度最高的元素

            # 使用模板匹配查找图像元素
            if element_type in ["button", "icon", "image"]:
                elements = self._find_image_elements(cv_image, screenshot_path, search_params)
                if elements:
                    return elements[0]

            return None

        except Exception as e:
            print(f"智能查找元素失败: {e}")
            return None

    def _find_text_elements(self, cv_image: np.ndarray, screenshot_path: str, params: Dict[str, Any]) -> List[ScreenElement]:
        """使用OCR查找文本元素"""
        elements = []

        try:
            # 使用pytesseract进行OCR
            data = pytesseract.image_to_data(cv_image, output_type=pytesseract.Output.DICT, lang='chi_sim+eng')

            search_text = params.get("text", "").lower()

            for i in range(len(data['text'])):
                confidence = int(data['conf'][i])
                text = data['text'][i].strip()

                if confidence > 60 and text:  # 置信度阈值
                    if search_text and search_text not in text.lower():
                        continue

                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]

                    element_type = self._classify_text_element(text, params)

                    element = ScreenElement(
                        element_type=element_type,
                        text=text,
                        position=(x + w//2, y + h//2),  # 中心点
                        size=(w, h),
                        confidence=confidence / 100.0,
                        screenshot_path=screenshot_path
                    )
                    elements.append(element)

            # 按置信度排序
            elements.sort(key=lambda x: x.confidence, reverse=True)

        except Exception as e:
            print(f"OCR文本识别失败: {e}")

        return elements

    def _find_image_elements(self, cv_image: np.ndarray, screenshot_path: str, params: Dict[str, Any]) -> List[ScreenElement]:
        """使用模板匹配查找图像元素"""
        elements = []

        try:
            template_path = params.get("template_path")
            if not template_path or not os.path.exists(template_path):
                return elements

            # 读取模板图像
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                return elements

            # 执行模板匹配
            result = cv2.matchTemplate(cv_image, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            # 设置阈值
            threshold = 0.8
            if max_val >= threshold:
                h, w = template.shape[:2]
                center_x = max_loc[0] + w // 2
                center_y = max_loc[1] + h // 2

                element = ScreenElement(
                    element_type="image",
                    text=os.path.basename(template_path),
                    position=(center_x, center_y),
                    size=(w, h),
                    confidence=max_val,
                    screenshot_path=screenshot_path
                )
                elements.append(element)

        except Exception as e:
            print(f"图像模板匹配失败: {e}")

        return elements

    def _classify_text_element(self, text: str, params: Dict[str, Any]) -> str:
        """分类文本元素类型"""
        text_lower = text.lower()

        # 按钮关键词
        button_keywords = ["确定", "取消", "确认", "提交", "保存", "删除", "编辑", "修改", "添加", "创建",
                          "ok", "cancel", "submit", "save", "delete", "edit", "add", "create",
                          "点击", "Click", "按钮", "button"]

        # 输入框关键词
        input_keywords = ["输入", "请输入", "用户名", "密码", "邮箱", "搜索", "search", "username", "password", "email"]

        # 链接关键词
        link_keywords = ["链接", "link", "查看", "详情", "more", "详情", "查看更多"]

        if any(keyword in text_lower for keyword in button_keywords):
            return "button"
        elif any(keyword in text_lower for keyword in input_keywords):
            return "input"
        elif any(keyword in text_lower for keyword in link_keywords):
            return "link"
        else:
            return "text"

    def execute_automation_workflow(self, workflow_name: str, steps: List[AutomationStep]) -> Dict[str, Any]:
        """执行自动化工作流"""
        result = {
            "success": False,
            "message": "",
            "workflow_name": workflow_name,
            "executed_steps": [],
            "failed_step": None,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration": 0
        }

        try:
            print(f"开始执行自动化工作流: {workflow_name}")
            self.is_running = True

            for i, step in enumerate(steps):
                if not self.is_running:
                    result["message"] = "工作流被中断"
                    break

                step_start = time.time()

                try:
                    # 步骤前等待
                    if step.wait_before > 0:
                        time.sleep(step.wait_before)

                    # 检查条件
                    if step.condition and not self._evaluate_condition(step.condition):
                        print(f"步骤 {i+1} 条件不满足，跳过")
                        result["executed_steps"].append({
                            "step": i+1,
                            "description": step.description,
                            "action": step.action,
                            "status": "skipped",
                            "reason": "条件不满足"
                        })
                        continue

                    # 执行动作
                    step_result = self._execute_step(step)

                    step_duration = time.time() - step_start

                    if step_result["success"]:
                        result["executed_steps"].append({
                            "step": i+1,
                            "description": step.description,
                            "action": step.action,
                            "status": "success",
                            "duration": step_duration,
                            "result": step_result.get("result", "")
                        })
                        print(f"步骤 {i+1} 执行成功: {step.description}")
                    else:
                        result["executed_steps"].append({
                            "step": i+1,
                            "description": step.description,
                            "action": step.action,
                            "status": "failed",
                            "duration": step_duration,
                            "error": step_result.get("error", "")
                        })
                        result["failed_step"] = i+1
                        result["message"] = f"步骤 {i+1} 执行失败: {step.description}"
                        break

                    # 步骤后等待
                    if step.wait_after > 0:
                        time.sleep(step.wait_after)

                except Exception as e:
                    result["executed_steps"].append({
                        "step": i+1,
                        "description": step.description,
                        "action": step.action,
                        "status": "error",
                        "error": str(e)
                    })
                    result["failed_step"] = i+1
                    result["message"] = f"步骤 {i+1} 发生异常: {str(e)}"
                    break

            if result["failed_step"] is None:
                result["success"] = True
                result["message"] = f"工作流 '{workflow_name}' 执行成功"

        except Exception as e:
            result["message"] = f"工作流执行异常: {str(e)}"

        finally:
            result["end_time"] = datetime.now().isoformat()
            start_dt = datetime.fromisoformat(result["start_time"])
            end_dt = datetime.fromisoformat(result["end_time"])
            result["duration"] = (end_dt - start_dt).total_seconds()
            self.is_running = False

        return result

    def _execute_step(self, step: AutomationStep) -> Dict[str, Any]:
        """执行单个自动化步骤"""
        try:
            if step.action == "click":
                x, y = step.parameters.get("position", (0, 0))
                pyautogui.click(x, y)
                return {"success": True, "result": f"点击坐标 ({x}, {y})"}

            elif step.action == "double_click":
                x, y = step.parameters.get("position", (0, 0))
                pyautogui.doubleClick(x, y)
                return {"success": True, "result": f"双击坐标 ({x}, {y})"}

            elif step.action == "right_click":
                x, y = step.parameters.get("position", (0, 0))
                pyautogui.rightClick(x, y)
                return {"success": True, "result": f"右键点击坐标 ({x}, {y})"}

            elif step.action == "type":
                text = step.parameters.get("text", "")
                pyautogui.typewrite(text, interval=0.1)
                return {"success": True, "result": f"输入文本: {text[:50]}..."}

            elif step.action == "hotkey":
                keys = step.parameters.get("keys", [])
                pyautogui.hotkey(*keys)
                return {"success": True, "result": f"按下快捷键: {'+'.join(keys)}"}

            elif step.action == "scroll":
                clicks = step.parameters.get("clicks", 0)
                direction = step.parameters.get("direction", "down")
                if direction == "up":
                    clicks = -clicks
                pyautogui.scroll(clicks)
                return {"success": True, "result": f"滚动 {direction} {abs(clicks)} 次"}

            elif step.action == "find_and_click":
                element_type = step.parameters.get("element_type", "button")
                search_params = step.parameters.get("search_params", {})
                element = self.smart_find_element(element_type, search_params)
                if element:
                    pyautogui.click(element.position)
                    return {"success": True, "result": f"找到并点击 {element_type}: {element.text}"}
                else:
                    return {"success": False, "error": f"未找到元素: {element_type}"}

            elif step.action == "launch_app":
                app_name = step.parameters.get("app_name", "")
                success = self.launch_application(app_name)
                return {"success": success, "result": f"启动应用: {app_name}"}

            elif step.action == "wait":
                duration = step.parameters.get("duration", 1.0)
                time.sleep(duration)
                return {"success": True, "result": f"等待 {duration} 秒"}

            else:
                return {"success": False, "error": f"未知动作: {step.action}"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _evaluate_condition(self, condition: str) -> bool:
        """评估条件表达式"""
        try:
            # 简单的条件评估，实际项目中应该使用更安全的表达式解析器
            context = {
                "screen_width": self.screen_width,
                "screen_height": self.screen_height,
                "time": time.time(),
                "datetime": datetime
            }

            # 安全的条件评估
            if condition == "daytime":
                return 6 <= datetime.now().hour <= 18
            elif condition == "nighttime":
                return datetime.now().hour < 6 or datetime.now().hour > 18
            else:
                return True  # 默认返回True

        except Exception as e:
            print(f"条件评估失败: {e}")
            return True

    def start_voice_control(self, commands: List[VoiceCommand] = None) -> Dict[str, Any]:
        """启动语音控制"""
        if not self.voice_enabled:
            return {"success": False, "error": "语音识别未启用"}

        commands = commands or self._get_default_voice_commands()

        def voice_listener():
            print("语音控制已启动，请说出命令...")
            try:
                with self.microphone as source:
                    while self.voice_enabled:
                        audio = self.voice_recognizer.listen(source, timeout=1, phrase_time_limit=5)

                        try:
                            # 识别语音
                            text = self.voice_recognizer.recognize_google(audio, language='zh-CN')
                            text_lower = text.lower()
                            print(f"识别到语音: {text}")

                            # 匹配命令
                            for command in commands:
                                if command.keyword in text_lower:
                                    print(f"执行命令: {command.description}")
                                    command.action(text)
                                    break

                        except sr.UnknownValueError:
                            pass  # 无法识别语音
                        except sr.RequestError as e:
                            print(f"语音识别服务错误: {e}")
                            break

            except Exception as e:
                print(f"语音监听异常: {e}")

        # 启动语音监听线程
        voice_thread = threading.Thread(target=voice_listener, daemon=True)
        voice_thread.start()

        return {
            "success": True,
            "message": "语音控制已启动",
            "available_commands": [cmd.description for cmd in commands]
        }

    def stop_voice_control(self):
        """停止语音控制"""
        self.voice_enabled = False
        print("语音控制已停止")

    def _get_default_voice_commands(self) -> List[VoiceCommand]:
        """获取默认语音命令"""
        return [
            VoiceCommand("打开记事本", lambda text: self.launch_application("notepad"), "打开记事本"),
            VoiceCommand("截图", lambda text: self.take_smart_screenshot(), "智能截图"),
            VoiceCommand("点击确定", lambda text: self._voice_click_button("确定"), "点击确定按钮"),
            VoiceCommand("点击取消", lambda text: self._voice_click_button("取消"), "点击取消按钮"),
            VoiceCommand("关闭窗口", lambda text: pyautogui.hotkey('alt', 'f4'), "关闭当前窗口"),
            VoiceCommand("最小化", lambda text: pyautogui.hotkey('win', 'down'), "最小化当前窗口"),
        ]

    def _voice_click_button(self, button_text: str):
        """语音命令：点击按钮"""
        element = self.smart_find_element("button", {"text": button_text})
        if element:
            pyautogui.click(element.position)
            print(f"已点击按钮: {button_text}")
        else:
            print(f"未找到按钮: {button_text}")

    def take_smart_screenshot(self, save_path: str = None) -> Dict[str, Any]:
        """智能截图并保存"""
        try:
            timestamp = int(time.time())
            if not save_path:
                save_path = f"screenshots/smart_screenshot_{timestamp}.png"

            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            # 截图
            screenshot = pyautogui.screenshot()
            screenshot.save(save_path)

            # 记录到历史
            self.screenshot_history.append({
                "path": save_path,
                "timestamp": timestamp,
                "size": screenshot.size
            })

            # 保持历史记录数量
            if len(self.screenshot_history) > self.max_screenshots:
                old_screenshot = self.screenshot_history.pop(0)
                try:
                    os.remove(old_screenshot["path"])
                except:
                    pass

            # 添加标注（可选）
            annotated_path = save_path.replace('.png', '_annotated.png')
            self._annotate_screenshot(screenshot, annotated_path)

            return {
                "success": True,
                "screenshot_path": save_path,
                "annotated_path": annotated_path,
                "size": screenshot.size,
                "timestamp": timestamp
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _annotate_screenshot(self, screenshot: Image.Image, save_path: str):
        """为截图添加标注"""
        try:
            draw = ImageDraw.Draw(screenshot)

            # 获取当前活动窗口信息
            active_window = win32gui.GetForegroundWindow()
            window_rect = win32gui.GetWindowRect(active_window)

            # 绘制窗口边框
            draw.rectangle(window_rect, outline="red", width=3)

            # 添加时间戳
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except:
                font = ImageFont.load_default()

            draw.text((10, 10), timestamp, fill="white", font=font)

            # 保存标注后的图片
            screenshot.save(save_path)

        except Exception as e:
            print(f"截图标注失败: {e}")

    def create_steam_purchase_workflow(self, game_name: str) -> List[AutomationStep]:
        """创建Steam游戏购买工作流"""
        return [
            AutomationStep(
                action="launch_app",
                parameters={"app_name": "steam"},
                description="启动Steam客户端",
                wait_before=1.0,
                wait_after=5.0
            ),
            AutomationStep(
                action="find_and_click",
                parameters={
                    "element_type": "input",
                    "search_params": {"text": "搜索"}
                },
                description="点击搜索框",
                wait_after=1.0
            ),
            AutomationStep(
                action="type",
                parameters={"text": game_name},
                description=f"输入游戏名称: {game_name}",
                wait_after=2.0
            ),
            AutomationStep(
                action="hotkey",
                parameters={"keys": ["enter"]},
                description="按回车搜索",
                wait_after=3.0
            ),
            AutomationStep(
                action="find_and_click",
                parameters={
                    "element_type": "button",
                    "search_params": {"text": "购买"}
                },
                description="点击购买按钮",
                wait_after=2.0
            ),
            AutomationStep(
                action="find_and_click",
                parameters={
                    "element_type": "button",
                    "search_params": {"text": "确认购买"}
                },
                description="确认购买",
                wait_after=2.0
            )
        ]

    def get_system_health_info(self) -> Dict[str, Any]:
        """获取系统健康信息"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)

            # 内存使用情况
            memory = psutil.virtual_memory()

            # 磁盘使用情况
            disk = psutil.disk_usage('/')

            # 网络连接数
            connections = len(psutil.net_connections())

            # 运行进程数
            processes = len(psutil.pids())

            # 系统启动时间
            boot_time = psutil.boot_time()

            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "count": psutil.cpu_count(),
                    "status": "正常" if cpu_percent < 80 else "高负载"
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent,
                    "status": "正常" if memory.percent < 80 else "内存紧张"
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round(disk.percent, 2),
                    "status": "正常" if disk.percent < 90 else "空间不足"
                },
                "network": {
                    "connections": connections,
                    "status": "正常" if connections < 1000 else "连接过多"
                },
                "processes": {
                    "count": processes,
                    "status": "正常" if processes < 200 else "进程过多"
                },
                "uptime_hours": round((time.time() - boot_time) / 3600, 2),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

# 创建增强版控制器实例
enhanced_controller = EnhancedComputerController()