# YOLO-LLM 项目文档索引

## 项目概述

**YOLO-LLM** 是一个企业级AI智能控制平台，集成了计算机视觉、自然语言处理、语音识别和自动化控制技术，为用户提供手势控制、语音交互和智能工作流的完整解决方案。

### 🏗️ 项目类型
- **架构**: Monorepo (多部分项目)
- **组成部分**: 4个主要服务
- **主要语言**: Vue.js + Java + Python
- **架构模式**: 微服务架构

### ⚡ 快速参考

| 服务 | 技术栈 | 端口 | 主要功能 |
|------|--------|------|----------|
| **Frontend** | Vue 3 + Vite + Element Plus | 5173 | Web界面、实时监控 |
| **Backend** | Spring Boot + MyBatis-Plus | 8080 | 业务编排、API网关 |
| **AI Service** | FastAPI + YOLO + MediaPipe | 8000 | 计算机视觉、AI推理 |
| **Agent** | Python + PyAutoGUI | 本地 | 系统控制、手势识别 |
| **MCP Server** | FastAPI + 外部API | 8083 | 工具扩展、外部服务 |

### 🌟 核心特性
- **🤖 多模态AI融合**: YOLO目标检测 + MediaPipe手势识别 + LLM智能理解
- **🎮 直观交互体验**: 8种手势识别 + 中文语音控制 + 智能对话
- **🏢 企业级架构**: 微服务设计，高可用性，可扩展性
- **🛠️ 智能工作流**: MCP协议集成，自动化编排
- **🌐 现代化界面**: Vue.js实时监控，响应式设计

## 📚 生成的文档

### 📋 核心文档
- [**项目概览**](./project-overview.md) - 完整的项目介绍和功能说明
- [**综合架构文档**](./architecture-comprehensive.md) - 详细的系统架构设计
- [**源代码树分析**](./source-tree-analysis.md) - 带注释的项目结构说明
- [**集成架构**](./integration-architecture.md) - 服务间通信和集成模式
- [**开发指南**](./development-guide.md) - 完整的开发环境和工作流指南

### 🏗️ 架构文档
- [**architecture.md**](./architecture.md) - 系统架构设计 (现有)
- [**数据模型**](./data-models.md) - 数据库设计和实体关系 _(To be generated)_
- [**API契约**](./api-contracts.md) - 完整的API接口文档 _(To be generated)_

### 🛠️ 开发文档
- [**development-guide.md**](./development-guide.md) - 开发环境和最佳实践
- [**组件清单**](./component-inventory.md) - 可复用组件和模块 _(To be generated)_

### 🔧 运维文档
- [**部署指南**](./deployment-guide.md) - 生产环境部署指南 _(To be generated)_
- [**监控手册**](./monitoring-guide.md) - 系统监控和故障排查 _(To be generated)_

## 🎯 按部分组织的文档

### Frontend (Web前端)
**技术栈**: Vue 3 + Vite + Element Plus + Pinia

#### 📁 关键目录结构
```
frontend/
├── src/
│   ├── main.js                    # 🚀 应用入口点
│   ├── router/index.js           # 🛣️ Vue Router配置
│   ├── stores/                   # 🏪 Pinia状态管理
│   │   ├── config.js             # ⚙️ 配置状态管理
│   │   ├── gesture.js            # ✋ 手势状态管理
│   │   └── monitor.js            # 📈 监控状态管理
│   ├── services/                 # 🏢 业务逻辑服务
│   ├── components/               # 🧩 Vue组件库
│   └── views/                    # 📄 页面级组件
```

#### 🔧 主要组件
- **AppLayout.vue** - 应用布局组件 (导航 + 侧边栏)
- **GestureIndicator.vue** - 手势指示器 (实时状态显示)
- **MonitorPanel.vue** - 监控面板 (图表 + 性能指标)
- **ConfigPanel.vue** - 配置面板 (参数调整 + 设置)

#### 🌐 API集成
- **API客户端** - 基于Axios的HTTP服务
- **WebSocket服务** - 实时通信管理
- **状态管理** - Pinia stores for reactive data

### Backend (Spring Boot后端)
**技术栈**: Spring Boot 3.3.4 + Java 17 + MyBatis-Plus + MySQL

#### 📁 关键目录结构
```
backend/src/main/java/com/example/aiorchestrator/
├── Application.java              # 🚀 Spring Boot启动类
├── controller/                  # 🎛️ REST API控制器
│   ├── ConfigController.java    # ⚙️ 配置管理API
│   ├── LLMController.java       # 🤖 LLM集成API
│   ├── MonitorController.java   # 📈 系统监控API
│   └── MCPController.java       # 🛠️ MCP工具API
├── service/                     # 🏢 业务逻辑层
├── domain/                      # 📋 领域模型层
├── mapper/                      # 💾 数据访问层
└── dto/                         # 📦 数据传输对象
```

