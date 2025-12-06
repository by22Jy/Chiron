"""
系统 MCP 工具

通过DeepSeek大模型智能处理系统操作任务
"""

import asyncio
import os
import subprocess
import time
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class SystemTool:
    """系统工具"""

    def __init__(self):
        pass

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行系统工具操作"""

        action = parameters.get("action", "")
        logger.info(f"执行系统工具操作: {action}")

        try:
            if action == "open_application":
                return await self._open_application(parameters)
            elif action == "file_operations":
                return await self._file_operations(parameters)
            elif action == "system_info":
                return await self._get_system_info(parameters)
            elif action == "notepad_operations":
                return await self._notepad_operations(parameters)
            elif action == "execute_command":
                return await self._execute_command(parameters)
            elif action == "check_status":
                return await self._check_status(parameters)
            else:
                return {
                    "success": False,
                    "error": f"未知的系统操作: {action}",
                    "available_actions": [
                        "open_application", "file_operations", "system_info",
                        "notepad_operations", "execute_command", "check_status"
                    ]
                }

        except Exception as e:
            logger.error(f"系统工具执行错误: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "action": action
            }

    async def _open_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """打开应用程序"""

        application = params.get("application", "")
        additional_params = params.get("parameters", {})

        if not application:
            return {
                "success": False,
                "error": "应用程序名称不能为空"
            }

        try:
            # 应用程序映射
            app_commands = {
                "notepad": ["notepad.exe"],
                "calculator": ["calc.exe"],
                "browser": ["cmd", "/c", "start", "chrome"],
                "explorer": ["explorer.exe"],
                "task_manager": ["taskmgr.exe"],
                "cmd": ["cmd.exe"],
                "powershell": ["powershell.exe"]
            }

            command = app_commands.get(application.lower(), [application])

            # 添加额外参数
            if additional_params:
                command.extend(additional_params)

            # 执行命令
            process = await asyncio.create_subprocess_exec(
                *command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return {
                    "success": True,
                    "message": f"应用程序 {application} 已启动",
                    "command": command,
                    "process_id": process.pid if process.pid else None
                }
            else:
                return {
                    "success": False,
                    "error": f"启动应用程序失败: {stderr.decode()}",
                    "command": command
                }

        except Exception as e:
            logger.error(f"打开应用程序失败: {str(e)}")
            return {
                "success": False,
                "error": f"打开应用程序失败: {str(e)}",
                "application": application
            }

    async def _file_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """文件操作"""

        operation = params.get("operation", "")
        file_path = params.get("file_path", "")
        content = params.get("content", "")

        if not operation or not file_path:
            return {
                "success": False,
                "error": "操作类型和文件路径不能为空"
            }

        try:
            if operation == "create":
                # 创建文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    if content:
                        f.write(content)
                return {
                    "success": True,
                    "message": f"文件 {file_path} 已创建",
                    "operation": operation,
                    "file_path": file_path,
                    "content_length": len(content) if content else 0
                }

            elif operation == "read":
                # 读取文件
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return {
                        "success": True,
                        "message": f"文件 {file_path} 读取成功",
                        "content": content,
                        "content_length": len(content),
                        "file_size": os.path.getsize(file_path)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"文件 {file_path} 不存在"
                    }

            elif operation == "delete":
                # 删除文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return {
                        "success": True,
                        "message": f"文件 {file_path} 已删除",
                        "operation": operation
                    }
                else:
                    return {
                        "success": False,
                        "error": f"文件 {file_path} 不存在"
                    }

            elif operation == "exists":
                # 检查文件是否存在
                exists = os.path.exists(file_path)
                return {
                    "success": True,
                    "exists": exists,
                    "file_path": file_path,
                    "message": f"文件 {file_path} {'存在' if exists else '不存在'}"
                }

            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {operation}",
                    "supported_operations": ["create", "read", "delete", "exists"]
                }

        except Exception as e:
            logger.error(f"文件操作失败: {str(e)}")
            return {
                "success": False,
                "error": f"文件操作失败: {str(e)}",
                "operation": operation,
                "file_path": file_path
            }

    async def _get_system_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """获取系统信息"""

        info_type = params.get("info_type", "basic")

        try:
            if info_type == "basic":
                import platform
                import psutil

                system_info = {
                    "platform": platform.system(),
                    "platform_version": platform.version(),
                    "architecture": platform.architecture()[0],
                    "processor": platform.processor(),
                    "python_version": platform.python_version(),
                    "hostname": platform.node(),
                    "cpu_count": psutil.cpu_count(),
                    "memory_total": f"{psutil.virtual_memory().total // (1024**3)} GB",
                    "disk_usage": f"{psutil.disk_usage('/').percent}%"
                }

                return {
                    "success": True,
                    "system_info": system_info,
                    "collected_at": time.strftime('%Y-%m-%d %H:%M:%S')
                }

            elif info_type == "processes":
                import psutil

                processes = []
                for proc in psutil.process_iter(['pid', 'name', 'status']):
                    try:
                        processes.append({
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "status": proc.info['status']
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                return {
                    "success": True,
                    "processes": processes[:20],  # 只返回前20个进程
                    "total_processes": len(processes)
                }

            else:
                return {
                    "success": False,
                    "error": f"不支持的信息类型: {info_type}",
                    "supported_types": ["basic", "processes"]
                }

        except Exception as e:
            logger.error(f"获取系统信息失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _notepad_operations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """记事本操作"""

        operation = params.get("operation", "")
        content = params.get("content", "")
        file_path = params.get("file_path", "")

        try:
            if operation == "open_and_write":
                # 打开记事本并写入内容
                import pyautogui
                import time

                # 打开记事本
                pyautogui.hotkey('win', 'r')
                time.sleep(1)
                pyautogui.write('notepad')
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(2)

                # 写入内容
                if content:
                    pyautogui.write(content, interval=0.01)

                # 保存文件（如果指定了路径）
                if file_path:
                    time.sleep(1)
                    pyautogui.hotkey('ctrl', 's')
                    time.sleep(1)
                    pyautogui.write(file_path)
                    time.sleep(1)
                    pyautogui.press('enter')

                return {
                    "success": True,
                    "message": "记事本已打开并写入内容",
                    "operation": operation,
                    "content_length": len(content) if content else 0,
                    "saved_to": file_path if file_path else "未保存"
                }

            elif operation == "get_active_window":
                import pyautogui
                try:
                    window = pyautogui.getActiveWindow()
                    if window:
                        return {
                            "success": True,
                            "window_title": window.title,
                            "window_size": (window.width, window.height),
                            "window_position": (window.left, window.top)
                        }
                    else:
                        return {
                            "success": False,
                            "error": "无法获取活动窗口信息"
                        }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"获取窗口信息失败: {str(e)}"
                    }

            else:
                return {
                    "success": False,
                    "error": f"不支持的记事本操作: {operation}",
                    "supported_operations": ["open_and_write", "get_active_window"]
                }

        except Exception as e:
            logger.error(f"记事本操作失败: {str(e)}")
            return {
                "success": False,
                "error": f"记事本操作失败: {str(e)}"
            }

    async def _execute_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行命令"""

        command = params.get("command", "")
        shell = params.get("shell", False)
        timeout = params.get("timeout", 30)

        if not command:
            return {
                "success": False,
                "error": "命令不能为空"
            }

        try:
            # 执行命令
            if shell:
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
            else:
                if isinstance(command, str):
                    command = command.split()
                process = await asyncio.create_subprocess_exec(
                    *command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return {
                    "success": False,
                    "error": f"命令执行超时 ({timeout}秒)",
                    "command": command,
                    "timeout": timeout
                }

            return {
                "success": process.returncode == 0,
                "command": command,
                "return_code": process.returncode,
                "stdout": stdout.decode('utf-8', errors='ignore'),
                "stderr": stderr.decode('utf-8', errors='ignore')
            }

        except Exception as e:
            logger.error(f"命令执行失败: {str(e)}")
            return {
                "success": False,
                "error": f"命令执行失败: {str(e)}",
                "command": command
            }

    async def _check_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """检查系统状态"""

        check_type = params.get("check_type", "applications")

        try:
            if check_type == "applications":
                # 检查应用程序运行状态
                import psutil

                running_apps = []
                app_names = ["notepad.exe", "chrome.exe", "firefox.exe", "explorer.exe"]

                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'].lower() in app_names:
                            running_apps.append({
                                "pid": proc.info['pid'],
                                "name": proc.info['name'],
                                "status": "running"
                            })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

                return {
                    "success": True,
                    "check_type": check_type,
                    "running_applications": running_apps,
                    "total_running": len(running_apps)
                }

            elif check_type == "system_resources":
                # 检查系统资源
                import psutil

                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')

                return {
                    "success": True,
                    "check_type": check_type,
                    "cpu_usage": f"{cpu_percent}%",
                    "memory_usage": f"{memory.percent}%",
                    "disk_usage": f"{disk.percent}%",
                    "available_memory": f"{memory.available // (1024**3)} GB",
                    "available_disk": f"{disk.free // (1024**3)} GB"
                }

            else:
                return {
                    "success": False,
                    "error": f"不支持的检查类型: {check_type}",
                    "supported_types": ["applications", "system_resources"]
                }

        except Exception as e:
            logger.error(f"状态检查失败: {str(e)}")
            return {
                "success": False,
                "error": f"状态检查失败: {str(e)}",
                "check_type": check_type
            }