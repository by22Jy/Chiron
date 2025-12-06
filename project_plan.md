🚀 YOLO-LLM 智能工作流代理 (Smart Workflow Agent) 开发计划

📖 项目上下文 (Context for AI)

给 Cursor 的核心提示：
本项目正在从简单的“手势->按键映射”系统升级为“多模态智能代理系统”。
核心架构：

大脑 (SpringBoot): 负责接收用户指令(语音/手势)，调用 LLM (deepseek) 进行意图理解和任务拆解，生成工作流计划 (Workflow Plan)。

执行器 (Python Agent): 负责执行具体的工具调用 (打开应用、输入文本、发邮件)，并利用 YOLO/MediaPipe 提供视觉上下文。

通信: 通过 REST API (配置/命令) 和 WebSocket (实时状态/日志) 连接。

Phase 1: 核心架构升级 (Workflow Engine)

1.1 后端：智能意图理解层

[ ] 集成 LLM 服务: 在 SpringBoot 中封装 LLM 调用接口 (ChatClient)。

[ ] 设计 Prompt 模板: 创建用于"任务拆解"的 System Prompt。

Prompt for Cursor:
"在 backend 中创建一个 LlmService。我们需要一个 Prompt 模板，它接收用户的自然语言指令（如'打开记事本写日报'），并返回一个标准的 JSON 格式的工作流计划列表。JSON 应包含：tool_name, action, parameters。请帮我设计这个 Prompt 和对应的 Java 类结构。"

1.2 后端：工作流编排引擎

[ ] 定义工作流数据结构: 创建 Workflow, WorkflowStep, ExecutionResult 等实体。

[ ] 实现工作流执行逻辑: 接收 LLM 的 JSON 计划，按顺序分发给 Agent 或直接处理。

Prompt for Cursor:
"在 backend 创建 WorkflowEngine 服务。它需要解析 LLM 返回的 JSON 步骤列表。如果步骤是本地执行的（如数据库操作），直接执行；如果步骤需要 Agent 执行（如打开 App），将其转换为指令推送到 Python Agent。请设计这个分发逻辑。"

1.3 Agent：工具注册表 (Tool Registry)

[ ] 重构 Python Agent: 废弃硬编码的 if/else，建立动态工具系统。

[ ] 创建工具基类: BaseTool (name, description, execute方法)。

Prompt for Cursor:
"在 agent 目录下重构代码。创建一个 tools/ 目录和 BaseTool 抽象类。实现一个 ToolRegistry 类，可以动态注册和查找工具。所有的具体工具（如 SystemTool）都应继承自 BaseTool。"

Phase 2: 核心工具库实现 (The "Skills")

2.1 系统控制工具 (System Tools)

[ ] 实现 App 启动工具: 使用 subprocess 或 os.startfile。

[ ] 实现键盘/鼠标工具: 封装 pyautogui 为标准 Tool。

Prompt for Cursor:
"实现一个 SystemControlTool。功能包括：1. open_app(app_name): 根据预定义的路径字典启动应用；2. type_text(content): 模拟键盘输入。请确保添加错误处理，防止应用启动失败导致 Agent 崩溃。"

2.2 通信与办公工具 (Productivity Tools)

[ ] 实现模拟邮件/消息工具: (先做 Mock 或简单的 Webhook)。

[ ] 实现文件操作工具: 创建文件、写入内容、读取内容。

Prompt for Cursor:
"实现一个 FileTool，支持 create_file(path, content) 和 read_file(path)。然后实现一个 EmailTool，目前先通过打印日志模拟发送过程，但在结构上要预留真实的 SMTP 接口位置。"

Phase 3: 多模态感知与上下文 (Multimodal Context)

3.1 视觉上下文注入

[ ] YOLO 物体检测集成: 将 YOLO 检测到的物体列表存入 Agent 内存。

[ ] 视觉状态上报: Agent 定期（或触发时）将“当前看到的物体”上报给后端。

