#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DeepSeek LLM智能工作流集成
提供智能对话、任务规划、自动化决策等功能
"""

import os
import time
import json
import requests
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import threading
import queue
import re
from pathlib import Path

class TaskType(Enum):
    """任务类型枚举"""
    QUERY = "query"           # 查询任务
    ANALYSIS = "analysis"     # 分析任务
    GENERATION = "generation" # 生成任务
    DECISION = "decision"     # 决策任务
    PLANNING = "planning"     # 规划任务
    AUTOMATION = "automation" # 自动化任务

class TaskStatus(Enum):
    """任务状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class MessageRole(Enum):
    """消息角色枚举"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

@dataclass
class Message:
    """消息数据结构"""
    role: MessageRole
    content: str
    timestamp: datetime = None
    tool_calls: List[Dict[str, Any]] = None
    tool_results: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.tool_calls is None:
            self.tool_calls = []
        if self.tool_results is None:
            self.tool_results = []

@dataclass
class Task:
    """任务数据结构"""
    id: str
    task_type: TaskType
    description: str
    context: Dict[str, Any] = None
    messages: List[Message] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0  # 0-10，10最高
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    estimated_duration: float = 0.0
    actual_duration: float = 0.0
    dependencies: List[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.context is None:
            self.context = {}
        if self.messages is None:
            self.messages = []
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class WorkflowDefinition:
    """工作流定义数据结构"""
    id: str
    name: str
    description: str
    steps: List[Dict[str, Any]]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    estimated_duration: float
    required_tools: List[str]
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class DeepSeekLLMIntegration:
    """DeepSeek LLM集成系统"""

    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.api_key = self.config.get("api_key", os.getenv("DEEPSEEK_API_KEY", ""))
        self.base_url = self.config.get("base_url", "https://api.deepseek.com")
        self.model_name = self.config.get("model_name", "deepseek-chat")
        self.max_tokens = self.config.get("max_tokens", 4000)
        self.temperature = self.config.get("temperature", 0.7)

        # 任务管理
        self.tasks: Dict[str, Task] = {}
        self.task_queue = queue.PriorityQueue()
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.running_tasks: Dict[str, Task] = {}

        # 性能监控
        self.task_history: List[Dict[str, Any]] = []
        self.performance_stats: Dict[str, Any] = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_duration": 0.0,
            "api_calls": 0,
            "total_tokens": 0
        }

        # 工作线程
        self.worker_thread: Optional[threading.Thread] = None
        self.worker_active = False

        # 加载预定义工作流
        self._load_predefined_workflows()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "api_key": os.getenv("DEEPSEEK_API_KEY", ""),
            "base_url": "https://api.deepseek.com",
            "model_name": "deepseek-chat",
            "max_tokens": 4000,
            "temperature": 0.7,
            "timeout": 60.0,
            "max_workers": 3,
            "cache_enabled": True,
            "cache_ttl": 3600,  # 1小时
            "workflows_file": "data/deepseek_workflows.json",
            "tasks_file": "data/deepseek_tasks.json",
            "history_file": "data/deepseek_history.json"
        }

    def _load_predefined_workflows(self):
        """加载预定义工作流"""
        # 智能内容分析工作流
        self.workflows["content_analysis"] = WorkflowDefinition(
            id="content_analysis",
            name="智能内容分析",
            description="分析文本内容，提取关键信息和情感倾向",
            steps=[
                {
                    "name": "预处理",
                    "description": "清洗和预处理输入文本",
                    "action": "preprocess_text",
                    "parameters": {}
                },
                {
                    "name": "信息提取",
                    "description": "提取关键信息、实体和主题",
                    "action": "extract_information",
                    "parameters": {}
                },
                {
                    "name": "情感分析",
                    "description": "分析文本的情感倾向",
                    "action": "analyze_sentiment",
                    "parameters": {}
                },
                {
                    "name": "生成摘要",
                    "description": "生成内容摘要和洞察",
                    "action": "generate_summary",
                    "parameters": {}
                }
            ],
            input_schema={"type": "object", "properties": {"text": {"type": "string"}}},
            output_schema={"type": "object"},
            estimated_duration=30.0,
            required_tools=["text_analyzer"]
        )

        # 智能任务规划工作流
        self.workflows["task_planning"] = WorkflowDefinition(
            id="task_planning",
            name="智能任务规划",
            description="根据目标自动规划执行步骤",
            steps=[
                {
                    "name": "目标理解",
                    "description": "分析和理解用户目标",
                    "action": "understand_goal",
                    "parameters": {}
                },
                {
                    "name": "资源分析",
                    "description": "分析可用资源和约束",
                    "action": "analyze_resources",
                    "parameters": {}
                },
                {
                    "name": "步骤规划",
                    "description": "制定详细的执行步骤",
                    "action": "plan_steps",
                    "parameters": {}
                },
                {
                    "name": "风险评估",
                    "description": "评估执行风险和备选方案",
                    "action": "assess_risks",
                    "parameters": {}
                }
            ],
            input_schema={"type": "object", "properties": {"goal": {"type": "string"}}},
            output_schema={"type": "object"},
            estimated_duration=45.0,
            required_tools=["planner", "resource_analyzer"]
        )

        # 自动化决策工作流
        self.workflows["auto_decision"] = WorkflowDefinition(
            id="auto_decision",
            name="自动化决策",
            description="基于数据和规则自动做出决策",
            steps=[
                {
                    "name": "数据收集",
                    "description": "收集相关数据和上下文",
                    "action": "collect_data",
                    "parameters": {}
                },
                {
                    "name": "规则应用",
                    "description": "应用预定义规则和逻辑",
                    "action": "apply_rules",
                    "parameters": {}
                },
                {
                    "name": "决策生成",
                    "description": "生成最终决策建议",
                    "action": "generate_decision",
                    "parameters": {}
                }
            ],
            input_schema={"type": "object"},
            output_schema={"type": "object"},
            estimated_duration=20.0,
            required_tools=["rule_engine", "data_collector"]
        )

    async def chat_with_llm(self, messages: List[Message],
                           functions: List[Dict[str, Any]] = None,
                           function_call: str = None) -> Dict[str, Any]:
        """与DeepSeek LLM进行对话"""
        try:
            if not self.api_key:
                return {"error": "DeepSeek API key未配置"}

            # 构建请求
            api_messages = []
            for msg in messages:
                api_messages.append({
                    "role": msg.role.value,
                    "content": msg.content
                })

            request_data = {
                "model": self.model_name,
                "messages": api_messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "stream": False
            }

            # 添加函数调用支持
            if functions:
                request_data["functions"] = functions
                if function_call:
                    request_data["function_call"] = function_call

            # 发送请求
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config["timeout"])) as session:
                async with session.post(f"{self.base_url}/chat/completions",
                                       headers=headers,
                                       json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()

                        # 更新统计
                        self.performance_stats["api_calls"] += 1
                        if "usage" in result:
                            self.performance_stats["total_tokens"] += result["usage"].get("total_tokens", 0)

                        return {
                            "success": True,
                            "content": result["choices"][0]["message"]["content"],
                            "function_call": result["choices"][0]["message"].get("function_call"),
                            "usage": result.get("usage", {})
                        }
                    else:
                        error_data = await response.text()
                        return {
                            "success": False,
                            "error": f"API请求失败: {response.status} - {error_data}"
                        }

        except asyncio.TimeoutError:
            return {"success": False, "error": "API请求超时"}
        except Exception as e:
            return {"success": False, "error": f"LLM对话异常: {str(e)}"}

    def create_task(self, task_type: TaskType, description: str,
                   context: Dict[str, Any] = None,
                   priority: int = 0,
                   workflow_id: str = None) -> str:
        """创建新任务"""
        task_id = f"task_{int(time.time())}_{len(self.tasks)}"

        task = Task(
            id=task_id,
            task_type=task_type,
            description=description,
            context=context or {},
            priority=priority,
            workflow_id=workflow_id
        )

        self.tasks[task_id] = task

        # 如果指定了工作流，添加工作流步骤
        if workflow_id and workflow_id in self.workflows:
            task.estimated_duration = self.workflows[workflow_id].estimated_duration

        # 添加到优先级队列（使用负优先级，因为PriorityQueue是最小堆）
        self.task_queue.put((-priority, task_id))

        print(f"创建任务: {task_id} - {description}")
        return task_id

    async def execute_task(self, task_id: str) -> Dict[str, Any]:
        """执行单个任务"""
        if task_id not in self.tasks:
            return {"success": False, "error": f"任务不存在: {task_id}"}

        task = self.tasks[task_id]
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        try:
            print(f"开始执行任务: {task_id} - {task.description}")

            # 根据任务类型执行不同的逻辑
            if task.task_type == TaskType.QUERY:
                result = await self._execute_query_task(task)
            elif task.task_type == TaskType.ANALYSIS:
                result = await self._execute_analysis_task(task)
            elif task.task_type == TaskType.GENERATION:
                result = await self._execute_generation_task(task)
            elif task.task_type == TaskType.DECISION:
                result = await self._execute_decision_task(task)
            elif task.task_type == TaskType.PLANNING:
                result = await self._execute_planning_task(task)
            elif task.task_type == TaskType.AUTOMATION:
                result = await self._execute_automation_task(task)
            else:
                result = {"success": False, "error": f"未知任务类型: {task.task_type}"}

            if result["success"]:
                task.status = TaskStatus.COMPLETED
                task.result = result
                self.performance_stats["completed_tasks"] += 1
                print(f"任务执行成功: {task_id}")
            else:
                task.error = result.get("error", "未知错误")
                task.retry_count += 1

                if task.retry_count < task.max_retries:
                    task.status = TaskStatus.RETRYING
                    print(f"任务执行失败，准备重试: {task_id} (重试 {task.retry_count}/{task.max_retries})")
                    # 延迟后重试
                    await asyncio.sleep(2 ** task.retry_count)  # 指数退避
                    return await self.execute_task(task_id)
                else:
                    task.status = TaskStatus.FAILED
                    self.performance_stats["failed_tasks"] += 1
                    print(f"任务执行失败: {task_id} - {task.error}")

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            self.performance_stats["failed_tasks"] += 1
            result = {"success": False, "error": f"任务执行异常: {str(e)}"}
            print(f"任务执行异常: {task_id} - {str(e)}")

        finally:
            task.completed_at = datetime.now()
            task.actual_duration = (task.completed_at - task.started_at).total_seconds()

        # 记录历史
        self._record_task_history(task)
        self.performance_stats["total_tasks"] += 1

        return result

    async def _execute_query_task(self, task: Task) -> Dict[str, Any]:
        """执行查询任务"""
        try:
            # 构建对话消息
            messages = [
                Message(role=MessageRole.SYSTEM, content="你是一个智能助手，负责回答用户问题。"),
                Message(role=MessageRole.USER, content=task.description)
            ]

            # 如果有上下文，添加到消息中
            if task.context:
                context_msg = Message(
                    role=MessageRole.SYSTEM,
                    content=f"上下文信息: {json.dumps(task.context, ensure_ascii=False, indent=2)}"
                )
                messages.insert(1, context_msg)

            # 调用LLM
            result = await self.chat_with_llm(messages)

            if result["success"]:
                # 记录对话
                assistant_msg = Message(
                    role=MessageRole.ASSISTANT,
                    content=result["content"]
                )
                task.messages.extend([messages[1], assistant_msg])

                return {
                    "success": True,
                    "answer": result["content"],
                    "usage": result.get("usage", {})
                }
            else:
                return result

        except Exception as e:
            return {"success": False, "error": f"查询任务执行异常: {str(e)}"}

    async def _execute_analysis_task(self, task: Task) -> Dict[str, Any]:
        """执行分析任务"""
        try:
            # 构建分析提示
            system_prompt = """你是一个专业的分析师，负责分析用户提供的内容。
            请提供详细的分析报告，包括：
            1. 关键信息提取
            2. 主要观点总结
            3. 潜在问题识别
            4. 建议和改进方案
            请以JSON格式返回分析结果。"""

            messages = [
                Message(role=MessageRole.SYSTEM, content=system_prompt),
                Message(role=MessageRole.USER, content=f"请分析以下内容: {task.description}")
            ]

            result = await self.chat_with_llm(messages)

            if result["success"]:
                # 尝试解析JSON结果
                try:
                    analysis_data = json.loads(result["content"])
                except:
                    # 如果无法解析JSON，返回原始内容
                    analysis_data = {"raw_analysis": result["content"]}

                assistant_msg = Message(
                    role=MessageRole.ASSISTANT,
                    content=result["content"]
                )
                task.messages.extend([messages[1], assistant_msg])

                return {
                    "success": True,
                    "analysis": analysis_data,
                    "usage": result.get("usage", {})
                }
            else:
                return result

        except Exception as e:
            return {"success": False, "error": f"分析任务执行异常: {str(e)}"}

    async def _execute_generation_task(self, task: Task) -> Dict[str, Any]:
        """执行生成任务"""
        try:
            # 根据上下文确定生成类型
            generation_type = task.context.get("type", "text")

            if generation_type == "code":
                system_prompt = "你是一个专业的程序员，请根据要求生成高质量的代码。"
            elif generation_type == "email":
                system_prompt = "你是一个专业的写作助手，请根据要求生成正式的邮件。"
            elif generation_type == "report":
                system_prompt = "你是一个专业的报告撰写专家，请根据要求生成详细的报告。"
            else:
                system_prompt = "你是一个专业的写作助手，请根据要求生成高质量的内容。"

            messages = [
                Message(role=MessageRole.SYSTEM, content=system_prompt),
                Message(role=MessageRole.USER, content=task.description)
            ]

            result = await self.chat_with_llm(messages)

            if result["success"]:
                assistant_msg = Message(
                    role=MessageRole.ASSISTANT,
                    content=result["content"]
                )
                task.messages.extend([messages[1], assistant_msg])

                return {
                    "success": True,
                    "generated_content": result["content"],
                    "type": generation_type,
                    "usage": result.get("usage", {})
                }
            else:
                return result

        except Exception as e:
            return {"success": False, "error": f"生成任务执行异常: {str(e)}"}

    async def _execute_decision_task(self, task: Task) -> Dict[str, Any]:
        """执行决策任务"""
        try:
            system_prompt = """你是一个专业的决策助手，请基于提供的信息做出决策。
            请考虑以下因素：
            1. 可用资源和约束
            2. 风险评估
            3. 成本效益分析
            4. 备选方案
            请提供明确的决策建议和理由。"""

            messages = [
                Message(role=MessageRole.SYSTEM, content=system_prompt),
                Message(role=MessageRole.USER, content=f"决策场景: {task.description}")
            ]

            # 添加上下文信息
            if task.context:
                context_msg = Message(
                    role=MessageRole.USER,
                    content=f"相关信息: {json.dumps(task.context, ensure_ascii=False, indent=2)}"
                )
                messages.append(context_msg)

            result = await self.chat_with_llm(messages)

            if result["success"]:
                assistant_msg = Message(
                    role=MessageRole.ASSISTANT,
                    content=result["content"]
                )
                task.messages.extend([messages[1], assistant_msg])

                return {
                    "success": True,
                    "decision": result["content"],
                    "usage": result.get("usage", {})
                }
            else:
                return result

        except Exception as e:
            return {"success": False, "error": f"决策任务执行异常: {str(e)}"}

    async def _execute_planning_task(self, task: Task) -> Dict[str, Any]:
        """执行规划任务"""
        try:
            system_prompt = """你是一个专业的规划助手，请根据目标制定详细的执行计划。
            请提供：
            1. 明确的目标分解
            2. 详细的执行步骤
            3. 时间预估
            4. 资源需求
            5. 风险评估和应对措施
            请以结构化的方式返回计划。"""

            messages = [
                Message(role=MessageRole.SYSTEM, content=system_prompt),
                Message(role=MessageRole.USER, content=f"规划目标: {task.description}")
            ]

            result = await self.chat_with_llm(messages)

            if result["success"]:
                assistant_msg = Message(
                    role=MessageRole.ASSISTANT,
                    content=result["content"]
                )
                task.messages.extend([messages[1], assistant_msg])

                return {
                    "success": True,
                    "plan": result["content"],
                    "usage": result.get("usage", {})
                }
            else:
                return result

        except Exception as e:
            return {"success": False, "error": f"规划任务执行异常: {str(e)}"}

    async def _execute_automation_task(self, task: Task) -> Dict[str, Any]:
        """执行自动化任务"""
        try:
            # 自动化任务通常涉及调用其他系统
            automation_type = task.context.get("automation_type", "general")

            if automation_type == "file_analysis":
                return await self._execute_file_analysis_automation(task)
            elif automation_type == "data_processing":
                return await self._execute_data_processing_automation(task)
            elif automation_type == "system_monitoring":
                return await self._execute_system_monitoring_automation(task)
            else:
                # 通用自动化任务
                system_prompt = f"""你是一个自动化专家，请设计一个自动化方案来完成以下任务: {task.description}
                请提供详细的执行步骤和所需工具。"""

                messages = [
                    Message(role=MessageRole.SYSTEM, content=system_prompt),
                    Message(role=MessageRole.USER, content=task.description)
                ]

                result = await self.chat_with_llm(messages)

                if result["success"]:
                    return {
                        "success": True,
                        "automation_plan": result["content"],
                        "usage": result.get("usage", {})
                    }
                else:
                    return result

        except Exception as e:
            return {"success": False, "error": f"自动化任务执行异常: {str(e)}"}

    async def _execute_file_analysis_automation(self, task: Task) -> Dict[str, Any]:
        """执行文件分析自动化"""
        try:
            file_path = task.context.get("file_path")
            if not file_path or not os.path.exists(file_path):
                return {"success": False, "error": "文件不存在或未指定"}

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 使用LLM分析文件
            messages = [
                Message(role=MessageRole.SYSTEM, content="你是一个文件分析专家，请分析文件内容并提供总结。"),
                Message(role=MessageRole.USER, content=f"请分析以下文件内容: {content}")
            ]

            result = await self.chat_with_llm(messages)

            if result["success"]:
                return {
                    "success": True,
                    "file_analysis": result["content"],
                    "file_path": file_path,
                    "usage": result.get("usage", {})
                }
            else:
                return result

        except Exception as e:
            return {"success": False, "error": f"文件分析自动化异常: {str(e)}"}

    async def _execute_data_processing_automation(self, task: Task) -> Dict[str, Any]:
        """执行数据处理自动化"""
        try:
            # 这里可以实现具体的数据处理逻辑
            return {"success": True, "message": "数据处理自动化功能待实现"}
        except Exception as e:
            return {"success": False, "error": f"数据处理自动化异常: {str(e)}"}

    async def _execute_system_monitoring_automation(self, task: Task) -> Dict[str, Any]:
        """执行系统监控自动化"""
        try:
            # 集成系统健康监控
            if hasattr(self, 'health_monitor'):
                health_data = self.health_monitor.get_health_summary()
                return {
                    "success": True,
                    "monitoring_data": health_data
                }
            else:
                return {"success": False, "error": "系统健康监控未集成"}
        except Exception as e:
            return {"success": False, "error": f"系统监控自动化异常: {str(e)}"}

    def start_worker(self):
        """启动工作线程"""
        if self.worker_active:
            print("工作线程已在运行")
            return

        print("启动DeepSeek工作线程...")
        self.worker_active = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()

    def stop_worker(self):
        """停止工作线程"""
        print("停止DeepSeek工作线程...")
        self.worker_active = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)

    def _worker_loop(self):
        """工作线程主循环"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        while self.worker_active:
            try:
                # 获取任务（最多等待1秒）
                try:
                    _, task_id = self.task_queue.get(timeout=1.0)
                except queue.Empty:
                    continue

                if task_id not in self.tasks:
                    continue

                task = self.tasks[task_id]

                # 检查任务依赖
                if not self._check_task_dependencies(task):
                    # 依赖未满足，重新放回队列
                    self.task_queue.put((-task.priority, task_id))
                    continue

                # 执行任务
                if task_id not in self.running_tasks:
                    self.running_tasks[task_id] = task

                try:
                    # 在事件循环中执行异步任务
                    result = loop.run_until_complete(self.execute_task(task_id))
                finally:
                    self.running_tasks.pop(task_id, None)

                # 标记任务完成
                self.task_queue.task_done()

            except Exception as e:
                print(f"工作线程异常: {str(e)}")
                time.sleep(5)  # 出错后短暂休息

        loop.close()

    def _check_task_dependencies(self, task: Task) -> bool:
        """检查任务依赖是否满足"""
        for dep_id in task.dependencies:
            if dep_id in self.tasks:
                dep_task = self.tasks[dep_id]
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
        return True

    def _record_task_history(self, task: Task):
        """记录任务历史"""
        history_record = {
            "task_id": task.id,
            "task_type": task.task_type.value,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "duration": task.actual_duration,
            "retry_count": task.retry_count,
            "error": task.error
        }

        self.task_history.append(history_record)

        # 保持历史记录数量限制
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-1000:]

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """获取任务状态"""
        if task_id not in self.tasks:
            return {"error": f"任务不存在: {task_id}"}

        task = self.tasks[task_id]
        return {
            "task_id": task.id,
            "task_type": task.task_type.value,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority,
            "progress": {
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                "duration": task.actual_duration,
                "estimated_duration": task.estimated_duration
            },
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
            "error": task.error,
            "result": task.result
        }

    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        pending_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
        running_tasks = list(self.running_tasks.values())

        return {
            "queue_size": self.task_queue.qsize(),
            "pending_tasks": len(pending_tasks),
            "running_tasks": len(running_tasks),
            "total_tasks": len(self.tasks),
            "worker_active": self.worker_active,
            "pending_task_details": [
                {
                    "task_id": t.id,
                    "type": t.task_type.value,
                    "description": t.description,
                    "priority": t.priority
                }
                for t in sorted(pending_tasks, key=lambda x: x.priority, reverse=True)[:10]
            ],
            "running_task_details": [
                {
                    "task_id": t.id,
                    "type": t.task_type.value,
                    "description": t.description,
                    "started_at": t.started_at.isoformat() if t.started_at else None
                }
                for t in running_tasks
            ]
        }

    def get_performance_statistics(self) -> Dict[str, Any]:
        """获取性能统计"""
        # 计算平均执行时间
        completed_tasks = [t for t in self.tasks.values() if t.status == TaskStatus.COMPLETED]
        if completed_tasks:
            avg_duration = sum(t.actual_duration for t in completed_tasks) / len(completed_tasks)
            self.performance_stats["average_duration"] = avg_duration

        return {
            **self.performance_stats,
            "success_rate": (self.performance_stats["completed_tasks"] /
                           max(self.performance_stats["total_tasks"], 1)) * 100,
            "available_workflows": [
                {
                    "id": wf.id,
                    "name": wf.name,
                    "description": wf.description,
                    "estimated_duration": wf.estimated_duration,
                    "required_tools": wf.required_tools
                }
                for wf in self.workflows.values()
            ]
        }

# 创建全局DeepSeek集成实例
deepseek_integration = DeepSeekLLMIntegration()