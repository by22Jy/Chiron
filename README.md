# YOLO-LLM 企业级AI智能控制平台

## 🚀 项目简介

YOLO-LLM 是一个基于AI的企业级智能控制平台，结合计算机视觉、机器学习、MCP(模型上下文协议)和Web技术，实现手势识别、语音控制、电脑自动化和智能工作流的完整解决方案。

## 🏗️ 系统架构

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend     │    │   MCP Server    │
│   (Vue.js)      │◄──►│  (Spring Boot)  │◄──►│   (FastAPI)     │
│   Port: 5173    │    │   Port: 8080    │    │   Port: 8083    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Service    │    │     Agent       │    │ Computer Control│
│   (FastAPI)     │    │   (Python)      │    │   (Universal)   │
│   Port: 8000    │    │  手势+语音识别   │    │   9种控制工具    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## ⚡ 快速开始

### 环境要求

- **Python 3.8+**
- **Java 17+**
- **Node.js 18+**
- **MySQL 8.0+** (可选)
- **摄像头设备** (手势识别)
- **麦克风** (语音控制)

### 🚀 一键启动

#### Windows (PowerShell)
```powershell
.\start-all.ps1
```

#### Linux/Mac
```bash
chmod +x start-all.sh
./start-all.sh
```

### 🛠️ API配置

在启动前配置以下环境变量：

```bash
# MCP工具API密钥
export NEWS_API_KEY="your_newsapi_key"
export WEATHER_API_KEY="your_openweathermap_key"
export BREVO_API_KEY="your_brevo_smtp_key"

# LLM API密钥 (可选)
export KIMI_API_KEY="your_kimi_key"
export QWEN_API_KEY="your_qwen_key"
```

## 🌟 核心功能

### 🤖 MCP服务器 (端口8083)
- **新闻查询**: 实时获取全球新闻
- **天气服务**: 全球城市天气预报
- **邮件发送**: 企业级邮件发送
- **电脑控制**: 9种专业控制工具
  - 鼠标控制、键盘控制、屏幕操作
  - 文件管理、进程管理、系统操作
  - 应用管理、性能统计、截图功能

### 🎯 智能控制
- **手势识别**: 实时8种手势检测
- **语音控制**: 中文语音命令识别
- **电脑自动化**: 应用启动、窗口管理、文件操作
- **智能工作流**: 可定制的自动化流程

### 🌐 Web界面
- **Vue.js前端**: 响应式用户界面
- **实时监控**: 服务状态、性能指标
- **可视化**: 手势识别、语音控制可视化

## 📚 服务地址

启动完成后，可通过以下地址访问：

- **🔧 MCP服务器**: http://localhost:8083
- **📱 Web界面**: http://localhost:5173
- **🔧 后端API**: http://localhost:8080
- **🤖 AI服务**: http://localhost:8000
- **📚 API文档**: http://localhost:8000/docs
- **🏥 健康检查**: http://localhost:8083/health

## 🎮 使用方法

### 语音控制
```bash
cd agent
python voice_simple_final.py
```

### 手势控制
```bash
cd agent
python main.py --realtime
```

### 电脑控制测试
```bash
python universal_computer_control.py
```

## 🛑 停止服务

```powershell
# Windows
.\stop-all.ps1

# Linux/Mac
./stop-all.sh
```

## 📁 项目结构

```
yolo-llm/
├── README.md                 # 项目说明
├── CLAUDE.md                 # AI助手指导
├── MCP-TOOLS-GUIDE.md        # MCP工具使用指南
├── start-all.ps1            # 启动脚本
├── stop-all.ps1             # 停止脚本
├── frontend/                # Vue.js前端
├── backend/                 # Spring Boot后端
├── ai/                      # FastAPI AI服务
├── mcp/                     # MCP服务器
├── agent/                   # 手势/语音控制代理
├── universal_computer_control.py  # 电脑控制模块
├── docs/                    # 详细文档
├── test_files/              # 测试文件
└── logs/                    # 日志文件
```

## 🔧 开发指南

详细的开发指南请查看 [docs/](docs/) 目录：

- [docs/architecture.md](docs/architecture.md) - 系统架构
- [docs/gesture-guide.md](docs/gesture-guide.md) - 手势控制
- [docs/voice-guide.md](docs/voice-guide.md) - 语音控制
- [docs/ai-features.md](docs/ai-features.md) - AI功能
- [docs/llm-setup.md](docs/llm-setup.md) - LLM配置
- [docs/agents.md](docs/agents.md) - 智能代理

## 🎯 特性亮点

- ✅ **企业级架构**: 微服务架构，高性能，可扩展
- ✅ **智能识别**: 8种手势，中文语音控制
- ✅ **电脑控制**: 9种专业控制工具，跨平台支持
- ✅ **MCP集成**: 新闻、天气、邮件等外部服务
- ✅ **Web界面**: 现代化UI，实时监控
- ✅ **自动化**: 智能工作流，一键操作
- ✅ **跨平台**: Windows、macOS、Linux支持

## 📄 许可证

MIT License

---

**🚀 立即开始体验YOLO-LLM智能控制平台！**