Prompt for Cursor:
"修改 agent/main.py。在主循环中，将 YOLO 检测到的 detected_objects (例如 ['cup', 'laptop']) 更新到一个全局的 ContextManager 中。当用户发送语音指令时，将这个视觉上下文一同发送给后端 LLM，以便 LLM 理解'打开它'指的是什么。"

3.2 路由策略 (Dual-Path)

[ ] 实现快慢通道路由: 区分“简单手势”和“复杂意图”。

Prompt for Cursor:
"在 Agent 端实现一个路由逻辑。如果检测到特定的快捷手势（如挥手），直接调用本地的 SystemControlTool（快通道）；如果接收到语音指令或复杂手势（如指物），则打包上下文发送给后端 LLM 进行规划（慢通道）。"

Phase 4: 用户体验与反馈 (UX & Feedback)

4.1 状态反馈机制

[ ] 增加 TTS 语音反馈: 让 Agent 会“说话”。

[ ] 增加视觉反馈: 在摄像头画面上绘制 Agent 的状态（思考中、执行中）。

Prompt for Cursor:
"在 Agent 中集成一个简单的 TTS 库（如 pyttsx3 或 Edge-TTS）。当工作流开始执行时，播报'正在为您处理...'；当任务完成时，播报执行结果。同时，使用 OpenCV 在视频帧的右上角显示当前 Agent 的状态文本。"

4.2 安全确认 (Human-in-the-loop)

[ ] 敏感操作确认机制: 删除、发送等操作需手势/语音确认。

Prompt for Cursor:
"为 EmailTool 添加一个 requires_confirmation 属性。在 WorkflowEngine 中，如果发现即将执行的工具需要确认，暂停执行，并通过 TTS 询问用户'确认发送吗？'，等待用户做一个'OK'手势后才继续执行。"

📝 调试与测试记录

[ ] 测试：简单指令 "打开记事本"

[ ] 测试：多步指令 "打开记事本，写入'Hello World'，然后保存"

[ ] 测试：视觉引用 "把这个(指着屏幕)截图保存"🚀 YOLO-LLM 智能工作流代理 (Smart Workflow Agent) 开发计划

📖 项目上下文 (Context for AI)

给 Cursor 的核心提示：
本项目正在从简单的“手势->按键映射”系统升级为“多模态智能代理系统”。
核心架构：

大脑 (SpringBoot): 负责接收用户指令(语音/手势)，调用 LLM (Kimi/Qwen) 进行意图理解和任务拆解，生成工作流计划 (Workflow Plan)。

执行器 (Python Agent): 负责执行具体的工具调用 (打开应用、输入文本、发邮件)，并利用 YOLO/MediaPipe 提供视觉上下文。

通信: 通过 REST API (配置/命令) 和 WebSocket (实时状态/日志) 连接。

Phase 1: 核心架构升级 (Workflow Engine)

1.1 后端：智能意图理解层

[ ] 集成 LLM 服务: 在 SpringBoot 中封装 LLM 调用接口 (ChatClient)。

[ ] 设计 Prompt 模板: 创建用于"任务拆解"的 System Prompt。

Prompt for Cursor:
"在 backend 中创建一个 LlmService。我们需要一个 Prompt 模板，它接收用户的自然语言指令（如'打开记事本写日报'），并返回一个标准的 JSON 格式的工作流计划列表。JSON 应包含：tool_name, action, parameters。请帮我设计这个 Prompt 和对应的 Java 类结构。"

1.2 后端：工作流编排引擎

[ ] 定义工作流数据结构: 创建 Workflow, WorkflowStep, ExecutionResult 等实体。

[ ] 实现工作流执行逻辑: 接收 LLM 的 JSON 计划，按顺序分发给 Agent 或直接处理。

Prompt for Cursor:
"在 backend 创建 WorkflowEngine 服务。它需要解析 LLM 返回的 JSON 步骤列表。如果步骤是本地执行的（如数据库操作），直接执行；如果步骤需要 Agent 执行（如打开 App），将其转换为指令推送到 Python Agent。请设计这个分发逻辑。"

