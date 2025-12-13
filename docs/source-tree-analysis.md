# YOLO-LLM 项目源代码树分析

## 🏗️ 项目整体结构

```
yolo-llm/                              # 项目根目录 (Monorepo)
├── README.md                          # 📋 企业级AI智能控制平台总览
├── CLAUDE.md                          # 🤖 AI助手开发指导原则
├── MCP-TOOLS-GUIDE.md                 # 🛠️ MCP工具使用指南
├── universal_computer_control.py      # 💻 电脑控制核心模块 (9种控制工具)
├── start-all.ps1                      # 🚀 Windows一键启动脚本
├── stop-all.ps1                       # 🛑 Windows一键停止脚本
├── .gitignore                         # ⚙️ Git忽略配置
│
├── agent/                             # 🎮 Python智能代理部分
│   ├── main.py                        # 🎯 主入口点 (手势+语音+系统控制)
│   ├── intelligent_controller.py      # 🧠 智能控制器 (AI集成+意图理解)
│   ├── gesture_analyzer.py            # ✋ 手势分析器 (MediaPipe集成)
│   ├── speech_controller.py           # 🗣️ 语音控制器 (SpeechRecognition)
│   ├── gesture_router.py              # 🛣️ 手势路由器 (快速/慢速路径分发)
│   ├── context_manager.py             # 🌐 视觉上下文管理器 (YOLO集成)
│   ├── safety_confirmation.py         # 🛡️ 安全确认系统 (多级确认机制)
│   ├── email_client.py                # 📧 邮件客户端 (邮件发送功能)
│   ├── api_config.json                # ⚙️ API配置文件
│   ├── config.yaml                    # 📝 主配置文件 (手势定义+行为映射)
│   ├── requirements.txt               # 📦 Python依赖包
│   ├── test_*.py                      # 🧪 测试文件集合
│   └── README.md                      # 📚 代理功能说明文档
│
├── backend/                           # 🔧 Spring Boot后端API部分
│   ├── pom.xml                        # 📦 Maven配置 (Spring Boot 3.3.4 + Java 17)
│   ├── src/main/java/com/example/aiorchestrator/
│   │   ├── Application.java           # 🚀 Spring Boot启动类
│   │   ├── controller/                # 🎛️ REST API控制器层
│   │   │   ├── ConfigController.java  # ⚙️ 配置管理API (/api/config)
│   │   │   ├── LLMController.java     # 🤖 LLM集成API (/api/llm/*)
│   │   │   ├── AuditController.java   # 📊 审计日志API (/api/audit/*)
│   │   │   ├── EventController.java   # 📡 事件处理API (/api/event)
│   │   │   ├── MonitorController.java # 📈 系统监控API (/api/monitor/*)
│   │   │   └── MCPController.java     # 🛠️ MCP工具API (/api/mcp/*)
│   │   ├── service/                   # 🏢 业务逻辑服务层
│   │   │   ├── ConfigService.java     # ⚙️ 配置管理服务
│   │   │   ├── LlmService.java        # 🤖 LLM编排服务
│   │   │   ├── MCPIntegrationService.java # 🛠️ MCP集成服务
│   │   │   ├── LogService.java        # 📊 日志记录服务
│   │   │   └── EventService.java      # 📡 事件处理服务
│   │   ├── domain/                    # 📋 数据模型/实体类
│   │   │   ├── Gesture.java           # ✋ 手势实体
│   │   │   ├── Mapping.java           # 🗺️ 手势-动作映射
│   │   │   ├── ActionEntity.java      # 🎬 动作实体
│   │   │   ├── LogEntry.java          # 📝 日志条目实体
│   │   │   └── Workflow.java          # 🔄 工作流实体
│   │   ├── mapper/                    # 💾 MyBatis-Plus数据访问层
│   │   │   ├── ConfigMapper.java      # ⚙️ 配置数据访问
│   │   │   ├── GestureMapper.java     # ✋ 手势数据访问
│   │   │   ├── MappingMapper.java     # 🗺️ 映射数据访问
│   │   │   └── LogMapper.java         # 📊 日志数据访问
│   │   └── dto/                       # 📦 数据传输对象
│   │       ├── ConfigResponseDto.java # ⚙️ 配置响应DTO
│   │       ├── GestureConfigDto.java  # ✋ 手势配置DTO
│   │       └── LogRequest.java        # 📝 日志请求DTO
│   └── README.md                      # 📚 后端功能说明
│
├── ai/                                # 🤖 FastAPI AI服务部分
│   ├── main.py                        # 🚀 FastAPI应用主入口
│   ├── requirements.txt               # 📦 AI依赖包 (YOLO+MediaPipe+DeepFace)
│   ├── enhanced_gesture_detector.py   # ✋ 增强手势检测器 (MediaPipe集成)
│   ├── simple_gesture_detector.py     # 📝 简易手势检测器 (OpenCV备用)
│   ├── pose_estimator.py              # 🧍 姿态估计器 (YOLOv8-pose)
│   ├── emotion_detector.py            # 😊 情绪检测器 (DeepFace集成)
│   ├── object_detector.py             # 🔍 对象检测器 (YOLOv8)
│   ├── inference_pipeline.py          # 🔗 推理管道 (多模态AI处理)
│   ├── utils/                         # 🛠️ AI工具函数
│   │   ├── image_utils.py             # 🖼️ 图像处理工具
│   │   └── model_utils.py             # 🧠 模型加载工具
│   ├── models/                        # 📁 AI模型文件目录
│   │   ├── yolov8m.pt                 # 🎯 YOLOv8对象检测模型
│   │   └── yolov8m-pose.pt            # 🧍 YOLOv8姿态估计模型
│   └── README.md                      # 📚 AI服务功能说明
│
├── frontend/                          # 🌐 Vue.js前端Web界面部分
│   ├── package.json                   # 📦 Node.js依赖配置 (Vue 3 + Vite)
│   ├── vite.config.js                 # ⚙️ Vite构建工具配置
│   ├── index.html                     # 🏠 HTML入口文件
│   ├── src/                           # 📁 Vue.js源代码目录
│   │   ├── main.js                    # 🚀 Vue应用入口点
│   │   ├── App.vue                    # 🖼️ 根组件
│   │   ├── router/                    # 🛣️ Vue Router路由配置
│   │   │   └── index.js               # 📍 路由定义 (首页、配置、监控等)
│   │   ├── stores/                    # 🏪 Pinia状态管理
│   │   │   ├── config.js              # ⚙️ 配置状态管理
│   │   │   ├── gesture.js             # ✋ 手势状态管理
│   │   │   └── monitor.js             # 📈 监控状态管理
│   │   ├── services/                  # 🏢 业务逻辑服务
│   │   │   ├── api.js                 # 🌐 HTTP API服务
│   │   │   ├── websocket.js           # 🔄 WebSocket服务
│   │   │   └── mobile.js              # 📱 移动端适配服务
│   │   ├── components/                # 🧩 Vue组件库
│   │   │   ├── AppLayout.vue          # 🎨 应用布局组件
│   │   │   ├── GestureIndicator.vue   # ✋ 手势指示器组件
│   │   │   ├── MonitorPanel.vue       # 📊 监控面板组件
│   │   │   └── ConfigPanel.vue        # ⚙️ 配置面板组件
│   │   ├── views/                     # 📄 页面级组件
│   │   │   ├── Home.vue               # 🏠 首页组件
│   │   │   ├── Gesture.vue            # ✋ 手势控制页面
│   │   │   ├── Monitor.vue            # 📈 系统监控页面
│   │   │   └── Config.vue             # ⚙️ 配置管理页面
│   │   ├── api/                       # 🌐 API客户端
│   │   │   └── index.js               # 📍 API调用封装
│   │   └── styles/                    # 🎨 全局样式
│   │       ├── main.css               # 📝 主样式文件
│   │       └── variables.css          # 🎨 CSS变量定义
│   └── README.md                      # 📚 前端功能说明
│
├── mcp/                               # 🛠️ MCP服务器部分
│   ├── main.py                        # 🚀 MCP服务器主入口
│   ├── requirements.txt               # 📦 MCP服务依赖
│   ├── services/                      # 🏢 MCP服务模块
│   │   ├── news_service.py            # 📰 新闻查询服务
│   │   ├── weather_service.py         # 🌤️ 天气服务
│   │   ├── email_service.py           # 📧 邮件发送服务
│   │   ├── computer_control.py        # 💻 电脑控制服务
│   │   └── file_manager.py            # 📁 文件管理服务
│   └── README.md                      # 📚 MCP服务说明
│
├── docs/                              # 📚 项目文档目录
│   ├── index.md                       # 🏠 文档主索引 (正在生成)
│   ├── README.md                      # 📋 文档导航
│   ├── architecture.md                # 🏗️ 系统架构设计
│   ├── agents.md                      # 🤖 智能代理设计
│   ├── gesture-guide.md               # ✋ 手势控制指南
│   ├── voice-guide.md                 # 🗣️ 语音控制指南
│   ├── ai-features.md                 # 🤖 AI功能说明
│   ├── llm-setup.md                   # 🔧 LLM配置指南
│   └── project-scan-report.json       # 📊 项目扫描状态报告
│
└── [其他配置和工具目录]
    ├── .bmad/                         # 🧠 BMAD框架配置
    ├── .claude/                       # 🤖 Claude AI配置
    ├── .vscode/                       # 💻 VS Code开发配置
    ├── test_files/                    # 🧪 测试文件
    └── logs/                          # 📝 日志文件目录
```

