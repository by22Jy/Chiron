# YOLO-LLM 智能工作流代理详细实施计划

## 🚀 项目概述
将YOLO-LLM从"手势→固定动作"升级为"语音/手势→智能工作流代理"，支持复杂多任务自动化。

## 📋 Phase 1: 基础架构设计 (第1-2周)

### 1.1 智能工具抽象层
```
agent/
├── intelligent_tools/
│   ├── __init__.py
│   ├── base_tool.py           # 工具基类
│   ├── tool_registry.py       # 工具注册表
│   ├── tool_types.py         # 工具类型定义
│   └── tool_result.py        # 工具执行结果
```

#### 1.1.1 工具基类设计
```python
# agent/intelligent_tools/base_tool.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ToolResult:
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    context_update: Optional[Dict[str, Any]] = None
    next_actions: Optional[List[str]] = None

class IntelligentTool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, action: str, params: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        """执行工具动作"""
        pass

    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """返回工具支持的动作列表"""
        pass

    @abstractmethod
    def validate_params(self, action: str, params: Dict[str, Any]) -> bool:
        """验证参数有效性"""
        pass

    def get_required_permissions(self) -> List[str]:
        """返回所需权限"""
        return []
```

#### 1.1.2 工具注册表
```python
# agent/intelligent_tools/tool_registry.py
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, IntelligentTool] = {}
        self.tool_categories: Dict[str, List[str]] = {}

    def register_tool(self, tool: IntelligentTool, category: str = "general"):
        """注册工具"""
        self.tools[tool.name] = tool

        if category not in self.tool_categories:
            self.tool_categories[category] = []
        self.tool_categories[category].append(tool.name)

    def get_tool(self, name: str) -> Optional[IntelligentTool]:
        """获取工具"""
        return self.tools.get(name)

    def get_tools_by_category(self, category: str) -> List[IntelligentTool]:
        """按分类获取工具"""
        return [self.tools[name] for name in self.tool_categories.get(category, [])]

    def list_all_tools(self) -> Dict[str, str]:
        """列出所有工具及其描述"""
        return {name: tool.description for name, tool in self.tools.items()}
```

### 1.2 工作流引擎
```
agent/
├── workflow/
│   ├── __init__.py
│   ├── workflow_engine.py     # 工作流执行引擎
│   ├── workflow_planner.py    # 工作流规划器
│   ├── workflow_types.py      # 工作流数据结构
│   └── context_manager.py     # 上下文管理
```

#### 1.2.1 工作流数据结构
```python
# agent/workflow/workflow_types.py
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class WorkflowStep:
    step_id: int
    tool_name: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[int] = None  # 依赖的步骤ID
    status: StepStatus = StepStatus.PENDING
    result: Optional[ToolResult] = None
    error_message: Optional[str] = None

@dataclass
class WorkflowPlan:
    workflow_id: str
    intent: str
    description: str
    steps: List[WorkflowStep]
    estimated_duration: int = 0  # 预估执行时间（秒）
    required_permissions: List[str] = None

@dataclass
class WorkflowResult:
    workflow_id: str
    success: bool
    completed_steps: List[WorkflowStep]
    failed_steps: List[WorkflowStep]
    final_context: Dict[str, Any]
    execution_time: float
    user_message: str
```