#### 🔌 核心API端点
- `GET /api/config` - 获取手势配置映射
- `POST /api/llm/gesture-analysis` - 手势意图分析
- `POST /api/llm/voice-command` - 语音命令解析
- `GET /api/monitor/status` - 系统健康状态
- `POST /api/audit/log` - 审计日志记录

#### 🏗️ 架构模式
- **分层架构**: Controller → Service → Mapper → Domain
- **依赖注入**: Spring构造器注入
- **数据传输对象**: DTO模式分离
- **策略模式**: 多LLM提供商支持

### AI Service (FastAPI AI服务)
**技术栈**: FastAPI + YOLOv8 + MediaPipe + DeepFace

#### 📁 关键目录结构
```
ai/
├── main.py                       # 🚀 FastAPI应用主入口
├── requirements.txt              # 📦 AI依赖包
├── enhanced_gesture_detector.py  # ✋ 增强手势检测器
├── pose_estimator.py             # 🧍 姿态估计器
├── emotion_detector.py           # 😊 情绪检测器
├── object_detector.py            # 🔍 对象检测器
├── inference_pipeline.py         # 🔗 推理管道
└── models/                       # 📁 AI模型文件
    ├── yolov8m.pt                # 🎯 YOLOv8对象检测模型
    └── yolov8m-pose.pt           # 🧍 YOLOv8姿态估计模型
```

#### 🤖 AI功能
- **对象检测**: YOLOv8m模型，多类目标识别
- **姿态估计**: YOLOv8m-pose，17点人体关键点
- **手势识别**: MediaPipe 0.10.9，21点手部跟踪
- **情绪识别**: DeepFace，面部表情分析

#### 🔄 实时处理
- **WebSocket端点**: `/ws/detect`, `/ws/analyze`, `/ws/gesture`
- **流式处理**: Base64图像数据实时分析
- **多客户端支持**: 独立的客户端处理器

### Agent (Python智能代理)
**技术栈**: Python + MediaPipe + PyAutoGUI + SpeechRecognition

#### 📁 关键目录结构
```
agent/
├── main.py                       # 🎯 主入口点
├── intelligent_controller.py     # 🧠 智能控制器
├── gesture_analyzer.py           # ✋ 手势分析器
├── speech_controller.py          # 🗣️ 语音控制器
├── gesture_router.py             # 🛣️ 手势路由器
├── context_manager.py            # 🌐 视觉上下文管理器
├── safety_confirmation.py        # 🛡️ 安全确认系统
├── config.yaml                   # 📝 主配置文件
└── requirements.txt              # 📦 Python依赖包
```

#### 🎮 核心功能
- **多模态输入处理**: 手势 + 语音 + 文本
- **智能路由系统**: 快速路径 (简单手势) / 慢速路径 (复杂手势)
- **安全机制**: 多级确认 + 危险操作拦截
- **系统控制**: 7种动作类型 (鼠标、键盘、窗口等)

#### 🛡️ 安全特性
- **多级确认**: 低风险(自动)、中风险(手势)、高风险(双重)、关键(三重)
- **危险模式检测**: 自动识别危险命令并要求额外确认
- **超时保护**: 确认请求超时自动取消

## 🔄 现有文档

### 📚 用户指南
- [**README.md**](../README.md) - 项目总览和快速开始
- [**gesture-guide.md**](./gesture-guide.md) - 手势识别与控制使用指南
- [**voice-guide.md**](./voice-guide.md) - 语音控制功能使用指南
- [**ai-features.md**](./ai-features.md) - AI功能详细说明
- [**llm-setup.md**](./llm-setup.md) - LLM配置指南
- [**agents.md**](./agents.md) - 智能代理设计说明

### 🔧 技术文档
- [**MCP-TOOLS-GUIDE.md**](../MCP-TOOLS-GUIDE.md) - MCP工具使用指南
- [**CLAUDE.md**](../CLAUDE.md) - AI助手开发指导原则

### 📖 各部分说明
- [**agent/README.md**](../agent/README.md) - Python智能代理说明
- [**ai/README.md**](../ai/README.md) - AI服务功能说明
- [**backend/README.md**](../backend/README.md) - Spring Boot后端说明
- [**frontend/README.md**](../frontend/README.md) - Vue.js前端说明
- [**mcp/README.md**](../mcp/README.md) - MCP服务器功能说明

## 🚀 快速开始

### 📋 环境要求
- **Python 3.8+** - AI服务和智能代理
- **Java 17+** - Spring Boot后端
- **Node.js 18+** - Vue.js前端
- **MySQL 8.0+** - 数据存储
- **摄像头设备** - 手势识别
- **麦克风** - 语音控制