1.3 Agent：工具注册表 (Tool Registry)

[ ] 重构 Python Agent: 废弃硬编码的 if/else，建立动态工具系统。

[ ] 创建工具基类: BaseTool (name, description, execute方法)。

Prompt for Cursor:
"在 agent 目录下重构代码。创建一个 tools/ 目录和 BaseTool 抽象类。实现一个 ToolRegistry 类，可以动态注册和查找工具。所有的具体工具（如 SystemTool）都应继承自 BaseTool。"

Phase 2: 核心工具库实现 (The "Skills")

2.1 系统控制工具 (System Tools)

[ ] 实现 App 启动工具: 使用 subprocess 或 os.startfile。

[ ] 实现键盘/鼠标工具: 封装 pyautogui 为标准 Tool。

Prompt for Cursor:
"实现一个 SystemControlTool。功能包括：1. open_app(app_name): 根据预定义的路径字典启动应用；2. type_text(content): 模拟键盘输入。请确保添加错误处理，防止应用启动失败导致 Agent 崩溃。"

2.2 通信与办公工具 (Productivity Tools)

[ ] 实现模拟邮件/消息工具: (先做 Mock 或简单的 Webhook)。

[ ] 实现文件操作工具: 创建文件、写入内容、读取内容。

Prompt for Cursor:
"实现一个 FileTool，支持 create_file(path, content) 和 read_file(path)。然后实现一个 EmailTool，目前先通过打印日志模拟发送过程，但在结构上要预留真实的 SMTP 接口位置。"

Phase 3: 多模态感知与上下文 (Multimodal Context)

3.1 视觉上下文注入

[ ] YOLO 物体检测集成: 将 YOLO 检测到的物体列表存入 Agent 内存。

[ ] 视觉状态上报: Agent 定期（或触发时）将“当前看到的物体”上报给后端。

Prompt for Cursor:
"修改 agent/main.py。在主循环中，将 YOLO 检测到的 detected_objects (例如 ['cup', 'laptop']) 更新到一个全局的 ContextManager 中。当用户发送语音指令时，将这个视觉上下文一同发送给后端 LLM，以便 LLM 理解'打开它'指的是什么。"

3.2 路由策略 (Dual-Path)

[ ] 实现快慢通道路由: 区分“简单手势”和“复杂意图”。

Prompt for Cursor:
"在 Agent 端实现一个路由逻辑。如果检测到特定的快捷手势（如挥手），直接调用本地的 SystemControlTool（快通道）；如果接收到语音指令或复杂手势（如指物），则打包上下文发送给后端 LLM 进行规划（慢通道）。"

Phase 4: 用户体验与反馈 (UX & Feedback)

4.1 状态反馈机制

[ ] 增加 TTS 语音反馈: 让 Agent 会“说话”。

[ ] 增加视觉反馈: 在摄像头画面上绘制 Agent 的状态（思考中、执行中）。

Prompt for Cursor:
"在 Agent 中集成一个简单的 TTS 库（如 pyttsx3 或 Edge-TTS）。当工作流开始执行时，播报'正在为您处理...'；当任务完成时，播报执行结果。同时，使用 OpenCV 在视频帧的右上角显示当前 Agent 的状态文本。"

4.2 安全确认 (Human-in-the-loop)

[ ] 敏感操作确认机制: 删除、发送等操作需手势/语音确认。

Prompt for Cursor:
"为 EmailTool 添加一个 requires_confirmation 属性。在 WorkflowEngine 中，如果发现即将执行的工具需要确认，暂停执行，并通过 TTS 询问用户'确认发送吗？'，等待用户做一个'OK'手势后才继续执行。"

📝 调试与测试记录

[ ] 测试：简单指令 "打开记事本"

[ ] 测试：多步指令 "打开记事本，写入'Hello World'，然后保存"

[ ] 测试：视觉引用 "把这个(指着屏幕)截图保存"