#### 1.2.2 工作流规划器
```python
# agent/workflow/workflow_planner.py
import json
from typing import Dict, Any, List

class WorkflowPlanner:
    def __init__(self, llm_service, tool_registry):
        self.llm_service = llm_service
        self.tool_registry = tool_registry

    def plan_workflow(self, user_input: str, context: Dict[str, Any]) -> WorkflowPlan:
        """基于用户输入规划工作流"""

        # 获取可用工具信息
        available_tools = self.tool_registry.list_all_tools()

        # 构建提示词
        prompt = self._build_planning_prompt(user_input, context, available_tools)

        # 调用LLM生成工作流
        llm_response = self.llm_service.orchestrateByUrl("", prompt)

        # 解析LLM响应
        workflow_plan = self._parse_workflow_response(llm_response)

        return workflow_plan

    def _build_planning_prompt(self, user_input: str, context: Dict[str, Any], tools: Dict[str, str]) -> str:
        """构建工作流规划提示词"""
        return f"""
你是一个智能工作流规划助手。请分析用户请求并生成详细的工作流计划。

用户请求: {user_input}

当前上下文: {json.dumps(context, ensure_ascii=False, indent=2)}

可用工具:
{json.dumps(tools, ensure_ascii=False, indent=2)}

请生成JSON格式的工作流计划，包含以下字段：
{{
    "intent": "用户的核心意图",
    "description": "工作流描述",
    "steps": [
        {{
            "step_id": 1,
            "tool_name": "工具名称",
            "action": "具体动作",
            "parameters": {{"param1": "value1", "param2": "value2"}},
            "dependencies": [],  # 依赖的前置步骤ID
            "description": "步骤描述"
        }}
    ],
    "estimated_duration": 30,  # 预估执行时间（秒）
    "required_permissions": ["file_access", "network"]  # 所需权限
}}

要求：
1. 步骤要具体可执行
2. 参数要明确指定
3. 考虑步骤间的依赖关系
4. 确保工具和动作的正确性
5. 提供合理的执行时间估算
"""

    def _parse_workflow_response(self, llm_response: str) -> WorkflowPlan:
        """解析LLM响应为工作流计划"""
        try:
            # 提取JSON部分
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            json_str = llm_response[json_start:json_end]

            # 解析JSON
            data = json.loads(json_str)

            # 创建WorkflowStep对象
            steps = []
            for step_data in data.get('steps', []):
                step = WorkflowStep(
                    step_id=step_data['step_id'],
                    tool_name=step_data['tool_name'],
                    action=step_data['action'],
                    parameters=step_data['parameters'],
                    dependencies=step_data.get('dependencies', []),
                    description=step_data.get('description', '')
                )
                steps.append(step)

            # 创建工作流计划
            workflow_plan = WorkflowPlan(
                workflow_id=f"workflow_{int(time.time())}",
                intent=data['intent'],
                description=data['description'],
                steps=steps,
                estimated_duration=data.get('estimated_duration', 0),
                required_permissions=data.get('required_permissions', [])
            )

            return workflow_plan

        except Exception as e:
            # 解析失败时创建错误工作流
            return WorkflowPlan(
                workflow_id=f"error_{int(time.time())}",
                intent="解析失败",
                description=f"无法解析LLM响应: {str(e)}",
                steps=[],
                estimated_duration=0,
                required_permissions=[]
            )
```