## 🔍 关键目录解析

### 🎮 Agent/ - 智能代理核心
- **核心功能**: 手势识别、语音控制、系统自动化
- **技术栈**: Python + MediaPipe + PyAutoGUI + SpeechRecognition
- **入口点**: `main.py --realtime` (实时手势识别)
- **安全机制**: 多级手势确认系统 + 危险操作拦截
- **集成点**: 与Backend API (端口8080) + AI Service (端口8000)

### 🔧 Backend/ - 企业级后端API
- **核心功能**: 配置管理、LLM编排、审计日志、系统监控
- **技术栈**: Spring Boot 3.3.4 + Java 17 + MyBatis-Plus + MySQL
- **端口**: 8080
- **架构模式**: 分层架构 (Controller → Service → Mapper → Domain)
- **API设计**: RESTful + 多LLM提供商集成 (Kimi, Qwen, GLM, DeepSeek)

### 🤖 AI/ - 多模态AI服务
- **核心功能**: 对象检测、姿态估计、手势识别、情绪分析
- **技术栈**: FastAPI + YOLOv8 + MediaPipe + DeepFace + OpenCV
- **端口**: 8000
- **实时能力**: WebSocket流式处理 + 实时图像分析
- **模型管理**: 预加载模型 + 全局实例共享

