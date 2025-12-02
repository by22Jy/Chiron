# YOLO-LLM 智能工作流代理设计方案

## 🎯 核心升级思路

从 **"手势→固定动作"** 升级到 **"语音/手势→智能工作流代理"**

## 🏗️ 架构升级方案

### 1. 智能意图理解层

```python
class IntelligentIntentAnalyzer:
    def analyze_intent(self, user_input: str, context: Dict) -> IntentResult:
        """理解用户真实意图，而不仅仅是关键词匹配"""

        prompt = f"""
        分析用户意图并生成工作流计划：

        用户输入：{user_input}
        当前上下文：{context}
        历史记录：{self.get_history()}

        请返回JSON格式的工作流计划：
        {{
            "intent": "用户真实意图",
            "workflow_steps": [
                {{
                    "step_id": 1,
                    "action": "open_notepad",
                    "parameters": {{"content": "今天的TODO列表"}},
                    "tool": "system_apps"
                }},
                {{
                    "step_id": 2,
                    "action": "type_content",
                    "parameters": {{"text": "生成的TODO内容"}},
                    "tool": "text_input"
                }},
                {{
                    "step_id": 3,
                    "action": "send_wechat",
                    "parameters": {{"content": "TODO内容", "recipient": "自己手机"}},
                    "tool": "messaging"
                }}
            ],
            "context_update": {{
                "user_goal": "记录并发送TODO",
                "deadline": "今天"
            }}
        }}
        """
```

### 2. 智能工具库扩展

```python
class IntelligentToolRegistry:
    def __init__(self):
        self.tools = {
            # 系统操作工具
            "system_apps": SystemAppTool(),
            "file_operations": FileOperationTool(),
            "clipboard": ClipboardTool(),

            # 通信工具
            "messaging": MessagingTool(),  # 微信、邮件、短信
            "notification": NotificationTool(),

            # 网络工具
            "web_scraping": WebScrapingTool(),
            "api_calls": ApiCallTool(),

            # 智能处理工具
            "text_processing": TextProcessingTool(),
            "image_processing": ImageProcessingTool(),

            # 数据管理工具
            "database": DatabaseTool(),
            "spreadsheet": SpreadsheetTool(),  # Excel等
        }

    def get_tool(self, tool_name: str):
        return self.tools.get(tool_name)
```

### 3. 工作流执行引擎

```python
class WorkflowEngine:
    def execute_workflow(self, workflow: WorkflowPlan) -> ExecutionResult:
        """执行多步骤工作流"""

        results = []
        context = {}

        for step in workflow.workflow_steps:
            try:
                # 获取工具
                tool = self.tool_registry.get_tool(step.tool)

                # 执行步骤
                result = tool.execute(step.action, step.parameters, context)

                # 更新上下文
                context.update(result.context_update)
                results.append(result)

                # 记录执行状态
                self.log_execution(step, result)

            except Exception as e:
                # 错误处理和回滚
                return self.handle_error(step, e, context)

        return ExecutionResult(success=True, results=results, final_context=context)
```

## 🛠️ 具体工具实现示例

### 1. 系统应用工具

```python
class SystemAppTool:
    def execute(self, action: str, params: Dict, context: Dict):
        if action == "open_notepad":
            return self.open_notepad(params.get("content", ""))
        elif action == "open_calculator":
            return self.open_calculator()
        # ... 其他应用

    def open_notepad(self, content: str = ""):
        import subprocess
        import time
        import pyautogui

        # 打开记事本
        subprocess.run(["notepad.exe"], check=True)
        time.sleep(1)

        # 输入内容
        if content:
            pyautogui.typewrite(content)

        return {"success": True, "message": "记事本已打开并填充内容"}
```

### 2. 消息发送工具

```python
class MessagingTool:
    def execute(self, action: str, params: Dict, context: Dict):
        if action == "send_wechat":
            return self.send_wechat_message(
                params.get("content", ""),
                params.get("recipient", "")
            )
        elif action == "send_email":
            return self.send_email(params)

    def send_wechat_message(self, content: str, recipient: str):
        """通过微信API或自动化发送消息"""

        # 方案1: 使用微信API（如果有企业微信）
        if self.wechat_api_available:
            return self.send_via_wechat_api(content, recipient)

        # 方案2: 使用UI自动化
        return self.send_via_ui_automation(content, recipient)

    def send_via_ui_automation(self, content: str, recipient: str):
        """通过UI自动化发送微信消息"""

        # 1. 打开微信
        # 2. 搜索联系人
        # 3. 输入消息
        # 4. 发送

        return {"success": True, "message": "微信消息已发送"}
```

