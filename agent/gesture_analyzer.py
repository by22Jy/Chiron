import logging
"""
手势意图分析器 - 使用LLM分析手势的意图、情感和含义
"""

import time
import requests
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from gestures.mediapipe_detector import GestureResult
# Removed duplicate logging import

# Use standard logging
logger = logging.getLogger(__name__)


@dataclass
class GestureAnalysis:
    """手势分析结果"""
    gesture_code: str
    intent: str  # 意图描述
    emotion: str  # 情感分析
    context: str  # 上下文含义
    suggestions: List[str]  # 建议和反馈
    confidence: float  # 分析置信度
    response_text: str  # LLM生成的回应
    timestamp: float


class GestureAnalyzer:
    """手势意图分析器"""

    def __init__(self, backend_url: str = "http://127.0.0.1:8080"):
        self.backend_url = backend_url
        self.analysis_cache = {}  # 缓存分析结果
        self.cache_ttl = 300  # 缓存5分钟

        # 手势情感映射
        self.gesture_emotions = {
            "thumbs_up": ["积极", "赞同", "满意", "鼓励"],
            "victory": ["胜利", "成功", "喜悦", "庆祝"],
            "ok_sign": ["同意", "认可", "正常", "满意"],
            "point_up": ["指示", "引导", "强调", "选择"],
            "palm": ["停止", "打招呼", "拒绝", "展示"],
            "fist": ["决心", "力量", "抗议", "紧张"],
            "rock_sign": ["热情", "兴奋", "支持", "活力"],
            "call_me": ["呼叫", "邀请", "沟通", "联系"]
        }

        logger.info("手势分析器初始化完成")

    def analyze_gesture(self, gesture_result: GestureResult, context: str = "") -> Optional[GestureAnalysis]:
        """分析手势意图"""
        try:
            # 调用LLM进行分析
            analysis = self._call_llm_analysis(gesture_result, context)

            if analysis:
                logger.info(f"✨ 手势分析完成: {gesture_result.gesture_code} -> {analysis.intent}")
                return analysis

        except Exception as e:
            logger.error(f"手势分析失败: {e}")
            return self._fallback_analysis(gesture_result, context)

    def _call_llm_analysis(self, gesture_result: GestureResult, context: str = "") -> Optional[GestureAnalysis]:
        """调用LLM进行手势分析"""
        try:
            # 构建分析提示词
            prompt = self._build_analysis_prompt(gesture_result, context)

            # 调用后端LLM接口
            response = requests.post(
                f"{self.backend_url}/api/llm/gesture-analysis",
                json={
                    "prompt": prompt,
                    "gesture_code": gesture_result.gesture_code,
                    "confidence": gesture_result.confidence,
                    "context": context
                },
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                return self._parse_llm_response(gesture_result, result)
            else:
                logger.error(f"LLM分析请求失败: {response.status_code}")
                return self._fallback_analysis(gesture_result, context)

        except Exception as e:
            logger.error(f"LLM分析异常: {e}")
            return self._fallback_analysis(gesture_result, context)

    def _build_analysis_prompt(self, gesture_result: GestureResult, context: str = "") -> str:
        """构建LLM分析提示词"""
        gesture_code = gesture_result.gesture_code.lower()
        confidence = gesture_result.confidence

        # 手势含义描述
        gesture_descriptions = {
            "thumbs_up": "竖起大拇指，通常表示赞同、满意或鼓励",
            "victory": "做出V字手势，通常表示胜利、成功或庆祝",
            "ok_sign": "做出OK手势，通常表示同意、认可或一切正常",
            "point_up": "指向上方，通常表示指示、强调或选择",
            "palm": "张开手掌，通常表示停止、打招呼或拒绝",
            "fist": "握紧拳头，通常表示决心、力量或抗议",
            "rock_sign": "做出摇滚手势，通常表示热情、兴奋或支持",
            "call_me": "做出打电话手势，通常表示呼叫、邀请或联系"
        }

        gesture_desc = gesture_descriptions.get(gesture_code, f"做出{gesture_code}手势")

        prompt = f"""作为一个专业的人类行为和手势分析专家，请分析以下手势：

手势类型：{gesture_desc}
识别置信度：{confidence:.2f}
上下文：{context or "无特定上下文"}

请从以下几个维度进行分析：
1. **意图分析**：这个手势可能表达什么意图或目的？
2. **情感状态**：做出这个手势的人可能处于什么情感状态？
3. **社交含义**：在社交互动中这个手势通常代表什么？
4. **使用建议**：对这个手势的使用给出适当的建议或反馈

请用简洁、友好的语气回应，长度控制在150字以内。如果置信度较低，请在分析中提及这一点。"""

        return prompt

    def _parse_llm_response(self, gesture_result: GestureResult, llm_result: Dict[str, Any]) -> GestureAnalysis:
        """解析LLM响应"""
        response_text = llm_result.get("response", "无法分析手势意图")

        # 简单的解析逻辑
        emotion = self._extract_emotion(response_text, gesture_result.gesture_code)
        intent = self._extract_intent(response_text)
        context_meaning = self._extract_context(response_text)
        suggestions = self._extract_suggestions(response_text)

        return GestureAnalysis(
            gesture_code=gesture_result.gesture_code,
            intent=intent or "表达特定意图",
            emotion=emotion or "中性情感",
            context=context_meaning or "常规社交手势",
            suggestions=suggestions or ["继续使用手势进行交流"],
            confidence=gesture_result.confidence * 0.8,
            response_text=response_text,
            timestamp=time.time()
        )

    def _fallback_analysis(self, gesture_result: GestureResult, context: str = "") -> GestureAnalysis:
        """LLM失败时的备用分析"""
        gesture_code = gesture_result.gesture_code.lower()

        # 使用预定义的情感和意图
        emotions = self.gesture_emotions.get(gesture_code, ["中性"])
        emotion = emotions[0] if emotions else "中性"

        intent_templates = {
            "thumbs_up": "表达赞同或鼓励",
            "victory": "庆祝成功或表达胜利",
            "ok_sign": "表示同意或认可",
            "point_up": "指示或强调某个目标",
            "palm": "表示停止或打招呼",
            "fist": "表达决心或力量",
            "rock_sign": "表达热情或支持",
            "call_me": "请求联系或沟通"
        }

        intent = intent_templates.get(gesture_code, "表达特定含义")

        return GestureAnalysis(
            gesture_code=gesture_result.gesture_code,
            intent=intent,
            emotion=emotion,
            context="常见的手势表达",
            suggestions=[f"这是一个很好的{emotion}表达"],
            confidence=gesture_result.confidence * 0.6,
            response_text=f"您做出了{gesture_code}手势，这通常{intent}，表达了{emotion}的情感。",
            timestamp=time.time()
        )

    def _extract_emotion(self, text: str, gesture_code: str) -> str:
        """从LLM响应中提取情感"""
        emotions = self.gesture_emotions.get(gesture_code.lower(), [])
        for emotion in emotions:
            if emotion in text:
                return emotion
        return "积极" if "积极" in text or "正面" in text else "中性"

    def _extract_intent(self, text: str) -> str:
        """从LLM响应中提取意图"""
        if "意图" in text or "目的" in text:
            lines = text.split('\n')
            for line in lines:
                if "意图" in line or "目的" in line:
                    return line.strip()
        return "表达特定意图"

    def _extract_context(self, text: str) -> str:
        """从LLM响应中提取上下文含义"""
        if "社交" in text or "含义" in text:
            lines = text.split('\n')
            for line in lines:
                if "社交" in line or "含义" in line:
                    return line.strip()
        return "社交交流手势"

    def _extract_suggestions(self, text: str) -> List[str]:
        """从LLM响应中提取建议"""
        suggestions = []
        lines = text.split('\n')
        for line in lines:
            if "建议" in line or "可以" in line or "应该" in line:
                suggestions.append(line.strip())
        return suggestions if suggestions else ["手势使用得当"]


# 全局手势分析器实例
_gesture_analyzer: Optional[GestureAnalyzer] = None


def get_gesture_analyzer(backend_url: str = "http://127.0.0.1:8080") -> GestureAnalyzer:
    """获取全局手势分析器实例"""
    global _gesture_analyzer
    if _gesture_analyzer is None:
        _gesture_analyzer = GestureAnalyzer(backend_url)
    return _gesture_analyzer


def analyze_gesture_intent(gesture_result: GestureResult, context: str = "") -> Optional[GestureAnalysis]:
    """便捷的手势意图分析函数"""
    analyzer = get_gesture_analyzer()
    return analyzer.analyze_gesture(gesture_result, context)
