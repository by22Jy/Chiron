import logging
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
import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
import psutil

# 导入数据标准化工具
from utils.data_standardizer import DataStandardizer
from utils.json_parser import JSONResponseParser

# Use standard logging
logger = logging.getLogger(__name__)


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

    # 动作类型映射和验证
    ACTION_TYPE_MAPPING = {
        # 抽象动作类型 -> 描述
        "open_app": {
            "description": "打开应用程序",
            "valid_commands": [".exe", ".app", "start ", "open "],
            "examples": ["打开微信", "启动记事本", "运行Chrome"]
        },
        "system_control": {
            "description": "系统控制",
            "valid_commands": ["volume", "brightness", "shutdown", "restart", "lock", "sleep"],
            "examples": ["调高音量", "降低亮度", "锁屏", "重启电脑"]
        },
        "file_operation": {
            "description": "文件操作",
            "valid_commands": ["explorer", "folder", "directory", "file"],
            "examples": ["打开我的文档", "显示下载文件夹", "创建新文件夹"]
        },
        "web_search": {
            "description": "网页搜索",
            "valid_commands": ["search", "google", "百度", "搜索"],
            "examples": ["搜索Python教程", "百度天气", "Google最新新闻"]
        },
        "custom_command": {
            "description": "自定义命令",
            "valid_commands": ["cmd", "powershell", "bash", "terminal"],
            "examples": ["打开命令提示符", "运行PowerShell", "执行ipconfig"]
        }
    }

    VALID_ACTION_TYPES = set(ACTION_TYPE_MAPPING.keys())
    VALID_SAFETY_LEVELS = {"safe", "warning", "dangerous"}

    def __init__(self, backend_url: str = "http://127.0.0.1:8080"):
        self.backend_url = backend_url
        self.data_standardizer = DataStandardizer()
        self.json_parser = JSONResponseParser()
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

    def _build_user_intent_description(self, user_input: str) -> Dict[str, Any]:
        """构建用户意图描述，用于后端组合系统提示词"""
        return {
            "user_input": user_input,
            "system_info": self.system_info,
            "installed_apps": list(self.installed_apps.keys()),
            "context": "智能语音控制，支持MCP工具调用"
        }

    def _call_llm_for_analysis(self, user_intent: Dict[str, Any]) -> Optional[str]:
        """调用LLM进行智能编排分析（支持MCP工具）"""
        try:
            # 使用标准化工具创建请求
            request_data = {
                "user_intent": user_intent,
                "context": "智能语音控制，支持MCP工具调用"
            }
            standard_request = self.data_standardizer.create_standard_request("intelligent", request_data)

            # 首先尝试使用智能编排API（支持MCP工具）
            response = requests.post(
                f"{self.backend_url}/api/llm/intelligent",
                json=standard_request,
                timeout=30  # 给MCP工具调用更多时间
            )

            if response.status_code == 200:
                response_data = response.json()
                # 使用标准化工具解析响应
                result = self.data_standardizer.parse_standard_response(response_data)

                if result.get('success'):
                    response_text = result.get('response', '')

                    # 记录MCP工具使用情况
                    data = result.get('data', {})
                    if 'tools_used' in data:
                        logger.info(f"MCP工具可用: {data['tools_used']}")

                    if 'mcp_status' in data:
                        logger.info(f"MCP状态: {data['mcp_status']}")

                    if data.get('fallback_used'):
                        logger.warning("使用了回退模式，MCP工具可能不可用")

                    return response_text
                else:
                    logger.warning(f"智能编排失败: {result.get('message')}")
                    if data.get('fallback_used') and data.get('fallback_response'):
                        logger.info("使用回退响应")
                        return data['fallback_response']
            else:
                logger.warning(f"智能编排API响应错误: {response.status_code}")

        except Exception as e:
            logger.error(f"调用智能编排API失败: {e}")
            logger.info("尝试回退到普通LLM调用")

        # 回退到普通LLM调用
        try:
            request_data = {
                "message": f"用户请求: {user_intent.get('user_input', '')}",
                "context": "智能电脑控制分析"
            }
            standard_request = self.data_standardizer.create_standard_request("chat", request_data)

            response = requests.post(
                f"{self.backend_url}/api/llm/chat",
                json=standard_request,
                timeout=15
            )

            if response.status_code == 200:
                response_data = response.json()
                result = self.data_standardizer.parse_standard_response(response_data)

                if result.get('success'):
                    return result.get('response', '')
            else:
                logger.warning(f"回退LLM服务响应错误: {response.status_code}")

        except Exception as e:
            logger.error(f"回退LLM调用也失败: {e}")

        return None

    def _parse_llm_response(self, response: str) -> Optional[ComputerAction]:
        """
        解析LLM响应 - 使用健壮的多层JSON解析器

        Args:
            response: LLM返回的原始响应

        Returns:
            解析后的ComputerAction对象，如果解析失败返回None
        """
        if not response or not response.strip():
            logger.warning("LLM响应为空")
            return None

        logger.debug(f"开始解析LLM响应: {response[:200]}...")

        try:
            # 使用新的健壮JSON解析器
            parsed_data = self.json_parser.parse_response(response)

            if parsed_data and parsed_data.get("action") != "unknown":
                logger.info(f"JSON解析成功，使用策略: {parsed_data.get('parsing_strategy', 'unknown')}")

                # 创建ComputerAction对象
                action = ComputerAction(
                    action_type=self._map_action_type(parsed_data.get("action", "unknown")),
                    command=parsed_data.get("command", ""),
                    description=parsed_data.get("description", "解析的操作"),
                    confidence=parsed_data.get("confidence", 0.0),
                    safety_level=self._determine_safety_level(parsed_data),
                    alternatives=[]
                )

                # 记录解析统计
                stats = self.json_parser.get_error_statistics()
                logger.debug(f"解析统计: {stats}")

                return action
            else:
                logger.warning("解析结果无效或action为unknown")
                return None

        except Exception as e:
            logger.error(f"JSON解析过程中发生异常: {e}")
            logger.error(f"原始响应: {response[:500]}...")
            return None

    def _map_action_type(self, action: str) -> str:
        """映射动作类型到有效的动作类型"""
        action_mapping = {
            "unknown": "unknown",
            "open_app": "open_app",
            "system_control": "system_control",
            "file_operation": "file_operation",
            "web_search": "web_search",
            "custom_command": "custom_command"
        }

        return action_mapping.get(action.lower(), "unknown")

    def _determine_safety_level(self, parsed_data: Dict[str, Any]) -> str:
        """根据解析的数据确定安全级别"""
        command = parsed_data.get("command", "").lower()
        confidence = parsed_data.get("confidence", 0.0)

        # 危险命令模式
        dangerous_keywords = ["delete", "remove", "shutdown", "restart", "format"]
        if any(keyword in command for keyword in dangerous_keywords):
            return "dangerous"

        # 警告命令模式
        warning_keywords = ["registry", "config", "system32"]
        if any(keyword in command for keyword in warning_keywords):
            return "warning"

        # 根据置信度判断
        if confidence < 0.5:
            return "warning"

        return "safe"

    def _try_parse_json(self, json_str: str) -> Optional[Dict[str, Any]]:
        """
        尝试解析JSON字符串 - 已废弃，使用新的JSONResponseParser
        保留此方法仅用于向后兼容
        """
        logger.warning("_try_parse_json方法已废弃，使用JSONResponseParser.parse_response")
        return self.json_parser.parse_response(json_str) if self.json_parser else None

    def _fix_common_json_issues(self, response: str) -> str:
        """
        修复常见的JSON格式问题 - 已废弃，使用新的JSONResponseParser
        保留此方法仅用于向后兼容
        """
        logger.warning("_fix_common_json_issues方法已废弃，使用JSONResponseParser")
        return response

    def _validate_action_type(self, action_type: str) -> bool:
        """验证动作类型是否有效"""
        if not action_type:
            logger.warning("动作类型为空")
            return False

        if action_type not in self.VALID_ACTION_TYPES:
            logger.warning(f"不支持的动作类型: {action_type}")
            logger.info(f"支持的动作类型: {', '.join(self.VALID_ACTION_TYPES)}")
            return False

        return True

    def _validate_safety_level(self, safety_level: str) -> str:
        """验证并标准化安全级别"""
        if not safety_level:
            return 'warning'

        if safety_level not in self.VALID_SAFETY_LEVELS:
            logger.warning(f"无效的安全级别: {safety_level}, 使用默认值warning")
            return 'warning'

        return safety_level

    def _get_action_type_info(self, action_type: str) -> Dict[str, Any]:
        """获取动作类型的详细信息"""
        return self.ACTION_TYPE_MAPPING.get(action_type, {
            "description": "未知操作类型",
            "valid_commands": [],
            "examples": []
        })

    def _create_computer_action(self, data: Dict[str, Any]) -> Optional[ComputerAction]:
        """从JSON数据创建ComputerAction对象 - 使用标准化验证"""
        try:
            # 验证必需字段
            action_type = data.get('action_type')
            if not self._validate_action_type(action_type):
                logger.warning(f"JSON中包含无效的action_type: {action_type}")
                return None

            # 获取动作类型信息用于验证
            action_info = self._get_action_type_info(action_type)
            logger.debug(f"动作类型信息: {action_info['description']}")

            # 解析confidence为浮点数
            confidence = 0.0
            if 'confidence' in data:
                try:
                    confidence = float(data['confidence'])
                    confidence = max(0.0, min(1.0, confidence))  # 限制在0-1范围
                except (ValueError, TypeError):
                    logger.warning(f"confidence值无效: {data['confidence']}, 使用默认值0.0")
                    confidence = 0.0

            # 验证safety_level
            safety_level = self._validate_safety_level(data.get('safety_level', 'warning'))

            # 处理alternatives
            alternatives = data.get('alternatives', [])
            if not isinstance(alternatives, list):
                logger.debug(f"alternatives不是列表类型，转换为空列表")
                alternatives = []

            # 创建ComputerAction对象
            action = ComputerAction(
                action_type=action_type,
                command=data.get('command', ''),
                description=data.get('description', ''),
                confidence=confidence,
                safety_level=safety_level,
                alternatives=alternatives
            )

            # 验证command是否为空
            if not action.command or not action.command.strip():
                logger.warning(f"动作命令为空，动作类型: {action_type}")
                logger.info(f"建议的命令示例: {', '.join(action_info['examples'])}")

            logger.info(f"成功创建ComputerAction: {action_type} - {action.description}")
            logger.debug(f"   动作详情: {action}")
            return action

        except Exception as e:
            logger.error(f"创建ComputerAction失败: {e}")
            import traceback
            logger.debug(f"   异常堆栈: {traceback.format_exc()}")
            return None

    def _execute_action(self, action: ComputerAction) -> bool:
        """执行电脑操作 - 增强错误处理和日志记录"""
        logger.info(f"开始执行操作: {action.action_type} - {action.description} (置信度: {action.confidence:.2f}, 安全级别: {action.safety_level})")

        try:
            # 安全检查
            if action.safety_level == "dangerous":
                logger.error(f"检测到危险操作，拒绝执行: {action.description}")
                logger.error(f"   命令: {action.command}")
                logger.error(f"   如需执行，请修改安全级别或手动执行")
                return False

            # 置信度检查
            if action.confidence < 0.3:
                logger.warning(f"操作置信度过低 ({action.confidence:.2f}), 建议确认后执行")
                logger.warning(f"   操作: {action.description}")

            # 执行具体操作
            success = False
            if action.action_type == "open_app":
                success = self._execute_open_app(action)
            elif action.action_type == "system_control":
                success = self._execute_system_control(action)
            elif action.action_type == "file_operation":
                success = self._execute_file_operation(action)
            elif action.action_type == "web_search":
                success = self._execute_web_search(action)
            elif action.action_type == "custom_command":
                success = self._execute_custom_command(action)
            else:
                logger.error(f"不支持的操作类型: {action.action_type}")
                return False

            if success:
                logger.info(f"操作执行成功: {action.description}")
            else:
                logger.error(f"操作执行失败: {action.description}")

            return success

        except Exception as e:
            logger.error(f"执行操作时发生异常: {e}")
            logger.error(f"   操作类型: {action.action_type}")
            logger.error(f"   操作描述: {action.description}")
            logger.error(f"   执行命令: {action.command}")
            import traceback
            logger.debug(f"   异常堆栈: {traceback.format_exc()}")
            return False

    def _execute_open_app(self, action: ComputerAction) -> bool:
        """执行打开应用程序 - 增强错误处理"""
        command = action.command
        original_command = command

        try:
            logger.debug(f"准备启动应用程序: {command}")

            # 验证命令不为空
            if not command or not command.strip():
                logger.error("应用程序命令为空")
                return False

            # 如果只是程序名，尝试从已安装应用中查找
            if not command.endswith('.exe') and not command.endswith('.app'):
                command_lower = command.lower()
                logger.debug(f"搜索应用程序: {command_lower}")

                found_match = False
                for app_name, app_exec in self.installed_apps.items():
                    if command_lower in app_name.lower() or app_name.lower() in command_lower:
                        command = app_exec
                        found_match = True
                        logger.debug(f"找到匹配: {app_name} -> {app_exec}")
                        break

                if not found_match:
                    logger.warning(f"未找到应用程序 '{command}'，尝试直接执行")

            # 执行程序
            if sys.platform == 'win32':
                # Windows平台
                try:
                    subprocess.Popen(command, shell=True)
                    logger.info(f"Windows应用程序启动成功: {command}")
                except FileNotFoundError:
                    logger.error(f"应用程序未找到: {command}")
                    # 尝试常见路径
                    common_paths = [
                        f"C:\\Program Files\\{command}",
                        f"C:\\Program Files (x86)\\{command}",
                        f"C:\\Windows\\System32\\{command}.exe"
                    ]
                    for path in common_paths:
                        if os.path.exists(path):
                            subprocess.Popen(path, shell=True)
                            logger.info(f"通过备选路径启动成功: {path}")
                            return True
                    return False
            else:
                # Linux/macOS平台
                try:
                    subprocess.Popen(['xdg-open', command])
                    logger.info(f"Linux/macOS应用程序启动成功: {command}")
                except FileNotFoundError:
                    logger.error(f"❌ xdg-open命令未找到，可能不支持此平台")
                    return False

            return True

        except subprocess.SubprocessError as e:
            logger.error(f"启动应用程序时发生子进程错误: {e}")
            logger.error(f"   原始命令: {original_command}")
            logger.error(f"   执行命令: {command}")
            return False
        except PermissionError as e:
            logger.error(f"权限不足，无法启动应用程序: {e}")
            logger.error(f"   命令: {command}")
            return False
        except Exception as e:
            logger.error(f"启动应用程序时发生未知错误: {e}")
            logger.error(f"   原始请求: {action.description}")
            logger.error(f"   原始命令: {original_command}")
            logger.error(f"   处理后命令: {command}")
            import traceback
            logger.debug(f"   异常堆栈: {traceback.format_exc()}")
            return False

    def _execute_system_control(self, action: ComputerAction) -> bool:
        """执行系统控制 - 增强错误处理"""
        command = action.command

        try:
            logger.debug(f"准备执行系统控制命令: {command}")

            # 验证命令不为空
            if not command or not command.strip():
                logger.error("系统控制命令为空")
                return False

            # 安全检查 - 避免执行危险命令
            dangerous_patterns = ['format', 'del ', 'rmdir', 'shutdown /f', 'reboot /f']
            command_lower = command.lower()
            for pattern in dangerous_patterns:
                if pattern in command_lower:
                    logger.error(f"检测到危险系统命令，拒绝执行: {command}")
                    return False

            # 执行系统命令
            if sys.platform == 'win32':
                result = subprocess.Popen(command, shell=True)
            else:
                result = subprocess.Popen(command, shell=True)

            logger.info(f"系统控制命令执行成功: {command}")
            return True

        except subprocess.SubprocessError as e:
            logger.error(f"系统命令执行失败: {e}")
            logger.error(f"   命令: {command}")
            return False
        except PermissionError as e:
            logger.error(f"❌ 权限不足，无法执行系统命令: {e}")
            logger.error(f"   命令: {command}")
            return False
        except Exception as e:
            logger.error(f"系统控制时发生未知错误: {e}")
            logger.error(f"   命令: {command}")
            return False

    def _execute_file_operation(self, action: ComputerAction) -> bool:
        """执行文件操作 - 增强错误处理"""
        try:
            logger.debug(f"准备执行文件操作: {action.description}")

            # 目前文件操作功能待完善
            logger.info(f"文件操作功能暂未完全实现: {action.description}")
            logger.warning("文件操作功能正在开发中，当前返回成功但不执行实际操作")

            return True

        except Exception as e:
            logger.error(f"文件操作时发生错误: {e}")
            logger.error(f"   操作描述: {action.description}")
            return False

    def _execute_web_search(self, action: ComputerAction) -> bool:
        """执行网页搜索 - 增强错误处理"""
        try:
            logger.debug(f"准备执行网页搜索: {action.description}")

            # 提取搜索关键词
            query = action.description.replace('搜索', '').replace('Search', '').strip()
            if not query:
                query = action.command  # 如果description中没有关键词，尝试使用command

            if not query:
                logger.error("网页搜索关键词为空")
                return False

            import webbrowser
            search_url = f"https://www.google.com/search?q={query}"

            logger.info(f"执行网页搜索: {query}")
            webbrowser.open(search_url)
            logger.info(f"网页浏览器已打开搜索页面")

            return True

        except ImportError:
            logger.error("webbrowser模块不可用")
            return False
        except Exception as e:
            logger.error(f"网页搜索时发生错误: {e}")
            logger.error(f"   搜索关键词: {query if 'query' in locals() else 'unknown'}")
            return False

    def _execute_custom_command(self, action: ComputerAction) -> bool:
        """执行自定义命令 - 增强错误处理"""
        command = action.command

        try:
            logger.debug(f"准备执行自定义命令: {command}")

            # 验证命令不为空
            if not command or not command.strip():
                logger.error("自定义命令为空")
                return False

            # 安全检查 - 对高风险命令发出警告
            high_risk_patterns = ['rm -rf', 'del /', 'format', 'shutdown', 'reboot']
            command_lower = command.lower()
            for pattern in high_risk_patterns:
                if pattern in command_lower:
                    logger.warning(f"检测到高风险命令，请确认执行: {command}")

            # 执行自定义命令
            result = subprocess.Popen(command, shell=True)

            logger.info(f"自定义命令执行成功: {command}")
            return True

        except subprocess.SubprocessError as e:
            logger.error(f"自定义命令执行失败: {e}")
            logger.error(f"   命令: {command}")
            return False
        except PermissionError as e:
            logger.error(f"❌ 权限不足，无法执行自定义命令: {e}")
            logger.error(f"   命令: {command}")
            return False
        except Exception as e:
            logger.error(f"自定义命令执行时发生未知错误: {e}")
            logger.error(f"   命令: {command}")
            import traceback
            logger.debug(f"   异常堆栈: {traceback.format_exc()}")
            return False

    def process_natural_language(self, user_input: str) -> Dict[str, Any]:
        """处理自然语言输入，返回操作结果"""
        start_time = time.time()

        logger.info(f"开始智能分析用户请求: '{user_input}'")

        # 构建用户意图描述
        user_intent = self._build_user_intent_description(user_input)

        # 调用LLM分析
        llm_response = self._call_llm_for_analysis(user_intent)

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