### 🌐 Frontend/ - 现代化Web界面
- **核心功能**: 实时监控、手势可视化、配置管理
- **技术栈**: Vue 3 + Vite + Element Plus + Pinia + WebSocket
- **端口**: 5173
- **架构模式**: Composition API + 模块化状态管理
- **UI设计**: Glass morphism现代设计 + 响应式布局

### 🛠️ MCP/ - 扩展工具服务
- **核心功能**: 新闻查询、天气服务、邮件发送、电脑控制
- **技术栈**: FastAPI + 外部API集成
- **端口**: 8083
- **协议支持**: Model Context Protocol (MCP)

## 🔄 服务间集成架构

```
┌─────────────────┐    HTTP/REST     ┌─────────────────┐
│   Frontend      │ ◄──────────────► │   Backend       │
│   (Vue.js)      │                  │  (Spring Boot)  │
│   Port: 5173    │                  │   Port: 8080    │
└─────────────────┘                  └─────────────────┘
         │                                   │
         │ WebSocket                           │ HTTP
         ▼                                   ▼
┌─────────────────┐    HTTP/REST     ┌─────────────────┐
│   AI Service    │ ◄──────────────► │   MCP Server    │
│   (FastAPI)     │                  │   (FastAPI)     │
│   Port: 8000    │                  │   Port: 8083    │
└─────────────────┘                  └─────────────────┘
         │
         │ HTTP/API Calls
         ▼
┌─────────────────┐
│   Agent         │
│   (Python)      │
│ 手势+语音+系统控制 │
└─────────────────┘
```

## 🎯 项目特色

1. **多模态AI集成**: 计算机视觉 + 自然语言处理 + 语音识别
2. **实时处理能力**: WebSocket流式处理 + 实时手势跟踪
3. **企业级架构**: 微服务架构 + 分层设计 + 安全机制
4. **跨平台支持**: Windows/Linux + Web/移动端适配
5. **可扩展设计**: MCP协议支持 + 模块化组件架构
6. **用户体验优先**: 现代UI设计 + 直观的交互方式

这个项目展现了一个完整的AI驱动的智能控制平台，从前端的实时可视化到后端的企业级API，再到AI服务的多模态处理，以及本地代理的精确控制，形成了一个端到端的智能控制系统生态。