#### 1.2.3 工作流执行引擎
```python
# agent/workflow/workflow_engine.py
import time
import logging
from typing import Dict, Any, List

class WorkflowEngine:
    def __init__(self, tool_registry, context_manager):
        self.tool_registry = tool_registry
        self.context_manager = context_manager
        self.logger = logging.getLogger(__name__)

    def execute_workflow(self, workflow_plan: WorkflowPlan) -> WorkflowResult:
        """执行工作流"""
        start_time = time.time()
        completed_steps = []
        failed_steps = []

        try:
            self.logger.info(f"开始执行工作流: {workflow_plan.workflow_id}")

            # 按依赖关系排序执行步骤
            sorted_steps = self._sort_steps_by_dependencies(workflow_plan.steps)

            for step in sorted_steps:
                if self._can_execute_step(step, completed_steps):
                    step.status = StepStatus.RUNNING

                    try:
                        # 获取工具
                        tool = self.tool_registry.get_tool(step.tool_name)
                        if not tool:
                            raise Exception(f"工具不存在: {step.tool_name}")

                        # 获取当前上下文
                        current_context = self.context_manager.get_context()

                        # 执行步骤
                        result = tool.execute(step.action, step.parameters, current_context)

                        # 更新步骤状态
                        step.status = StepStatus.COMPLETED
                        step.result = result

                        # 更新上下文
                        if result.context_update:
                            self.context_manager.update_context(result.context_update)

                        completed_steps.append(step)
                        self.logger.info(f"步骤 {step.step_id} 执行成功: {result.message}")

                    except Exception as e:
                        step.status = StepStatus.FAILED
                        step.error_message = str(e)
                        failed_steps.append(step)
                        self.logger.error(f"步骤 {step.step_id} 执行失败: {str(e)}")

                        # 根据错误处理策略决定是否继续
                        if not self._should_continue_on_error(step, failed_steps):
                            break
                else:
                    # 跳过无法执行的步骤
                    step.status = StepStatus.SKIPPED
                    self.logger.warning(f"跳过步骤 {step.step_id}: 依赖未满足")

            # 计算执行结果
            execution_time = time.time() - start_time
            success = len(failed_steps) == 0
            final_context = self.context_manager.get_context()

            # 生成用户消息
            user_message = self._generate_user_message(workflow_plan, completed_steps, failed_steps)

            return WorkflowResult(
                workflow_id=workflow_plan.workflow_id,
                success=success,
                completed_steps=completed_steps,
                failed_steps=failed_steps,
                final_context=final_context,
                execution_time=execution_time,
                user_message=user_message
            )

        except Exception as e:
            self.logger.error(f"工作流执行异常: {str(e)}")
            return WorkflowResult(
                workflow_id=workflow_plan.workflow_id,
                success=False,
                completed_steps=completed_steps,
                failed_steps=failed_steps,
                final_context=self.context_manager.get_context(),
                execution_time=time.time() - start_time,
                user_message=f"工作流执行失败: {str(e)}"
            )

    def _sort_steps_by_dependencies(self, steps: List[WorkflowStep]) -> List[WorkflowStep]:
        """按依赖关系排序步骤（拓扑排序）"""
        # 实现拓扑排序算法
        # 这里简化实现，实际项目中需要完整的拓扑排序
        return sorted(steps, key=lambda x: x.step_id)

    def _can_execute_step(self, step: WorkflowStep, completed_steps: List[WorkflowStep]) -> bool:
        """检查步骤是否可以执行"""
        if not step.dependencies:
            return True

        completed_step_ids = {s.step_id for s in completed_steps}
        return all(dep_id in completed_step_ids for dep_id in step.dependencies)

    def _should_continue_on_error(self, step: WorkflowStep, failed_steps: List[WorkflowStep]) -> bool:
        """决定遇到错误时是否继续执行"""
        # 可以基于步骤重要性、错误类型等决定
        return len(failed_steps) < 3  # 简单策略：失败步骤少于3个时继续

    def _generate_user_message(self, workflow_plan: WorkflowPlan,
                              completed_steps: List[WorkflowStep],
                              failed_steps: List[WorkflowStep]) -> str:
        """生成用户友好的执行结果消息"""
        if not failed_steps:
            return f"✅ 工作流执行成功！完成了 {len(completed_steps)} 个步骤：{workflow_plan.description}"
        else:
            return f"⚠️ 工作流部分完成。成功 {len(completed_steps)} 个步骤，失败 {len(failed_steps)} 个步骤。"
```

### 1.3 上下文管理系统
```python
# agent/workflow/context_manager.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import os

@dataclass
class ContextData:
    short_term: Dict[str, Any] = field(default_factory=dict)
    long_term: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)

class ContextManager:
    def __init__(self, storage_path: str = "agent/context/"):
        self.storage_path = storage_path
        self.context = ContextData()
        self.max_history = 50

        # 确保存储目录存在
        os.makedirs(storage_path, exist_ok=True)

        # 加载持久化数据
        self._load_context()

    def get_context(self) -> Dict[str, Any]:
        """获取当前完整上下文"""
        return {
            "short_term": self.context.short_term,
            "long_term": self.context.long_term,
            "recent_history": self.context.conversation_history[-10:],
            "user_preferences": self.context.user_preferences,
            "timestamp": time.time()
        }

    def update_context(self, updates: Dict[str, Any]):
        """更新上下文"""
        self.context.short_term.update(updates.get("short_term", {}))
        self.context.long_term.update(updates.get("long_term", {}))

        if "user_preferences" in updates:
            self.context.user_preferences.update(updates["user_preferences"])

    def add_conversation(self, user_input: str, ai_response: str, metadata: Dict[str, Any] = None):
        """添加对话记录"""
        conversation = {
            "user_input": user_input,
            "ai_response": ai_response,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }

        self.context.conversation_history.append(conversation)

        # 限制历史记录数量
        if len(self.context.conversation_history) > self.max_history:
            self.context.conversation_history = self.context.conversation_history[-self.max_history:]

    def get_relevant_history(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """获取相关历史记录"""
        # 简化实现：返回最近的记录
        # 实际项目中可以实现语义搜索
        return self.context.conversation_history[-limit:]

    def _load_context(self):
        """加载持久化上下文"""
        try:
            context_file = os.path.join(self.storage_path, "context.json")
            if os.path.exists(context_file):
                with open(context_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.context = ContextData(**data)
        except Exception as e:
            logging.warning(f"加载上下文失败: {e}")

    def save_context(self):
        """保存上下文到文件"""
        try:
            context_file = os.path.join(self.storage_path, "context.json")
            with open(context_file, 'w', encoding='utf-8') as f:
                json.dump(self.context.__dict__, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"保存上下文失败: {e}")
```