### 3. 文件操作工具

```python
class FileOperationTool:
    def execute(self, action: str, params: Dict, context: Dict):
        if action == "create_todo_file":
            return self.create_todo_file(params.get("todos", []))
        elif action == "save_screenshot":
            return self.save_screenshot(params.get("filename", ""))

    def create_todo_file(self, todos: List[str]):
        """创建TODO文件"""

        import json
        from datetime import datetime

        todo_data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "todos": todos,
            "created_at": datetime.now().isoformat()
        }

        filename = f"todo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(os.path.expanduser("~/Desktop"), filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(todo_data, f, ensure_ascii=False, indent=2)

        return {"success": True, "filepath": filepath}
```

## 🧠 上下文记忆系统

```python
class ContextMemory:
    def __init__(self):
        self.short_term_memory = {}
        self.long_term_memory = {}
        self.conversation_history = []

    def update_context(self, new_context: Dict):
        """更新上下文"""
        self.short_term_memory.update(new_context)

        # 提取重要信息存入长期记忆
        if "user_goal" in new_context:
            self.long_term_memory["current_goal"] = new_context["user_goal"]

    def get_relevant_context(self, current_input: str) -> Dict:
        """获取相关上下文"""
        return {
            "short_term": self.short_term_memory,
            "recent_history": self.conversation_history[-5:],
            "long_term": self.long_term_memory
        }
```

## 🔄 集成到现有架构

### 1. 修改语音控制流程

```python
class EnhancedVoiceController:
    def process_voice_command(self, command: str):
        """增强的语音命令处理"""

        # 1. 获取上下文
        context = self.memory.get_relevant_context(command)

        # 2. 智能意图分析
        intent_result = self.intent_analyzer.analyze_intent(command, context)

        # 3. 执行工作流
        if intent_result.workflow_steps:
            execution_result = self.workflow_engine.execute_workflow(intent_result.workflow)

            # 4. 更新上下文
            self.memory.update_context(execution_result.final_context)

            return execution_result
        else:
            # 回退到传统方式
            return self.traditional_command_handler(command)
```

### 2. 修改手势控制流程

```python
class EnhancedGestureController:
    def process_gesture_with_context(self, gesture_code: str, context: Dict):
        """基于上下文的手势处理"""

        # 检查是否有进行中的工作流
        if context.get("current_workflow"):
            return self.continue_workflow(gesture_code, context)
        else:
            # 传统手势处理
            return self.traditional_gesture_handler(gesture_code)
```

## 🚀 实施步骤

### Phase 1: 基础设施
1. 创建 `IntelligentAgent` 模块
2. 实现工具注册表
3. 建立上下文记忆系统

### Phase 2: 核心工具
1. 实现系统应用工具
2. 实现文件操作工具
3. 实现基础通信工具

### Phase 3: 高级功能
1. 实现微信/邮件集成
2. 实现网络API调用
3. 实现智能文本处理

### Phase 4: 集成测试
1. 集成到现有语音控制
2. 集成到现有手势控制
3. 端到端测试

## 📝 示例工作流

### 用户输入: "帮我记录今天的TODO，然后发给我"

1. **意图理解**: 识别出需要：创建TODO + 发送消息
2. **工作流规划**:
   - 步骤1: 生成TODO内容
   - 步骤2: 打开记事本
   - 步骤3: 输入TODO内容
   - 步骤4: 保存文件
   - 步骤5: 打开微信
   - 步骤6: 发送TODO内容
3. **执行**: 依次执行各步骤
4. **反馈**: "已完成TODO记录和发送"

## 🎯 关键优势

1. **灵活性**: 不再局限于预定义动作
2. **上下文感知**: 理解用户真实意图
3. **多步骤执行**: 支持复杂工作流
4. **工具扩展**: 轻松添加新工具
5. **学习能力**: 记忆用户偏好和历史