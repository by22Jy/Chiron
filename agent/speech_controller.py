"""
语音控制器 - 处理语音识别和命令解析
"""

import asyncio
import threading
import queue
import time
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
import json
import requests

try:
    import speech_recognition as sr
except ImportError:
    print("正在安装语音识别库...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "SpeechRecognition"])
    import speech_recognition as sr

try:
    import pyautogui
except ImportError:
    print("正在安装pyautogui库...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    import pyautogui

from logger_config import setup_component_logger

logger = setup_component_logger("speech")


@dataclass
class VoiceCommand:
    """语音命令数据结构"""
    command_type: str  # "swipe", "open", "action", "gesture_analysis"
    parameters: Dict[str, Any]
    confidence: float
    raw_text: str


class VoiceController:
    """语音控制器主类"""

    def __init__(self, backend_url: str = "http://127.0.0.1:8080"):
        self.backend_url = backend_url
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        self.is_running = False

        # 命令队列和回调
        self.command_queue = queue.Queue()
        self.on_command_detected: Optional[Callable[[VoiceCommand], None]] = None
        self.on_speech_text: Optional[Callable[[str], None]] = None

        # 线程管理
        self.listening_thread = None
        self.processing_thread = None

        # 语音识别设置
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3

        logger.info("语音控制器初始化完成")

    def initialize(self) -> bool:
        """初始化语音识别器"""
        try:
            # 获取可用麦克风列表
            mic_list = sr.Microphone.list_microphone_names()
            logger.info(f"可用麦克风: {len(mic_list)} 个")

            # 使用默认麦克风
            self.microphone = sr.Microphone()

            # 在安静环境中校准
            with self.microphone as source:
                logger.info("正在校准麦克风...")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)

            logger.info("语音识别器初始化成功")
            return True

        except Exception as e:
            logger.error(f"语音识别器初始化失败: {e}")
            return False

    def start_listening(self):
        """开始语音监听"""
        if self.is_running:
            logger.warning("语音识别已在运行")
            return

        if not self.initialize():
            logger.error("无法初始化语音识别器")
            return

        self.is_running = True
        self.is_listening = True

        # 启动监听线程
        self.listening_thread = threading.Thread(target=self._listening_loop, name="VoiceListeningThread")
        self.listening_thread.daemon = True
        self.listening_thread.start()

        # 启动处理线程
        self.processing_thread = threading.Thread(target=self._processing_loop, name="VoiceProcessingThread")
        self.processing_thread.daemon = True
        self.processing_thread.start()

        logger.info("🎤 语音监听已启动")

    def stop_listening(self):
        """停止语音监听"""
        self.is_running = False
        self.is_listening = False

        if self.listening_thread and self.listening_thread.is_alive():
            self.listening_thread.join(timeout=2)
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2)

        logger.info("🔇 语音监听已停止")

    def _listening_loop(self):
        """语音监听循环"""
        while self.is_running:
            try:
                if not self.is_listening:
                    time.sleep(0.1)
                    continue

                with self.microphone as source:
                    logger.debug("监听中...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)

                # 异步识别语音
                threading.Thread(
                    target=self._recognize_speech,
                    args=(audio,),
                    daemon=True
                ).start()

            except sr.WaitTimeoutError:
                # 超时是正常的，继续监听
                continue
            except Exception as e:
                logger.error(f"监听错误: {e}")
                time.sleep(1)

    def _recognize_speech(self, audio):
        """识别语音文本"""
        try:
            # 使用Google语音识别（可以替换为其他引擎）
            text = self.recognizer.recognize_google(audio, language='zh-CN')
            logger.info(f"🎤 识别到语音: {text}")

            # 触发语音文本回调
            if self.on_speech_text:
                self.on_speech_text(text)

            # 解析命令
            command = self._parse_command(text)
            if command:
                self.command_queue.put(command)

        except sr.UnknownValueError:
            logger.debug("无法识别语音")
        except sr.RequestError as e:
            logger.error(f"语音识别服务错误: {e}")
        except Exception as e:
            logger.error(f"语音识别异常: {e}")

    def _processing_loop(self):
        """命令处理循环"""
        while self.is_running:
            try:
                if not self.command_queue.empty():
                    command = self.command_queue.get(timeout=0.1)
                    self._execute_command(command)

                    # 触发命令检测回调
                    if self.on_command_detected:
                        self.on_command_detected(command)
                else:
                    time.sleep(0.1)

            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"命令处理错误: {e}")

    def _parse_command(self, text: str) -> Optional[VoiceCommand]:
        """解析语音命令"""
        text_lower = text.lower().strip()

        # 滑动命令
        if any(keyword in text_lower for keyword in ["左滑", "向左滑", "往左滑"]):
            return VoiceCommand(
                command_type="swipe",
                parameters={"direction": "left", "distance": 200},
                confidence=0.9,
                raw_text=text
            )

        if any(keyword in text_lower for keyword in ["右滑", "向右滑", "往右滑"]):
            return VoiceCommand(
                command_type="swipe",
                parameters={"direction": "right", "distance": 200},
                confidence=0.9,
                raw_text=text
            )

        if any(keyword in text_lower for keyword in ["上滑", "向上滑", "往上滑"]):
            return VoiceCommand(
                command_type="swipe",
                parameters={"direction": "up", "distance": 200},
                confidence=0.9,
                raw_text=text
            )

        if any(keyword in text_lower for keyword in ["下滑", "向下滑", "往下滑"]):
            return VoiceCommand(
                command_type="swipe",
                parameters={"direction": "down", "distance": 200},
                confidence=0.9,
                raw_text=text
            )

        # 打开软件命令
        if "打开" in text_lower or "启动" in text_lower:
            # 尝试提取软件名称
            app_names = {
                "浏览器": "chrome.exe",
                "Chrome": "chrome.exe",
                "谷歌": "chrome.exe",
                "记事本": "notepad.exe",
                "计算器": "calc.exe",
                "画图": "mspaint.exe",
                "资源管理器": "explorer.exe",
                "文件管理器": "explorer.exe",
                "命令提示符": "cmd.exe",
                "终端": "cmd.exe",
                "任务管理器": "taskmgr.exe"
            }

            for app_name, exe_name in app_names.items():
                if app_name in text_lower:
                    return VoiceCommand(
                        command_type="open",
                        parameters={"app_name": app_name, "executable": exe_name},
                        confidence=0.85,
                        raw_text=text
                    )

            # 通用打开命令（未识别具体软件）
            return VoiceCommand(
                command_type="open",
                parameters={"app_name": "未知", "executable": None},
                confidence=0.6,
                raw_text=text
            )

        # 系统命令
        if any(keyword in text_lower for keyword in ["音量加", "调高音量", "增加音量"]):
            return VoiceCommand(
                command_type="system",
                parameters={"action": "volume_up"},
                confidence=0.9,
                raw_text=text
            )

        if any(keyword in text_lower for keyword in ["音量减", "调低音量", "减小音量"]):
            return VoiceCommand(
                command_type="system",
                parameters={"action": "volume_down"},
                confidence=0.9,
                raw_text=text
            )

        if any(keyword in text_lower for keyword in ["锁屏", "锁定屏幕", "锁电脑"]):
            return VoiceCommand(
                command_type="system",
                parameters={"action": "lock_screen"},
                confidence=0.9,
                raw_text=text
            )

        # 手势分析请求
        if any(keyword in text_lower for keyword in ["分析", "评价", "怎么看", "什么意思"]):
            return VoiceCommand(
                command_type="gesture_analysis",
                parameters={"query": text},
                confidence=0.8,
                raw_text=text
            )

        logger.debug(f"未识别的命令: {text}")
        return None

    def _execute_command(self, command: VoiceCommand):
        """执行语音命令"""
        try:
            if command.command_type == "swipe":
                self._execute_swipe(command.parameters)
            elif command.command_type == "open":
                self._execute_open(command.parameters)
            elif command.command_type == "system":
                self._execute_system_command(command.parameters)
            elif command.command_type == "gesture_analysis":
                self._execute_gesture_analysis(command.parameters)

        except Exception as e:
            logger.error(f"命令执行失败: {e}")

    def _execute_swipe(self, params: Dict[str, Any]):
        """执行滑动命令"""
        direction = params.get("direction", "right")
        distance = params.get("distance", 200)

        try:
            screen_width, screen_height = pyautogui.size()
            center_x, center_y = screen_width // 2, screen_height // 2

            if direction == "left":
                start_x, end_x = center_x + distance//2, center_x - distance//2
                pyautogui.drag(end_x - start_x, 0, duration=0.5)
            elif direction == "right":
                start_x, end_x = center_x - distance//2, center_x + distance//2
                pyautogui.drag(end_x - start_x, 0, duration=0.5)
            elif direction == "up":
                start_y, end_y = center_y + distance//2, center_y - distance//2
                pyautogui.drag(0, end_y - start_y, duration=0.5)
            elif direction == "down":
                start_y, end_y = center_y - distance//2, center_y + distance//2
                pyautogui.drag(0, end_y - start_y, duration=0.5)

            logger.info(f"👆 执行滑动: {direction} ({distance}px)")

        except Exception as e:
            logger.error(f"滑动执行失败: {e}")

    def _execute_open(self, params: Dict[str, Any]):
        """执行打开应用命令"""
        executable = params.get("executable")
        app_name = params.get("app_name", "未知")

        if not executable:
            logger.warning(f"无法识别应用: {app_name}")
            return

        try:
            import subprocess
            subprocess.Popen([executable])
            logger.info(f"🚀 打开应用: {app_name} ({executable})")

        except Exception as e:
            logger.error(f"打开应用失败: {e}")

    def _execute_system_command(self, params: Dict[str, Any]):
        """执行系统命令"""
        action = params.get("action")

        try:
            if action == "volume_up":
                pyautogui.press("volumeup", presses=3)
                logger.info("🔊 音量增加")
            elif action == "volume_down":
                pyautogui.press("volumedown", presses=3)
                logger.info("🔉 音量减少")
            elif action == "lock_screen":
                import subprocess
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
                logger.info("🔒 锁定屏幕")

        except Exception as e:
            logger.error(f"系统命令执行失败: {e}")

    def _execute_gesture_analysis(self, params: Dict[str, Any]):
        """执行手势分析（通过LLM）"""
        query = params.get("query", "")

        try:
            # 调用后端LLM接口进行分析
            response = requests.post(
                f"{self.backend_url}/api/llm/gesture-analysis",
                json={"query": query, "context": "用户询问关于手势的问题"},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"🤖 手势分析结果: {result.get('response', '无响应')}")
            else:
                logger.warning(f"手势分析请求失败: {response.status_code}")

        except Exception as e:
            logger.error(f"手势分析失败: {e}")

    def pause_listening(self):
        """暂停监听"""
        self.is_listening = False
        logger.info("语音监听已暂停")

    def resume_listening(self):
        """恢复监听"""
        self.is_listening = True
        logger.info("语音监听已恢复")

    def get_status(self) -> Dict[str, Any]:
        """获取状态信息"""
        return {
            "is_running": self.is_running,
            "is_listening": self.is_listening,
            "queue_size": self.command_queue.qsize(),
            "microphone_available": self.microphone is not None
        }


# 全局语音控制器实例
_voice_controller: Optional[VoiceController] = None


def get_voice_controller(backend_url: str = "http://127.0.0.1:8080") -> VoiceController:
    """获取全局语音控制器实例"""
    global _voice_controller
    if _voice_controller is None:
        _voice_controller = VoiceController(backend_url)
    return _voice_controller


def start_voice_control(backend_url: str = "http://127.0.0.1:8080") -> VoiceController:
    """启动语音控制"""
    controller = get_voice_controller(backend_url)
    controller.start_listening()
    return controller


def stop_voice_control():
    """停止语音控制"""
    global _voice_controller
    if _voice_controller:
        _voice_controller.stop_listening()