## 📋 Phase 2: 核心工具实现 (第3-5周)

### 2.1 系统操作工具
```python
# agent/intelligent_tools/system_tool.py
import subprocess
import pyautogui
import time
from typing import Dict, Any
from .base_tool import IntelligentTool, ToolResult

class SystemTool(IntelligentTool):
    def __init__(self):
        super().__init__("system", "系统操作工具：应用启动、窗口管理、文件操作等")

    def get_capabilities(self) -> List[str]:
        return [
            "open_app", "close_app", "focus_window",
            "create_file", "save_file", "read_file",
            "open_directory", "screenshot"
        ]

    def execute(self, action: str, params: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        if action == "open_app":
            return self._open_app(params)
        elif action == "create_file":
            return self._create_file(params)
        elif action == "screenshot":
            return self._screenshot(params)
        else:
            return ToolResult(False, f"不支持的动作: {action}")

    def _open_app(self, params: Dict[str, Any]) -> ToolResult:
        """打开应用程序"""
        app_name = params.get("app_name")
        if not app_name:
            return ToolResult(False, "缺少应用名称参数")

        try:
            if app_name.lower() == "notepad":
                subprocess.Popen(["notepad.exe"])
            elif app_name.lower() == "calculator":
                subprocess.Popen(["calc.exe"])
            elif app_name.lower() == "chrome":
                subprocess.Popen(["chrome.exe"])
            else:
                # 尝试直接运行
                subprocess.Popen([app_name])

            time.sleep(1)  # 等待应用启动

            return ToolResult(
                success=True,
                message=f"成功打开应用: {app_name}",
                context_update={"last_opened_app": app_name}
            )

        except Exception as e:
            return ToolResult(False, f"打开应用失败: {str(e)}")
```

### 2.2 通信工具
```python
# agent/intelligent_tools/messaging_tool.py
import requests
import time
from typing import Dict, Any
from .base_tool import IntelligentTool, ToolResult

class MessagingTool(IntelligentTool):
    def __init__(self):
        super().__init__("messaging", "通信工具：微信、邮件、通知等")

    def get_capabilities(self) -> List[str]:
        return ["send_wechat", "send_email", "send_notification"]

    def execute(self, action: str, params: Dict[str, Any], context: Dict[str, Any]) -> ToolResult:
        if action == "send_wechat":
            return self._send_wechat(params)
        elif action == "send_notification":
            return self._send_notification(params)
        else:
            return ToolResult(False, f"不支持的动作: {action}")

    def _send_wechat(self, params: Dict[str, Any]) -> ToolResult:
        """发送微信消息"""
        content = params.get("content", "")
        recipient = params.get("recipient", "")

        if not content:
            return ToolResult(False, "消息内容不能为空")

        try:
            # 方案1: 企业微信API（如果有）
            if self._has_enterprise_wechat_api():
                return self._send_via_enterprise_api(content, recipient)

            # 方案2: UI自动化
            return self._send_via_ui_automation(content, recipient)

        except Exception as e:
            return ToolResult(False, f"发送微信消息失败: {str(e)}")

    def _send_via_ui_automation(self, content: str, recipient: str) -> ToolResult:
        """通过UI自动化发送微信消息"""
        try:
            # 1. 打开微信
            subprocess.Popen(["wechat.exe"])
            time.sleep(2)

            # 2. 搜索联系人（如果指定）
            if recipient:
                # 实现搜索逻辑
                pass

            # 3. 输入消息
            pyautogui.typewrite(content)

            # 4. 发送消息
            pyautogui.press('enter')

            return ToolResult(
                success=True,
                message=f"微信消息发送成功",
                context_update={"last_message": content}
            )

        except Exception as e:
            return ToolResult(False, f"UI自动化发送失败: {str(e)}")
```

