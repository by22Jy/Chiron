"""
TTS语音引擎模块

支持多种TTS后端，提供语音反馈功能
"""

import threading
import time
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# 设置TTS引擎日志
logger = logging.getLogger(__name__)


class TTSEngineType(Enum):
    """TTS引擎类型"""
    EDGE_TTS = "edge_tts"
    PYTTSX3 = "pyttsx3"
    ELEVENLABS = "elevenlabs"
    OFFLINE = "offline"


@dataclass
class TTSConfig:
    """TTS配置"""
    engine_type: TTSEngineType = TTSEngineType.OFFLINE
    voice: str = "zh-CN-XiaoxiaoNeural"  # Edge TTS中文语音
    rate: int = 200  # 语速
    volume: float = 0.9  # 音量 0.0-1.0
    enabled: bool = True
    api_key: Optional[str] = None  # ElevenLabs等付费服务需要
    output_device: Optional[str] = None


class BaseTTSEngine(ABC):
    """TTS引擎基类"""

    def __init__(self, config: TTSConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def speak(self, text: str) -> bool:
        """语音播报文本"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查引擎是否可用"""
        pass

    @abstractmethod
    def cleanup(self):
        """清理资源"""
        pass


class OfflineTTSEngine(BaseTTSEngine):
    """离线TTS引擎（仅日志，不实际语音）"""

    def __init__(self, config: TTSConfig):
        super().__init__(config)
        self.logger.info("初始化离线TTS引擎（仅模式，无语音输出）")

    def speak(self, text: str) -> bool:
        """仅记录日志，不实际语音"""
        try:
            self.logger.info(f"[TTS] {text}")
            return True
        except Exception as e:
            self.logger.error(f"TTS日志记录失败: {e}")
            return False

    def is_available(self) -> bool:
        return True

    def cleanup(self):
        pass


class EdgeTTSEngine(BaseTTSEngine):
    """Edge TTS引擎（Microsoft Edge在线TTS）"""

    def __init__(self, config: TTSConfig):
        super().__init__(config)
        self.edge_tts = None
        self.audio_player = None
        self._initialize_edge_tts()

    def _initialize_edge_tts(self):
        """初始化Edge TTS"""
        try:
            import edge_tts
            import asyncio
            self.edge_tts = edge_tts
            self.asyncio = asyncio

            # 尝试初始化音频播放器
            try:
                import pygame
                pygame.mixer.init()
                self.audio_player = pygame
                self.logger.info("Edge TTS引擎初始化成功，使用pygame音频播放")
            except ImportError:
                self.logger.warning("pygame未安装，Edge TTS将使用系统默认播放器")

        except ImportError:
            self.logger.error("edge_tts库未安装，请运行: pip install edge-tts")
            self.edge_tts = None

    def speak(self, text: str) -> bool:
        """使用Edge TTS播报文本"""
        if not self.is_available():
            return False

        try:
            async def _speak_async():
                communicate = self.edge_tts.Communicate(text, self.config.voice)
                await communicate.save("temp_tts.mp3")

                # 播放音频
                if self.audio_player:
                    self.audio_player.mixer.music.load("temp_tts.mp3")
                    self.audio_player.mixer.music.play()

                    # 等待播放完成
                    while self.audio_player.mixer.music.get_busy():
                        time.sleep(0.1)
                else:
                    # 使用系统默认播放器
                    import os
                    import platform
                    if platform.system() == "Windows":
                        os.startfile("temp_tts.mp3")
                    else:
                        import subprocess
                        subprocess.run(["xdg-open", "temp_tts.mp3"])

                # 清理临时文件
                try:
                    os.remove("temp_tts.mp3")
                except:
                    pass

            # 运行异步任务
            self.asyncio.run(_speak_async())
            return True

        except Exception as e:
            self.logger.error(f"Edge TTS播报失败: {e}")
            return False

    def is_available(self) -> bool:
        return self.edge_tts is not None

    def cleanup(self):
        if self.audio_player:
            self.audio_player.mixer.quit()


class Pyttsx3TTSEngine(BaseTTSEngine):
    """pyttsx3离线TTS引擎"""

    def __init__(self, config: TTSConfig):
        super().__init__(config)
        self.engine = None
        self._initialize_pyttsx3()

    def _initialize_pyttsx3(self):
        """初始化pyttsx3"""
        try:
            import pyttsx3
            self.engine = pyttsx3.init()

            # 设置语音参数
            self.engine.setProperty('rate', self.config.rate)
            self.engine.setProperty('volume', self.config.volume)

            # 尝试设置中文语音
            voices = self.engine.getProperty('voices')
            for voice in voices:
                if 'chinese' in voice.name.lower() or 'zh' in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break

            self.logger.info("pyttsx3 TTS引擎初始化成功")

        except ImportError:
            self.logger.error("pyttsx3库未安装，请运行: pip install pyttsx3")
            self.engine = None
        except Exception as e:
            self.logger.error(f"pyttsx3初始化失败: {e}")
            self.engine = None

    def speak(self, text: str) -> bool:
        """使用pyttsx3播报文本"""
        if not self.is_available():
            return False

        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            self.logger.error(f"pyttsx3播报失败: {e}")
            return False

    def is_available(self) -> bool:
        return self.engine is not None

    def cleanup(self):
        if self.engine:
            self.engine.stop()


class TTSEngine:
    """TTS引擎管理器"""

    def __init__(self, config: TTSConfig = None):
        self.config = config or TTSConfig()
        self.engine: Optional[BaseTTSEngine] = None
        self.speaking_lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

        # 尝试初始化不同的TTS引擎
        self._initialize_engine()

    def _initialize_engine(self):
        """按优先级初始化TTS引擎"""
        if not self.config.enabled:
            self.logger.info("TTS已禁用")
            self.engine = OfflineTTSEngine(self.config)
            return

        # 尝试Edge TTS
        if self.config.engine_type == TTSEngineType.EDGE_TTS:
            edge_engine = EdgeTTSEngine(self.config)
            if edge_engine.is_available():
                self.engine = edge_engine
                self.logger.info("使用Edge TTS引擎")
                return

        # 尝试pyttsx3
        if self.config.engine_type == TTSEngineType.PYTTSX3:
            pyttsx_engine = Pyttsx3TTSEngine(self.config)
            if pyttsx_engine.is_available():
                self.engine = pyttsx_engine
                self.logger.info("使用pyttsx3 TTS引擎")
                return

        # 回退到离线模式
        self.logger.warning("所有TTS引擎不可用，使用离线模式")
        self.engine = OfflineTTSEngine(self.config)

    def speak(self, text: str, async_mode: bool = True) -> bool:
        """语音播报文本"""
        if not self.engine or not text.strip():
            return False

        # 清理文本
        text = text.strip()
        if not text:
            return False

        # 防止并发播报
        if not self.speaking_lock.acquire(blocking=False):
            self.logger.debug("TTS正在播报中，跳过本次请求")
            return False

        try:
            if async_mode:
                # 异步播报
                def _speak_thread():
                    try:
                        self.engine.speak(text)
                    finally:
                        self.speaking_lock.release()

                thread = threading.Thread(target=_speak_thread, daemon=True)
                thread.start()
                return True
            else:
                # 同步播报
                try:
                    result = self.engine.speak(text)
                    return result
                finally:
                    self.speaking_lock.release()

        except Exception as e:
            self.logger.error(f"TTS播报失败: {e}")
            self.speaking_lock.release()
            return False

    def speak_async(self, text: str) -> bool:
        """异步语音播报（便捷方法）"""
        return self.speak(text, async_mode=True)

    def stop(self):
        """停止当前播报"""
        try:
            if self.engine and hasattr(self.engine, 'stop'):
                self.engine.stop()
        except Exception as e:
            self.logger.error(f"停止TTS播报失败: {e}")

    def is_available(self) -> bool:
        """检查TTS是否可用"""
        return self.engine is not None and self.engine.is_available()

    def get_engine_info(self) -> Dict[str, Any]:
        """获取引擎信息"""
        if not self.engine:
            return {"available": False}

        return {
            "available": True,
            "engine_type": self.engine.__class__.__name__,
            "config": {
                "voice": self.config.voice,
                "rate": self.config.rate,
                "volume": self.config.volume,
                "enabled": self.config.enabled
            }
        }

    def cleanup(self):
        """清理资源"""
        try:
            if self.engine:
                self.engine.cleanup()
        except Exception as e:
            self.logger.error(f"TTS清理失败: {e}")


# 全局TTS实例
_tts_instance: Optional[TTSEngine] = None


def get_tts_engine(config: TTSConfig = None) -> TTSEngine:
    """获取全局TTS引擎实例"""
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSEngine(config)
    return _tts_instance


def speak(text: str, async_mode: bool = True) -> bool:
    """便捷的语音播报函数"""
    tts = get_tts_engine()
    return tts.speak(text, async_mode)


# 预定义的常用语音反馈
class VoiceFeedback:
    """预定义的语音反馈"""

    # 工作流相关
    WORKFLOW_START = "正在为您处理..."
    WORKFLOW_COMPLETE = "任务已完成"
    WORKFLOW_ERROR = "执行过程中出现错误"
    WORKFLOW_STEP = "正在执行下一步"

    # 确认相关
    CONFIRM_SEND = "确认发送吗？"
    CONFIRM_DELETE = "确认删除吗？"
    CONFIRM_CANCEL = "确认取消吗？"
    OPERATION_CANCELLED = "操作已取消"
    OPERATION_CONFIRMED = "操作已确认"

    # 状态相关
    LISTENING = "我在听..."
    THINKING = "正在思考..."
    PROCESSING = "正在处理..."
    SUCCESS = "操作成功"
    FAILED = "操作失败"

    @staticmethod
    def speak_feedback(feedback_text: str, async_mode: bool = True) -> bool:
        """播报预定义反馈"""
        return speak(feedback_text, async_mode)