### ⚡ 一键启动
```powershell
# Windows PowerShell
.\start-all.ps1

# 访问服务
# Web界面: http://localhost:5173
# 后端API: http://localhost:8080
# AI服务: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 🔧 手动启动
```bash
# 1. MCP服务器 (8083)
cd mcp && python main.py

# 2. 后端服务 (8080)
cd backend && mvn spring-boot:run

# 3. AI服务 (8000)
cd ai && python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload

# 4. 前端 (5173)
cd frontend && npm install && npm run dev

# 5. 代理 (可选)
cd agent && python main.py --realtime
```

## 🛠️ 开发工作流

### 🔍 探索代码库
- **Frontend**: `src/components/` - Vue组件, `src/stores/` - 状态管理
- **Backend**: `src/main/java/com/example/aiorchestrator/` - Spring Boot代码
- **AI Service**: 根目录 - FastAPI应用和AI模型
- **Agent**: 根目录 - Python智能代理代码

### 🧪 测试
- **Frontend**: `npm run test` - 单元测试, `npm run test:e2e` - E2E测试
- **Backend**: `mvn test` - JUnit测试, `mvn jacoco:report` - 覆盖率
- **AI Service**: `pytest tests/` - Python测试

### 📊 监控
- **健康检查**: `/actuator/health` (Backend), `/health` (AI/MCP)
- **API文档**: http://localhost:8000/docs (Swagger)
- **实时状态**: http://localhost:5173 (Web界面)

## 🔧 配置管理

### 🌍 环境变量
```bash
# 数据库
DB_URL=jdbc:mysql://localhost:3306/yolo_platform
DB_USER=root
DB_PASS=your_password

# LLM API (选择一个)
DEEPSEEK_API_KEY=your_deepseek_key
KIMI_API_KEY=your_kimi_key
QWEN_API_KEY=your_qwen_key

# MCP工具
NEWS_API_KEY=your_newsapi_key
WEATHER_API_KEY=your_weather_key
BREVO_API_KEY=your_email_key
```

### 📝 配置文件
- **Agent**: `agent/config.yaml` - 手势定义和行为映射
- **Backend**: `backend/src/main/resources/application.yml` - Spring Boot配置
- **Frontend**: `frontend/vite.config.js` - Vite构建配置
- **AI Service**: `ai/` - 模型路径和参数配置

## 🎯 使用场景

### 🏢 企业办公
- **无接触会议**: 手势控制PPT，语音记录要点
- **高效工作流**: 智能文件管理，自动化任务处理
- **信息助手**: 实时新闻摘要，智能问答

### 🎨 创意工作
- **设计辅助**: 手势切换工具，语音执行操作
- **内容创作**: 智能文案生成，素材搜索
- **演示控制**: 手势流程控制，智能问答

### 🏠 家庭使用
- **智能家居**: 语音控制家电，手势娱乐切换
- **教育学习**: 智能答疑，知识搜索
- **健康管理**: 运动识别，健康提醒

## 📈 技术特点

### 🚀 性能优化
- **AI模型加速**: TensorRT优化，GPU加速推理
- **低延迟通信**: WebSocket实时流，连接池优化
- **缓存策略**: 多级缓存，模型预加载
- **批处理**: 并行处理，吞吐量优化

### 🛡️ 安全设计
- **输入验证**: 严格的图像、语音、文本安全检查
- **权限控制**: RBAC角色访问控制
- **安全确认**: 多级手势确认，危险操作拦截
- **数据保护**: HTTPS传输，敏感数据加密

### 📊 监控运维
- **健康检查**: 多维度服务监控
- **性能指标**: 实时性能数据收集
- **日志聚合**: 结构化日志，集中管理
- **错误追踪**: 分布式链路追踪

## 🔮 扩展能力

### 🔌 插件系统
- **MCP协议**: 支持第三方工具插件
- **模型扩展**: 支持新AI模型热插拔
- **功能模块**: 可插拔功能组件

### 🌐 多语言支持
- **界面国际化**: Vue.js i18n支持
- **语音识别**: 多语言语音API
- **手势文化**: 文化差异手势适配

### ☁️ 云原生部署
- **容器化**: Docker + Kubernetes支持
- **微服务**: 水平扩展，负载均衡
- **云存储**: 对象存储集成

---

**🤖 这个索引文档是AI辅助开发的主要入口点，包含了完整的YOLO-LLM项目信息、架构设计、开发指南和使用说明。**

**📚 当创建brownfield PRD时，请将此index.md作为项目上下文输入，以便AI助手能够准确理解项目结构和现有功能。**

**🔗 项目仓库**: [GitHub Repository](https://github.com/your-repo/yolo-llm)

**📧 联系方式**: 如有问题，请查看项目README或提交Issue。