## 📋 Phase 3: 集成实施 (第6-7周)

### 3.1 语音控制集成
```python
# 修改 agent/speech_controller.py
from .workflow.workflow_engine import WorkflowEngine
from .workflow.workflow_planner import WorkflowPlanner
from .intelligent_tools.tool_registry import ToolRegistry

class EnhancedSpeechController:
    def __init__(self, backend_url: str):
        self.backend_url = backend_url

        # 初始化智能代理组件
        self.tool_registry = ToolRegistry()
        self.context_manager = ContextManager()
        self.workflow_planner = WorkflowPlanner(llm_service, self.tool_registry)
        self.workflow_engine = WorkflowEngine(self.tool_registry, self.context_manager)

        # 注册所有工具
        self._register_tools()

    def _register_tools(self):
        """注册所有可用工具"""
        from .intelligent_tools.system_tool import SystemTool
        from .intelligent_tools.messaging_tool import MessagingTool
        from .intelligent_tools.text_tool import TextTool

        self.tool_registry.register_tool(SystemTool(), "system")
        self.tool_registry.register_tool(MessagingTool(), "messaging")
        self.tool_registry.register_tool(TextTool(), "text")

    def process_voice_command_intelligently(self, text: str):
        """智能处理语音命令"""
        try:
            # 获取当前上下文
            context = self.context_manager.get_context()

            # 规划工作流
            workflow_plan = self.workflow_planner.plan_workflow(text, context)

            # 执行工作流
            result = self.workflow_engine.execute_workflow(workflow_plan)

            # 记录对话
            self.context_manager.add_conversation(text, result.user_message)

            return result.user_message

        except Exception as e:
            # 回退到传统处理方式
            return self._traditional_process(text)
```

## 📋 Phase 4: 高级功能 (第8-10周)

### 4.1 工作流模板化
```python
# agent/workflow/templates.py
class WorkflowTemplates:
    TEMPLATES = {
        "todo_and_share": {
            "intent": "创建TODO并分享",
            "description": "创建TODO列表并通过指定方式分享",
            "workflow": {
                "steps": [
                    {"tool": "ai", "action": "generate_todo", "params": {"date": "today"}},
                    {"tool": "system", "action": "open_notepad"},
                    {"tool": "input", "action": "type_text", "params": {"text": "{{step1.result}}"}},
                    {"tool": "messaging", "action": "send_wechat", "params": {"content": "{{step1.result}}"}}
                ]
            }
        }
    }
```

### 4.2 学习和优化
```python
# agent/workflow/learning.py
class WorkflowLearning:
    def learn_from_execution(self, workflow_plan: WorkflowPlan, result: WorkflowResult):
        """从执行结果中学习"""
        if result.success:
            # 记录成功的工作流模式
            self._record_successful_pattern(workflow_plan)
        else:
            # 分析失败原因
            self._analyze_failure_pattern(workflow_plan, result)

    def optimize_workflow_planning(self, user_input: str):
        """基于历史数据优化工作流规划"""
        # 实现学习逻辑
        pass
```

## 🎯 关键成功因素

1. **渐进式实施**: 从简单到复杂，逐步添加功能
2. **充分测试**: 每个工具和工作流都需要充分测试
3. **错误处理**: 完善的错误处理和回滚机制
4. **用户反馈**: 及时收集和处理用户反馈
5. **性能优化**: 确保响应时间在可接受范围内

## 📊 项目里程碑

- **Week 2**: 基础架构完成，工具框架可用
- **Week 5**: 核心工具实现，基本工作流可用
- **Week 7**: 语音/手势集成完成，智能代理可用
- **Week 10**: 高级功能完成，系统优化完成

---

*这个计划提供了详细的实施路径，我们可以按照这个计划逐步实现智能工作流代理。*