#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能电脑控制器 - 让LLM理解和执行自然语言命令
"""

import os
import sys
import json
import time
import requests
import subprocess
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import psutil

from logger_config import setup_component_logger

logger = setup_component_logger("intelligent_controller")


@dataclass
class ComputerAction:
    """电脑操作动作"""
    action_type: str  # "open_app", "system_control", "file_operation", "web_search", "custom_command"
    command: str     # 具体要执行的命令
    description: str # 动作描述
    confidence: float # LLM的置信度
    safety_level: str # "safe", "warning", "dangerous"
    alternatives: list = field(default_factory=list)  # 备选方案


class IntelligentController:
    """智能电脑控制器 - 使用LLM理解自然语言并生成电脑操作"""

    def __init__(self, backend_url: str = "http://127.0.0.1:8080"):
        self.backend_url = backend_url
        self.installed_apps = self._get_installed_apps()
        self.system_info = self._get_system_info()

    def _get_installed_apps(self) -> Dict[str, str]:
        """获取已安装的应用程序列表"""
        apps = {}

        # Windows常用应用程序路径
        common_paths = [
            r"C:\Program Files",
            r"C:\Program Files (x86)",
            r"C:\Users\%USERNAME%\AppData\Local",
            r"C:\Users\%USERNAME%\AppData\Roaming"
        ]

        # 预定义常用应用映射
        predefined_apps = {
            "记事本": "notepad.exe",
            "计算器": "calc.exe",
            "画图": "mspaint.exe",
            "浏览器": "chrome.exe",
            "谷歌浏览器": "chrome.exe",
            "edge": "msedge.exe",
            "资源管理器": "explorer.exe",
            "任务管理器": "taskmgr.exe",
            "命令提示符": "cmd.exe",
            "powershell": "powershell.exe",
            "写字板": "wordpad.exe",
            "媒体播放器": "wmplayer.exe",
            "截图工具": "SnippingTool.exe",
            "控制面板": "control.exe",
            "设置": "ms-settings:",
            "注册表编辑器": "regedit.exe",
            "服务": "services.msc",
            "设备管理器": "devmgmt.msc",
            "磁盘管理": "diskmgmt.msc"
        }

        apps.update(predefined_apps)

        # 尝试从常用路径检测更多应用
        try:
            for path in common_paths:
                if os.path.exists(path):
                    for item in os.listdir(path):
                        if item.endswith('.exe') and not item.startswith('.'):
                            app_name = item.replace('.exe', '')
                            if app_name not in apps:
                                apps[app_name.lower()] = item
        except Exception as e:
            logger.warning(f"扫描应用程序时出错: {e}")

        logger.info(f"发现 {len(apps)} 个应用程序")
        return apps

    def _get_system_info(self) -> Dict[str, Any]:
        """获取系统信息"""
        try:
            return {
                "platform": sys.platform,
                "os_name": os.name,
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "disk_usage": psutil.disk_usage('/').total if os.name != 'nt' else psutil.disk_usage('C:').total
            }
        except Exception as e:
            logger.warning(f"获取系统信息失败: {e}")
            return {}

    def _build_intelligent_prompt(self, user_input: str) -> str:
        """构建智能分析提示词"""
        return f"""
你是一个专业的AI智能电脑助手，能够理解复杂的自然语言请求并进行智能行为编排。

系统信息: {json.dumps(self.system_info, ensure_ascii=False, indent=2)}

已安装的应用程序: {json.dumps(list(self.installed_apps.keys()), ensure_ascii=False, indent=2)}

用户请求: "{user_input}"

请仔细分析用户的完整意图，这可能包含多个步骤的复杂操作。理解上下文，支持邮件、天气查询、多步骤任务等。

返回JSON对象：
{{
  "action_type": "open_app" | "system_control" | "file_operation" | "web_search" | "email_operation" | "weather_query" | "multi_step_task" | "custom_command" | "unknown",
  "command": "具体要执行的命令或操作描述",
  "description": "对用户意图的详细理解",
  "confidence": 0.0-1.0之间的置信度,
  "safety_level": "safe" | "warning" | "dangerous",
  "alternatives": ["智能替代方案"],
  "explanation": "详细解释理解的用户意图和执行计划",
  "context_understanding": "对用户完整请求的理解，包括连续语句的上下文"
}}

能力说明：
- 邮件操作：理解"发邮件"、"发送给邮箱"、"邮件发送"等
- 天气查询：理解"天气"、"查询天气"、"今天天气"等
- 多步骤任务：理解"打开记事本并记录天气"、"查询天气然后发送邮件"等
- 上下文理解：结合前后语音片段理解完整意图
- 应用程序：智能匹配常用软件

请只返回JSON，确保理解用户的完整意图。
"""

    def _call_llm_for_analysis(self, prompt: str) -> Optional[str]:
        """调用LLM进行智能编排分析（支持MCP工具）"""
        try:
            # 首先尝试使用智能编排API（支持MCP工具）
            response = requests.post(
                f"{self.backend_url}/api/llm/intelligent",
                json={
                    "message": prompt,
                    "context": "智能语音控制，支持MCP工具调用"
                },
                timeout=30  # 给MCP工具调用更多时间
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    response_text = result.get('response', '')

                    # 记录MCP工具使用情况
                    if 'tools_used' in result:
                        logger.info(f"MCP工具可用: {result['tools_used']}")

                    if 'mcp_status' in result:
                        logger.info(f"MCP状态: {result['mcp_status']}")

                    if result.get('fallback_used'):
                        logger.warning("使用了回退模式，MCP工具可能不可用")

                    return response_text
                else:
                    logger.warning(f"智能编排失败: {result.get('error')}")
                    if result.get('fallback_used') and result.get('fallback_response'):
                        logger.info("使用回退响应")
                        return result['fallback_response']
            else:
                logger.warning(f"智能编排API响应错误: {response.status_code}")

        except Exception as e:
            logger.error(f"调用智能编排API失败: {e}")
            logger.info("尝试回退到普通LLM调用")

        # 回退到普通LLM调用
        try:
            response = requests.post(
                f"{self.backend_url}/api/llm/chat",
                json={
                    "message": prompt,
                    "context": "智能电脑控制分析"
                },
                timeout=15
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    return result.get('response', '')
            else:
                logger.warning(f"回退LLM服务响应错误: {response.status_code}")

        except Exception as e:
            logger.error(f"回退LLM调用也失败: {e}")

        return None

    def _parse_llm_response(self, response: str) -> Optional[ComputerAction]:
        """解析LLM响应"""
        try:
            # 尝试提取JSON
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                data = json.loads(json_str)

                return ComputerAction(
                    action_type=data.get('action_type', 'unknown'),
                    command=data.get('command', ''),
                    description=data.get('description', ''),
                    confidence=float(data.get('confidence', 0.0)),
                    safety_level=data.get('safety_level', 'warning'),
                    alternatives=data.get('alternatives', [])
                )
            else:
                logger.warning("LLM响应中未找到有效的JSON")

        except json.JSONDecodeError as e:
            logger.error(f"解析LLM响应JSON失败: {e}")
        except Exception as e:
            logger.error(f"解析LLM响应失败: {e}")

        return None

    def _execute_action(self, action: ComputerAction) -> bool:
        """执行电脑操作"""
        try:
            if action.safety_level == "dangerous":
                logger.warning(f"检测到危险操作，需要用户确认: {action.description}")
                # 这里可以添加用户确认逻辑
                return False

            if action.action_type == "open_app":
                return self._execute_open_app(action)
            elif action.action_type == "system_control":
                return self._execute_system_control(action)
            elif action.action_type == "file_operation":
                return self._execute_file_operation(action)
            elif action.action_type == "web_search":
                return self._execute_web_search(action)
            elif action.action_type == "custom_command":
                return self._execute_custom_command(action)
            else:
                logger.warning(f"未知的操作类型: {action.action_type}")
                return False

        except Exception as e:
            logger.error(f"执行操作失败: {e}")
            return False

    def _execute_open_app(self, action: ComputerAction) -> bool:
        """执行打开应用程序"""
        try:
            command = action.command

            # 如果只是程序名，尝试从已安装应用中查找
            if not command.endswith('.exe'):
                command_lower = command.lower()
                for app_name, app_exec in self.installed_apps.items():
                    if command_lower in app_name.lower() or app_name.lower() in command_lower:
                        command = app_exec
                        break

            # 执行程序
            if sys.platform == 'win32':
                subprocess.Popen(command, shell=True)
            else:
                subprocess.Popen(['xdg-open', command])

            logger.info(f"成功启动应用程序: {command}")
            return True

        except Exception as e:
            logger.error(f"启动应用程序失败: {e}")
            return False

    def _execute_system_control(self, action: ComputerAction) -> bool:
        """执行系统控制"""
        try:
            command = action.command

            if sys.platform == 'win32':
                subprocess.Popen(command, shell=True)
            else:
                subprocess.Popen(command, shell=True)

            logger.info(f"执行系统命令: {command}")
            return True

        except Exception as e:
            logger.error(f"执行系统命令失败: {e}")
            return False

    def _execute_file_operation(self, action: ComputerAction) -> bool:
        """执行文件操作"""
        try:
            # 这里可以实现文件操作逻辑
            logger.info(f"文件操作: {action.description}")
            return True
        except Exception as e:
            logger.error(f"文件操作失败: {e}")
            return False

    def _execute_web_search(self, action: ComputerAction) -> bool:
        """执行网页搜索"""
        try:
            import webbrowser
            query = action.description.replace('搜索', '').replace('Search', '').strip()
            webbrowser.open(f"https://www.google.com/search?q={query}")
            logger.info(f"执行网页搜索: {query}")
            return True
        except Exception as e:
            logger.error(f"网页搜索失败: {e}")
            return False

    def _execute_custom_command(self, action: ComputerAction) -> bool:
        """执行自定义命令"""
        try:
            subprocess.Popen(action.command, shell=True)
            logger.info(f"执行自定义命令: {action.command}")
            return True
        except Exception as e:
            logger.error(f"自定义命令执行失败: {e}")
            return False

    def process_natural_language(self, user_input: str) -> Dict[str, Any]:
        """处理自然语言输入，返回操作结果"""
        start_time = time.time()

        logger.info(f"开始智能分析用户请求: '{user_input}'")

        # 构建提示词
        prompt = self._build_intelligent_prompt(user_input)

        # 调用LLM分析
        llm_response = self._call_llm_for_analysis(prompt)

        if not llm_response:
            return {
                "success": False,
                "error": "无法连接到LLM服务",
                "processing_time": time.time() - start_time
            }

        # 解析LLM响应
        action = self._parse_llm_response(llm_response)

        if not action:
            return {
                "success": False,
                "error": "无法解析LLM响应",
                "raw_response": llm_response,
                "processing_time": time.time() - start_time
            }

        # 执行操作
        execution_success = self._execute_action(action)

        processing_time = time.time() - start_time

        result = {
            "success": execution_success,
            "action": {
                "type": action.action_type,
                "command": action.command,
                "description": action.description,
                "confidence": action.confidence,
                "safety_level": action.safety_level
            },
            "alternatives": action.alternatives,
            "processing_time": processing_time,
            "user_input": user_input
        }

        if execution_success:
            logger.info(f"[OK] 智能控制成功: {action.description} (耗时: {processing_time:.2f}s)")
        else:
            logger.warning(f"[ERROR] 智能控制失败: {action.description}")

        return result

    def get_available_apps(self) -> List[str]:
        """获取可用应用程序列表"""
        return list(self.installed_apps.keys())

    def refresh_app_list(self):
        """刷新应用程序列表"""
        self.installed_apps = self._get_installed_apps()
        logger.info("应用程序列表已刷新")


# 测试函数
def test_intelligent_controller():
    """测试智能控制器"""
    controller = IntelligentController()

    test_commands = [
        "打开微信",
        "帮我搜索Python教程",
        "调高音量",
        "打开我的文档",
        "启动Photoshop",
        "关闭屏幕",
        "查看系统信息"
    ]

    for cmd in test_commands:
        print(f"\n测试命令: {cmd}")
        result = controller.process_natural_language(cmd)
        print(f"结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        time.sleep(2)  # 避免请求过于频繁


if __name__ == "__main__":
    test_intelligent_controller()